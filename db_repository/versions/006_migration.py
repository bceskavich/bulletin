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


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['story'].columns['pocket_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['story'].columns['pocket_id'].drop()
