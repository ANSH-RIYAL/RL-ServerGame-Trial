import requests
import json

mainServer = 5000

req = {
'agentId': 123,
'initial_i': 3,
'initial_j': 4
}

res = requests.post("http://localhost:{}/addAgent".format(mainServer), json = req)
print(res)

resField = requests.get("http://localhost:{}/checkField".format(mainServer))
for i in json.loads(resField.json().get("field")):
	for j in i:
		print(j, end = " ")
	print()

ch = int(input("\n\nEnter direction choice:\nPS: 6 to exit\n\n"))

resField = requests.get("http://localhost:{}/checkField".format(mainServer))
for i in json.loads(resField.json().get("field")):
	for j in i:
		print(j, end = " ")
	print()

while (ch != 6):
	ch = int(input("\n\nEnter direction choice:\nPS: 6 to exit\n\n"))
	req = {
	'agentId': 123,
	'action': str(ch)
	}
	# print(req)
	res = requests.post("http://localhost:{}/moveAgent".format(mainServer), json = req)
	print(res)

	resField = requests.get("http://localhost:{}/checkField".format(mainServer))
	for i in json.loads(resField.json().get("field")):
		for j in i:
			print(j, end = " ")
		print()
