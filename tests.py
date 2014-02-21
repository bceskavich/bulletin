#!env/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Story
from datetime import datetime, timedelta

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['CSRF_ENABLED'] = True
		app.config['SQLALCHEMY_DATABSE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_is_unique_story(self):
		u = User(username='billy')
		db.session.add(u)
		db.session.commit()
		s1 = Story(title='First Story', pocket_id='1234')
		s2 = Story(title='Second Story', pocket_id='4567')
		db.session.add(s1)
		db.session.add(s2)
		db.session.commit()
		assert u.is_unique_story(s1) == False

if __name__ == '__main__':
	unittest.main()