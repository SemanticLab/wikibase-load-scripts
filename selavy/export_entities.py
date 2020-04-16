

# make sure you have ran: pip3 install requests
import requests

import json
import csv
# change this
url = "http://159.89.242.202:3000/document/e651dacfe4bf966347452b38d2fb1380/export"


print('downloading from selavy')

r = requests.get(url)
data = json.loads(r.text)

entities = {}
print('extracting entities')
for b in data['blocks']:
	for i in b['identities']:
		key = i['identLabel'] + str(i['identType']) + str(i['identUri'])
		if key not in entities:
			entities[key] = {'label':i['identLabel'],'type':i['identType'],"uri":i['identUri']}


with open('csv_out.csv','w') as out:

	writer = csv.writer(out)

	for x in entities:
		writer.writerow([entities[x]['label'],entities[x]['type'],entities[x]['uri']])