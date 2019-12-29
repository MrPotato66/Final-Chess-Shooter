import pygame
from os import getcwd, chdir
from Game import Movement

directory = getcwd()
chdir(directory + '/Images')

pygame.init()


class Color:

    def __init__(self, opposite, ownPieces):
        self.opposite = opposite
        self.ownPieces = ownPieces


rows = 8
dist = 50
width = rows*dist
height = rows*dist
disp_width = width + 200
disp_height = height
column_center = (width+disp_width)//2

backWhite = (250, 236, 192)
backBrown = (206, 159, 96)
whiteChosen = (249, 177, 113)
blackChosen = (224, 141, 58)
whiteAiming = (135, 239, 137)
blackAiming = (55, 149, 53)
background = (81, 90, 90)

whiteKingImg = pygame.image.load('White King.png')
blackKingImg = pygame.image.load('Black King.png')
whiteSquireImg = pygame.image.load('White Squire.png')
blackSquireImg = pygame.image.load('Black Squire.png')
whiteShooterImg = pygame.image.load('White Shooter.png')
blackShooterImg = pygame.image.load('Black Shooter.png')
bulletImg = pygame.image.load('Bullet.png')

kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
shooterMoves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
squireMoves = [(-2, 0), (-1, -1), (0, -2), (1, -1), (2, 0), (1, 1), (0, 2), (-1, 1)]
shooterAiming = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

myfont = pygame.font.SysFont('Arial', 10, True)
text_font = pygame.font.SysFont('Arial', 20)


white = Color('temp', [])
black = Color(white, [])
empty = Color('empty', [])
white.opposite = black
empty.opposite = empty


class Piece:

    def __init__(self, x, y, moves, color, img):
        self.x = x
        self.y = y
        self.alive = True
        self._moves = moves
        self._img = img
        self.chosen = False
        self._color = color
        self._color.ownPieces.append(self)
        self.ownInd = len(self._color.ownPieces) - 1

    def valid_space(self, b):
        pos = []
        dim = len(b)
        for dl in self._moves:
            dx, dy = dl
            if 0 <= (self.x + dx) < dim and 0 <= (self.y + dy) < dim:
                if b[self.x + dx][self.y + dy][0] != self._color:
                    pos.append((self.x + dx, self.y + dy))
        return pos

    def move(self, i, j, b):
        if (i, j) in self.valid_space(b):
            b[self.x][self.y] = (empty, 0)
            col, ind = b[i][j]
            self.x = i
            self.y = j
            if col == self._color.opposite:
                self._color.opposite.ownPieces[ind].alive = False
            b[i][j] = (self._color, self.ownInd)

    def drawPossibleMoves(self, surface, b):
        for pos in self.valid_space(b):
            i, j = pos
            if (i + j) % 2 == 0:
                pygame.draw.rect(surface, whiteChosen, (i * dist, j * dist, dist, dist))
            else:
                pygame.draw.rect(surface, blackChosen, (i * dist, j * dist, dist, dist))


class King(Piece):

    def __init__(self, x, y, color, image):
        Piece.__init__(self, x, y, kingMoves, color, image)
        textColor = 'White'
        if self._color == black:
            textColor = 'Black'
        print('A ' + textColor + ' King has been created')

    def draw(self, surface):
        if self.alive:
            surface.blit(self._img, (self.x * dist, self.y * dist))


class Squire(Piece):

    def __init__(self, x, y, color, img):
        Piece.__init__(self, x, y, squireMoves, color, img)
        self.shield = 3
        textColor = 'White'
        if self._color == black:
            textColor = 'Black'
        print('A ' + textColor + ' Squire has been created')

    def draw(self, surface):
        if self.alive:
            surface.blit(self._img, (self.x * dist, self.y * dist))
            shieldLevel = myfont.render(str(self.shield), True, (0, 0, 0))
            surface.blit(shieldLevel, (self.x * dist, self.y * dist + 40))


class Shooter(Piece):

    def __init__(self, x, y, color, img):
        Piece.__init__(self, x, y, shooterMoves, color, img)
        self.ammo = 5
        self.aimingSpots = shooterAiming
        textColor = 'White'
        if self._color == black:
            textColor = 'Black'
        print('A ' + textColor + ' Shooter has been created')

    def valid_aiming(self):
        spots = []
        for pos in shooterAiming:
            i, j = pos
            if 0 <= (self.x + i) < rows and 0 <= (self.y + j) < rows:
                spots.append((i, j))
        return spots

    def draw(self, surface):
        if self.alive:
            surface.blit(self._img, (self.x * dist, self.y * dist))
            ammoDisp = myfont.render(str(self.ammo), True, (0, 0, 0))
            surface.blit(ammoDisp, (self.x * dist, self.y * dist))

    def drawAiming(self, surface):
        for pos in self.valid_aiming():
            i, j = pos
            biais0, biais1 = biais(i, j)
            pygame.draw.circle(surface, (0, 0, 255), (self.x*dist + biais0, self.y*dist + biais1), 3)


class Bullet:

    def __init__(self, x, y, dirnx, dirny, color, img):
        self.x = x
        self.y = y
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color
        self._image = img
        self.triggered = False
        self.collided = False
        self.colx = -1
        self.coly = -1

    def colliding_position(self, b):
        originx = self.x // dist
        originy = self.y // dist
        posx = originx
        posy = originy
        while 0 <= posx < rows and 0 <= posy < rows and b[posx][posy][0] != self.color.opposite:
            posx += self.dirnx
            posy += self.dirny
        self.colx = posx
        self.coly = posy

    def move(self):
        if 0 < (self.x + self.dirnx) < width and 0 < (self.y + self.dirny) < height:
            if (self.x // dist, self.y // dist) != (self.colx, self.coly):
                self.x += self.dirnx
                self.y += self.dirny
            else:
                self.collided = True
                self.triggered = False
        else:
            self.reset()

    def collide(self, b):
        color, ind = b[self.colx][self.coly]
        piece = color.ownPieces[ind]
        if type(piece) == Squire:
            if piece.shield > 1:
                piece.shield -= 1
            else:
                piece.alive = False
                b[self.colx][self.coly] = (empty, 0)
        else:
            piece.alive = False
            b[self.colx][self.coly] = (empty, 0)
        self.reset()

    def intercept(self, i, j):
        originx = self.x//dist
        originy = self.y//dist
        dx = i - originx
        dy = j - originy

        if (normalize(dx), normalize(dy)) == (self.dirnx, self.dirny):
            if (abs(dx) <= abs(self.colx - originx)) and (abs(dy) <= abs(self.coly - originy)):
                self.colx = i
                self.coly = j

    def update_by_move(self, move):
        originx, originy = move.origin
        destx, desty = move.destination
        self.dirnx = normalize(destx - originx)
        self.dirny = normalize(desty - originy)
        self.x = originx*dist + self.biais()[0]
        self.y = originy*dist + self.biais()[1]
        self.colx = destx
        self.coly = desty

    def reset(self):
        self.x = 0
        self.y = 0
        self.dirnx = 0
        self.dirny = 0
        self.colx = -1
        self.coly = -1
        self.triggered = False
        self.collided = False

    def draw(self, surface):
        surface.blit(self._image, (self.x - 5, self.y))


def normalize(x):
    if x == 0:
        return 0
    else:
        return x // abs(x)


def biais(dx, dy):
    # I will have to settle better the biais in order to make it more realistic
    d = dist // 2
    temp = [(-d, -d), (-d, d), (-d, 3 * d), (d, 3 * d), (3 * d, 3 * d), (3 * d, d), (3 * d, -d), (d, -d)]
    i = shooterAiming.index((dx, dy))
    return temp[i]