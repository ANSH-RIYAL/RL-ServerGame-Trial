import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from random import randint

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


cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

@cron.interval_schedule(minutes = 1)
def graceEnergy():
    print("Adding Grace Energy to all agents:\n")
    for agentId in energy:
        energy[agentId] += 12
        print("\nAgent:{}\tEnergy:{}".format(agentId,energy[agentId]))

@cron.interval_schedule(seconds = 5)
def redistributeWealth():
    global bigPrizes
    global smallPrizes
    global field
    print(bigPrizes,smallPrizes)
    for i in range(bigPrizes,5):
        randomI = randint(1,9)
        randomJ = randint(1,9)
        field[randomI][randomJ] = 3
    bigPrizes = 5

    for i in range(smallPrizes,5):
        randomI = randint(1,9)
        randomJ = randint(1,9)
        field[randomI][randomJ] = 2
    smallPrizes = 5

    for i in range(len(field)):
        for j in range(len(field[0])):
            print(field[i][j], end = " ")
        print("")
    print("\n\n")


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

@app.route('/addAgent', methods = ['POST'])
def agentAdd():
    values = request.get_json()
    initialPosition = [values['initial_i'],values['initial_j']]
    field[initialPosition[0]][initialPosition[1]] = 1
    energy[values["agentId"]] = 50
    currentPositions[values["agentId"]] = initialPosition

    res = {
    'message': "Watashi ga kita!!!!"
    }

    for i in range(len(field)):
        for j in range(len(field[0])):
            print(field[i][j], end = " ")
        print("")
    print("\n\n")

    return jsonify(res), 200

@app.route('/checkField', methods = ['GET'])
def getField():
    res = {
    "field" : str(field)
    }
    return jsonify(res), 200

@app.route('/moveAgent', methods = ['POST'])
def move():
    # move value 1 means left, 2 means right, 3 means up 4 means down, 5 means nowhere
    # all moves (legal or illegal) cost 1 energy except for 5

    values = request.get_json()
    agentId = values["agentId"]
    current_i, current_j = currentPositions[agentId]
    move = values["action"]
    flag = True
    field[current_i][current_j] = 0
    if (int(move) == 5):
        energy[agentId] += 1
    elif (int(move) == 1):
        if (current_j >= 1):
            current_j -= 1
        else:
            flag = False

    elif (int(move) == 2):
        if (current_j < (height-1)):
            current_j += 1
        else:
            flag = False
        
    elif (int(move) == 3):
        if (current_i >= 1):
            current_i -= 1
        else:
            flag = False
        
    elif (int(move) == 4):
        if (current_i < (width-1)):
            current_i += 1
        else:
            flag = False

    energy[agentId] -= 1

    reward = field[current_i][current_j]
    field[current_i][current_j] = 1
    print("\nRewards obtained is:\t{}\n\n".format(reward))
    if reward == 2:
        smallPrizes -= 1
    if reward == 3:
        bigPrizes -= 1

    currentPositions[agentId] = [current_i,current_j]

    res = {
    'message': "legal move, Hence done" if flag else "illegal move, learn to play idiot"
    }
    return jsonify(res), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    width = 10
    height = 10
    field = [[0 for i in range(width)] for j in range(height)]
    energy = {}
    bigPrizes = 0
    smallPrizes = 0
    acceptPermission = {}
    currentPositions = {}

    print("Initialising the field:\n\n")
    for i in range(len(field)):
        for j in range(len(field[0])):
            print(field[i][j], end = " ")
        print("")
    print("\n\n")

    app.run(host='0.0.0.0', port=port)
