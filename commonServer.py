import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from random import randint
import pickle

import atexit
# v2.x version - see https://stackoverflow.com/a/38501429/135978
# for the 3.x version
from apscheduler.scheduler import Scheduler

import requests
from flask import Flask, jsonify, request

import numpy as np

# Instantiate the Node
app = Flask(__name__)

# 0 means nothing, 1 means player, 2 means small reward(5 pts), 3 means big reward(15 pts), -1 pts per move, starting energy = 50, +12 energy every 60 seconds
field = []
energy = {}
bigPrizes = 0
smallPrizes = 0
acceptPermission = {}
currentPositions = {}

def consecutiveMoves(l):
    start = l[0]
    for i in l:
        if i != start:
            return False
    return True

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

@cron.interval_schedule(seconds = 1)
def exportField():
    print("\n\nExported!!!!\n\n")
    np.save("field.npy", np.asarray(field))

@cron.interval_schedule(minutes = 1)
def graceEnergy():
    print("Adding Grace Energy to all agents:\n")
    for agentId in energy:
        energy[agentId] += 12
        print("\nAgent:{}\tEnergy:{}".format(agentId,energy[agentId]))

@cron.interval_schedule(seconds = 15)
def redistributeWealth():
    global bigPrizes
    global smallPrizes
    global field
    print("\n\n\nCurent values of prizes: \n",bigPrizes,smallPrizes,"\n\n\n")
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
    # agentId = values["agentId"]
    # if agentId in energy.keys():

    if field[initialPosition[0]][initialPosition[1]] != 0:
        print("field at index was not zero!")
        res = {
        "done": False
        }
        return jsonify(res), 200
    field[initialPosition[0]][initialPosition[1]] = 1
    energy[values["agentId"]] = 200
    directions[values["agentId"]] = 0
    if values["agentId"] in currentPositions:
        orig_i, orig_j = currentPositions[values["agentId"]]
        field[orig_i][orig_j] = 0
    currentPositions[values["agentId"]] = initialPosition
    lastMoves[values["agentId"]] = [0,0,0]

    res = {
    'message': "Watashi ga kita!!!!",
    "done": True
    }

    # for i in range(len(field)):
    #     for j in range(len(field[0])):
    #         print(field[i][j], end = " ")
    #     print("")
    # print("\n\n")

    return jsonify(res), 200

@app.route('/checkField', methods = ['POST'])
def getField():
    
    values = request.get_json()
    agentId = values["agentId"]
    current_i, current_j = currentPositions[agentId]
    
    # print(len(field), len(field[0]))
    # print(field[16:25])
    # print(current_i, current_j)
    
    # smallField = np.copy(field[current_i - 4 : current_i + 5, current_j - 4 : current_j + 5])
    smallField = np.copy(field[current_i - 9 : current_i + 10, current_j - 9 : current_j + 10])
    # print("\n\n\n\n\n{}\n\n\n\n\n".format(smallField))
    # print(str(smallField))
    
    # direction = directions[agentId]
    
    # if direction == 0:
    #     smallField[5:9] = np.zeros((4,9))
    # elif direction == 1:
    #     smallField[:,0:4] = np.zeros((9,4))
    # elif direction == 2:
    #     smallField[0:4] = np.zeros((4,9))
    # elif direction == 3:
    #     smallField[:,5:9] = np.zeros((9,4))

    smallField = smallField.tolist()
    
    res = {
    "field" : str(smallField),
    "direction": str(directions[agentId])
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
    move = int(values["action"]) + 1
    flag = True
    print("\nMove is: ",move,"\n")
    lastMoves[values["agentId"]] = lastMoves[values["agentId"]][1:] + [int(move)]

    direction = directions[agentId]
    orig_i, orig_j = int(current_i), int(current_j)
    if (move == 5):
        energy[agentId] += 2
        reward = 0.1
    
    elif (move == 1):
        reward = 0.4
        energy[agentId] += 2
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
        
    elif (move == 2):
        reward = 0.2
        direction = (direction-1)%4
        energy[agentId] += 1
        
    elif (move == 3):
        reward = 0.2
        direction = (direction+1)%4
        energy[agentId] += 1

    elif (move == 4):
        reward = 0.2
        direction = (direction-2)%4
        energy[agentId] += 1

    else:
        flag = False

    energy[agentId] -= 2

    if (current_i != orig_i) or (current_j != orig_j):
        field[orig_i][orig_j] = 0
        reward += (field[current_i][current_j]**3)/50

    if consecutiveMoves(lastMoves[values["agentId"]]):
        reward = 0
        print("\n\n\nRepeated Moves\n\n\n")
    
    print("\nRewards obtained is:\t{}\n\n".format(reward))
    if field[current_i][current_j] == 2:
        smallPrizes -= 1
        energy[agentId] += 5
    if field[current_i][current_j] == 3:
        bigPrizes -= 1
        energy[agentId] += 15
    print("Yaay! Updated Energy level: ", energy[agentId])
    print("\n\n\n")
    field[current_i][current_j] = 1

    directions[agentId] = direction

    currentPositions[agentId] = [current_i,current_j]

    res = {
    'message': "legal move, Hence done" if flag else "illegal move, learn to play idiot",
    'reward': str(reward),
    'done': False
    }

    if energy[agentId] < 0:
        res['done'] = True

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
    lastMoves = {}
    directions = {}

    redistributeWealth()

    np.save("continue.npy", True)
    print("Initialising the field:\n\n")
    for i in range(len(field)):
        for j in range(len(field[0])):
            print(field[i][j], end = "")
        print("")
    print("\n\n")
    field = np.asarray(field)
    
    app.run(host='0.0.0.0', port=port)
