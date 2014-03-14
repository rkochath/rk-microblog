from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, IntegerField,DecimalField,HiddenField, SelectField
#from wtforms_components  import read_only
from wtforms.ext.dateutil.fields import DateField, DateTimeField
from wtforms.validators import Required, Length
from flask.ext.babel import gettext
from app.models import User
    

class EnvelopeForm(Form):
    id = HiddenField('id')
    description = TextField('description',validators = [Required()])    
    start_date = DateField('start_date', validators = [Required()], display_format='%m-%d-%Y')
    end_date = DateField('end_date', validators = [Required()], display_format='%m-%d-%Y')
    amount = DecimalField('amount',  places=2) 
    currency = TextField('currency')
    status = TextField('status')
     
    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        
    def validate(self):
	if not Form.validate(self):
            return False
        return True

class EnvelopeHoldersForm(Form):
    someone = TextField('someone',validators = [Required()])	

class EnvelopeListForm(Form):
    search = TextField('search',validators = [Required()])	
    def __init__(self,   *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        
    def validate(self):
	if not Form.validate(self):
            return False
        return True

