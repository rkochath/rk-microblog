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
    Column('income', Numeric(precision=14, scale=2)),
    Column('expense', Numeric(precision=14, scale=2)),
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
    Column('is_hsa_pre_tax', Boolean),
    Column('retirement_contr', Numeric(precision=6, scale=2)),
    Column('retirement_contr_freq', String(length=2)),
    Column('is_retirement_pre_tax', Boolean),
    Column('health_ins_prem', Numeric(precision=6, scale=2)),
    Column('health_ins_freq', String(length=2)),
    Column('is_health_pre_tax', Boolean),
    Column('vision_ins_prem', Numeric(precision=6, scale=2)),
    Column('is_vision_pre_tax', Boolean),
    Column('vision_ins_freq', String(length=2)),
    Column('dental_ins_prem', Numeric(precision=6, scale=2)),
    Column('dental_ins_freq', String(length=2)),
    Column('is_dental_pre_tax', Boolean),
    Column('shortterm_dis_prem', Numeric(precision=6, scale=2)),
    Column('shortterm_dis_freq', String(length=2)),
    Column('is_shortterm_pre_tax', Boolean),
    Column('longterm_dis_prem', Numeric(precision=6, scale=2)),
    Column('longterm_dis_freq', String(length=2)),
    Column('is_longterm_pre_tax', Boolean),
    Column('life_ins_prem', Numeric(precision=6, scale=2)),
    Column('life_ins_freq', String(length=2)),
    Column('is_life_pre_tax', Boolean),
    Column('fed_tax_perc', Numeric(precision=6, scale=2)),
    Column('state_tax_perc', Numeric(precision=6, scale=2)),
    Column('ssn_tax_perc', Numeric(precision=6, scale=2)),
    Column('self_emp_tax_perc', Numeric(precision=6, scale=2)),
    Column('medicare_tax_perc', Numeric(precision=6, scale=2)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['dental_ins_freq'].create()
    post_meta.tables['contracts'].columns['dental_ins_prem'].create()
    post_meta.tables['contracts'].columns['fed_tax_perc'].create()
    post_meta.tables['contracts'].columns['health_ins_freq'].create()
    post_meta.tables['contracts'].columns['health_ins_prem'].create()
    post_meta.tables['contracts'].columns['hsa_contr'].create()
    post_meta.tables['contracts'].columns['hsa_contr_freq'].create()
    post_meta.tables['contracts'].columns['is_dental_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_health_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_hsa_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_life_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_longterm_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_retirement_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_shortterm_pre_tax'].create()
    post_meta.tables['contracts'].columns['is_vision_pre_tax'].create()
    post_meta.tables['contracts'].columns['life_ins_freq'].create()
    post_meta.tables['contracts'].columns['life_ins_prem'].create()
    post_meta.tables['contracts'].columns['longterm_dis_freq'].create()
    post_meta.tables['contracts'].columns['longterm_dis_prem'].create()
    post_meta.tables['contracts'].columns['medicare_tax_perc'].create()
    post_meta.tables['contracts'].columns['retirement_contr'].create()
    post_meta.tables['contracts'].columns['retirement_contr_freq'].create()
    post_meta.tables['contracts'].columns['self_emp_tax_perc'].create()
    post_meta.tables['contracts'].columns['shortterm_dis_freq'].create()
    post_meta.tables['contracts'].columns['shortterm_dis_prem'].create()
    post_meta.tables['contracts'].columns['ssn_tax_perc'].create()
    post_meta.tables['contracts'].columns['state_tax_perc'].create()
    post_meta.tables['contracts'].columns['vision_ins_freq'].create()
    post_meta.tables['contracts'].columns['vision_ins_prem'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contracts'].columns['dental_ins_freq'].drop()
    post_meta.tables['contracts'].columns['dental_ins_prem'].drop()
    post_meta.tables['contracts'].columns['fed_tax_perc'].drop()
    post_meta.tables['contracts'].columns['health_ins_freq'].drop()
    post_meta.tables['contracts'].columns['health_ins_prem'].drop()
    post_meta.tables['contracts'].columns['hsa_contr'].drop()
    post_meta.tables['contracts'].columns['hsa_contr_freq'].drop()
    post_meta.tables['contracts'].columns['is_dental_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_health_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_hsa_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_life_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_longterm_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_retirement_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_shortterm_pre_tax'].drop()
    post_meta.tables['contracts'].columns['is_vision_pre_tax'].drop()
    post_meta.tables['contracts'].columns['life_ins_freq'].drop()
    post_meta.tables['contracts'].columns['life_ins_prem'].drop()
    post_meta.tables['contracts'].columns['longterm_dis_freq'].drop()
    post_meta.tables['contracts'].columns['longterm_dis_prem'].drop()
    post_meta.tables['contracts'].columns['medicare_tax_perc'].drop()
    post_meta.tables['contracts'].columns['retirement_contr'].drop()
    post_meta.tables['contracts'].columns['retirement_contr_freq'].drop()
    post_meta.tables['contracts'].columns['self_emp_tax_perc'].drop()
    post_meta.tables['contracts'].columns['shortterm_dis_freq'].drop()
    post_meta.tables['contracts'].columns['shortterm_dis_prem'].drop()
    post_meta.tables['contracts'].columns['ssn_tax_perc'].drop()
    post_meta.tables['contracts'].columns['state_tax_perc'].drop()
    post_meta.tables['contracts'].columns['vision_ins_freq'].drop()
    post_meta.tables['contracts'].columns['vision_ins_prem'].drop()
