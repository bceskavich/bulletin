from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from forms import LoginForm, LoadForm
from models import User, Story, ROLE_USER, ROLE_ADMIN
from config import CONSUMER_KEY, TROVE_KEY, NYTIMES_SEARCH_KEY
from pocket import Pocket
from datetime import datetime, timedelta
import json
import requests

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('home'))
	else:
		return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
	form = LoadForm()
	content = {}
	if g.user is not None and g.user.is_authenticated():
		if form.validate_on_submit():
			# Queries the Pocket API for user's conent
			content = g.user.load_stories(CONSUMER_KEY)
			for item in content:
				# Checks if a story is already saved in our DB,
				# only saves if not previously saved
				if g.user.is_unique_story(content[item]) and g.user.has_trove_presence(TROVE_KEY, content[item]):
					g.user.save_story(content[item])
			return redirect(url_for('index'))
		content = Story.query.filter_by(user_id = g.user.id).all()
	return render_template('home.html',
		content = content,
		form = form)

@app.route('/story/<id>')
@login_required
def story(id):
	story = Story.query.get(int(id))
	date_saved = datetime.fromtimestamp(story.added)
	channels = g.user.troveChannelSearch(TROVE_KEY, story.url)
	common_channels = g.user.troveQuery(TROVE_KEY, channels, channel_search=True)
	top_channels = g.user.topChannels(common_channels)
	related_trove_stories = g.user.troveQuery(TROVE_KEY, top_channels, story_search=True)
	common_tags = g.user.searchTimesArticles(NYTIMES_SEARCH_KEY, top_channels, date_saved, tag_search=True)
	related_times_stories = g.user.searchTimesArticles(NYTIMES_SEARCH_KEY, top_channels, date_saved, story_search=True)
	all_tags = g.user.combineTopTags(common_channels, common_tags)
	related_stories = g.user.combineRelatedStories(related_trove_stories, related_times_stories)
	if story == None:
		flash('This story was not found!')
		return redirect(url_for('index'))
	return render_template('story.html',
		story = story,
		date_saved = date_saved,
		topics = all_tags,
		related_stories = related_stories)

### Login Logic ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
	# If user is already logged in, simply redirect to index
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('home'))
	# Load login if not logged in
	else:
		form = LoginForm()
		if form.validate_on_submit():
			# Grabs request token from Pocket and stores in session for later authentication
			request_token = Pocket.get_request_token(consumer_key=CONSUMER_KEY, redirect_uri="http://localhost:5000/login")
			session['request_token'] = request_token
			# Grabs auth url from Pocket to redirect user to
			auth_url = Pocket.get_auth_url(code=request_token, redirect_uri="http://localhost:5000" + url_for('auth'))
			return redirect(auth_url)
	return render_template('index.html',
		form = form)

@app.route('/auth', methods= ['GET', 'POST'])
def auth():
	# Pulls request token from session, deletes
	if 'request_token' in session:
		request_token = session['request_token']
		session.pop('request_token', None)
	# Authenticates user via Pocket API
	# Grabs both Pocket username and API access token to store in DB
	credentials = Pocket.get_credentials(consumer_key=CONSUMER_KEY, code=request_token)
	token = credentials['access_token']
	username = credentials['username']
	# If access token is received, redirect back to login
	if token is None or token == "":
		flash('Login Failed! Please try again.')
		return redirect(url_for('login'))
	# Creates user if one doesn't already exist w/ the username + access token pair
	user = User.query.filter_by(username = username).first()
	if user is None:
		user = User(username = username, token = token, role = ROLE_USER)
		db.session.add(user)
		db.session.commit()
	# Logs in user and redirects back to index!
	login_user(user)
	return redirect(request.args.get('next') or url_for('home'))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
