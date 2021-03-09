import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from random import randint
import cv2

import atexit
# v2.x version - see https://stackoverflow.com/a/38501429/135978
# for the 3.x version
from apscheduler.scheduler import Scheduler

import requests
from flask import Flask, jsonify, request

import numpy as np

# Helper Function

# def overWrite(startI, startJ, originalImage, smallImage):
#     for i in range(smallImage.shape[0]):
#         for j in range(smallImage.shape[1]):
#             originalImage[startI + i][startJ + j] = smallImage[i][j]
#     return originalImage

# def displayfield():
#     # field is the field position matrix of size 6x9 such that player is at index [5][4] (bottom center)
#     image = np.zeros((70*20, 70*20, 3), dtype = np.uint8)
#     # cv2.imshow("total Field", image)
#     # cv2.waitKey()
#     # field = np.asarray(field)
#     # print(field)
#     for i in range(field.shape[0]):
#         for j in range(field.shape[1]):
#             if field[i][j] == 1:
#                 image = overWrite(20*i,20*j,image,otherPlayer)
#             elif field[i][j] == 2:
#                 image = overWrite(20*i,20*j,image,smallFruit)
#             elif field[i][j] == 3:
#                 image = overWrite(20*i,20*j,image,bigFruit)
#     # image = overWrite(64*ownI,64*ownJ,image,hero)
#     cv2.imshow("total Field", image)
#     cv2.waitKey(5000)
#     cv2.destroyAllWindows()
#     return

# hero = cv2.imread("./images/mainMonster.jpg")
# # print(hero.shape)
# hero = cv2.resize(hero, (20,20))
# # cv2.imshow("window1",hero)
# # cv2.waitKey()
# # cv2.destroyAllWindows()

# otherPlayer = cv2.imread("./images/otherMonster.jpg")
# # print(otherPlayer.shape)
# otherPlayer = cv2.resize(otherPlayer, (20,20))
# # cv2.imshow("window2",otherPlayer)
# # cv2.waitKey()
# # cv2.destroyAllWindows()

# smallFruit = cv2.imread("./images/smallFruit.png")
# # print(smallFruit.shape)
# smallFruit = cv2.resize(smallFruit, (20,20))
# # cv2.imshow("window3",smallFruit)
# # cv2.waitKey()
# # cv2.destroyAllWindows()

# bigFruit = cv2.imread("./images/bigFruit.jpg")
# # print(bigFruit.shape)
# bigFruit = cv2.resize(bigFruit, (20,20))

# Instantiate the Node
app = Flask(__name__)

# 0 means nothing, 1 means player, 2 means small reward(5 pts), 3 means big reward(15 pts), -1 pts per move, starting energy = 50, +12 energy every 60 seconds
field = []
energy = {}
bigPrizes = 0
smallPrizes = 0
acceptPermission = {}
currentPositions = {}

# import apscheduler.schedulers.blocking

cron = Scheduler(daemon=True)

# cron = apscheduler.schedulers.blocking.BackgroundScheduler('apscheduler.job_defaults.max_instances': '10')

# Explicitly kick off the background thread
cron.start()

@cron.interval_schedule(minutes = 1)
def graceEnergy():
    print("Adding Grace Energy to all agents:\n")
    for agentId in energy:
        energy[agentId] += 12
        print("\nAgent:{}\tEnergy:{}".format(agentId,energy[agentId]))

    # displayfield()

@cron.interval_schedule(seconds = 5)
def displayTheField():
    print("Displaying the field\nDimensions of field: ", field.shape)
    req = {
    "field": str(field.tolist())
    }
    displayServer = 5005
    res = requests.post("http://localhost:{}/field".format(displayServer), json = req)
    print("Donezooo!!, req response = ", res)

@cron.interval_schedule(seconds = 15)
def redistributeWealth():
    global bigPrizes
    global smallPrizes
    global field
    print(bigPrizes,smallPrizes)
    # cv2.destroyAllWindows()
    for i in range(bigPrizes,60):
        randomI = randint(10,height/2)
        randomJ = randint(10,width)
        
        while (field[randomI][randomJ] in [1,2,3]):
            randomI = randint(10,height/2)
            randomJ = randint(10,width)

        field[randomI][randomJ] = 3
    bigPrizes = 60

    for i in range(smallPrizes,60):
        randomI = randint(height/2+1,height)
        randomJ = randint(10,width)

        while (field[randomI][randomJ] in [1,2,3]):
            randomI = randint(height/2+1,height)
            randomJ = randint(10,width)

        field[randomI][randomJ] = 2
    smallPrizes = 60

    print("redistributeWealth done")
    

    # for i in range(len(field)):
    #     for j in range(len(field[0])):
    #         print(field[i][j], end = "")
    #     print("")
    # print("\n\n")


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

@app.route('/addAgent', methods = ['POST'])
def agentAdd():
    values = request.get_json()
    initialPosition = [values['initial_i'],values['initial_j']]
    field[initialPosition[0]][initialPosition[1]] = 1
    energy[values["agentId"]] = 50
    directions[values["agentId"]] = 0
    currentPositions[values["agentId"]] = initialPosition

    res = {
    'message': "Watashi ga kita!!!!"
    }

    # for i in range(len(field)):
    #     for j in range(len(field[0])):
    #         print(field[i][j], end = " ")
    #     print("")
    # print("\n\n")

    # displayfield()

    return jsonify(res), 200

@app.route('/checkField', methods = ['POST'])
def getField():
    values = request.get_json()
    agentId = values["agentId"]
    current_i, current_j = currentPositions[agentId]
    # print(len(field), len(field[0]))
    # print(field[16:25])
    # print(current_i, current_j)
    smallField = field[current_i - 4 : current_i + 5, current_j - 4 : current_j + 5]
    # print("\n\n\n\n\n{}\n\n\n\n\n".format(smallField))
    # print(str(smallField))
    smallField = smallField.tolist()
    res = {
    "field" : str(smallField),
    "direction": directions[agentId]
    }
    return jsonify(res), 200

@app.route('/moveAgent', methods = ['POST'])
def move():
    # move value 1 means move in front, 2 means turn left, 3 means turn right, 4 means turn backwards, 5 means nowhere
    # all turn moves (legal or illegal) cost 1 energy 
    # forward move consumes 2 energy and move = 5 costs 0 energy
    # directions: 0(up), 1(right), 2(down), 3(left)

    global bigPrizes
    global smallPrizes
    global field

    values = request.get_json()
    agentId = values["agentId"]
    current_i, current_j = currentPositions[agentId]
    move = values["action"]
    flag = True
    direction = directions[agentId]
    orig_i, orig_j = int(current_i), int(current_j)
    if (int(move) == 5):
        energy[agentId] += 2
    
    elif (int(move) == 1):

        if (direction == 0) and (current_i > 10) and (field[current_i-1][current_j] != 1):
            current_i -= 1

        elif (direction == 1) and (current_j < width) and (field[current_i][current_j+1] != 1):
            current_j += 1

        elif (direction == 2) and (current_i < height) and (field[current_i+1][current_j] != 1):
            current_i += 1

        elif (direction == 3) and (current_j > 10) and (field[current_i][current_j-1] != 1):
            current_j -= 1

        else:
            flag = False
        
    elif (int(move) == 2):
        direction = (direction-1)%4
        energy[agentId] += 1
        
    elif (int(move) == 3):
        direction = (direction+1)%4
        energy[agentId] += 1

    elif (int(move) == 4):
        direction = (direction-2)%4
        energy[agentId] += 1

    else:
        flag = False

    energy[agentId] -= 2

    reward = field[current_i][current_j]
    if (current_i != orig_i) or (current_j != orig_j):
        field[orig_i][orig_j] = 0
    field[current_i][current_j] = 1
    print("\nRewards obtained is:\t{}\n\n".format(reward))
    if reward == 2:
        smallPrizes -= 1
        energy[agentId] += 5
    if reward == 3:
        bigPrizes -= 1
        energy[agentId] += 15
    print("Yaay! Updated Energy level: ", energy[agentId])
    print("\n\n\n")

    directions[agentId] = direction

    currentPositions[agentId] = [current_i,current_j]

    res = {
    'message': "legal move, Hence done" if flag else "illegal move, learn to play idiot",
    'field': str(field)
    }

    # displayfield()
    return jsonify(res), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    width = 50
    height = 50
    field = [[0 for i in range(width + 20)] for j in range(height + 20)]
    energy = {}
    bigPrizes = 0
    smallPrizes = 0
    acceptPermission = {}
    currentPositions = {}
    directions = {}

    print("Initialising the field:\n\n")
    for i in range(len(field)):
        for j in range(len(field[0])):
            print(field[i][j], end = "")
        print("")
    print("\n\n")
    field = np.asarray(field, dtype = np.uint8)

    redistributeWealth()
    print(field)

    # displayfield()

    app.run(host='0.0.0.0', port=port)
