from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
story = Table('story', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('pocket_id', Integer),
    Column('title', String(length=256)),
    Column('url', String(length=256)),
    Column('excerpt', Text),
    Column('wordcount', Integer),
    Column('added', Integer),
    Column('status', SmallInteger),
    Column('favorite', SmallInteger),
    Column('tags', Text),
    Column('user_id', Integer),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('token', String(length=64)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
    Column('last_seen', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['story'].create()
    post_meta.tables['user'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['story'].drop()
    post_meta.tables['user'].drop()
