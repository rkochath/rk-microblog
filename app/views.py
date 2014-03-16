from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.babel import gettext
from app import app, db, lm, oid, babel, gi
from forms import LoginForm, EditForm, PostForm, SearchForm, RateCalcForm,ContractsListForm
from models import User, ROLE_USER, ROLE_ADMIN, Post,Contracts
from datetime import datetime
from emails import follower_notification
from guess_language import guessLanguage
from translate import microsoft_translate
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES, DATABASE_QUERY_TIMEOUT, WHOOSH_ENABLED, OAUTH_ENABLED,ADMINS
from calculate_income import calculate_income
import sys
from dateutil.parser import *
import inspect
import bust_a_bill_views
import pygeoip





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
	
        return redirect(url_for('index'))
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
        
    if geo_data :
	#form.geoip = jsonify(geo_data)
        form.geoip = geo_data.city +","+geo_data.region_name+","+geo_data.country_code

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
	

    if request.method == "POST" and form.validate_on_submit():
	app.logger.info('id %s' % form.id)        	
	

	if contract_id > 0 :
	    contract = Contracts.query.filter_by(id = contract_id).first()	

	else:
	    contract = Contracts()
	"""
	    contract = Contracts(  id = form.id,
				description = form.description.data,
				start_date = form.start_date.data ,
				end_date = form.end_date.data, 
				no_vacations = form.no_vacations.data , 
				no_holidays = form.no_holidays.data ,
			    	no_sickdays = form.no_sickdays.data ,
				hourly_rate = form.hourly_rate.data  ,
				work_hours = form.work_hours.data  ,
				income = float(form.income.data)  ,
				timestamp = datetime.utcnow(),
			        user_id = g.user.id)
	
	"""
	form.populate_obj(contract)

	contract.timestamp = datetime.utcnow()
	contract.user_id = g.user.id

        db.session.add(contract)
	db.session.flush()

        db.session.commit()
        flash(gettext('Data saved successfully' ))
        
	#return redirect(url_for('rateinput',contract_id = contract.id.data))
	#return redirect(url_for('rateinput',contract_id = contract.id))
	
        return redirect(url_for('contracts_list'))

    contract = Contracts.query.filter_by(id = contract_id).first()	
    form = RateCalcForm(obj=contract)
	
    return render_template('rate_input.html',
        form = form)

@app.route('/calculate', methods = ['POST'])
@login_required
def calculate():
   

    return jsonify({
        'income': calculate_income(
            request.form['start_date'],
            request.form['end_date'],
            request.form['no_vacations'],
            request.form['no_holidays'],
            request.form['no_sickdays'],
            request.form['hourly_rate'],
            request.form['work_hours']
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




@app.route('/save_contract', methods = ['POST'])
@login_required
def save_contract():
	app.logger.info('inside server going to save contract for id %s' % request.form['id'])
	if request.form['id'] == '':	
		contract_id = 0	
	else:
		contract_id = request.form['id']	
	if contract_id > 0  :
	    	contract = Contracts.query.filter_by(id = contract_id).first()	

		#(  #id = int(request.form['id']),
		contract.description = request.form['description']
		app.logger.info('updated description')
		contract.start_date = 	parse(request.form['start_date']) 
		app.logger.info('start date')
		ontract.end_date = parse(request.form['end_date']) 
		app.logger.info('end date')
		contract.no_vacations = int(request.form['no_vacations'] )
		app.logger.info('no vacations')
		contract.no_holidays = int(request.form['no_holidays']) 
		app.logger.info('holidays')
	    	contract.no_sickdays = int(request.form['no_sickdays']) 
		app.logger.info('sickdays')
		contract.hourly_rate = float(request.form['hourly_rate'])  
		app.logger.info('hourly rate')
		contract.work_hours = float(request.form['work_hours'])  
		app.logger.info('work hours')
		app.logger.info('income %s' % request.form['income'] )
		contract.income = float(request.form['income'])  
		app.logger.info('income')
	
		contract.timestamp = datetime.utcnow()
		app.logger.info('timestamp')
		contract.user_id = g.user.id
		app.logger.info('user id')
		app.logger.info('contract obj created')
		db.session.add(contract)
		app.logger.info('add contract')
		db.session.flush()
		db.session.commit()
		app.logger.info('contract updated')


	else:
		try:
		    	contract = Contracts(id= None,
			        description = request.form['description'],
				start_date = 	parse(request.form['start_date']) ,
				end_date = parse(request.form['end_date']) ,
				no_vacations = int(request.form['no_vacations'] ),
				no_holidays = int(request.form['no_holidays']) ,
			    	no_sickdays = int(request.form['no_sickdays']) ,
				hourly_rate = float(request.form['hourly_rate'])  ,
				work_hours = float(request.form['work_hours'])  ,
				income = float(request.form['income']),
				timestamp = datetime.utcnow(),
				user_id = g.user.id
				)
			app.logger.info('contract obj created')
			db.session.add(contract)
			app.logger.info('add contract')
			db.session.flush()
			db.session.commit()
			app.logger.info('new contract created')

			#flash(gettext('Data saved successfully' ))

		except:
			e = sys.exc_info()[0]
			app.logger.info('creation of contract object failed %s' % e)
			return jsonify({
					'message': '500' })
	
	return jsonify({
	'message': 'Data Saved Successfully' })




