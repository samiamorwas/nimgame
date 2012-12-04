"""Maintain server information that is shared between threads."""

# The host name and port number which the server is bound to
host = ''
port = 7777
# The list of players connected to the server
player_list = []
# The list of ongoing games
game_list = []
# The next unique identifier for a new game
next_id = 1
# The dictionary of observers, which maps game id's to a list of connections
# which are observer that game
observers = {}
