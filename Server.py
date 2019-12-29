import socket
import pickle
from _thread import *
from Game import *

server = "192.168.43.63"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(4)
print("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gmeId):
    global idCount

    print('Sending player\'s id: '+str(p))
    conn.send(str.encode(str(p)))
    reset = False

    while True:
        try:
            data = pickle.loads(conn.recv(4096))

            if gameId in games:
                game = games[gmeId]

                if not data:
                    print('Disconnected')
                    break
                else:
                    if reset:
                        game.resetWent()
                        reset = False
                    if data.nature != 'unknown':
                        game.play(p, data)
                    if game.bothWent():
                        game.set_priority()
                        reset = True
                    conn.sendall(pickle.dumps(game))
            else:
                print(str(gameId)+' is not in games')
                break
        except:
            break
    print('Connection Lost')
    try:
        del games[gmeId]
        print('Closing game '+str(gmeId))
    except:
        pass
    idCount -= 1
    conn.close()


currentId = 0

while True:
    connection, addr = s.accept()
    print('Connected to', addr)

    idCount += 1
    player = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        print('Creating a new game...')
        games[gameId] = Game(gameId)
    else:
        games[gameId].ready = True
        player = 1

    start_new_thread(threaded_client, (connection, player, gameId))
