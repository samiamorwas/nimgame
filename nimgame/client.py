import socket
import sys

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket.'
    sys.exit()

script, host, port = sys.argv
port = int(port)

server_socket.connect((host, port))
response = "201 WT"

while True:
    while "201 WT" in response:
        response = server_socket.recv(4096)
        message = response[7:]
        print message

    command = raw_input('>')
    if command == "" or command is None:
        continue
    server_socket.send(command)
    response = server_socket.recv(4096)
    if response == "401 RS":
        server_socket.send(command)
        response = "201 WT"
        continue
    else:
        message = response[7:]
        print message
        if message == "Goodbye!":
            sys.exit()

server_socket.close()
