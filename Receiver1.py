from socket import *
import sys
import os

BUFF_SIZE = 1027 #same as payload size + header size 

def main(argv):

    #Track
    packets_received = 0

    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])

    receiver_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    receiver_socket.bind(('localhost', PORT)) #bind socket to the port

    file = open(FILENAME, 'wb+') #open a file ready to write to
    print('FILE OPENED')

    received_packet,address = receiver_socket.recvfrom(BUFF_SIZE) #store the packet received from socket
    print('PACKET RECEIVED')

    while True:#while there is a received packet


        packets_received += 1
        received_packet_bytes = bytearray(received_packet[0]) #store the payload data of the packet
        print('PACKET RECEIVED NO', packets_received)
        end_of_file = received_packet_bytes[2]

        payload_data = received_packet_bytes[3:]

        if end_of_file == 1: #if the end of the file has been reached.
            file.write(payload_data)
            file.close
            print('<FILE HAS BEEN TRANSFERRED CORRECTLY>')
            break

        file.write(payload_data)
        received_packet,address = receiver_socket.recvfrom(BUFF_SIZE) #receive the next packet from the socket.

        

    print("<TOTAL PACKETS RECEIVED %d"%packets_received)
    file.close()
    receiver_socket.close()

if __name__ == "__main__":
    main(sys.argv)
        











