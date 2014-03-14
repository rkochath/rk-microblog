from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
bust = Table('bust', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('envelope_id', Integer),
    Column('mate_id', Integer),
    Column('mates_share', Numeric(precision=12, scale=2)),
    Column('mates_contribution', Numeric(precision=12, scale=2)),
    Column('to_recieve', Numeric(precision=12, scale=2)),
    Column('to_pay', Numeric(precision=12, scale=2)),
    Column('settled_amount', Numeric(precision=12, scale=2)),
    Column('currency', String(length=3)),
)

envelope = Table('envelope', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('description', String(length=140)),
    Column('start_date', Date),
    Column('end_date', Date),
    Column('amount', Numeric(precision=12, scale=2)),
    Column('currency', String(length=3)),
    Column('status', String(length=1)),
)

event = Table('event', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=140)),
    Column('envelope_id', Integer),
    Column('event_date', Date),
    Column('amount', Numeric(precision=12, scale=2)),
    Column('currency', String(length=3)),
    Column('bust_by', String(length=1)),
)

event_mates = Table('event_mates', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('envelope_id', Integer),
    Column('mate_id', Integer),
    Column('mates_share', Numeric(precision=12, scale=2)),
    Column('mates_contribution', Numeric(precision=12, scale=2)),
    Column('currency', String(length=3)),
)

holders = Table('holders', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('envelope_id', Integer),
    Column('user_id', Integer),
    Column('members_in_group', Integer),
)

pop_money = Table('pop_money', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('envelope_id', Integer),
    Column('paid_by', Integer),
    Column('paid_to', Integer),
    Column('amount', Numeric(precision=12, scale=2)),
    Column('currency', String(length=3)),
    Column('is_seettled', Numeric(precision=1)),
    Column('settled_on', Date),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['bust'].create()
    post_meta.tables['envelope'].create()
    post_meta.tables['event'].create()
    post_meta.tables['event_mates'].create()
    post_meta.tables['holders'].create()
    post_meta.tables['pop_money'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['bust'].drop()
    post_meta.tables['envelope'].drop()
    post_meta.tables['event'].drop()
    post_meta.tables['event_mates'].drop()
    post_meta.tables['holders'].drop()
    post_meta.tables['pop_money'].drop()
