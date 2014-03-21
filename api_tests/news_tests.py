import json
import requests

def trove_query(key, find_items=False, item_by_id=False, **kwargs):
	url = "http://api.washingtonpost.com/trove/v1/"
	if find_items:
		url = url + "items"
		story_url = kwargs['story_url']
		story_title = kwargs['story_title']
		params = {
			'key':key,
			'url':story_url
		}
		resp = requests.get(url, params=params)
		encoded = json.loads(resp.content)
		channel_id = encoded['items'][0]['relatedChannels'][0]['id']
		channel_name = encoded['items'][0]['relatedChannels'][0]['displayName']
		print "Trove Info For: " + story_title
		print json.dumps(encoded, indent=1)
	elif item_by_id:
		item_id = kwargs['item_id']
		url = url + "items/" + item_id
		params = {
			'key':key
		}
		resp = requests.get(url, params=params)
		encoded = json.loads(resp.content)
		print json.dumps(encoded, indent=1)
	"""
	print "----"
	print "Now searching relevant content for channel id:", channel_name
	url = "http://api.washingtonpost.com/trove/v1/channels/" + str(channel_id) + "/result"
	params = {
		'key':key
	}
	resp = requests.get(url, params=params)
	encoded = json.loads(resp.content)
	return encoded
	"""

if __name__ == '__main__':
	developer_key = 'EE272629-4004-4A46-B003-4992DF29BFEE'

	url = 'http://www.washingtonpost.com/world/plane-search-stymied-by-intense-weather-in-pretty-rough-part-of-the-world/2014/03/21/0e7a5c5a-b0e9-11e3-a49e-76adc9210f19_story.html'
	title = 'Malaysia Flight 370 Story'

	# BY TROVE ID
	# trove_query(developer_key, item_by_id=True, item_id='3Ej4K', story_url=url, story_title=title)

	# BY TITLE
	data = trove_query(developer_key, find_items=True, story_url=url, story_title=title)
	
	print json.dumps(data, indent=1)

	"""
	print "LOADING RELATED INFO TO STORY:", title 

	for i in range(len(items)):
		print "#############"
		print "Story Title:", items[i]['displayName']
		print "Story Source:", items[i]['url']
		print "Story Source:", items[i]['source']['displayName'] 
	"""