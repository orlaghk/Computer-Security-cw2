from socket import *
import os
import sys

BUFF_SIZE = 1027

#this function will seperate the header information from the payload
def unpack_packet(packet):
    seq_num = int.from_bytes(packet[0:2], 'big')
    eof = int.from_bytes(packet[2:3], 'big')
    payload = packet[3:]
    return seq_num, eof, payload

def main(argv):

    #parse command line arguements
    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])

    #create the socket and bind the port number to the socket
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    #open a new file that can be written to
    file = open(FILENAME, 'wb+')

    #track the expected sequence number to be received
    expected_seqnum = 1

    #print(f'ready to receive packets')

    while True:
        #receive a packet from the socket
        recv = receiver_socket.recvfrom(BUFF_SIZE)

        #store the message, and the sender address seperately
        recv_packet = recv[0]
        sender_addr = recv[1]

        #unpack the packet and split the sequence number, EOF flag and payload into seperate variables
        seq_num, eof, payload = unpack_packet(recv_packet)

        #print(f'received seq_num is {seq_num}, expected seq_num is = {expected_seqnum}')

        #if the sequence number from the packet is not the expected sequence number
        if seq_num != expected_seqnum:
            expected_seqnum_bytes = (expected_seqnum - 1).to_bytes(2, 'big')
            receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
            continue
        #if it is the expected sequence number
        else:
            #if it is the last packet
            if eof == 1:
                file.write(payload) #write data to the file
                expected_seqnum_bytes = expected_seqnum.to_bytes(2, 'big')
                receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
                receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
                receiver_socket.sendto(expected_seqnum_bytes, sender_addr)

                print('END OF FILE')
                expected_seqnum += 1
                break #break out of the while loop

            file.write(payload) #write the data to the file
            expected_seqnum_bytes = expected_seqnum.to_bytes(2, 'big')
            receiver_socket.sendto(expected_seqnum_bytes, sender_addr) #send an ACK back to the sender

        expected_seqnum += 1 #iterate the expected sequence number

    file.close() #close the file
    receiver_socket.close() #close the socket

if __name__ == '__main__':
    main(sys.argv)