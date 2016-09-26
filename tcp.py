""" A simple TCP server/client pair.

    The application protocol is a simple format: For each file uploaded, the client first sends
    four (big-endian) bytes indicating the number of lines as an unsigned binary number.

    The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

    The server responds with "A" if it accepts the file, and "R" if it rejects it.

    Then the client can send the next file.
"""
__author__ = "Mark Sebern, Josiah Yoder, Phileus Fogg"

# import the "socket" module -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket
import struct
import time
import sys

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address to listen on when acting as server.
# The address '' means accept any connection for our "receive" port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the "other" ("server") host that should be connected to for "send" operations.
# When connecting on one system, use 'localhost'
# When "sending" to another system, use its IP address (or DNS name if there it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print("Unknown action: '{0}'".format(action))


# Send multiple messages over a TCP connection to a designated host/port.
# Receive a one-character response from the "server".
# Print the received response.
# Close the socket
# Return
def tcp_send(server_host, server_port):
    print("tcp_send: dst_host='{0}', dst_port={1}".format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input("Enter the number of lines you want to send (0 to exit):"))

    print("Now enter all the lines of your message")
    while num_lines != 0:
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # You will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        tcp_socket.sendall(b"\x00\x00")
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b"\x00" + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input("Enter the number of lines you want to send (0 to exit):"))

    tcp_socket.sendall(b"\x00\x00")
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b"\x00\x00")
    response = tcp_socket.recv(1)
    if response == b'Q':  # Note: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()

#new comment
# Listen for a TCP connection on a designated "listening" port
# Accept the connection, creating a connection socket
# Print the address and port of the sender
# Repeat until a zero-length message is received:
#  Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
#  Send a single-character response 'A' to indicate that the upload was accepted.
# Send a 'Q' to indicate a zero-length message was received.
# Close data connection.
def tcp_receive(listen_port):
    print("tcp_receive (server): listen_port={0}".format(listen_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(OTHER_HOST,listen_port)
    numberOfLines = getNumOfLines(tcp_socket)
    i = 1
    while numberOfLines != 0:
        listOfLinesInMessage = []
        readMessage(numberOfLines, listOfLinesInMessage, tcp_socket)
        tcp_socket.sendall(b'A')
        writeMessageToFile(listOfLinesInMessage, i)
        i += 1
        numberOfLines = getNumOfLines(tcp_socket)

    if numberOfLines == 0:
        tcp_socket.sendall(b'Q')
        tcp_socket.close()


"""
Author: Ben Ritter
Purpose: get the first 4 bytes and then convert them into a number to be passed to the other functions
Arguments: socket dataSocket
Return: the number of newlines as an int
"""
def getNumOfLines(dataSocket):
    number = b''
    for i in range(0,4):
        msg = next_byte(dataSocket)
        number += msg
    return int.from_bytes(number,'big')

"""
Author: Eric Nowac
Purpose: use the number found in the first four bytes (numOfNewLines) and read that amount of lines and add them to a list (listOfLines) to be saved later
Arguments: int numOfNewLines, empty list listOfLines, socket dataSocket
Return: nothing
"""
def readMessage(numOfNewLines, listOfLines, dataSocket):
    i = 0;
    while i < numOfNewLines:
        msg = next_byte(dataSocket)
        if len(listOfLines) - 1 < i :
            listOfLines.append(msg)
        else:
            listOfLines[i] += msg

        if msg == b'\n':
            i += 1

"""
Author: Eric Nowac
Purpose: print the message to a text file
Arguments: list listOfLines, int fileIndex
Return: nothing
"""
def writeMessageToFile(listOfLines, numberOfFile):
    file = open(str(numberOfFile) + ".txt","w")
    for bytes in listOfLines:
        file.write(bytes.decode())
    file.close()


# Read the next byte from the socket data_socket.
# The data_socket argument should be an open tcp data connection socket, not a tcp listening socket.
#
# Returns the next byte, as a bytes object of one character.
#
# If the byte is not yet available, this method blocks (waits)
#   until the byte becomes available.
# If there are no more bytes, this method blocks indefinitely.
def next_byte(data_socket):
    return data_socket.recv(1)


# Invoke the main method to run the program.
main()