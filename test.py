# I am back bitches

from random import randint
import requests
import json

def initializeAgent(agentId):
    mainServer = "http://localhost:5001/addAgent"
    req = {
    'agentId': agentId,
    'initial_i': randint(20,50),
    'initial_j': randint(20,50)
    }

    res = requests.post(mainServer, json = req)
    return res.json().get("done")

for i in range(6):
	initializeAgent(randint(20,80))