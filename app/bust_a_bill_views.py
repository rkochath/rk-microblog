from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.babel import gettext
from app import app, db, lm, oid, babel
from bust_a_bill_forms import EnvelopeListForm, EnvelopeForm,EnvelopeHoldersForm
from models import User, ROLE_USER, ROLE_ADMIN, Post,Contracts, Holders, Envelope
from datetime import datetime
from emails import follower_notification
from guess_language import guessLanguage
from translate import microsoft_translate
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES, DATABASE_QUERY_TIMEOUT, WHOOSH_ENABLED
import sys
from dateutil.parser import *
import inspect



@app.route('/envelope_list', methods = ['GET'])
@app.route('/envelope_list/<int:page>', methods = ['GET'])
@login_required
def envelope_list(page=1):

    holders = Holders.query.filter_by(user_id = g.user.id).paginate(page, POSTS_PER_PAGE, False)
    
    form = EnvelopeListForm()
        
    return render_template('envelope_list.html',
        title = 'List of Envelopes',
        form = form,
        pagination = holders)

@app.route('/envelope_entry/<int:envelope_id>', methods = ['GET', 'POST'])
@login_required
def envelope_entry(envelope_id):

    app.logger.info('inside envelope entry')        	

    form = EnvelopeForm()


    #user = g.user
    holder_form = EnvelopeHoldersForm()
    #holder_form.populate_obj(user)
    #holder_form.holders.choices = [(g.id, g.nickname) for g in User.query.order_by('nickname')]


    if request.method == "POST" and form.validate_on_submit():
	app.logger.info('id %s' % form.id)        	
	

	if envelope_id > 0 :
	    envelope = Envelope.query.filter_by(id = envelope_id).first()	
	else:
	    envelope = Envelope()
	form.populate_obj(envelope)

	envelope.timestamp = datetime.utcnow()
	#envelope.user_id = g.user.id

        db.session.add(envelope)
	db.session.flush()

        db.session.commit()
        flash(gettext('Data saved successfully' ))
        return redirect(url_for('envelope_list'))


    envelope = Envelope.query.filter_by(id = envelope_id).first()
    form = EnvelopeForm(obj=envelope)






    holders = User.query.join(Holders).filter_by(envelope_id = envelope_id).paginate(1, POSTS_PER_PAGE, False)
    #holders = db.session.query(User,Holders).join(Holders).filter_by(envelope_id = envelope_id).all()


    
    
        
    return render_template('envelope_entry.html',
        title = 'List of Envelopes',
        form = form,
        holder_form = holder_form,
        envelope = envelope, 
        pagination = holders)



