class Player:

    def __init__(self, username, connection, status):
        self.username = username
        self.connection = connection
        self.status = status

    def send(self, message):
        self.connection.send(message)

    def make_busy(self):
        self.status = "busy"

    def make_available(self):
        self.status = "available"
