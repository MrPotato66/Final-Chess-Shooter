from random import randint


class Game:
    def __init__(self, identity):
        self.id = identity
        self.wins = [0, 0]
        self.p0Went = False
        self.p1Went = False
        self.moves = [None, None]
        self.ready = False
        self.priority = randint(0, 1)
        self.knowledge = 0
        self.rounds = 0

    def set_priority(self):
        self.rounds = self.rounds + 1
        self.priority = randint(0, 1)
        self.knowledge = (self.rounds//2) % 2

    # I think I can delete this function
    def get_player_move(self, player):
        return self.moves[player]

    def play(self, player, move):
        self.moves[player] = move
        if player == 0:
            self.p0Went = True
        else:
            self.p1Went = True

    def connected(self):
        return self.ready

    def bothWent(self):
        return self.p0Went and self.p1Went

    def resetWent(self):
        self.p0Went = False
        self.p1Went = False
        self.moves = [None, None]
        print('We are resetting the moves in the game')


class Movement:

    def __init__(self, nature, origin, destination):
        self.nature = nature
        self.origin = origin
        self.destination = destination
        self.reset = False

    def print_move(self, color):
        if self.nature == 'moving':
            print(color + ': Piece located at ' + str(self.origin) + ' is moving to ' + str(self.destination))
        elif self.nature == 'shooting':
            print(color + ': Piece located at ' + str(self.origin) + ' is shooting at ' + str(self.destination))
        else:
            print('Movement\'s nature is unknown')

    def resetMove(self):
        self.nature = 'unknown'
        self.origin = (-1, -1)
        self.destination = (-1, -1)
        self.reset = False
        print('We are resetting the move')

    def primordial(self):
        return (self.nature == 'unknown') and (self.origin == (-1, -1)) and (self.destination == (-1, -1)) \
               and not self.reset
