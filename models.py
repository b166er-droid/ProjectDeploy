from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class SignUp(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField('Sign Up', render_kw={'class': 'btn waves-effect waves-light white-text'})

class LogIn(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login', render_kw={'class': 'btn waves-effect waves-light white-text'})

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    watchlist = db.relationship('Watchlist', backref='user_watchlist')

    def toDict(self):
      return {
        "id": self.id,
        "username": self.username,
        "password": self.password
      }
    
    #hashes the password parameter and stores it in the object
    def set_password(self, password):
        """Create hashed password."""
        hashP = hashlib.md5(bytes(password,'utf-8'))
        self.password = hashP.digest()
    
    #Returns true if the parameter is equal to the object's password property
    def check_password(self, password):
        """Check hashed password."""
        hashP = hashlib.md5(bytes(password,'utf-8'))
        hashP = hashP.digest()
        if(self.password == hashP):
            return True
        return False
    
    #To String method
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    movie_id = db.Column(db.Integer) #For getting casts

    title = db.Column(db.String(120))
    homepage = db.Column(db.String(120))
    lang = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    poster = db.Column(db.String(120))
    overview = db.Column(db.String(180))
    release_date = db.Column(db.String(120))
    release_day = db.Column(db.Integer)
    release_month = db.Column(db.Integer)
    release_year = db.Column(db.Integer)
    average_rating = db.Column(db.Float)
    watchlist = db.relationship('Watchlist', backref='movie_watchlist')

    cast = db.relationship('Cast', backref='movie')
    crew = db.relationship('Crew', backref='movie')
    comments = db.relationship('Comment', backref='movie')

    imdb_id = db.Column(db.String(120))

    def toDict(self):
        return {
            "id":self.id,
            "title":self.title,
            "homepage":self.homepage,
            "lang":self.lang,
            "genres":self.genres,
            "poster":self.poster,
            "overview":self.overview,
            "release_date":self.release_date,
            "average_rating":self.average_rating
        }

class Cast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120)) #Cast member Real Name
    character = db.Column(db.String(120))
    cast_id = db.Column(db.Integer)
    credit_id = db.Column(db.String(120))

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def toDict(self):
        return {
            "id":self.id,
            "name":self.name,
            "cast_id":self.cast_id,
            "credit_id":self.credit_id,
            "character":self.character
        }

class Crew(db.Model):
    id  = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    job = db.Column(db.String(120))
    department = db.Column(db.String(120))
    credit_id = db.Column(db.String(120))

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def toDict(self):
        return {
            "id":self.id,
            "name":self.name,
            "credit_id":self.credit_id,
            "job":self.job,
            "department":self.department
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(360))
    username = db.Column(db.String(50))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def toDict(self):
        return {
            'id':self.id,
            'text':self.text,
            'username':self.username,
            'movie_id':self.movie_id
        }
