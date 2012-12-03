import random


class Nimgame:

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.whoseTurn = player1
        self.numSets = random.randint(3, 5)
        self.setDict = self.fillSets()

    def fillSets(self):
        setDict = {}
        for i in range(1, self.numSets + 1):
            numItems = random.randint(1, 7)
            setDict[i] = numItems

        return setDict

    def remove(self, setChoice, numItems):
        done = True

        if numItems <= self.setDict[setChoice]:
            self.setDict[setChoice] = self.setDict[setChoice] - numItems
            for i in range(1, self.numSets + 1):
                if self.setDict[i] != 0:
                    done = False
            if done:
                return "201 GAMEOVER"
            else:
                self.changeTurn()
                return "200 OK"

        else:
            return "400 ERROR"

    def changeTurn(self):
        if self.whoseTurn == self.player1:
            self.whoseTurn = self.player2
        else:
            self.whoseTurn = self.player1
