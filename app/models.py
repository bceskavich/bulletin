from app import db, app
import json
import requests

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index = True, unique = True)
	token = db.Column(db.String(64), index = True, unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	last_seen = db.Column(db.DateTime)
	stories = db.relationship('Story', backref='user', lazy = 'dynamic')

	def load_stories(self, key):
		# Requests params
		params = {
			'consumer_key': key,
			'access_token': self.token,
			'since': '1393172035'
		}
		headers={'content-type':'application/json'}
		# Initial request & raw data response
		resp = requests.post('https://getpocket.com/v3/get', data=json.dumps(params), headers=headers)
		raw = json.loads(resp.content)
		content = raw['list']
		return content

	def is_unique_story(self, story):
		saved = Story.query.filter_by(user_id = self.id, pocket_id = int(story['item_id']))
		if len(saved.all()) > 0:
			return False
		else:
			return True

	def has_trove_presence(self, key, story):
		if story['status'] != '2':
			story_url = story['resolved_url']
			trove_url = 'http://api.washingtonpost.com/trove/v1/items'
			params = {'url':story_url, 'key':key}

			response = requests.get(trove_url, params=params)
			encoded = json.loads(response.content)

			if len(encoded['items']) > 0:
				return True
			else:
				return False

	def save_story(self, item):
		# Stories marked w/ status 2 are faulty and should be deleted
		# and are thus not saved
		if item['status'] != '2':
			# Pulls a proper title
			if item['resolved_title'] is None:
				title = item['given_title']
			else:
				title = item['resolved_title']
			# Saves story w/ proper content from Pocket request
			story = Story(
				user_id = self.id,
				pocket_id = item['item_id'],
				title = title,
				url = item['resolved_url'],
				excerpt = item['excerpt'],
				wordcount = item['word_count'],
				added = item['time_added'],
				status = item['status'],
				favorite = item['favorite'])
			db.session.add(story)
			db.session.commit()

	def troveChannelSearch(self, key, story_url):
	    # TroveAPI URL
	    url = 'http://api.washingtonpost.com/trove/v1/items'
	    params = {'url':story_url, 'key':key}

	    # Query Trove
	    response = requests.get(url, params=params)
	    encoded = json.loads(response.content)
	    data = encoded['items'][0] # Actual response data

	    # Code 200 is the only response we're interested in
	    if encoded['status']['code'] != 200:
	        print 'Ah snap, something went wrong!'
	        channels = None
	    # Populates channel dictionary based on app-wide convention:
	    # { [name]: { source: (Trove/NYT), name: (tag/channel name), (frequency:
	    # int), (id: TroveID), (type: NYT tag type) }
	    elif 'relatedChannels' in data.keys():
	        channels = {}
	        for item in data['relatedChannels']:
	            channels[item['displayName']] = {'source':'Trove', 'id':item['id']}
	    else:
	        print 'No related channels found for this story!'
	        channels = None

	    return channels

	def troveQuery(self, key, channels, story_search=False, channel_search=False):
	    related_stories = [] # For final related stories
	    common_channels = {} # For common channels across queries

	    channel_ids = [item['id'] for item in channels.values()]

	    # Iterates thru each given channel
	    for cid in channel_ids:
	        # Constructions URL & requests info based on specific channel ID
	        url = 'http://api.washingtonpost.com/trove/v1/channels/' + str(cid) + '/result'
	        params = {'key':key}
	        resp = requests.get(url, params=params)
	        encoded = json.loads(resp.content)
	        items = encoded['result']['items'] # Content we care about

	        # Iterates thru response content
	        for i in range(len(items)):
	            if story_search:
	                # Populates list with info on each related story found
	                related_stories.append({
	                    'story_title':items[i]['displayName'],
	                    'story_source':items[i]['source']['displayName'],
	                    'story_url':items[i]['url']
	                    })
	            if channel_search:
	                # Figures out prevalance of channels among the related stories,
	                # but only if there are related channels present.
	                if 'relatedChannels' in items[i].keys():
	                    for channel in items[i]['relatedChannels']:
	                        if channel['displayName'] not in common_channels.keys():
	                            common_channels[channel['displayName']] = {'source':'Trove', 'id':channel['id'], 'frequency':1}
	                        else:
	                            common_channels[channel['displayName']]['frequency'] += 1

	    if story_search:
	        return related_stories
	    elif channel_search:
	        return common_channels

	# Returns top three most common channels based on value frequency
	def topChannels(self, channels):
	    # Initiates top channels dictionary
	    top_channels = {}

	    # Sorts thru & orders channel by frequency
	    # Could be useful for other parts of the app, but not used currently
	    tuples = channels.items()
	    sorted_channels = sorted(tuples, key = lambda tuples: tuples[1]['frequency'], reverse=True)

	    # Finds Top Channel(s) (multiple if tied)
	    max_frequency = sorted_channels[0][1]['frequency']
	    for item in sorted_channels:
	        if item[1]['frequency'] == max_frequency:
	            top_channels[item[0]] = {'source':'Trove', 'id':item[1]['id'], 'frequency':item[1]['frequency']}

	    return top_channels

	# NEEDS START DATE FROM POCKET STORY
	def searchTimesArticles(self, key, channels, story_search=False, tag_search=False):
	    related_stories = [] # For final related stories
	    common_tags = {} # For common channels across queries

	    # Grabs all query names from Trove channel input, assumes could be multiple
	    queries = [name for name in channels.keys()]
	    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'

	    for q in queries:
	        # Makes a request and loads in actual information
	        params = {'q':q, 'api-key':key}
	        response = requests.get(url, params=params)
	        encoded = json.loads(response.content)
	        items = encoded['response']['docs']

	        # Populates related stories array if method called for that purpose
	        if story_search:
	            for item in items:
	                related_stories.append({
	                    'story_title':item['headline']['main'],
	                    'story_source':'New York Times',
	                    'story_url':item['web_url']
	                    })

	        # Populates tag frequency dictionary if method called for that purpose
	        if tag_search:
	            for item in items:
	                for tag in item['keywords']:
	                    if tag['value'] not in common_tags.keys():
	                        common_tags[tag['value']] = {'source':'NY Times','type':tag['name'], 'frequency':1}
	                    else:
	                        common_tags[tag['value']]['frequency'] += 1

	    if story_search:
	        return related_stories
	    elif tag_search:
	        return common_tags

	# Simply combines related searches from Trove & NY Times
	def combineRelatedStories(self, related_trove_stories, related_times_stories):
	    related_stories = related_trove_stories + related_times_stories
	    return related_stories

	# Simply combines tag dictionaries from Trove ('channels') &
	# NY Times (sometimes called 'keywords')
	def combineTopTags(self, common_trove_channels, common_times_tags):
	    all_common_tags = dict(common_trove_channels.items() + common_times_tags.items())
	    return all_common_tags

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<User %r>' % (self.username)

class Story(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	# Uses Pocket's given ID for a saved story to confirm uniqueness
	pocket_id = db.Column(db.Integer, index = True, unique = True)
	title = db.Column(db.String(256), index = True) # should point to 'resolved_title'
	url = db.Column(db.String(256), index = True) # should point to 'resolved_url'
	excerpt = db.Column(db.Text)
	wordcount = db.Column(db.Integer)
	added = db.Column(db.Integer) # unicode time when story was saved by user
	status = db.Column(db.SmallInteger) #0, 1, 2 - 1 if the item is archived - 2 if the item should be deleted
	favorite = db.Column(db.SmallInteger) #0 or 1 - 1 If the item is favorited
	tags = db.Column(db.Text) # JSON object of tags, if had
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Story %r>' % (self.title)
