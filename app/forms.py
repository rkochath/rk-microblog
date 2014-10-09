from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, IntegerField,DecimalField,HiddenField,SelectField
from wtforms.widgets import HiddenInput
#from wtforms_components  import read_only
from wtforms.ext.dateutil.fields import DateField, DateTimeField
from wtforms.validators import Required, Length
from flask.ext.babel import gettext
from app.models import User
import bust_a_bill_forms
 

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
    
class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

    
    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname
        
    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(gettext('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        user = User.query.filter_by(nickname = self.nickname.data).first()
        if user != None:
            self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
            return False
        return True
        
class PostForm(Form):
    post = TextField('post', validators = [Required()])
    
class SearchForm(Form):
    search = TextField('search', validators = [Required()])

class InputIncomeForm(Form):
    id = IntegerField('id',widget=HiddenInput())
    next_step = HiddenField('next_step')
    start_date = DateField('start_date', validators = [Required()], display_format='%m-%d-%Y')
    end_date = DateField('end_date', validators = [Required()], display_format='%m-%d-%Y')
    description = TextField('description',validators = [Required()])
    no_vacations = IntegerField('no_vacations', validators = [Required()])
    no_holidays = IntegerField('no_holidays', validators = [Required()])
    no_sickdays = IntegerField('no_sickdays', validators = [Required()])
    hourly_rate = DecimalField('hourly_rate', validators = [Required()], places=2) 

    work_hours = DecimalField('work_hours', validators = [Required()],places=2)
#    exclude_nth = SelectField('exclude_nth', choices=[('1', 'Every'), ('2', '2nd'), ('3', '3rd'),('4', '4th'),('5', '5th'),('6', '6th'),('7', '7th'),('8', '8th'),('9', '9th'),('10', '10th')])
    exclude_nth = SelectField('exclude_nth',choices=[(0, 'Select'),(1, 'Every')])

    exclude_day = SelectField('exclude_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])

    income = DecimalField('income',places=2)
    total_days=IntegerField('total_days',widget=HiddenInput()) 
    total_weekends=IntegerField('total_weekends',widget=HiddenInput())
    total_exclusion_days=IntegerField('total_exclusion_days',widget=HiddenInput())
	
    
    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        
    def validate(self):
	#if not Form.validate(self):
        #    return False
        #if self.nickname.data != User.make_valid_nickname(self.nickname.data):
        #    self.nickname.errors.append(gettext('Error message here.'))
        #    return False
        #user = User.query.filter_by(nickname = self.nickname.data).first()
        #if user != None:
        #    self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
        #    return False
        return True


class ContractsListForm(Form):
    """
    start_date = DateField('start_date', validators = [Required()], display_format='%Y-%m-%d')
    end_date = DateField('end_date', validators = [Required()], display_format='%Y-%m-%d')
    description = TextField('description',validators = [Required()])
    income = TextField('income')  
    """
    search = TextField('search',validators = [Required()])	
    sel = BooleanField('sel')
    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        
    def validate(self):
	if not Form.validate(self):
            return False
        return True

class InputExpenseForm(Form):
    id = IntegerField('id',widget=HiddenInput())
    next_step = HiddenField('next_step')
    description = TextField('description')
    start_date = DateField('start_date', display_format='%m-%d-%Y')
    end_date = DateField('end_date', display_format='%m-%d-%Y')
    
    is_rent_acar = BooleanField('is_rent_acar')
    rental_st_day = SelectField('rental_st_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])
    rental_end_day = SelectField('rental_end_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])
    rental_car_rate = DecimalField('rental_car_rate', validators = [Required()], places=2) 
    
    is_hotel = BooleanField('is_hotel')
    hotel_st_day = SelectField('hotel_st_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])
    hotel_end_day = SelectField('hotel_end_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])
    hotel_rate = DecimalField('hotel_rate', validators = [Required()], places=2)
    daily_expense = DecimalField('daily_expense', validators = [Required()], places=2)

    is_flight = BooleanField('is_flight')
    flight_ticket = DecimalField('flight_ticket', validators = [Required()], places=2)

    is_airport_pickup = BooleanField('is_airport_pickup')
    airport_pickup = DecimalField('airport_pickup', validators = [Required()], places=2)

    is_mileage = BooleanField('is_mileage')
    commute_st_day = SelectField('commute_st_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])
    commute_end_day = SelectField('commute_end_day', choices=[('SU', 'SU'), ('MO', 'MO'), ('TU', 'TU'),('WE', 'WE'),('TH', 'TH'),('FR', 'FR'),('SA', 'SA')])
    daily_miles = DecimalField('daily_miles', validators = [Required()], places=2)
    mileage_rate = DecimalField('mileage_rate', validators = [Required()], places=2)
    expense = DecimalField('expense',places=2)
    
    rental_days=IntegerField('rental_days',widget=HiddenInput())
    hotel_days=IntegerField('hotel_days',widget=HiddenInput())
    no_flights=IntegerField('no_flights',widget=HiddenInput())
    commute_days=IntegerField('commute_days',widget=HiddenInput())

    
    
    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        
    def validate(self):
	#if not Form.validate(self):
        #    return False
        return True
    



class InputOtherDedForm(Form):

    id = IntegerField('id',widget=HiddenInput())
    next_step = HiddenField('next_step')
    description = TextField('description')
    start_date = DateField('start_date', display_format='%m-%d-%Y')
    end_date = DateField('end_date', display_format='%m-%d-%Y')
    other_deductions = DecimalField('other_deductions',places=2)
    
    hsa_contr = DecimalField('hsa_contr', validators = [Required()], places=2)
    hsa_contr_freq = SelectField('hsa_contr_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_hsa_pre_tax = BooleanField('is_hsa_pre_tax')
    retirement_contr = DecimalField('retirement_contr', validators = [Required()], places=2)
    retirement_contr_freq = SelectField('retirement_contr_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_retirement_pre_tax =BooleanField('is_retirement_pre_tax')
    health_ins_prem = DecimalField('health_ins_prem', validators = [Required()], places=2)
    health_ins_freq = SelectField('health_ins_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_health_pre_tax = BooleanField('is_health_pre_tax')
    vision_ins_prem = DecimalField('vision_ins_prem', validators = [Required()], places=2)
    is_vision_pre_tax = BooleanField('is_vision_pre_tax')
    vision_ins_freq = SelectField('vision_ins_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    dental_ins_prem = DecimalField('dental_ins_prem', validators = [Required()], places=2)
    dental_ins_freq =SelectField('dental_ins_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_dental_pre_tax = BooleanField('is_dental_pre_tax')
    shortterm_dis_prem = DecimalField('shortterm_dis_prem', validators = [Required()], places=2)
    shortterm_dis_freq=SelectField('shortterm_dis_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_shortterm_pre_tax=BooleanField('is_shortterm_pre_tax')
    longterm_dis_prem = DecimalField('longterm_dis_prem', validators = [Required()], places=2)
    longterm_dis_freq=SelectField('longterm_dis_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_longterm_pre_tax = BooleanField('is_longterm_pre_tax')
    life_ins_prem = DecimalField('life_ins_prem', validators = [Required()], places=2)
    life_ins_freq=SelectField('life_ins_freq', choices=[('W', 'Weekly'), ('BW', 'Bi-Weekly'), ('M', 'Monthly')]) 
    is_life_pre_tax = BooleanField('is_life_pre_tax')


    no_hsa_contr=IntegerField('no_hsa_contr',widget=HiddenInput())
    no_retirement_contr=IntegerField('no_retirement_contr',widget=HiddenInput())
    no_health_ins=IntegerField('no_health_ins',widget=HiddenInput())
    no_vision_ins=IntegerField('no_vision_ins',widget=HiddenInput())
    no_dental_ins=IntegerField('no_dental_ins',widget=HiddenInput())
    no_shortterm_dis=IntegerField('no_shortterm_dis',widget=HiddenInput())
    no_longterm_dis=IntegerField('no_longterm_dis',widget=HiddenInput())
    no_life_ins=IntegerField('no_life_ins',widget=HiddenInput())

    

    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
	#if not Form.validate(self):
        #    return False
        return True

class InputTaxForm(Form):

    id = IntegerField('id',widget=HiddenInput())
    description = TextField('description')
    
    next_step = HiddenField('next_step')
    start_date = DateField('start_date', display_format='%m-%d-%Y')
    end_date = DateField('end_date', display_format='%m-%d-%Y')
    taxes = DecimalField('taxes',places=2)

    fed_tax_perc = DecimalField('fed_tax_perc', validators = [Required()], places=2)
    state_tax_perc = DecimalField('state_tax_perc', validators = [Required()], places=2)
    ssn_tax_perc = DecimalField('ssn_tax_perc', validators = [Required()], places=2)
    self_emp_tax_perc = DecimalField('self_emp_tax_perc', validators = [Required()], places=2)
    medicare_tax_perc=DecimalField('medicare_tax_perc', validators = [Required()], places=2)
    
    fed_tax = DecimalField('fed_tax', validators = [Required()], places=2)
    state_tax = DecimalField('state_tax', validators = [Required()], places=2)
    ssn_tax = DecimalField('ssn_tax', validators = [Required()], places=2)
    self_emp_tax = DecimalField('self_emp_tax', validators = [Required()], places=2)
    medicare_tax=DecimalField('medicare_tax', validators = [Required()], places=2)

    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
	#if not Form.validate(self):
        #    return False
        return True

