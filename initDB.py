from main import db, app, Movie, Cast, Crew
from datetime import datetime
import csv, ast
import requests

db.drop_all()
db.create_all(app=app)

# replace any null values with None to avoid db errors
def noNull(val):
    if str(val) == "":
        return None
    return val

#'''
#Movies
movieList = []
crewList = []
castList = []
i = 0
stop = 500

with open('./Application/API/movies_metadata.csv', 'r', encoding="utf8") as movie:
    reader = csv.DictReader(movie)

    for line in reader:
        homepage = ""
        if line['homepage'] != None:
            homepage = line['homepage']
        movieList.append(
            {
                'id':i,
                'title':line['title'],
                "homepage":homepage,
                'lang':line['original_language'],
                'genres':"",
                'poster':"",
                'overview':line['overview'],
                'release_date':line['release_date'],
                'average_rating':line['vote_average'],

                'imdb_id':line['imdb_id'],
                'movie_id':line['id']
            }
        )
        i = i+1
        if i == stop:
            break

i = 0
with open('./Application/API/MovieGenre.csv', 'r') as movieStuff:
    reader = csv.DictReader(movieStuff)

    for line in reader:
        for movie in movieList:
            if int(line['imdbId']) == int(movie['imdb_id']):
                movie['poster'] = line['Poster']
                movie['genres'] = line['Genre']
    
        i = i+1
        if i == stop:
            break


i=0

#Cast & Crew
with open('./Application/API/credits.csv', 'r', encoding="utf8") as credits:
    reader = csv.DictReader(credits)

    for line in reader:
        cast = ast.literal_eval(line['cast'])
        crew = ast.literal_eval(line['crew'])
        check = True
        movieID = -1

        for member in cast: #Cast
            
            if check:
                for movie in movieList:
                    if line['id'] == movie['movie_id']:
                        movieID = movie['id']
                        check = False
                        break

            castList.append(
                {
                    'name':member['name'],
                    'character':member['character'],
                    'credit_id':member['credit_id'],
                    'cast_id':member['cast_id'],
                    'movie_id':movieID #Intiailze it to this before compare
                }
            )

        check = True
        movieID = -1

        for member in crew: #Crew

            if check:
                for movie in movieList:
                    if line['id'] == movie['movie_id']:
                        movieID = movie['id']
                        check = False
                        break

            crewList.append(
                {
                    'name':member['name'],
                    'job':member['job'],
                    'department':member['department'],
                    'credit_id':member['credit_id'],
                    'temp':member['id'], #Checker
                    'movie_id':movieID
                }
            )


        i = i+1
        if i == stop:
            break









#=========================
#Add to the database
#=========================

for movie in movieList:
    
    de = datetime.strptime(movie['release_date'], "%m/%d/%Y")
    te = str(de.strftime("%b")) + ", "+ str(de.day) + " " + str(de.year)

    db.session.add(
        Movie(
            id=movie['id'],
            title=movie['title'],
            homepage=movie['homepage'],
            lang=movie['lang'],
            genres=movie['genres'],
            poster=movie['poster'],
            overview=movie['overview'],
            release_date=te,
            average_rating=movie['average_rating'],

            release_day=de.day,
            release_month=de.month,
            release_year=de.year
        )
    )

db.session.commit() #save

for cast in castList:
    db.session.add(
        Cast(
            name=cast['name'],
            character=cast['character'],

            cast_id=cast['cast_id'],
            movie_id=cast['movie_id']
        )
    )

db.session.commit() #save

for crew in crewList:
    db.session.add(
        Crew(
            name=crew['name'],
            job=crew['job'],
            department=crew['department'],

            credit_id=crew['credit_id'],
            movie_id=crew['movie_id']
        )
    )

db.session.commit() #save


#print(castList[7]['name'], castList[7]['character'])
#print(crewList[7]['name'], crewList[7]['job'])
# index = 3
# list = Movie.query.limit(99)
# print(list[index].title, " - ", list[index].average_rating, "\n")
#for te in list[index].crew:
#    print(te.name, "-", te.job)
#'''
