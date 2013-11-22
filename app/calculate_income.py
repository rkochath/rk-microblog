#from dateutil.rrule import *
#from dateutil.parser import *
from datetime import *

def calculate_income(start_date,   end_date,  no_vacations, no_holidays,  no_sickdays, hourly_rate, work_hours):
	
	#set = rruleset()
	#sd = parse(start_date)
	#ed = parse(end_date)
	#set.rrule(rrule(DAILY, dtstart=sd, until=ed))
	#set.exrule(rrule(YEARLY, byweekday=(SA,SU), dtstart=sd, until=ed))
	#working_days = len(list(set))
	working_days = 0
	income = ( working_days - int(no_vacations) - int(no_holidays) - int(no_sickdays) ) * float(work_hours) * float(hourly_rate)
	
        return str(income)
