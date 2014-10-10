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
    Column('hourly_perdiem', Numeric(precision=6, scale=2)),
    Column('work_hours', Numeric(precision=6, scale=2)),
    Column('exclude_nth', Integer),
    Column('exclude_day', String(length=2)),
    Column('income', Numeric(precision=14, scale=2)),
    Column('expense', Numeric(precision=14, scale=2)),
    Column('other_deductions', Numeric(precision=14, scale=2)),
    Column('taxes', Numeric(precision=14, scale=2)),
    Column('is_rent_acar', SmallInteger),
    Column('rental_st_day', String(length=2)),
    Column('rental_end_day', String(length=2)),
    Column('rental_car_rate', Numeric(precision=6, scale=2)),
    Column('is_hotel', SmallInteger),
    Column('hotel_st_day', String(length=2)),
    Column('hotel_end_day', String(length=2)),
    Column('hotel_rate', Numeric(precision=6, scale=2)),
    Column('daily_expense', Numeric(precision=6, scale=2)),
    Column('is_flight', SmallInteger),
    Column('flight_ticket', Numeric(precision=6, scale=2)),
    Column('is_airport_pickup', SmallInteger),
    Column('airport_pickup', Numeric(precision=6, scale=2)),
    Column('is_mileage', SmallInteger),
    Column('commute_st_day', String(length=2)),
    Column('commute_end_day', String(length=2)),
    Column('daily_miles', Numeric(precision=6, scale=2)),
    Column('mileage_rate', Numeric(precision=6, scale=2)),
    Column('timestamp', DateTime),
    Column('hsa_contr', Numeric(precision=6, scale=2)),
    Column('hsa_contr_freq', String(length=2)),
    Column('is_hsa_pre_tax', SmallInteger),
    Column('retirement_contr', Numeric(precision=6, scale=2)),
    Column('retirement_contr_freq', String(length=2)),
    Column('is_retirement_pre_tax', SmallInteger),
    Column('health_ins_prem', Numeric(precision=6, scale=2)),
    Column('health_ins_freq', String(length=2)),
    Column('is_health_pre_tax', SmallInteger),
    Column('vision_ins_prem', Numeric(precision=6, scale=2)),
    Column('is_vision_pre_tax', SmallInteger),
    Column('vision_ins_freq', String(length=2)),
    Column('dental_ins_prem', Numeric(precision=6, scale=2)),
    Column('dental_ins_freq', String(length=2)),
    Column('is_dental_pre_tax', SmallInteger),
    Column('shortterm_dis_prem', Numeric(precision=6, scale=2)),
    Column('shortterm_dis_freq', String(length=2)),
    Column('is_shortterm_pre_tax', SmallInteger),
    Column('longterm_dis_prem', Numeric(precision=6, scale=2)),
    Column('longterm_dis_freq', String(length=2)),
    Column('is_longterm_pre_tax', SmallInteger),
    Column('life_ins_prem', Numeric(precision=6, scale=2)),
    Column('life_ins_freq', String(length=2)),
    Column('is_life_pre_tax', SmallInteger),
    Column('fed_tax_perc', Numeric(precision=6, scale=2)),
    Column('state_tax_perc', Numeric(precision=6, scale=2)),
    Column('ssn_tax_perc', Numeric(precision=6, scale=2)),
    Column('self_emp_tax_perc', Numeric(precision=6, scale=2)),
    Column('medicare_tax_perc', Numeric(precision=6, scale=2)),
    Column('fed_tax', Numeric(precision=12, scale=2)),
    Column('state_tax', Numeric(precision=12, scale=2)),
    Column('ssn_tax', Numeric(precision=12, scale=2)),
    Column('self_emp_tax', Numeric(precision=12, scale=2)),
    Column('medicare_tax', Numeric(precision=12, scale=2)),
    Column('total_days', Integer),
    Column('total_weekends', Integer),
    Column('total_exclusion_days', Integer),
    Column('rental_days', Integer),
    Column('hotel_days', Integer),
    Column('no_flights', Integer),
    Column('commute_days', Integer),
    Column('no_hsa_contr', Integer),
    Column('no_retirement_contr', Integer),
    Column('no_health_ins', Integer),
    Column('no_vision_ins', Integer),
    Column('no_dental_ins', Integer),
    Column('no_shortterm_dis', Integer),
    Column('no_longterm_dis', Integer),
    Column('no_life_ins', Integer),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['hourly_perdiem'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['hourly_perdiem'].drop()
