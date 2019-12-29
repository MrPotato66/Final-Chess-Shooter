from os import chdir
from Network import Network
from Game import *
from Pieces import *

pygame.init()


def interaction():
    global chosenPiece, board, waiting, sent_move

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if not waiting:
            pres = pygame.mouse.get_pressed()
            tempx, tempy = pygame.mouse.get_pos()
            if 0 <= tempx < width and 0 <= tempy < height:
                if pres[0]:
                    posx = tempx // dist
                    posy = tempy // dist
                    if chosenPiece:
                        chosenColor, chosenInd = chosenPiece[0]
                        piece = chosenColor.ownPieces[chosenInd]
                        if (posx, posy) in piece.valid_space(board):
                            sent_move.nature = 'moving'
                            sent_move.origin = (piece.x, piece.y)
                            sent_move.destination = (posx, posy)
                            waiting = True
                        piece.chosen = False
                        chosenPiece = []
                    else:
                        color, ind = board[posx][posy]
                        if color == pColor:
                            chosenPiece = [(color, board[posx][posy][1])]
                            color.ownPieces[ind].chosen = True
                if pres[2]:
                    tempx, tempy = pygame.mouse.get_pos()
                    posx = tempx // dist
                    posy = tempy // dist
                    if chosenPiece:
                        chosenColor, chosenInd = chosenPiece[0]
                        piece = chosenColor.ownPieces[chosenInd]
                        if type(piece) == Shooter:
                            ownx = piece.x
                            owny = piece.y
                            if (posx - ownx, posy - owny) in piece.aimingSpots:
                                if piece.ammo > 0:
                                    ownBullet.dirnx = (posx - ownx)
                                    ownBullet.dirny = (posy - owny)
                                    ownBullet.x = ownx * dist + biais(ownBullet.dirnx, ownBullet.dirny)[0]
                                    ownBullet.y = owny * dist + biais(ownBullet.dirnx, ownBullet.dirny)[1]
                                    ownBullet.colliding_position(board)
                                    sent_move.nature = 'shooting'
                                    sent_move.origin = (piece.x, piece.y)
                                    sent_move.destination = (ownBullet.colx, ownBullet.coly)
                                    waiting = True
                            piece.chosen = False
                            chosenPiece = []
                            chosenColor.ownPieces[chosenInd] = piece


def update(g):
    global board, moving, player, ownBullet, oppositeBullet

    colors = [white, black]
    prioritary = colors[game.priority]
    unprioritary = colors[1-game.priority]

    pri_move = g.moves[game.priority]
    pri_originx, pri_originy = pri_move.origin
    _, pri_ind = board[pri_originx][pri_originy]
    pri_destx, pri_desty = pri_move.destination
    pri_piece = prioritary.ownPieces[pri_ind]

    unpri_move = g.moves[1-game.priority]
    unpri_originx, unpri_originy = unpri_move.origin
    _, unpri_ind = board[unpri_originx][unpri_originy]
    unpri_destx, unpri_desty = unpri_move.destination
    unpri_piece = unprioritary.ownPieces[unpri_ind]

    if pri_move.nature == 'shooting' and unpri_move.nature == 'shooting':
        print('Both shooting')
        pri_piece.ammo -= 1
        unpri_piece.ammo -= 1
        if game.priority == player:
            ownBullet.update_by_move(pri_move)
            oppositeBullet.update_by_move(unpri_move)
        else:
            ownBullet.update_by_move(unpri_move)
            oppositeBullet.update_by_move(pri_move)
        ownBullet.triggered = True
        oppositeBullet.triggered = True
        moving = True
    elif pri_move.nature == 'shooting' and unpri_move.nature == 'moving':
        unpri_piece.move(unpri_destx, unpri_desty, board)
        pri_piece.ammo -= 1
        if game.priority == player:
            ownBullet.update_by_move(pri_move)
            ownBullet.colliding_position(board)
            # ownBullet.intercept(unpri_destx, unpri_desty)
            ownBullet.triggered = True
        else:
            oppositeBullet.update_by_move(pri_move)
            oppositeBullet.colliding_position(board)
            # oppositeBullet.intercept(unpri_destx, unpri_desty)
            oppositeBullet.triggered = True
        moving = True
    elif pri_move.nature == 'moving' and unpri_move.nature == 'shooting':
        pri_piece.move(pri_destx, pri_desty, board)
        unpri_piece.ammo -= 1
        if game.priority == player:
            oppositeBullet.update_by_move(unpri_move)
            oppositeBullet.colliding_position(board)
            # ownBullet.intercept(pri_destx, pri_desty)
            oppositeBullet.triggered = True
        else:
            ownBullet.update_by_move(unpri_move)
            ownBullet.colliding_position(board)
            # oppositeBullet.intercept(pri_destx, pri_desty)
            ownBullet.triggered = True
        moving = True
    elif pri_move.nature == 'moving' and unpri_move.nature == 'moving':
        print('Both moving')
        if (pri_destx, pri_desty) == (unpri_destx, unpri_desty):
            unpri_piece.alive = False
            pri_piece.move(pri_destx, pri_desty, board)
        else:
            pri_piece.move(pri_destx, pri_desty, board)
            unpri_piece.move(unpri_destx, unpri_desty, board)


def drawBoard(surface):
    for i in range(rows):
        for j in range(rows):
            if (i + j) % 2 == 0:
                pygame.draw.rect(surface, backWhite, (i * dist, j * dist, dist, dist))
            else:
                pygame.draw.rect(surface, backBrown, (i * dist, j * dist, dist, dist))


def show_board(surface):
    M = [['empty']*rows  for i in range(rows)]
    for i in range(rows):
        for j in range(rows):
            c, ind = board[j][i]
            if c == empty:
                M[i][j] = 'empty'
            else:
                piece = c.ownPieces[ind]
                M[i][j] = str(type(piece))
    print(M)


def redrawWindow(surface):
    surface.fill(background)
    drawBoard(surface)
    for white_item in white.ownPieces:
        if white_item.chosen:
            white_item.drawPossibleMoves(surface, board)
            if type(white_item) == Shooter:
                white_item.drawAiming(surface)
    for black_item in black.ownPieces:
        if black_item.chosen:
            black_item.drawPossibleMoves(surface, board)
            if type(black_item) == Shooter:
                black_item.drawAiming(surface)
    for white_item in white.ownPieces:
        white_item.draw(surface)
    for black_item in black.ownPieces:
        black_item.draw(surface)
    if ownBullet.triggered:
        ownBullet.draw(surface)
    if oppositeBullet.triggered:
        oppositeBullet.draw(surface)
    if player == 0:
        centered_writting(surface, 'You are playing', 20)
        centered_writting(surface, 'with white pieces', 45)
        if game.p0Went:
            pygame.draw.rect(surface, (255, 0, 0), (0, 0, 10, 10))
    elif player == 1:
        centered_writting(surface, 'You are playing', 20)
        centered_writting(surface, 'with black pieces', 45)
        if game.p1Went:
            pygame.draw.rect(surface, (255, 0, 0), (0, 0, 10, 10))
    centered_writting(surface, 'Priority goes for:', 80)
    centered_writting(surface, 'Rounds Played:', 150)
    centered_writting(surface, str(game.rounds//2), 175)
    if knowledge:
        if game.priority == 0:
            pygame.draw.circle(surface, (255, 255, 255), (width + 101, 115), 12)
        else:
            pygame.draw.circle(surface, (0, 0, 0), (width + 101, 115), 12)
    else:
        pygame.draw.circle(surface, (127, 140, 141), (width + 101, 115), 12)
        centered_writting(surface, '?', 115)
    pygame.display.update()


def centered_writting(surface, t, h):
    text = text_font.render(t, True, (0, 0, 0))
    text_rect = text.get_rect(center=(column_center, h))
    surface.blit(text, text_rect)


def main():
    global whiteKing, whiteSquire1, whiteSquire2, whiteShooter1, whiteShooter2, blackKing, blackSquire1, blackSquire2, \
        blackShooter1, blackShooter2, chosenPiece, ownBullet, oppositeBullet, board, waiting, sent_move, moving, player, game, \
        knowledge, pColor, win

    win = pygame.display.set_mode((disp_width, disp_height))
    clock = pygame.time.Clock()

    whiteKing = King(4, 7, white, whiteKingImg)
    whiteSquire1 = Squire(3, 6, white, whiteSquireImg)
    whiteSquire2 = Squire(5, 6, white, whiteSquireImg)
    whiteShooter1 = Shooter(3, 7, white, whiteShooterImg)
    whiteShooter2 = Shooter(5, 7, white, whiteShooterImg)
    blackKing = King(4, 0, black, blackKingImg)
    blackSquire1 = Squire(3, 1, black, blackSquireImg)
    blackSquire2 = Squire(5, 1, black, blackSquireImg)
    blackShooter1 = Shooter(3, 0, black, blackShooterImg)
    blackShooter2 = Shooter(5, 0, black, blackShooterImg)

    chosenPiece = []

    board = [[(empty, 0)] * rows for k in range(rows)]
    for wInd, whiteItem in enumerate(white.ownPieces):
        board[whiteItem.x][whiteItem.y] = (white, wInd)
    for bInd, blackItem in enumerate(black.ownPieces):
        board[blackItem.x][blackItem.y] = (black, bInd)

    sent_move = Movement('unknown', (-1, -1), (-1, -1))

    run = True
    waiting = False
    moving = False
    n = Network()
    tmp = n.getP()
    if tmp is None:
        player = 0
    else:
        player = int(n.getP())
    pColor = white
    knowledge = True
    if player == 1:
        pColor = black
        knowledge = False
    ownBullet = Bullet(0, 0, 0, 0, pColor, bulletImg)
    oppositeBullet = Bullet(0, 0, 0, 0, pColor.opposite, bulletImg)
    game = n.send(sent_move)

    while run:
        clock.tick(60)
        interaction()
        if not moving:
            try:
                game = n.send(sent_move)
                knowledge = game.knowledge == player
                if not sent_move.primordial():
                    sent_move.resetMove()
            except:
                run = False
                print('Could not get game')
                break
            if game.bothWent():
                update(game)
                waiting = False
                sent_move.reset = True
        else:
            if ownBullet.triggered:
                ownBullet.move()
            if oppositeBullet.triggered:
                oppositeBullet.move()
            if ownBullet.collided:
                ownBullet.collide(board)
            if oppositeBullet.collided:
                oppositeBullet.collide(board)
            if (not ownBullet.triggered) and (not oppositeBullet.triggered):
                moving = False
        redrawWindow(win)

    pygame.quit()


main()
