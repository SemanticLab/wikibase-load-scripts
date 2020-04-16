from python_wikibase import PyWikibase
import csv
import sys
import re
import os.path
import time


path_to_csv = './lljs_batch_1_enhancements.csv'


if os.path.isfile('./my_config.json'):
	config_path = './my_config.json'
else:
	config_path = './config.json'

wb = PyWikibase(config_path=config_path)



qnumber_regex = re.compile('Q[0-9]+')


def clean_value(val):
	if isinstance(val,str):
		val=val.strip()
		if val[0] == '"' and val[-1] =='"':
			val=val[1:-2]

	return val

data = []
# open the csv doc
with open(path_to_csv) as infile:
	reader = csv.DictReader(infile)
	for r in reader:
		# turn the dictrow into a normal dict not a ordered dict and then add it to our data and normalize the key name
		r = dict(r)
		d = {}
		for k in r:
			d[k.strip().lower().replace(' ','_')] = r[k]	
		data.append(d)

allP={}
# find the unique p's 
for d in data:
	if 'property' in d:
		d['property'] = d['property'].upper()
		if d['property'] not in allP:
			allP[d['property']] = None

# find out what these P should be
for k in allP:
	# try:
	r = wb.Property().get(entity_id=k)
	# except:
	# 	print('you are tring to use the property', k, 'but wikibase does not know that P number')
	# 	sys.exit()
	allP[k]= r.data_type

print('validating your property usage')
# {'P1': 'Item', 'P11': 'Item', 'P8': 'ExternalId', 'P9': 'Url'}

for line, d in enumerate(data):

	if d['property'] == None or d['property'] == '':
		continue

	if 'P' in d['property']:

		val = clean_value(d['value'])

		d['val']=val

		if allP[d['property']] == 'Item':
			if qnumber_regex.match(val) == None:
				print('this data element does not match the datatype (Item):') 
				print(d)
				print('fix the csv and try again', f'line #{line+2}')
				sys.exit()

		elif allP[d['property']] == 'ExternalId':

			if isinstance(val,str) == False or val == '':
				print('this data element does not match the datatype (ExternalId):') 
				print(d)
				print('fix the csv and try again', f'line #{line+2}')
				sys.exit()

		elif allP[d['property']] == 'Url':
			if 'http://' not in val and 'https://' not in val:
				print('this data element does not match the datatype (Url):') 
				print(d)
				print('fix the csv and try again', f'line #{line+2}')
				sys.exit()

		else:

			print('--------')
			print('uh oh',allP[d['property']], 'is not a datatype this script knows how to validate, update the script', f'line #{line+2}')
			print('--------')
			sys.exit()


		# also make sure if they are saying use a P number they have a Q number to go with it		
		if d['qid'] != 'last' and d['qid'] != 'create' and qnumber_regex.match(d['qid']) == None:
			print(' You are trying to set the property without a valid Q number', f'line #{line+2}')
			print(d)
			sys.exit()

print('Your properties look noice')

print('starting data load')





with open(f"log_{int(time.time())}.txt",'w') as logout:

	for line, d in enumerate(data):

		logmsg = f'Working on line: {line+2}\n'
		print(logmsg)
		logout.write(logmsg)

		## we are creating a claim
		if 'P' in d['property']:

			logmsg = f"\t Creating claim {d['property']} ({allP[d['property']]}) to {d['qid']} with value \"{d['val']}\"\n"
			print(logmsg)
			logout.write(logmsg)

			if allP[d['property']] =='Item':
				item = wb.Item().get(entity_id=d['qid'])
				prop = wb.Property().get(entity_id=d['property'])
				value = wb.Item().get(entity_id=d['val']) 
				item.claims.add(prop, value)
			elif allP[d['property']] =='Url':
				item = wb.Item().get(entity_id=d['qid'])
				prop = wb.Property().get(entity_id=d['property'])
				value = wb.StringValue().create(d['val'])
				item.claims.add(prop, value)
			elif allP[d['property']] =='ExternalId':
				item = wb.Item().get(entity_id=d['qid'])
				prop = wb.Property().get(entity_id=d['property'])
				value = wb.ExternalId().create(d['val'])
				item.claims.add(prop, value)

			else:
				print('unknown data type',allP[d['property']] )
				sys.exit()






