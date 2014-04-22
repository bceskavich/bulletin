#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/bulletin/")

from app import app as application
from config import SECRET_KEY
application.secret_key = SECRET_KEY
