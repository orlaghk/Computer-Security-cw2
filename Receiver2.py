from socket import *
import sys
import os


BUFF_SIZE = 1027

def main(argv):
    #parse command line arguements
    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])

    #create the socket and bind the port number to PORT
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    #open a new file that can be written to
    file = open(FILENAME, 'wb+')

    #empty array to hold the sequence numbers of previously received packets
    last_sequence = (0).to_bytes(2, 'big')

    packets_received = 0

    while True: #(recv):
        #receive a packet from the socket, store the payload and sender address
        recv = receiver_socket.recvfrom(BUFF_SIZE)
        #split the message and the sender address
        received_packet = recv[0]
        sender_address = recv[1]
        #seperate the sequence number, EOF flag and payload
        seq_num = received_packet[0:2]
        eof = int.from_bytes(received_packet[2:3], byteorder='big')
        payload = received_packet[3:]

        if seq_num == last_sequence: #if an incorrect packet has been received
            receiver_socket.sendto(last_sequence, sender_address) #send the previous sequence number/NAK
            continue

        else:
            if eof == 1: #if the latest packet received is the last packet
                packets_received += 1
                last_sequence = seq_num
                file.write(payload)
                ack = seq_num
                receiver_socket.sendto(ack, sender_address)
                print("END OF FILE")
                break

            packets_received += 1

            last_sequence = seq_num
            file.write(payload)
            ack = seq_num

            receiver_socket.sendto(ack, sender_address)
    #close the file and the socket.
    file.close()
    receiver_socket.close()


if __name__ == '__main__':
    main(sys.argv)
