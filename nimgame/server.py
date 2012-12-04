import socket
import sys

from thread import *
from nimgame import Nimgame
from player import Player

host = ''
port = 7777
player_list = []

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


def connectThread(client_socket):

    client_socket.send(
        "200 OK Welcome to NimGame! Enter a command, or type 'help'.")

    while True:
        try:
            command = client_socket.recv(4096)
            if command == "help":
                help_msg = """
                    login - allows you to log in with a chosen name
                remove n s - removes n objects from set s (while in game)
                bye - exit the game server
                """
                client_socket.send(help_msg + "\nEnter a command")

            elif command == "login":
                client_socket.send("200 OK Enter your username.")
                username = client_socket.recv(4096)
                taken = False
                for player in player_list:
                    if player.username == username:
                        taken = True

                if taken:
                    client_socket.send(
                        "400 ER Username taken\nEnter a command")
                else:
                    new_player = Player(username, client_socket, "available")
                    player_list.append(new_player)
                    if len(player_list) == 2:
                        game = Nimgame(player_list[0], player_list[1])
                        player_list[0].make_busy()
                        player_list[1].make_busy()
                        startGame(game)
                        continue
                    else:
                        client_socket.send(
                        "201 WT User registered. Please wait")

            elif command == "bye":
                client_socket.send("200 OK Goodbye!")
                client_socket.close()

            elif command.startswith("remove"):
                client_socket.send("401 RS")

            else:
                client_socket.send(
                    "400 ER Command not recognized.\nEnter a command")

        except socket.error:
            print 'Client has disconnected'
            break

    client_socket.close()


def startGame(game):
    gameover = False

    while not gameover:
        current_player = game.whose_turn
        wait_player = game.wait_player
        current_player.send("200 OK " + str(game.set_dict) + "\nYour turn")
        wait_player.send(
            "201 WT " + str(game.set_dict) + "\n" +
            current_player.username + "'s turn")

        move = current_player.connection.recv(4096)
        if verifyMove(move, game):
            setChoice = int(move[7])
            numItems = int(move[9])
            response = game.remove(setChoice, numItems)
            if response == "202 GO":
                gameover = True
                current_player.send("201 WT You win!")
                game.changeTurn()
                game.whose_turn.send("201 WT You lose...")
            else:
                current_player.send(response + " Move accepted")
        else:
            current_player.send("400 ER Illegal move")

    game = Nimgame(current_player, wait_player)
    startGame(game)


def verifyMove(move, game):
    if not move.startswith("remove"):
        return False
    try:
        setChoice = int(move[7])
        numItems = int(move[9])
    except:
        return False
    if numItems > game.set_dict[setChoice]:
        return False
    if not setChoice in game.set_dict.keys():
        return False

    return True


while True:
    client_socket, addr = server_socket.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    start_new_thread(connectThread, (client_socket,))

server_socket.close()
