import socket
import sys

# Attempt to create a stream socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket.'
    sys.exit()

# The desired host and port number are given on the command line
script, host, port = sys.argv
port = int(port)

# Connect to server, and begin waiting
server_socket.connect((host, port))
response = "201 WT"

while True:
    # When a 201 WT message is received, wait for further messages
    while "201 WT" in response:
        response = server_socket.recv(4096)
        message = response[7:]
        print message

    # Once a non-WT message is received, get desired input from the user,
    # send it to the server, and print the server's reply
    command = raw_input('>')
    if command == "" or command is None:
        continue
    server_socket.send(command)
    response = server_socket.recv(4096)
    # If 401 RS is received, there was a processing error on the server,
    # and the message must be resent. Then, enter the wait state until
    # the server replies.
    if response == "401 RS":
        server_socket.send(command)
        response = "201 WT"
        continue
    else:
        # Slice the code from the response, leaving the message to print
        message = response[7:]
        print message
        # Exit when the closing message is received
        if message == "Goodbye!":
            sys.exit()

server_socket.close()
