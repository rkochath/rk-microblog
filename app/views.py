from flask import render_template, flash, redirect, session, url_for, request, g, jsonify,json
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.babel import gettext
from app import app, db, lm, oid, babel, gi,fujs

from forms import LoginForm, EditForm, PostForm, SearchForm, RateCalcForm,ContractsListForm,InputDeductionsForm
from models import User, ROLE_USER, ROLE_ADMIN, Post,Contracts
from datetime import datetime
from emails import follower_notification
from guess_language import guessLanguage
from translate import microsoft_translate
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES, DATABASE_QUERY_TIMEOUT, WHOOSH_ENABLED, OAUTH_ENABLED,ADMINS
from calculate_income import calculate_income,calculate_total_expense
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







@app.route('/rateinput/<int:contract_id>', methods = ['GET', 'POST'])
@login_required
def rateinput(contract_id):

    app.logger.info('inside rateinput')        	

    form = RateCalcForm()
	
    contract = Contracts()	
    if request.method == "POST" and form.validate_on_submit():
	app.logger.info('id %s' % contract_id)        	
	
	
	if contract_id > 0 :
	    contract = Contracts.query.filter_by(id = contract_id).first()

	#else:
	#    contract = Contracts()
	form.populate_obj(contract)


	contract.timestamp = datetime.utcnow()
	contract.user_id = g.user.id

        db.session.add(contract)
	db.session.flush()
	#db.session.refresh(contract,['id'])
        #if contract_id == 0 :
		#db.session.refresh(contract)
	contract_id = contract.id
	app.logger.info('newly inserted id after flush %s' % contract_id)        	

        db.session.commit()

        flash(gettext('Data saved successfully' ))
        
	
        #return redirect(url_for('rate_input_deductions',contract_id = contract_id))
	#return
    if 	request.method == "GET" : 
    	contract = Contracts.query.filter_by(id = contract_id).first()	
    form = RateCalcForm(obj=contract)
    
    return render_template('rate_input.html',
        form = form)

@app.route('/calculate', methods = ['POST'])
@login_required
def calculate():
   
    #This server function is called when user clicks on the calculate link. Form data is send to calculate income function 
    #and the result of function is returned to the client.
    return jsonify({
        'income': calculate_income(
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

@app.route('/calculate_expense', methods = ['POST'])
@login_required
def calculate_expense():
   
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




@app.route('/save_contract/<contract_str>', methods = ['GET','POST'])
@login_required
def save_contract(contract_str):

        contract_str = contract_str.replace('=',':')
        contract_dict = dict([i.split(':') for i in contract_str.split('&')])
	for key in contract_dict:
		app.logger.info("%s:%s" %(key, contract_dict[key]))
	contract_dict['start_date'] = '-'.join(contract_dict['start_date'].split('%2F'))
	contract_dict['end_date'] = '-'.join(contract_dict['end_date'].split('%2F'))
        contract_id = None if contract_dict['id'] == '' else int(contract_dict['id'])
	contract = Contracts( id=contract_id,
				description = contract_dict['description'],
				start_date = parse(contract_dict['start_date'],fuzzy=True),
				end_date = parse(contract_dict['end_date'],fuzzy=True),
				no_sickdays= int(contract_dict['no_sickdays']),
				no_vacations = int(contract_dict['no_vacations']),
				work_hours = float(contract_dict['work_hours']),
				exclude_day = contract_dict['exclude_day'],
				exclude_nth = int(contract_dict['exclude_nth']),
				income = float(contract_dict['income']),
				no_holidays = int(contract_dict['no_holidays']),
				hourly_rate = float(contract_dict['hourly_rate']))
        
        rateform = RateCalcForm(obj=contract)
	
	if contract_id > 0  :
		
		app.logger.info('Retrieving contract for update %s' % contract_id)
	    	contract = Contracts.query.filter_by(id = contract_id).first()	
		rateform.populate_obj(contract)
		contract.timestamp = datetime.utcnow()
		contract.user_id = g.user.id

		db.session.add(contract)
		db.session.flush()
		contract_id = contract.id
		app.logger.info('Contract created/updated %s' % contract_id)        	
		db.session.commit()
		
	else:

		contract.timestamp = datetime.utcnow()
		contract.user_id = g.user.id

		db.session.add(contract)
		db.session.flush()
		contract_id = contract.id
		app.logger.info('Contract created/updated %s' % contract_id)        	
		db.session.commit()

	return redirect(url_for('rate_input_deductions', contract_id=contract_id))


@app.route('/update_deductions', methods = ['POST'])
@login_required
def update_deductions():
	app.logger.info('Udate contract expenses %s' % request.form['id'])

        contract_id = int(request.form['id'])




	if contract_id > 0  :
	    	contract = Contracts.query.filter_by(id = contract_id).first()	

		    
	        contract.is_rent_acar =(True) if request.form['is_rent_acar'] =='true' else False
	        contract.rental_st_day =request.form['rental_st_day'] 

	        contract.rental_end_day=request.form['rental_end_day'] 
	        contract.is_hotel=(True) if request.form['is_hotel'] =='true' else False 
	        contract.hotel_st_day=request.form['hotel_st_day'] 

	        contract.hotel_end_day=request.form['hotel_end_day'] 

	        contract.is_flight=(True) if request.form['is_flight'] =='true' else False 
	        contract.is_airport_pickup=(True) if request.form['is_airport_pickup'] =='true' else False 
	        contract.is_mileage=(True) if request.form['is_mileage'] =='true' else False 
	        contract.commute_st_day=request.form['commute_st_day'] 
	        contract.commute_end_day=request.form['commute_end_day'] 
	        contract.rental_car_rate=float(request.form['rental_car_rate'] )
	        contract.hotel_rate=float(request.form['hotel_rate'] )
	        contract.flight_ticket=float(request.form['flight_ticket'] )
	        contract.airport_pickup=float(request.form['airport_pickup'] )
	        contract.daily_expense=float(request.form['daily_expense'] )
	        contract.daily_miles=float(request.form['daily_miles'] )
	        contract.mileage_rate=float(request.form['mileage_rate'] )
	        contract.expense=float(request.form['expense'] )
	
		contract.timestamp = datetime.utcnow()
		contract.user_id = g.user.id
		db.session.add(contract)
		app.logger.info('contract added to db session')	
		db.session.flush()
		app.logger.info('after flush')
		db.session.commit()
		app.logger.info('after commit')
		return jsonify({
	'result':str(contract_id) })
	
	app.logger.info('some thing went wrong.... ')
	return jsonify({
	'message':'-1' })




@app.route('/rate_input_deductions/<contract_id>', methods = ['GET','POST'])
#@app.route('/rate_input_deductions', methods = ['GET','POST'])
@login_required
def rate_input_deductions(contract_id):

    deduction_form = InputDeductionsForm()
    app.logger.info('inside deduction save') 
    #if request.method == "POST"  and deduction_form.validate_on_submit():
    if request.method == "POST" :
        app.logger.info('Inside POST') 
	#contract = Contracts.query.filter_by(id = deduction_form['id']).first()
	contract = Contracts.query.filter_by(id = request.form['id']).first()				
	try:
	    InputDeductionsForm(request.form).populate_obj(contract)    	    
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
	return redirect(url_for('contracts_list'))
    elif  request.method == "GET" :
        app.logger.info('inside GET %s' % contract_id) 
        #contract_str = contract_str.replace('=',':')
        #contract_dict = dict([i.split(':') for i in contract_str.split('&')])
	#contract_dict = dict(contract_str)
	#contract_id = int(request.form[id]) if contract_str == -1 else int(contract_str)

	#contract_id = int(contract_str)
	app.logger.info('retrieving contract deductions %s' % contract_id ) 
    	contract = Contracts.query.filter_by(id = contract_id).first()	
        deduction_form = InputDeductionsForm(obj=contract)
        return render_template('rate_input_deductions.html',
			title = 'Input Deductions',
			form = deduction_form)

