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

	def load_stories(self, key, headers={'content-type':'application/json'}):
		# Requests params
		params = {
			'consumer_key': key,
			'access_token': self.token,
			'since': '1391212800'
		}
		# Initial request & raw data response
		resp = requests.post('https://getpocket.com/v3/get', data=json.dumps(params), headers=headers)
		raw = json.loads(resp.content)
		content = raw['list']
		return content

	"""
	def is_unique_story(self, story):
		saved = self.stories.all()
		while True:
			for item in saved:
				if item.pocket_id == story.pocket_id:
					return False
	"""

	def save_story(self, item):
		story = Story(
			user_id = self.id,
			pocket_id = item['item_id'],
			title = item['given_title'],
			url = item['resolved_url'],
			excerpt = item['excerpt'],
			wordcount = item['word_count'],
			added = item['time_added'],
			status = item['status'],
			favorite = item['favorite'])
		db.session.add(story)
		db.session.commit()

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
