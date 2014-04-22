import sys
#import couchdb
import json
import pocket
import requests

#server = couchdb.Server('http://localhost:5984')

username = 'ceskavich'
access_token = 'f2f6b3ea-4f72-d71d-bdaf-43ad9f'
consumer_key = '23571-333bb5dbab872eee6686bf86'

url = "https://getpocket.com/v3/get"
params = {
	'consumer_key':consumer_key,
	'access_token':access_token,
	'since':'1391212800',
	'contentType':'image'
	}
headers = {'content-type': 'application/json'}

def pocket_query(url, params):
	r = requests.post(url, data=json.dumps(params), headers=headers)
	encoded = json.loads(r.content)
	return encoded

	#print json.dumps(encoded, indent=1)

	#results = encoded['list'].values() # values equals json for each story ID
	#print json.dumps(results, indent=1)
	#return results

def save_to_DB(dbname, data):
	try:
		db = server.create(dbname)
		print "Created new database named:", dbname
		db.update(data, all_or_nothing = True)
		print "Data saved to new database!"
	except ValueError, e:
		print "Invalid database name"
		sys.exit(0)

def load_from_DB(dbname):
	try:
		db = server[dbname]
		print "Connected to database named:", dbname
	except couchdb.http.PreconditionFailed, e:
		db = server[dbname]
		print "Could not find database named:", dbname
	except ValueError, e:
		print "Invalid database name"

	results = [db[key] for key in db]
	return results

def send_to_pocket(url):
	# Requests params
	params = {
		'consumer_key': '23571-333bb5dbab872eee6686bf86',
		'access_token': 'f2f6b3ea-4f72-d71d-bdaf-43ad9f',
		'url':url
	}
	headers={'content-type':'application/json'}
	# Initial request & raw data response
	resp = requests.post('https://getpocket.com/v3/add', data=json.dumps(params), headers=headers)
	raw = json.loads(resp.content)
	return raw

if __name__ == '__main__':
	#dbname = raw_input("Please enter database name: ")

	#results = pocket_query(url, params)
	#print json.dumps(results, indent=1)
	# save_to_DB(dbname, results)

	test_url = 'http://www.mirror.co.uk/news/world-news/missing-mh370-live-relatives-passengers-3440767'
	response = send_to_pocket(test_url)
	print json.dumps(response, indent=1)

	"""
	saved_data = load_from_DB(dbname)
	for record in saved_data:
		print "----"
		print
		print "TITLE:", record['resolved_title']
		print "SOURCE:", record['resolved_url']
		print
		print "EXCERPT:", record['excerpt']
		print
		print "----"
	"""
