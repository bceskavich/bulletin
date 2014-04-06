import os

CSRF_ENABLED = True
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'this-should-be-changed'

# Heroku vs. Local Configs
if os.environ.get('HEROKU') is None:
    # Database path
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    # CSRF Key
    SECRET_KEY = 'this-should-be-changed'
    # Pocket API
    CONSUMER_KEY = '23571-333bb5dbab872eee6686bf86'
    # News API Credentials
    TROVE_KEY = 'E767C55D-0941-4993-BB3A-1CB81FD2B9E9'
    NYTIMES_SEARCH_KEY = 'b2f1032fbec2cb261c1e153ab6b5a6b8:13:69075429'
else:
    # Database path
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    # CSRF Key
    SECRET_KEY = os.environ['CSRF_SECRET_KEY']
    # Pocket API
    CONSUMER_KEY = os.environ['POCKET_KEY']
    # News API Credentials
    TROVE_KEY = os.environ['TROVE_KEY']
    NYTIMES_SEARCH_KEY = os.environ['NYTIMES_KEY']

# Path where we store the migration data files
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
