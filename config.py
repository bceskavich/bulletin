import os

CSRF_ENABLED = True
SECRET_KEY = 'this-should-be-changed'

basedir = os.path.abspath(os.path.dirname(__file__))

# Path of the database file
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# Path where we store the migration data files
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Pocket API credentials
CONSUMER_KEY = '23571-333bb5dbab872eee6686bf86'
