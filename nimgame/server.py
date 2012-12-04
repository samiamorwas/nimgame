import socket
import sys
import serverstatus

from thread import *
from threading import RLock
from nimgame import Nimgame
from player import Player

lock = RLock()
current_player = ""

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

print 'Socket created'

try:
    server_socket.bind((serverstatus.host, serverstatus.port))
except socket.error:
    print 'Failed to bind socket to port ' + str(serverstatus.port)
    sys.exit()

server_socket.listen(5)
print 'Now listening on port ' + str(serverstatus.port)


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
                for player in serverstatus.player_list:
                    if player.username == username:
                        taken = True
                if taken:
                    client_socket.send(
                        "400 ER Username taken\nEnter a command")
                else:
                    lock.acquire()
                    new_player = Player(username, client_socket, "available")
                    serverstatus.player_list.append(new_player)
                    lock.release()
                    current_player = username
                    client_socket.send(
                        "200 OK User registered.\nEnter a command")

            elif command == "games":
                response = "200 OK "
                lock.acquire()
                for game in serverstatus.game_list:
                    response = response + "Game " + str(game.game_id) + " "
                    response = response + game.player1.username + " "
                    response = response + game.player2.username + "\n"
                client_socket.send(response)
                lock.release()

            elif command == "who":
                response = "200 OK "
                lock.acquire()
                for player in serverstatus.player_list:
                    if player.status == "available":
                        response = response + player.username + "\n"
                client_socket.send(response)
                lock.release()

            elif command.startswith("play"):
                opponent_name = command[5:]
                opponent = None
                for player in serverstatus.player_list:
                    if player.username == opponent_name:
                        if player.username != current_player:
                            opponent = player

                if opponent is None:
                    client_socket.send(
                        "400 ER Player does not exist\nEnter a command")

                else:
                    lock.acquire()
                    for player in serverstatus.player_list:
                        if player.username == current_player:
                            game = Nimgame(
                                player, opponent, serverstatus.next_id)
                            serverstatus.next_id += 1
                            serverstatus.game_list.append(game)
                            player.make_busy()
                            opponent.make_busy()
                            lock.release()
                            startGame(game)

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
