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
    Column('exclude_nth', Integer),
    Column('exclude_day', String(length=2)),
    Column('income', Numeric(precision=12, scale=2)),
    Column('is_rent_acar', Boolean),
    Column('rental_st_day', String(length=2)),
    Column('rental_end_day', String(length=2)),
    Column('rental_car_rate', Numeric(precision=6, scale=2)),
    Column('is_hotel', Boolean),
    Column('hotel_st_day', String(length=2)),
    Column('hotel_end_day', String(length=2)),
    Column('hotel_rate', Numeric(precision=6, scale=2)),
    Column('daily_expense', Numeric(precision=6, scale=2)),
    Column('is_flight', Boolean),
    Column('flight_ticket', Numeric(precision=6, scale=2)),
    Column('is_airport_pickup', Boolean),
    Column('airport_pickup', Numeric(precision=6, scale=2)),
    Column('is_mileage', Boolean),
    Column('commute_st_day', String(length=2)),
    Column('commute_end_day', String(length=2)),
    Column('daily_miles', Numeric(precision=6, scale=2)),
    Column('mileage_rate', Numeric(precision=6, scale=2)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['airport_pickup'].create()
    post_meta.tables['contracts'].columns['commute_end_day'].create()
    post_meta.tables['contracts'].columns['commute_st_day'].create()
    post_meta.tables['contracts'].columns['daily_expense'].create()
    post_meta.tables['contracts'].columns['daily_miles'].create()
    post_meta.tables['contracts'].columns['exclude_day'].create()
    post_meta.tables['contracts'].columns['exclude_nth'].create()
    post_meta.tables['contracts'].columns['hotel_end_day'].create()
    post_meta.tables['contracts'].columns['hotel_st_day'].create()
    post_meta.tables['contracts'].columns['is_airport_pickup'].create()
    post_meta.tables['contracts'].columns['is_flight'].create()
    post_meta.tables['contracts'].columns['is_hotel'].create()
    post_meta.tables['contracts'].columns['is_mileage'].create()
    post_meta.tables['contracts'].columns['is_rent_acar'].create()
    post_meta.tables['contracts'].columns['mileage_rate'].create()
    post_meta.tables['contracts'].columns['rental_end_day'].create()
    post_meta.tables['contracts'].columns['rental_st_day'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['airport_pickup'].drop()
    post_meta.tables['contracts'].columns['commute_end_day'].drop()
    post_meta.tables['contracts'].columns['commute_st_day'].drop()
    post_meta.tables['contracts'].columns['daily_expense'].drop()
    post_meta.tables['contracts'].columns['daily_miles'].drop()
    post_meta.tables['contracts'].columns['exclude_day'].drop()
    post_meta.tables['contracts'].columns['exclude_nth'].drop()
    post_meta.tables['contracts'].columns['hotel_end_day'].drop()
    post_meta.tables['contracts'].columns['hotel_st_day'].drop()
    post_meta.tables['contracts'].columns['is_airport_pickup'].drop()
    post_meta.tables['contracts'].columns['is_flight'].drop()
    post_meta.tables['contracts'].columns['is_hotel'].drop()
    post_meta.tables['contracts'].columns['is_mileage'].drop()
    post_meta.tables['contracts'].columns['is_rent_acar'].drop()
    post_meta.tables['contracts'].columns['mileage_rate'].drop()
    post_meta.tables['contracts'].columns['rental_end_day'].drop()
    post_meta.tables['contracts'].columns['rental_st_day'].drop()
