from flask import render_template, flash, redirect, session, url_for, request, g, jsonify,json
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.babel import gettext
from app import app, db, lm, oid, babel, gi,fujs

from forms import LoginForm, EditForm, PostForm, SearchForm, InputIncomeForm,ContractsListForm,InputExpenseForm, InputOtherDedForm, InputTaxForm
from models import User, ROLE_USER, ROLE_ADMIN, Post,Contracts
from datetime import datetime
from emails import follower_notification
from guess_language import guessLanguage
from translate import microsoft_translate
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES, DATABASE_QUERY_TIMEOUT, WHOOSH_ENABLED, OAUTH_ENABLED,ADMINS
from calculate_income import calculate_total_income,calculate_total_expense, calculate_total_other_deductions, calculate_total_taxes
import sys
from dateutil.parser import *
import inspect
import bust_a_bill_views
import pygeoip
import time


@app.context_processor
def inject_fujs():
    return dict(fujs=fujs)




@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())
    
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = get_locale()
    g.search_enabled = WHOOSH_ENABLED
    

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
   

    form = PostForm()
    if form.validate_on_submit():
        language = guessLanguage(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body = form.post.data,
            timestamp = datetime.utcnow(),
            author = g.user,
            language = language)
#	app.logger.info('inside post submit')        
#	flash(gettext('Your post is going to commit!'))

        try :
	        db.session.add(post)
		db.session.commit()
        	flash(gettext('Your post is now live!'))
	except :
		flash(gettext('Could not commit your post'))
	
        return redirect(url_for('index' ))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
        title = 'Home',
        form = form,
        posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():

    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit() and OAUTH_ENABLED:
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    elif not  OAUTH_ENABLED:
        user = User.query.filter_by(email = ADMINS[0]).first()	
	login_user(user, remember = False)
	
        return redirect(url_for('index'))


        
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp=""):
    if OAUTH_ENABLED and resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'))
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()	

    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash(gettext('User %(nickname)s not found.', nickname = nickname))
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
        user = user,
        posts = posts)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    geo_data = gi.record_by_addr(request.remote_addr)


    
#{'city': 'Mountain View', 'region_name': 'CA', 'area_code': 650, 'longitude': -122.0574, 'country_code3': 'USA', 'latitude': 37.419199999999989, 'postal_code': '94043', 'dma_code': 807, 'country_code': 'US', 'country_name': 'United States'}
    #form.geoip = str(request.remote_addr)    
    flash('You are logged in from ' + str(request.remote_addr))
    if geo_data :
	#form.geoip = jsonify(geo_data)
        flash('You are logged in from ' +  str(request.remote_addr) +":"+geo_data['city'] +","+geo_data['region_code']+","+geo_data['country_code'])

    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(gettext('Your changes have been saved.'))
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
	

    return render_template('edit.html',
        form = form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t follow yourself!'))
        return redirect(url_for('user', nickname = nickname))
    u = g.user.follow(user)
    if u is None:
        flash(gettext('Cannot follow %(nickname)s.', nickname = nickname))
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You are now following %(nickname)s!', nickname = nickname))
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t unfollow yourself!'))
        return redirect(url_for('user', nickname = nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('Cannot unfollow %(nickname)s.', nickname = nickname))
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You have stopped following %(nickname)s.', nickname = nickname))
    return redirect(url_for('user', nickname = nickname))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    try:
	    db.session.delete(post)
	    db.session.commit()
    	    flash('Your post has been deleted.')
    except:
	    flash('Could not delete the post.')

    return redirect(url_for('index'))
    
@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
        query = query,
        results = results)

@app.route('/translate', methods = ['POST'])
@login_required
def translate():
    return jsonify({
        'text': microsoft_translate(
            request.form['text'],
            request.form['sourceLang'],
            request.form['destLang']) })





@app.route('/contracts_list', methods = ['GET'])
@app.route('/contracts_list/<int:page>', methods = ['GET'])
@login_required
def contracts_list(page=1):
    #app.logger.info('inside contracts list view')        	
    contracts = Contracts.query.filter_by(user_id = g.user.id).order_by(Contracts.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    
    form = ContractsListForm()
        
    return render_template('contracts_list.html',
        title = 'List of Contracts',
        form = form,
        pagination = contracts)


@app.route('/input_income/<int:contract_id>', methods = ['GET', 'POST'])
@login_required
def input_income(contract_id):

    app.logger.info('inside input income')        	

    
    form = InputIncomeForm()
    contract = Contracts()	
    contract_copy = Contracts()	
    if request.method == "POST" and form.validate_on_submit():
	app.logger.info('id %s' % contract_id)        	
	
	
	if contract_id > 0 :
	    contract = Contracts.query.filter_by(id = contract_id).first()
	    
	InputIncomeForm(request.form).populate_obj(contract)
	
	if request.form['next_step']=='save_as':
		db.session.expunge(contract)
	        
	        for key in contract.__dict__:
	             if not (key == 'id' or key == '_sa_instance_state' ) :
	                #app.logger.info("%s:%s" %(key, contract_copy.__dict__[key]))
	                contract_copy.__dict__[key]=contract.__dict__[key]
	                
	             
	             
	        contract_copy.timestamp = datetime.utcnow()
	        contract_copy.user_id = g.user.id
                
                db.session.add(contract_copy)
	        db.session.flush()
	        contract_id = contract_copy.id
	        app.logger.info('Contract saved as  %s' % contract_id)        	

                db.session.commit()
                flash(gettext('Data saved successfully' ))

                form = InputIncomeForm(obj=contract_copy)
    
                return render_template('input_income.html',
                        form = form)
        else:	        
	        contract.timestamp = datetime.utcnow()
	        contract.user_id = g.user.id
                db.session.add(contract)
	        db.session.flush()
	        contract_id = contract.id
	        app.logger.info('newly inserted id after flush %s' % contract_id)        	
                db.session.commit()

                flash(gettext('Data saved successfully' ))
                
	        if request.form['next_step']=='input_expenses':
                        return redirect(url_for('input_expenses',contract_id = contract_id))
                else:

                    form = InputIncomeForm(obj=contract)
                    
                    return render_template('input_income.html',
                        form = form)

    if 	request.method == "GET" and contract_id > 0: 
    	contract = Contracts.query.filter_by(id = contract_id).first()	
    
    form = InputIncomeForm(obj=contract)
            
    return render_template('input_income.html',
                form = form)

@app.route('/calculate_income', methods = ['POST'])
@login_required
def calculate_income():
   
    #This server function is called when user clicks on the calculate link. Form data is send to calculate income function 
    #and the result of function is returned to the client.
    app.logger.info('calculate income ' )        	
    return jsonify({
        'income': calculate_total_income(
            request.form['start_date'],
            request.form['end_date'],
            request.form['no_vacations'],
            request.form['no_holidays'],
            request.form['no_sickdays'],
            request.form['hourly_rate'],
            request.form['work_hours'],
	    request.form['exclude_nth'],
	    request.form['exclude_day']
	) })



@app.route('/input_expenses/<contract_id>', methods = ['GET','POST'])
#@app.route('/input_expenses', methods = ['GET','POST'])
@login_required
def input_expenses(contract_id):

    
    app.logger.info('inside deduction save') 
    #if request.method == "POST"  and deduction_form.validate_on_submit():
    
    
    contract = Contracts()	
    if request.method == "POST" :
        app.logger.info('Inside POST') 
	contract = Contracts.query.filter_by(id = request.form['id']).first()
	try:
	    InputExpenseForm(request.form).populate_obj(contract)    	    
	    app.logger.info('form data populated')
        except AttributeError as err:
	    app.logger.info('ERROR:%s' % err)  
	contract.timestamp = datetime.utcnow()
	contract.user_id = g.user.id
	app.logger.info('Saving contract with deduction') 
	db.session.add(contract)
	db.session.flush()
	db.session.commit()
	app.logger.info('data saved with deduction') 
	if request.form['next_step']=='input_other_deductions':
	        return redirect(url_for('input_other_deductions', contract_id=request.form['id']))
    elif  request.method == "GET" :
        app.logger.info('retrieving contract deductions %s' % contract_id ) 
        contract = Contracts.query.filter_by(id = contract_id).first()	
        
    expense_form = InputExpenseForm(obj=contract)
    return render_template('input_expenses.html',
		        title = 'Input expense',
		        form = expense_form)


@app.route('/calculate_expenses', methods = ['POST'])
@login_required
def calculate_expenses():
   
    #This server function is called when user clicks on the calculate link in the deductions page. Form data is send to calculate expense function 
    #and the result of function is returned to the client.
    app.logger.info('inside calculate expense view')        	
    return jsonify({
        'expense': calculate_total_expense(
            request.form['start_date'],
            request.form['end_date'],
	    request.form['is_rent_acar'],
	    request.form['rental_st_day'],
	    request.form['rental_end_day'],
	    request.form['rental_car_rate'],
	    request.form['is_mileage'],
	    request.form['commute_st_day'],
	    request.form['commute_end_day'],
	    request.form['daily_miles'],
	    request.form['mileage_rate'],
	    request.form['is_hotel'],
	    request.form['hotel_st_day'],
	    request.form['hotel_end_day'],
	    request.form['hotel_rate'],
	    request.form['daily_expense'],
	    request.form['is_flight'],
	    request.form['flight_ticket'],
	    request.form['is_airport_pickup'],
	    request.form['airport_pickup']		    
	) })



@app.route('/input_other_deductions/<contract_id>', methods = ['GET','POST'])
@login_required
def input_other_deductions(contract_id):

    app.logger.info('inside other deductions save') 
    contract = Contracts()	
    if request.method == "POST" :
        app.logger.info('Inside POST') 
	contract = Contracts.query.filter_by(id = request.form['id']).first()				
	try:
	    InputOtherDedForm(request.form).populate_obj(contract)    	    
	    app.logger.info('form data populated')
        except AttributeError as err:
	    app.logger.info('ERROR:%s' % err)  
	contract.timestamp = datetime.utcnow()
	contract.user_id = g.user.id
	app.logger.info('Saving contract with deduction') 
	db.session.add(contract)
	db.session.flush()
	db.session.commit()
	app.logger.info('data saved with deduction') 
	if request.form['next_step']=='input_tax':
	        return redirect(url_for('input_taxes',contract_id=request.form['id']))
	
    elif  request.method == "GET" :
    #app.logger.info('inside GET %s' % contract_id) 
        contract = Contracts.query.filter_by(id = contract_id).first()	
    
    other_ded_form = InputOtherDedForm(obj=contract)
    return render_template('input_other_deductions.html',
			title = 'Input Other Deductions',
			form = other_ded_form)



@app.route('/calculate_other_deductions', methods = ['POST'])
@login_required
def calculate_other_deductions():
   
    #This server function is called when user clicks on the calculate link in the deductions page. Form data is send to calculate expense function 
    #and the result of function is returned to the client.
    app.logger.info('inside calculate other deductions view')        	
    return jsonify({
        'other_deductions': calculate_total_other_deductions(
            request.form['start_date'],
            request.form['end_date'],
	    request.form['hsa_contr'],
	    request.form['hsa_contr_freq'],
	    request.form['retirement_contr'],
	    request.form['retirement_contr_freq'],
	    request.form['health_ins_prem'],
	    request.form['health_ins_freq'],
	    request.form['vision_ins_prem'],
	    request.form['vision_ins_freq'],
	    request.form['dental_ins_prem'],
	    request.form['dental_ins_freq'],
	    request.form['shortterm_dis_prem'],
	    request.form['shortterm_dis_freq'],
	    request.form['longterm_dis_prem'],
	    request.form['longterm_dis_freq'],
            request.form['life_ins_prem'],
	    request.form['life_ins_freq']
	    
	) })

		    
@app.route('/input_taxes/<contract_id>', methods = ['GET','POST'])
@login_required
def input_taxes(contract_id):

    app.logger.info('inside taxes save') 
    contract = Contracts()	
    if request.method == "POST" :
        app.logger.info('Inside POST') 
	contract = Contracts.query.filter_by(id = request.form['id']).first()				
	try:
	    InputTaxForm(request.form).populate_obj(contract)    	    
	    app.logger.info('tax rates %s, %s'%(contract.fed_tax_perc,contract.state_tax_perc))
        except AttributeError as err:
	    app.logger.info('ERROR:%s' % err)  
	contract.timestamp = datetime.utcnow()
	contract.user_id = g.user.id
	app.logger.info('Saving contract with deduction') 
	db.session.add(contract)
	db.session.flush()
	db.session.commit()
	app.logger.info('data saved with deduction') 
	
    elif  request.method == "GET" :
        contract = Contracts.query.filter_by(id = contract_id).first()	
    
    taxes_form = InputTaxForm(obj=contract)
    return render_template('input_taxes.html',
			title = 'Input Taxes',
			form = taxes_form)




@app.route('/calculate_taxes', methods = ['POST'])
@login_required
def calculate_taxes():
   
    #This server function is called when user clicks on the calculate link in the deductions page. Form data is send to calculate expense function 
    #and the result of function is returned to the client.
    app.logger.info('inside calculate taxes view')        	
    return jsonify({
         'taxes':calculate_total_taxes(
            request.form['contract_id'],    
            request.form['start_date'],
            request.form['end_date'],
	    request.form['fed_tax_perc'],
	    request.form['state_tax_perc'],
	    request.form['ssn_tax_perc'],
	    request.form['self_emp_tax_perc'],
	    request.form['medicare_tax_perc']) })



@app.route('/compare_contracts/<contract_ids>', methods = ['GET','POST'])
@login_required
def compare_contracts(contract_ids):
    contract1 = Contracts()
    contract2 = Contracts()
    contract3 = Contracts()
    app.logger.info('contract_ids %s'% contract_ids)        	
    ids = [int(i) for i in contract_ids.split(',')][::-1] #take the last 3 incase the array has more than 3
    
    if len(ids) > 0:
            contract1 = Contracts.query.filter_by(id = ids[0]).first()	
    if len(ids) > 1:        
            contract2 = Contracts.query.filter_by(id = ids[1]).first()	
    if len(ids) > 2 :        
            contract3 = Contracts.query.filter_by(id = ids[2]).first()	
    
    return render_template('compare_contracts.html',
			title = 'Compare Contracts', contract1=contract1, contract2=contract2, contract3=contract3)

@app.route('/delete_contract/<contract_ids>', methods = ['GET','POST'])
@login_required
def delete_contract(contract_ids):

    app.logger.info('inside delete contract') 
    contract_ids = [int(i) for i in contract_ids.split(',')]
    for contract_id in contract_ids:
        contract = Contracts.query.filter_by(id = contract_id).first()				
	db.session.delete(contract)
	db.session.flush()
	db.session.commit()
	app.logger.info('Contract record deleted')

    return redirect(url_for('contracts_list'))    
        

