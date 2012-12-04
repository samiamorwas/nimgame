import socket
import sys
import serverstatus

from thread import *
from threading import RLock
from nimgame import Nimgame
from player import Player

# Use a ReentrantLock for accessing shared data
lock = RLock()
# Store the username of each thread's human user
current_player = ""

# Attempt to create the server socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

print 'Socket created'

# Bind the server to the host and port given in serverstatus
try:
    server_socket.bind((serverstatus.host, serverstatus.port))
except socket.error:
    print 'Failed to bind socket to port ' + str(serverstatus.port)
    sys.exit()

# Begin listening, and buffer up to five requests to connect
server_socket.listen(5)
print 'Now listening on port ' + str(serverstatus.port)


def connectThread(client_socket):
    """Create a new thread for each connection."""

    client_socket.send(
        "200 OK Welcome to NimGame! Enter a command, or type 'help'.")

    # Communicate until client disconnects
    while True:
        try:
            command = client_socket.recv(4096)
            # Print help message
            if command == "help":
                help_msg = """
                      login - allows you to log in with a chosen name
                who - shows players who are available to play
                games - shows the ID and players for games currently running
                remove n s - removes n objects from set s (while in game)
                bye - exit the game server
                """
                client_socket.send(help_msg + "\nEnter a command")

            # Attempt to create a new username, as long as it is not taken,
            # create new player, set current_player for this thread, and update
            # player_list
            elif command == "login":
                client_socket.send("200 OK Enter your username.")
                username = client_socket.recv(4096)
                taken = False
                for player in serverstatus.player_list:
                    if player.username == username:
                        taken = True
                # Error if name is taken
                if taken:
                    client_socket.send(
                        "400 ER Username taken\nEnter a command")
                else:
                    # Get lock while updating server status
                    lock.acquire()
                    new_player = Player(username, client_socket, "available")
                    serverstatus.player_list.append(new_player)
                    lock.release()
                    current_player = username
                    client_socket.send(
                        "200 OK User registered.\nEnter a command")

            # Get list of games from server status, and send it to client
            elif command == "games":
                response = "200 OK "
                # Get lock while accessing shared data
                lock.acquire()
                for game in serverstatus.game_list:
                    response = response + "Game " + str(game.game_id) + " "
                    response = response + game.player1.username + " "
                    response = response + game.player2.username + "\n"
                client_socket.send(response)
                lock.release()

            # Get list of available players from server status,
            # and send it to client
            elif command == "who":
                response = "200 OK "
                lock.acquire()
                for player in serverstatus.player_list:
                    if player.status == "available":
                        response = response + player.username + "\n"
                client_socket.send(response)
                lock.release()

            # Attempt to start game with given player
            elif command.startswith("play"):
                opponent_name = command[5:]
                opponent = None
                # Player must be available and exist, and not be the client
                for player in serverstatus.player_list:
                    if player.username == opponent_name:
                        if player.username != current_player:
                            if player.status == "available":
                                opponent = player
                # Error if not found
                if opponent is None:
                    client_socket.send(
                        "400 ER Player is not available\nEnter a command")

                else:
                    # Acquire lock while updating server status
                    lock.acquire()
                    for player in serverstatus.player_list:
                        if player.username == current_player:
                            # Find client, then create game
                            game = Nimgame(
                                player, opponent, serverstatus.next_id)
                            serverstatus.next_id += 1
                            serverstatus.game_list.append(game)
                            player.make_busy()
                            opponent.make_busy()
                            lock.release()
                            # Lock must be released or all other clients will
                            # be blocked until the game is over
                            startGame(game)
                            lock.acquire()
                            # Reaquire lock after game ends, make players
                            # available, and delete the completed game and
                            # its observers
                            player.make_available()
                            opponent.make_available()
                            serverstatus.game_list.remove(game)
                            to_delete = 0
                            for i in serverstatus.observers:
                                if i == game.game_id:
                                    to_delete = i
                            if to_delete > 0:
                                del serverstatus.observers[to_delete]
                            lock.release()

            # Attempt to observe game
            elif command.startswith("observe"):
                game_to_watch = command[8:]
                game_to_watch = int(game_to_watch)
                exists = False
                # Determine if game exists
                for game in serverstatus.game_list:
                    if game_to_watch == game.game_id:
                        exists = True
                        # If it already has an observer list, just add client
                        # to it
                        if game.game_id in serverstatus.observers:
                            serverstatus.observers[game.game_id].append(
                                client_socket)
                        # Otherwise, create list, and add client
                        else:
                            serverstatus.observers[game.game_id] = []
                            serverstatus.observers[game.game_id].append(
                                client_socket)
                # Tell client to begin waiting for game updates
                if exists:
                    client_socket.send(
                        "201 WT Now observing game " + str(game_to_watch))
                # Or inform client of error
                else:
                    client_socket.send(
                        "400 ER Game does not exists\nEnter a command")

            # Disconnect from the server
            elif command == "bye":
                client_socket.send("200 OK Goodbye!")
                client_socket.close()

            # If remove command is processed here incorrectly, instead of in
            # the startGame method, request the client to resend the command
            elif command.startswith("remove"):
                client_socket.send("401 RS")

            # Send error for any unsupported commands
            else:
                client_socket.send(
                    "400 ER Command not recognized.\nEnter a command")

        # Track client disconnects
        except socket.error:
            print 'Client has disconnected'
            break

    client_socket.close()


def startGame(game):
    """Run the game between two players, using Nimgame class."""
    gameover = False
    # After challenge is sent, wait for response
    game.whose_turn.connection.send(
        "201 WT Waiting for " + game.wait_player.username)
    game.wait_player.connection.recv(4096)
    observers = []

    while not gameover:
        # Set the current player, and inform both players of the game state
        current_player = game.whose_turn
        wait_player = game.wait_player
        current_player.send("200 OK " + str(game.set_dict) + "\nYour turn")
        wait_player.send(
            "201 WT " + str(game.set_dict) + "\n" +
            current_player.username + "'s turn")
        # Find observers, and inform them of game state
        for i in serverstatus.observers:
            if i == game.game_id:
                observers = serverstatus.observers[game.game_id]

        for observer in observers:
            observer.send("201 WT " + str(game.set_dict) + "\n")

        move = current_player.connection.recv(4096)
        # Verify the remove command, and send it to the Nimgame
        if verifyMove(move, game):
            setChoice = int(move[7])
            numItems = int(move[9])
            response = game.remove(setChoice, numItems)
            # Inform players and observers when the game is over
            if response == "202 GO":
                gameover = True
                current_player.send("200 OK You win!")
                game.changeTurn()
                game.whose_turn.send("200 OK You lose...")
                for observer in observers:
                    observer.send(
                        "200 OK " + current_player.username + " wins!")
            # Inform current player that the move was processed
            else:
                current_player.send(response + " Move accepted")
        # Or send the current player and error message, and let them try again
        else:
            current_player.send("400 ER Illegal move")
    # Return to the main thread method when the game ends
    return


def verifyMove(move, game):
    """
    Verify the format and contents of a remove command, which must
    start with the word remove, then contain an integer which is a valid
    set number, and an integer which is a valid number of items to remove
    from that set.
    """
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
    # Server forever, creating a new thread for each connection
    client_socket, addr = server_socket.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    start_new_thread(connectThread, (client_socket,))

server_socket.close()
