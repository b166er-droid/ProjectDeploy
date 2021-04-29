import json
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from models import db, User, Movie, Watchlist, Comment, Cast, Crew, SignUp, LogIn

''' Begin boilerplate code '''

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  

''' End Flask Login Functions '''

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigData.db'
  app.config['SECRET_KEY'] = "MYSECRET"
  login_manager.init_app(app)
  db.init_app(app)
  return app

app = create_app()

app.app_context().push()
db.create_all(app=app)


#========================
# Pages
#=========================

# Home Page
@app.route('/')
def index():
  numOfMovies1 = 15 #For slider
  numOfMovies2 = 32 #For List below
  movieSlider = Movie.query.limit(numOfMovies1)
  movieList = Movie.query.offset(numOfMovies1).limit(numOfMovies2)
  return render_template('index.html', movieSlider=movieSlider, movieList=movieList)


# Movies Page
@app.route('/movies', methods=['GET'])
def movies():
  movieList = Movie.query.limit(32)
  return render_template('movies.html', movieList=movieList, i=1)

# Movies Page
@app.route('/movies/page/<i>', methods=['GET'])
def movieList(i):
    if i == 0:
        i = 1
    numOfMovies = 32
    movieList = Movie.query.offset(i*32).limit(32)
    return render_template('movies.html', movieList=movieList, i=i)  

# Movie Info Page
@app.route('/movies/<id>', methods=['GET'])
def movie(id):
  isSavedMovie = False
  movie = Movie.query.get(id)
  test = None
  if(current_user.is_authenticated):
    test = Watchlist.query.filter(Watchlist.user.like(current_user.id)).filter(Watchlist.movie.like(id)).first()
  if test != None:
    isSavedMovie = True
  return render_template('movie.html', movie=movie, isSavedMovie=isSavedMovie) 

#Comment on Movie
@app.route('/movies/<id>/comments', methods=['POST'])
#@login_required #If only users can comment
def create_comment_action(id):

  username = request.form["username"]
  text = request.form["text"]
  movie_id = request.form["movie_id"]
  newComment = Comment(username=username, text=text, movie_id=movie_id)

  db.session.add(newComment)
  db.session.commit()
  return redirect(request.referrer) # redirect to previous page

#Add to user watchlist
@app.route('/movies/addToWatchList/<id>', methods=['GET', 'POST'])
@login_required
def addToWatchList(id):
  test = Watchlist.query.filter(Watchlist.user.like(current_user.id)).filter(Watchlist.movie.like(id)).first()
  if test != None:
    return redirect(request.referrer)
  newSavedMovie = Watchlist(user=current_user.id, movie=id)

  db.session.add(newSavedMovie)
  db.session.commit()

  return redirect(request.referrer)


# Movies Page
@app.route('/about', methods=['GET'])
def about():
  return render_template('about.html')

# Profile Page
@app.route('/profile', methods=['GET'])
@login_required
def profile():
  userList = Watchlist.query.filter_by(user=current_user.id)
  movieList = []
  for l in userList:
    movieList.append(Movie.query.get(l.movie))
  
  return render_template('profile.html', movieList=movieList)

#========================
# Auth Pages
#=========================

@app.route('/signup', methods=['GET'])
def signup():
  form = SignUp() # create form object
  return render_template('signup.html', form=form, invalid = False, same = False) # pass form object to template

@app.route('/signup', methods=['POST'])
def signupAction():
  signupPage = url_for('signup')
  form = SignUp() # create form object
  if form.validate_on_submit():
    data = request.form # get data from form submission
    user = User.query.filter_by(username = data['username']).first()
    if( user != None):
      return render_template('signup.html', form=form, invalid = False, same = True) 
    loginPage = url_for('login')    
    newuser = User(username=data['username']) # create user object
    newuser.set_password(data['password']) # set password
    db.session.add(newuser) # save new user
    db.session.commit()
    return redirect(url_for('index'));
  return render_template('signup.html', form=form, invalid = True, same = False)

@app.route('/login', methods = ['GET'])
def login():
    form = LogIn()
    return render_template('login.html', form = form, invalid = False)

@app.route('/login', methods = ['POST'])
def loginAction():
    form = LogIn()
    loginPage = url_for('login')
    if form.validate_on_submit(): # respond to form submission
        data = request.form
        user = User.query.filter_by(username = data['username']).first()
        if user and user.check_password(data['password']): # check credentials
            login_user(user) # login the user
            return redirect(url_for('index'));
    return render_template('login.html', form = form, invalid = True)


@app.route('/logout')
@login_required
def logOut():
  logout_user()
  flash('Logged Out!', 'info')
  return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)