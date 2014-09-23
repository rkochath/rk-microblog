from hashlib import md5
from app import db
from app import app
from config import WHOOSH_ENABLED
import re

ROLE_USER = 0
ROLE_ADMIN = 1

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname
        
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
        
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self
            
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self
            
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self): # pragma: no cover
        return '<User %r>' % (self.nickname)    
        
class Post(db.Model):
    __searchable__ = ['body']
    
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))
    
    def __repr__(self): # pragma: no cover
        return '<Post %r>' % (self.body)

class Contracts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(140))
    
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    no_vacations = db.Column(db.Integer)
    no_holidays = db.Column(db.Integer)
    no_sickdays = db.Column(db.Integer)
    hourly_rate = db.Column(db.Numeric(6,2))

    work_hours = db.Column(db.Numeric(6,2))

    exclude_nth = db.Column(db.Integer)
    exclude_day = db.Column(db.String(2))

    income = db.Column(db.Numeric(12,2))
    expense = db.Column(db.Numeric(12,2))   


    is_rent_acar=db.Column(db.Boolean)
    rental_st_day=db.Column(db.String(2))
    rental_end_day=db.Column(db.String(2))

    rental_car_rate = db.Column(db.Numeric(6,2))

    is_hotel = db.Column(db.Boolean)
    hotel_st_day = db.Column(db.String(2))
    hotel_end_day = db.Column(db.String(2))
    hotel_rate = db.Column(db.Numeric(6,2))
    daily_expense = db.Column(db.Numeric(6,2))
    
    is_flight = db.Column(db.Boolean)
    flight_ticket = db.Column(db.Numeric(6,2))

    is_airport_pickup = db.Column(db.Boolean)
    airport_pickup = db.Column(db.Numeric(6,2))

    is_mileage = db.Column(db.Boolean)
    commute_st_day = db.Column(db.String(2))
    commute_end_day = db.Column(db.String(2))
    daily_miles = db.Column(db.Numeric(6,2))
    mileage_rate = db.Column(db.Numeric(6,2))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        
    def __repr__(self): # pragma: no cover
        return '<Contract %r>' % (self.description)

class Envelope(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(140))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(12,2))
    currency = db.Column(db.String(3))
    status = db.Column(db.String(1))
    holders = db.relationship('Holders', backref = 'envelope', lazy = 'dynamic')

    

    def __repr__(self): # pragma: no cover
        return '<Envelope %r>' % (self.description)

class Holders(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    envelope_id = db.Column(db.Integer, db.ForeignKey('envelope.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    members_in_group = db.Column(db.Integer)


class Event(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(140))

    envelope_id = db.Column(db.Integer, db.ForeignKey('envelope.id'))
    event_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(12,2)) # bill amount excluding taxes and gratuity
    currency = db.Column(db.String(3))
    bust_by = db.Column(db.String(1)) #M - by members in holder's group E -  equally for each holder

class Event_mates(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)

    envelope_id = db.Column(db.Integer, db.ForeignKey('envelope.id'))
    mate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mates_share = db.Column(db.Numeric(12,2)) #default:Equally divided among all participants. Override as needed
    mates_contribution = db.Column(db.Numeric(12,2)) 
    currency = db.Column(db.String(3))

class Bust(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    envelope_id = db.Column(db.Integer, db.ForeignKey('envelope.id'))
    mate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mates_share = db.Column(db.Numeric(12,2)) #for each user, from all events sum of user share
    mates_contribution = db.Column(db.Numeric(12,2)) #for each user, sum of amount contributed for events
    currency = db.Column(db.String(3))
    to_recieve = db.Column(db.Numeric(12,2)) # share - contributioon , is share is less than contributed amount
    to_pay = db.Column(db.Numeric(12,2)) #contribution  - share , if share was more than contributed amount
    settled_amount = db.Column(db.Numeric(12,2)) #the payments received or payed
    currency = db.Column(db.String(3))

class pop_money(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    envelope_id = db.Column(db.Integer, db.ForeignKey('envelope.id'))
    paid_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    paid_to = db.Column(db.Integer, db.ForeignKey('user.id'))

    amount = db.Column(db.Numeric(12,2))
    currency = db.Column(db.String(3))
    is_seettled	= db.Column(db.Numeric(1))
    settled_on = db.Column(db.Date)






if WHOOSH_ENABLED:
    import flask.ext.whooshalchemy as whooshalchemy
    whooshalchemy.whoosh_index(app, Post)
