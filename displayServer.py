import requests
from flask import Flask, jsonify, request
import json
import cv2
import numpy as np

# Instantiate the Node
app = Flask(__name__)

def overWrite(startI, startJ, originalImage, smallImage):
    for i in range(smallImage.shape[0]):
        for j in range(smallImage.shape[1]):
            originalImage[startI + i][startJ + j] = smallImage[i][j]
    return originalImage

@app.route('/field', methods = ['POST'])
def displayfield():
    # field is the field position matrix of size 6x9 such that player is at index [5][4] (bottom center)
    image = np.zeros((70*20, 70*20, 3), dtype = np.uint8)
    value = request.get_json()
    field = np.asarray(json.loads(value["field"]))
    for i in range(field.shape[0]):
        for j in range(field.shape[1]):
            if field[i][j] == 1:
                image = overWrite(20*i,20*j,image,otherPlayer)
            elif field[i][j] == 2:
                image = overWrite(20*i,20*j,image,smallFruit)
            elif field[i][j] == 3:
                image = overWrite(20*i,20*j,image,bigFruit)
    # image = overWrite(64*ownI,64*ownJ,image,hero)
    cv2.imshow("total Field", image)
    cv2.waitKey(20)
    return jsonify(res), 200

hero = cv2.imread("./images/mainMonster.jpg")
# print(hero.shape)
hero = cv2.resize(hero, (20,20))
# cv2.imshow("window1",hero)
# cv2.waitKey()
# cv2.destroyAllWindows()

otherPlayer = cv2.imread("./images/otherMonster.jpg")
# print(otherPlayer.shape)
otherPlayer = cv2.resize(otherPlayer, (20,20))
# cv2.imshow("window2",otherPlayer)
# cv2.waitKey()
# cv2.destroyAllWindows()

smallFruit = cv2.imread("./images/smallFruit.png")
# print(smallFruit.shape)
smallFruit = cv2.resize(smallFruit, (20,20))
# cv2.imshow("window3",smallFruit)
# cv2.waitKey()
# cv2.destroyAllWindows()

bigFruit = cv2.imread("./images/bigFruit.jpg")
# print(bigFruit.shape)
bigFruit = cv2.resize(bigFruit, (20,20))


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5005, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
