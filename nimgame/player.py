class Player:
    """This class maintains the status of each human player."""

    def __init__(self, username, connection, status):
        """Set the username, connection, and status."""

        self.username = username
        self.connection = connection
        self.status = status

    def send(self, message):
        """Send a message through the player's socket."""

        self.connection.send(message)

    def make_busy(self):
        self.status = "busy"

    def make_available(self):
        self.status = "available"
