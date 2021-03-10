import requests
import json
import cv2
import numpy as np

# Helper Functions

# Render Help Functions

def overWrite(startI, startJ, originalImage, smallImage):
    for i in range(smallImage.shape[0]):
        for j in range(smallImage.shape[1]):
            originalImage[startI + i][startJ + j] = smallImage[i][j]
    return originalImage

# def displayBoard(board, direction, ownI, ownJ):
def displayBoard(board, ownI, ownJ):
    # board is the board position matrix of size 6x9 such that player is at index [5][4] (bottom center)
    image = np.zeros((64*9, 64*9, 3), dtype = np.uint8)
    board = np.asarray(board)
    print(board)
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if board[i][j] == 1:
                overWrite(64*i,64*j,image,otherPlayer)
            elif board[i][j] == 2:
                overWrite(64*i,64*j,image,smallFruit)
            elif board[i][j] == 3:
                overWrite(64*i,64*j,image,bigFruit)
    overWrite(64*ownI,64*ownJ,image,hero)
    return image
    

# Variable declarations

hero = cv2.imread("./images/mainMonster.jpg")
# print(hero.shape)
hero = cv2.resize(hero, (64,64))
cv2.imshow("window1",hero)
# cv2.waitKey()
# cv2.destroyAllWindows()

otherPlayer = cv2.imread("./images/otherMonster.jpg")
# print(otherPlayer.shape)
otherPlayer = cv2.resize(otherPlayer, (64,64))
cv2.imshow("window2",otherPlayer)
# cv2.waitKey()
# cv2.destroyAllWindows()

smallFruit = cv2.imread("./images/smallFruit.png")
# print(smallFruit.shape)
smallFruit = cv2.resize(smallFruit, (64,64))
cv2.imshow("window3",smallFruit)
# cv2.waitKey()
# cv2.destroyAllWindows()

bigFruit = cv2.imread("./images/bigFruit.jpg")
# print(bigFruit.shape)
bigFruit = cv2.resize(bigFruit, (64,64))
cv2.imshow("window4",bigFruit)
cv2.waitKey()
cv2.destroyAllWindows()


mainServer = 5001

# Dummy user:

req = {
'agentId': 1007,
'initial_i': 19,
'initial_j': 28
}

res = requests.post("http://localhost:{}/addAgent".format(mainServer), json = req)
# print(res)

# Real Agent:

req = {
'agentId': 123,
'initial_i': 20,
'initial_j': 23
}

res = requests.post("http://localhost:{}/addAgent".format(mainServer), json = req)
# print(res)

req = {
	'agentId': 123
}
resField = requests.post("http://localhost:{}/checkField".format(mainServer), json = req)
# print(resField.json().content)

# cv2.imshow("window", displayBoard(resField, 5, 5))
# cv2.waitKey()

# for i in json.loads(resField.json().get("field")):
# 	for j in i:
# 		print(j, end = " ")
# 	print()

ch = int(input("\n\nEnter direction choice:\nPS: 6 to exit\n\n"))

req = {
	'agentId': 123
}
resField = requests.post("http://localhost:{}/checkField".format(mainServer), json = req)
field = json.loads(resField.json().get("field"))

print(type(field))
print(field)
print(type(field[0]))

cv2.imshow("window", displayBoard(field, 5, 5))
cv2.waitKey(20)
# for i in field:
# 	for j in i:
# 		print(j, end = " ")
# 	print()

while True:
	if ch == 6:
		np.save("continue.npy", False)
		break
	ch = int(input("\n\nEnter direction choice:\nPS: 6 to exit\n\n"))

	req = {
	'agentId': 123,
	'action': str(ch)
	}
	# print(req)
	res = requests.post("http://localhost:{}/moveAgent".format(mainServer), json = req)
	print("message received is: ",res.json().get("message"))
	print("\nreward obtained is: ",res.json().get("reward"))

	req = {
	'agentId': 123
	}
	resField = requests.post("http://localhost:{}/checkField".format(mainServer), json = req)

	field = json.loads(resField.json().get("field"))
	img = displayBoard(field, 4, 4)
	print("Here before displaying:\n\n")
	cv2.imshow("window", img)
	cv2.waitKey(20)
	print("Here!")
# 	for i in field:
# 		for j in i:
# 			print(j, end = " ")
# 		print()

cv2.destroyAllWindows()
