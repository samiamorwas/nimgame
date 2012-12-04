import random


class Nimgame:
    """
    This class maintains the state of a game of nim, and provides the logic
    needed to play the game out.
    """

    def __init__(self, player1, player2, game_id):
        """Initialize the players, turn order, id, and game state."""

        self.player1 = player1
        self.player2 = player2
        self.game_id = game_id
        self.whose_turn = player1
        self.wait_player = player2
        # Create a random number of sets, between 3 and 5
        self.num_sets = random.randint(3, 5)
        self.set_dict = self.fillSets()

    def fillSets(self):
        """Fill each set with a random number of object, between 1 and 7."""

        set_dict = {}
        for i in range(1, self.num_sets + 1):
            numItems = random.randint(1, 7)
            set_dict[i] = numItems

        return set_dict

    def remove(self, setChoice, numItems):
        """
        Remove the given number of items from the given set, then check
        if the game is over.
        """

        done = True

        self.set_dict[setChoice] = self.set_dict[setChoice] - numItems
        for i in range(1, self.num_sets + 1):
            if self.set_dict[i] != 0:
                done = False
        if done:
            return "202 GO"
        else:
            self.changeTurn()
            return "201 WT"

    def changeTurn(self):
        """Change which player is currently taking his turn."""

        if self.whose_turn == self.player1:
            self.whose_turn = self.player2
            self.wait_player = self.player1
        else:
            self.whose_turn = self.player1
            self.wait_player = self.player2
