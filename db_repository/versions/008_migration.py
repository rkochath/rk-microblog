from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
contracts = Table('contracts', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('description', String(length=140)),
    Column('start_date', Date),
    Column('end_date', Date),
    Column('no_vacations', Integer),
    Column('no_holidays', Integer),
    Column('no_sickdays', Integer),
    Column('hourly_rate', Numeric(precision=6, scale=2)),
    Column('work_hours', Numeric(precision=6, scale=2)),
    Column('income', Numeric(precision=12, scale=2)),
    Column('federal_tax_rate', Numeric(precision=6, scale=2)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['federal_tax_rate'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['federal_tax_rate'].drop()
