from socket import *
import sys
import os
import time

BUFF_SIZE = 1024 #Buffer size
HEADER_SIZE = 3 #Size of header

def main(argv):

    #command line arguements
    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    TIMEOUT = int(os.path.basename(argv[4])) / 1000 #in miliseconds


    sender_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    file = open(FILE, 'rb') #open the file to be read
    read_file = file.read(BUFF_SIZE) #read the file in chunks of size 1024

    packet_no = 1 #keep track of the packet being sent, used to determine the sequence number of the packet

    re_transmit = 0 #Track retransmissions
    file_size = 0 #Track the size of the file, needed to calculate throughput

    start_time = time.time()

    while(read_file): #while read_file has data
        if (len(read_file) < BUFF_SIZE): #if the length of read_file is less than BUFF_SIZE that indicates its the fin>
            break #break out of the while loop

        print("SEND PACKET %d"%packet_no)
        seq_num = packet_no.to_bytes(2, byteorder='big') #store the sequence number
        eof = (0).to_bytes(1, byteorder='big') #EOF flag
        payload = bytearray(read_file) #payload as bytes

        send_file = bytearray(HEADER_SIZE + BUFF_SIZE) #create the packet called send_file
        send_file[0:2] = seq_num
        send_file[2:3] = eof
        send_file[3:] = payload

        sender_socket.sendto(send_file, (HOST, PORT)) #send the packet to the receiver
        print("SENT PACKET %d"%packet_no)

        correctAck = False
        receiveAck = False

        while (correctAck == False): #while correctAck is False
            try:
                sender_socket.settimeout(TIMEOUT) #set the socket to timeout after TIMEOUT seconds
                ack, sender_addr = sender_socket.recvfrom(2) #receive in a 2 byte packet from the socket
                print("RECEIVED ACK %d"%packet_no)
                ack = ack[0:2] #make sure to store only the first 2 bytes of the ACK packet
                print("ACK %d"%packet_no)
                receiveAck = True #we have no received the ack
                print('ack received %d'%packet_no)

            except timeout: #if the socket times out, keep receiveAck as false and resend the packet (send_file)
                receiveAck = False
                sender_socket.sendto(send_file, (HOST, PORT))
                print("TIMEOUT %d"%packet_no)
                re_transmit += 1 #due to retransmissions, add one to re_transmit

            if (receiveAck == True): #if we have received an ACK and it is the correct ACK
                if (ack == seq_num):
                    correctAck = True
                    break

        print("update read_file")
        file_size += len(read_file) #update file size
        packet_no += 1 #update the packet counter
        read_file = file.read(BUFF_SIZE) #read in the next 1024 bytes of the file.

    if (len(read_file) < BUFF_SIZE): #if the lenght of read_file is smaller than the BUFF_SIZE

        #store the sequence number of the packet, set the EOF flag to 1 to indicate it is the last packet
        seq_num = packet_no.to_bytes(2, byteorder='big')
        print("seq_num: %d"%seq_num)
        eof = (1).to_bytes(1, byteorder='big')
        payload = bytearray(read_file)

        #create the final packet
        send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
        send_file[0:2] = seq_num
        send_file[2:3] = eof
        send_file[3:] = payload
        print("FINAL PACKET %d"%packet_no)

        sender_socket.sendto(send_file, (HOST, PORT)) #send the packet to the receiver

        while (correctAck == False):
            try:
                sender_socket.settimeout(TIMEOUT)
                ack, sender_addr = sender_socket.recvfrom(2)
                ack = ack[0:2]
                receiveAck = True
            except timeout:
                receiveAck = False
                sender_socket.sendto(send_file, (HOST, PORT))
                print("TIMEOUT2 %d"%packet_no)
                re_transmit += 1
            if receiveAck == True:
                if ack == seq_num:
                    correctAck = True
                    break

        file_size += len(read_file)
        packet_no += 1


    total_time_taken = time.time() - start_time #calculate total runtime of the program once all packets sent
    file_size_kb = file_size / 1000
    throughput = round(file_size_kb / total_time_taken) #calculate throughput

    print("Number of retransmissions: " +str(re_transmit) + ", Throughput: " + str(throughput)) #necessary output
    print(f'{re_transmit}, {throughput}')

    file.close() #close file
    sender_socket.close() #close socket



if __name__ == "__main__":
    main(sys.argv)
  
    





