from socket import *
import sys
import os
from time import sleep


def main(argv):

    print('hello')

    BUFF_SIZE = 1024 #equivalent to payload length
    HEADER_SIZE = 3

    #getting the command line arguements
    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])

    

    senderSocket = socket(AF_INET, SOCK_DGRAM)#Create socket

    senderSocket.bind((HOST, PORT))

    file = open(FILE, 'rb')                                  #read the file (store it in file). 'r' means we read the file, 'b' means binary mode such >
    read_file = file.read(BUFF_SIZE)
    packet_no = 0                                               #track the current packet being delivered

    while (read_file):
        #if eof = 0 - not end of the fileSe
        #if eof = 1 - it is the end of the file
        end_of_file = (0).to_bytes(1, 'big')
        

        if (len(read_file) < BUFF_SIZE):
            end_of_file = (1).to_bytes(1, 'big')
            print("<END OF FILE>")
        
        sequence_number = packet_no.to_bytes(2, 'big')
        
        file_to_send = bytearray(BUFF_SIZE + HEADER_SIZE)
        file_to_send[0:2] = sequence_number                 #sequence number is 2 bytes long, starts from the index 0 and occupies bot>
        file_to_send[2:3] = end_of_file                     #end of file flag is 1 byte long and is directly after the sequence number, th>
        file_to_send[3:] = bytearray(read_file)             #the payload occupies the rest of the packet and starts after the end >

        senderSocket.sendto(file_to_send, (HOST, PORT))


        print("<PACKET %d HAS BEEN DELIVERED>"%packet_no)

        read_file = file.read(BUFF_SIZE)
        packet_no += 1

        sleep(0.001)
    
    file.close()
    senderSocket.close()
    print(packet_no)
    print('FILE HAS BEEN SENT')

if __name__ == "__main__":
    main(sys.argv)