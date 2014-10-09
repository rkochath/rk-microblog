from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from app import app
from app import app, db
from models import User, ROLE_USER, ROLE_ADMIN, Post,Contracts


def calculate_total_income(start_date,   end_date,  no_vacations, no_holidays,  no_sickdays, hourly_rate, work_hours,
exclude_nth ,	exclude_day):
	
	set = rruleset()
	sd = parse(start_date)
	ed = parse(end_date)
        app.logger.info('calculate total income ' )        	
	set.rrule(rrule(DAILY, dtstart=sd, until=ed))
	total_days = len(list(set))
	set.exrule(rrule(YEARLY, byweekday=(SA,SU), dtstart=sd, until=ed))
        total_exclusion_days=0
        total_weekends =  total_days - len(list(set))
        
        if exclude_nth != '0' :
		rrule_constant = {'SU':SU,'MO':MO,'TU':TU,'WE':WE,'TH':TH,'FR':FR,'SA':SA}
		set.exrule(rrule(YEARLY, interval=int(exclude_nth),  byweekday=rrule_constant[exclude_day], dtstart=sd, until=ed))
		total_exclusion_days = total_days - total_weekends - len(list(set))
		

	working_days = len(list(set))
        working_days =  working_days - int(no_vacations) - int(no_holidays) - int(no_sickdays) 
	income =  working_days  * float(work_hours) * float(hourly_rate)
	
	app.logger.info(str('{"income":%s,"total_days":%s, "total_weekends":%s, "total_exclusion_days": %s}' % ( income,total_days, total_weekends, total_exclusion_days)) )        	
	
        return str('{"income":%s,"total_days":%s, "total_weekends":%s, "total_exclusion_days": %s}' % ( income,total_days, total_weekends, total_exclusion_days))

def calculate_total_expense(start_date,   end_date,  is_rent_acar, rental_st_day, rental_end_day, rental_car_rate, is_mileage, commute_st_day,   commute_end_day, daily_miles, mileage_rate, is_hotel, hotel_st_day, hotel_end_day, hotel_rate, daily_expense, is_flight, flight_ticket, is_airport_pickup, airport_pickup):
	app.logger.info('inside calculate total expense fucntion') 
	rrule_constant = {'SU':SU,'MO':MO,'TU':TU,'WE':WE,'TH':TH,'FR':FR,'SA':SA}
	day_no = {'SU':0,'MO':1,'TU':2,'WE':3,'TH':4,'FR':5,'SA':6}
        day_no_constant = {0:SU,1:MO,2:TU,3:WE,4:TH,5:FR,6:SA}

	sd = parse(start_date)
	ed = parse(end_date)
	total_expense = 0
	rental_days=0
	hotel_days=0
	no_flights=0
	commute_days=0
	
	app.logger.info('boolean values %s %s %s %s %s' % (is_rent_acar, is_mileage, is_hotel, is_flight, is_airport_pickup) )


	if is_rent_acar=='true':
    		set = rruleset()
		st_day_no = day_no[rental_st_day]
		end_day_no = day_no[rental_end_day]
		days = [day_no_constant[x] for x in range(st_day_no,end_day_no+1)]
		app.logger.info('days=%s'% days) 
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		rental_days = len(list(set))
		total_expense += len(list(set))*float(rental_car_rate)
		
	if is_mileage =='true':
    		set = rruleset()
		st_day_no = day_no[commute_st_day]
		end_day_no = day_no[commute_end_day]
		days = [day_no_constant[x] for x in range(st_day_no,end_day_no+1)]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))	
		commute_days = len(list(set))
		total_expense += len(list(set))*float(daily_miles)*float(mileage_rate)

	if is_hotel =='true':
    		set = rruleset()
		st_day_no = day_no[hotel_st_day]
		end_day_no = day_no[hotel_end_day]
		days = [day_no_constant[x] for x in range(st_day_no,end_day_no+1)]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		hotel_days = len(list(set))
		total_expense += len(list(set))*float(hotel_rate) + len(list(set))*float(daily_expense)

	if is_flight =='true':
    		set = rruleset()
		#add flight depart and arrival day in the form and calc. for now calculating with rental st day and end day
		st_day_no = day_no[rental_st_day]
		days = day_no_constant[st_day_no]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		no_flights = len(list(set))
		total_expense += len(list(set))*float(flight_ticket)

	if is_airport_pickup =='true':
    		set = rruleset()
		#add flight depart and arrival day in the form and calc
		st_day_no = day_no[rental_st_day]
		days = day_no_constant[st_day_no]
		set.rrule(rrule(YEARLY, byweekday=days, dtstart=sd, until=ed))
		total_expense += len(list(set))*float(airport_pickup)


	app.logger.info(str('{"expense":%s,"rental_days":%s, "hotel_days": %s, "no_flights":%s, "commute_days": %s}' % ( total_expense,rental_days,hotel_days,no_flights,commute_days)))


	
        return str('{"expense":%s,"rental_days":%s, "hotel_days": %s, "no_flights":%s, "commute_days": %s}' % ( total_expense,rental_days,hotel_days,no_flights,commute_days))
        
def calculate_no_payments(start_date,end_date,freq):
    if freq=='W':
        #weekly freq
        no_payments = len(list(rrule(WEEKLY, dtstart=start_date, until = end_date)))
    elif freq == 'BW':
        #bi-weekly freq
        no_payments = len(list(rrule(WEEKLY, interval=2,dtstart=start_date, until = end_date)))
    elif freq == 'M':
        #monthly
        no_payments = len(list(rrule(MONTHLY, bymonthday=(MO, -1), bysetpos=1, dtstart=start_date, until = end_date))) 
    
    return no_payments
              

            
def calculate_total_other_deductions(start_date,   end_date,  hsa_contr,hsa_contr_freq,retirement_contr,retirement_contr_freq,health_ins_prem,health_ins_freq,vision_ins_prem,vision_ins_freq,dental_ins_prem, dental_ins_freq, shortterm_dis_prem,shortterm_dis_freq, longterm_dis_prem, longterm_dis_freq, life_ins_prem, life_ins_freq):

	sd = parse(start_date)
	ed = parse(end_date)

        no_hsa_contr = calculate_no_payments(sd,ed,hsa_contr_freq)
        hsa = no_hsa_contr*float(hsa_contr)
        no_retirement_contr=calculate_no_payments(sd,ed,retirement_contr_freq)
        retirement = no_retirement_contr*float(retirement_contr)
        no_health_ins=calculate_no_payments(sd,ed,health_ins_freq)
        health_ins = no_health_ins*float(health_ins_prem)
        no_vision_ins= calculate_no_payments(sd,ed,vision_ins_freq)
        vision_ins = no_vision_ins*float(vision_ins_prem)
        no_dental_ins=calculate_no_payments(sd,ed,dental_ins_freq)
        dental_ins = no_dental_ins*float(dental_ins_prem )
        no_shortterm_dis=calculate_no_payments(sd,ed,shortterm_dis_freq)
        shortterm_dis = no_shortterm_dis*float(shortterm_dis_prem)
        no_longterm_dis=calculate_no_payments(sd,ed,longterm_dis_freq)
        longterm_dis = no_longterm_dis*float(longterm_dis_prem)
        no_life_ins=calculate_no_payments(sd,ed,life_ins_freq)
        life_ins = no_life_ins*float(life_ins_prem)
        
        other_deductions = hsa + retirement + health_ins + vision_ins+ dental_ins + shortterm_dis + longterm_dis + life_ins        
        app.logger.info(str('{"other_deductions":%s,"no_hsa_contr":%s, "no_retirement_contr": %s, "no_health_ins":%s, "no_vision_ins": %s, "no_dental_ins": %s, "no_shortterm_dis":%s, "no_longterm_dis": %s,"no_life_ins": %s}' % (other_deductions, no_hsa_contr, no_retirement_contr,no_health_ins,no_vision_ins,no_dental_ins,no_shortterm_dis,no_longterm_dis,no_life_ins ))
)
        return str('{"other_deductions":%s,"no_hsa_contr":%s, "no_retirement_contr": %s, "no_health_ins":%s, "no_vision_ins": %s, "no_dental_ins": %s, "no_shortterm_dis":%s, "no_longterm_dis": %s,"no_life_ins": %s}' % (other_deductions, no_hsa_contr, no_retirement_contr,no_health_ins,no_vision_ins,no_dental_ins,no_shortterm_dis,no_longterm_dis,no_life_ins ))

                
def calculate_total_taxes(contract_id, start_date,   end_date, fed_tax_perc,state_tax_perc,ssn_tax_perc,self_emp_tax_perc,medicare_tax_perc ):

	sd = parse(start_date)
	ed = parse(end_date)

        contract = Contracts.query.filter_by(id = int(contract_id)).first()
        income = float(contract.income)
        expense = contract.expense #assuming all expenses are paid with taxablel income
        
        if contract.is_hsa_pre_tax:
                income -= calculate_no_payments(sd,ed,contract.hsa_contr_freq)*float(contract.hsa_contr)
        if contract.is_retirement_pre_tax:
                income -= calculate_no_payments(sd,ed,contract.retirement_contr_freq)*float(contract.retirement_contr)
        
        if contract.is_health_pre_tax:
                income -= calculate_no_payments(sd,ed,contract.health_ins_freq)*float(contract.health_ins_prem)
        if contract.is_vision_pre_tax:
                income -= calculate_no_payments(sd,ed,contract.vision_ins_freq)*float(contract.vision_ins_prem)
        if contract.is_dental_pre_tax:
        
                income -= calculate_no_payments(sd,ed,contract.dental_ins_freq)*float(contract.dental_ins_prem )
        if contract.is_shortterm_pre_tax:
                income -= calculate_no_payments(sd,ed,contract.shortterm_dis_freq)*float(contract.shortterm_dis_prem)
        if contract.is_longterm_pre_tax: 
                income -= calculate_no_payments(sd,ed,contract.longterm_dis_freq)*float(contract.longterm_dis_prem)
        if contract.is_life_pre_tax:
                income -= calculate_no_payments(sd,ed,contract.life_ins_freq)*float(contract.life_ins_prem)

        fed_tax = income*float(fed_tax_perc)/100
        state_tax = income*float(state_tax_perc)/100
        ssn_tax = income* float(ssn_tax_perc)/100
        self_emp_tax = income*float(self_emp_tax_perc)/100
        medicare_tax = income*float(medicare_tax_perc)/100
	app.logger.info('income:%s, Fed Tax:%s, State Tax:%s, SSN Tax:%s, Self Emp Tax: %s, Medicare Tax:%s, Total Taxes:%s' % ( income, fed_tax, state_tax, ssn_tax, self_emp_tax, medicare_tax, (fed_tax+state_tax+ssn_tax+self_emp_tax+medicare_tax) ))
	
        return str('{"FedTax":%s,"StateTax":%s, "SSNTax":%s, "SelfEmpTax": %s, "MedicareTax":%s , "TotalTaxes":%s}' % ( fed_tax,state_tax,ssn_tax,self_emp_tax,medicare_tax,(fed_tax+state_tax+ssn_tax+self_emp_tax+medicare_tax)))
        
        
         
                

