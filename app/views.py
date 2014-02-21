from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN
from config import CONSUMER_KEY
from pocket import Pocket
import json
import requests

@app.before_request
def before_request():
	g.user = current_user

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
	content = {}
	if g.user.is_authenticated():
		params = {
			'consumer_key': CONSUMER_KEY,
			'access_token': g.user.token,
			'since':'1391212800'
		}
		headers = {'content-type':'application/json'}
		resp = requests.post('https://getpocket.com/v3/get', data=json.dumps(params), headers=headers)
		raw = json.loads(resp.content)
		content = raw['list']
	return render_template('index.html',
		content = content)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	# If user is already logged in, simply redirect to index
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	# Load login form
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data # Session data for remembering user
		# Grabs request token from Pocket and stores in session for later authentication
		request_token = Pocket.get_request_token(consumer_key=CONSUMER_KEY, redirect_uri="http://localhost:5000/login")
		session['request_token'] = request_token
		# Grabs auth url from Pocket to redirect user to
		auth_url = Pocket.get_auth_url(code=request_token, redirect_uri="http://localhost:5000" + url_for('auth'))
		return redirect(auth_url)
	return render_template('login.html',
		title = 'Sign In',
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
	# Sets remember me via flask login if set that way
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	# Logs in user and redirects back to index!
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))