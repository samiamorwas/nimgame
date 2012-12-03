import socket
import sys
from thread import *

host = ''
port = 7777
player_list = {}

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

print 'Socket created'

try:
    server_socket.bind((host, port))
except socket.error:
    print 'Failed to bind socket to port ' + str(port)
    sys.exit()

server_socket.listen(5)
print 'Now listening on port ' + str(port)


def gameThread(client_socket):

    client_socket.send("Welcome to NimGame! Enter a command, or type 'help'.")

    while True:
        try:
            command = client_socket.recv(4096)
            if command == "help":
                help_msg = """
                login - allows you to log in with a chosen name
                remove n s - removes n objects from set s
                bye - exit the game server
                """
                client_socket.send(help_msg + "\nEnter a command")
            elif command == "login":
                client_socket.send("200 OK Enter your username.\n")
                username = client_socket.recv(4096)
                player_list[username] = "available"
                client_socket.send("200 OK User registered\nEnter a command")
            else:
                client_socket.send("400 ERROR Command not recognized.\nEnter a command")

        except socket.error:
            print 'Client has disconnected'
            break

    client_socket.close()

while True:
    client_socket, addr = server_socket.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    start_new_thread(gameThread, (client_socket,))

server_socket.close()
