from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import os
from flask.ext.login import LoginManager
from config import basedir

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)

from app import views, models
