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
		#print "Trove Info For: " + story_title
		#print json.dumps(encoded, indent=1)
	elif item_by_id:
		item_id = kwargs['item_id']
		url = url + "items/" + channel_id
		params = {
			'key':key
		}
		resp = requests.get(url, params=params)
		encoded = json.loads(resp.content)
		print json.dumps(encoded, indent=1)
	print "----"
	print "Now searching relevant content for channel id: " + str(channel_id)
	url = "http://api.washingtonpost.com/trove/v1/channels/" + str(channel_id) + "/result"
	params = {
		'key':key
	}
	resp = requests.get(url, params=params)
	encoded = json.loads(resp.content)
	return encoded

if __name__ == '__main__':
	developer_key = '0B71E343-7663-423D-9FD1-8C7364D683CE'

	url = 'http://www.bbc.com/news/business-26414285'
	title = 'Russian rouble hits new low against the dollar and euro'

	data = trove_query(developer_key, find_items=True, story_url=url, story_title=title)
	items = data['result']['items']

	print "LOADING RELATED INFO TO STORY:", title 

	for i in range(len(items)):
		print "#############"
		print "Story Title:", items[i]['displayName']
		print "Story Source:", items[i]['url']
		print "Story Source:", items[i]['source']['displayName'] 