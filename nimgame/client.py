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
welcome_msg = server_socket.recv(4096)
print welcome_msg

while True:
    command = raw_input('>')
    server_socket.send(command)
    response = server_socket.recv(4096)
    if "200 OK" in response:
        response = response[7:]
        print response
    elif "400 ERROR" in response:
        response = response[10:]
        print response
    else:
        print response

server_socket.close()
