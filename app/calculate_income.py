from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from app import app

def calculate_income(start_date,   end_date,  no_vacations, no_holidays,  no_sickdays, hourly_rate, work_hours,
exclude_nth ,	exclude_day):
	
	set = rruleset()
	sd = parse(start_date)
	ed = parse(end_date)

	set.rrule(rrule(DAILY, dtstart=sd, until=ed))
	set.exrule(rrule(YEARLY, byweekday=(SA,SU), dtstart=sd, until=ed))

        if exclude_nth != 0 :
		rrule_constant = {'SU':SU,'MO':MO,'TU':TU,'WE':WE,'TH':TH,'FR':FR,'SA':SA}
		set.exrule(rrule(YEARLY, interval=int(exclude_nth),  byweekday=rrule_constant[exclude_day], dtstart=sd, until=ed))

	working_days = len(list(set))
        working_days =  working_days - int(no_vacations) - int(no_holidays) - int(no_sickdays) 
	income =  working_days  * float(work_hours) * float(hourly_rate)
        return str(income)

def calculate_total_expense(start_date,   end_date,  is_rent_acar, rental_st_day, rental_end_day, rental_car_rate, is_mileage, commute_st_day,   commute_end_day, daily_miles, mileage_rate, is_hotel, hotel_st_day, hotel_end_day, hotel_rate, daily_expense, is_flight, flight_ticket, is_airport_pickup, airport_pickup):
	app.logger.info('inside calculate total expense fucntion') 
	rrule_constant = {'SU':SU,'MO':MO,'TU':TU,'WE':WE,'TH':TH,'FR':FR,'SA':SA}
	day_no = {'SU':0,'MO':1,'TU':2,'WE':3,'TH':4,'FR':5,'SA':6}
        day_no_constant = {0:SU,1:MO,2:TU,3:WE,4:TH,5:FR,6:SA}

	sd = parse(start_date)
	ed = parse(end_date)
	total_expense = 0
	app.logger.info('boolean values %s %s %s %s %s' % (is_rent_acar, is_mileage, is_hotel, is_flight, is_airport_pickup) )


	if is_rent_acar=='true':
    		set = rruleset()
		st_day_no = day_no[rental_st_day]
		end_day_no = day_no[rental_end_day]
		days = [day_no_constant[x] for x in range(st_day_no,end_day_no+1)]
		app.logger.info('days=%s'% days) 
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		total_expense += len(list(set))*float(rental_car_rate)
		
	if is_mileage =='true':
    		set = rruleset()
		st_day_no = day_no[commute_st_day]
		end_day_no = day_no[commute_end_day]
		days = [day_no_constant[x] for x in range(st_day_no,end_day_no+1)]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))	
		total_expense += len(list(set))*float(daily_miles)*float(mileage_rate)

	if is_hotel =='true':
    		set = rruleset()
		st_day_no = day_no[hotel_st_day]
		end_day_no = day_no[hotel_end_day]
		days = [day_no_constant[x] for x in range(st_day_no,end_day_no+1)]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		total_expense += len(list(set))*float(hotel_rate) + len(list(set))*float(daily_expense)

	if is_flight =='true':
    		set = rruleset()
		#add flight depart and arrival day in the form and calc
		st_day_no = day_no[rental_st_day]
		days = day_no_constant[st_day_no]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		total_expense += len(list(set))*float(flight_ticket)

	if is_airport_pickup =='true':
    		set = rruleset()
		#add flight depart and arrival day in the form and calc
		st_day_no = day_no[rental_st_day]
		days = day_no_constant[st_day_no]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		total_expense += len(list(set))*float(airport_pickup)
	app.logger.info('Total expense %s'% total_expense) 
        return str(total_expense)
