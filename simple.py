from python_wikibase import PyWikibase
import os

if os.path.isfile('./my_config.json'):
	config_path = './my_config.json'
else:
	config_path = './config.json'


wb = PyWikibase(config_path=config_path)

# add a new instance of link
item = wb.Item().get(entity_id="Q1")
prop = wb.Property().get(entity_id='P1')
value = wb.Item().get(entity_id='Q19091') 
item.claims.add(prop, value)