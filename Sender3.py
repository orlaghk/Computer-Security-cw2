from socket import *
import sys
import os
import time
import math

BUFF_SIZE = 1024
HEADER_SIZE = 3

#funtion to create the packets, with correct sequence number, EOF flag and data
def make_packet(data, sequence_number, eof):
    sequence_num = sequence_number.to_bytes(2, 'big')
    end_of_file = eof.to_bytes(1, 'big')
    payload = bytearray(data)

    send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
    send_file[0:2] = sequence_num
    send_file[2:3] = end_of_file
    send_file[3:] = payload

    return send_file

def main(argv):
    #command line arguements
    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    TIMEOUT = int(os.path.basename(argv[4])) / 1000 #time in miliseconds
    WINDOW = int(os.path.basename(argv[5])) #window size (N)

    sender_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    sender_socket.setblocking(0) #set the socket to non-blocking

    file = open(FILE, 'rb') #open the file to be read

    #calculate the total number of packets needed to send all the data of the image
    total_packets = math.ceil(os.path.getsize(FILE) / BUFF_SIZE)

    base = 1
    next_seq = 1

    true_start = time.time()

    while next_seq != total_packets: #Loops through until we reach the final packet
        try:
            resend_packets = [] #incase of timeout, resend the packets that have been sent
            while (next_seq < base + WINDOW) and (next_seq != total_packets):
                read_file = file.read(BUFF_SIZE) #read in 1024 bytes of the file
                send_file = make_packet(read_file, next_seq, 0) #create the packet

                resend_packets.append(send_file) #append packet to array incase of resend

                sender_socket.sendto(send_file, (HOST, PORT)) #send the packet to receiver

                if base == next_seq: #if the first packet in the window
                    sender_socket.settimeout(TIMEOUT) #start the timer
                next_seq += 1


            receiveAck = False
            correctAck = False
            while (correctAck == False): #while the correct ACK has not been received
                try:
                    base, sender_addr = sender_socket.recvfrom(2) #receive 2 byte packet from the socket

                    base = int.from_bytes(base, 'big') + 1
                    receiveAck = True


                    #if base is equal to next_seq, that means all the packets have been received by the receiver
                    if (base == next_seq) and (receiveAck == True):
                        #stop the timer
                        sender_socket.settimeout(0)
                        correctAck = True


                        break
                    else: #otherwise
                        #restart the timer

                        sender_socket.settimeout(TIMEOUT)
                        continue

                except timeout: #if the socket timer runs out

                    #resend all the packets
                    for packet in resend_packets:
                        sender_socket.sendto(packet, (HOST, PORT))

                    continue

        except: #if an error occurs, restart the while loop.
            continue

    #if there is only the final packet left to send


    try:
        if (next_seq == total_packets):
            read_file = file.read(BUFF_SIZE)
            send_file = make_packet(read_file, next_seq, 1)
            sender_socket.sendto(send_file, (HOST, PORT))
            if base == next_seq:
                 sender_socket.settimeout(TIMEOUT)
            next_seq += 1

            receiveAck = False
            correctAck = False
            while (correctAck == False):
                try:
                    base, sender_addr = sender_socket.recvfrom(2)
                    base = int.from_bytes(base, 'big') + 1
                    receiveAck = True
                    if (base == next_seq) and (receiveAck == True):
                        sender_socket.settimeout(0)
                        correctAck = True

                    else:
                        sender_socket.settimeout(TIMEOUT)
                except timeout:
                    sender_socket.sendto(send_file, (HOST, PORT))
                    continue

    except:
        print('')

    file.close() #close the file
    sender_socket.close() #close the socket

    total_time = time.time() - true_start
    throughput = round((os.path.getsize(FILE)/1000) / total_time)

    print(throughput)
        
            
        


if __name__ == '__main__':
    main(sys.argv)