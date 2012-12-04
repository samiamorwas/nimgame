import random


class Nimgame:

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.whose_turn = player1
        self.wait_player = player2
        self.num_sets = random.randint(3, 5)
        self.set_dict = self.fillSets()

    def fillSets(self):
        set_dict = {}
        for i in range(1, self.num_sets + 1):
            numItems = random.randint(1, 7)
            set_dict[i] = numItems

        return set_dict

    def remove(self, setChoice, numItems):
        done = True
        sets = self.set_dict.keys()

        if numItems <= self.set_dict[setChoice] and setChoice in sets:
            self.set_dict[setChoice] = self.set_dict[setChoice] - numItems
            for i in range(1, self.num_sets + 1):
                if self.set_dict[i] != 0:
                    done = False
            if done:
                return "202 GO"
            else:
                self.changeTurn()
                return "201 WT"

        else:
            return "400 ER"

    def changeTurn(self):
        if self.whose_turn == self.player1:
            self.whose_turn = self.player2
            self.wait_player = self.player1
        else:
            self.whose_turn = self.player1
            self.wait_player = self.player2
