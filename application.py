#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response

# importing SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, MovieDB, User
import random
import string
import httplib2
import json
import requests

# importing oauth

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

# app initiate

app = Flask(__name__)


# google client secret
g_file = json.loads(open('client_secret.json', 'r').read())
CLIENT_ID = g_file['web']['client_id']
APPLICATION_NAME = 'Item-Catalog'

engine = create_engine('sqlite:///MovieCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# check login

def check_user():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# admin details

def check_admin():
    return session.query(User).filter_by(
        email='dolfiedekock@gmail.com').one_or_none()


# Add new user into database

def createUser():
    name = login_session['name']
    email = login_session['email']
    url = login_session['img']
    provider = login_session['provider']
    newUser = User(name=name, email=email, image=url, provider=provider)
    session.add(newUser)
    session.commit()


def new_state():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


def queryAllMovies():
    return session.query(MovieDB).all()


# Routes

# main

@app.route('/')
@app.route('/movies/')
def showMovies():
    movies = queryAllMovies()
    state = new_state()
    return render_template('main.html', movies=movies, currentPage='main',
                           state=state, login_session=login_session)


# add a new movie

@app.route('/movie/new/', methods=['GET', 'POST'])
def newMovie():
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and \
                    login_session['provider'] != 'null':
            movieName = request.form['movieName']
            movieAuthor = request.form['directorName']
            coverUrl = request.form['movieImage']
            description = request.form['movieDescription']
            description = description.replace('\n', '<br>')
            movieCategory = request.form['category']
            user_id = check_user().id

            if movieName and movieAuthor and coverUrl and description \
                    and movieCategory:
                newMovie = MovieDB(
                    movieName=movieName,
                    directorName=movieAuthor,
                    coverUrl=coverUrl,
                    description=description,
                    category=movieCategory,
                    user_id=user_id,
                    )
                session.add(newMovie)
                session.commit()
                return redirect(url_for('showMovies'))
            else:
                state = new_state()
                return render_template(
                    'newItem.html',
                    currentPage='new',
                    title='Add New Movie',
                    errorMsg='All Fields are Required!',
                    state=state,
                    login_session=login_session,
                    )
        else:
            state = new_state()
            movies = queryAllMovies()
            return render_template(
                'main.html',
                movies=movies,
                currentPage='main',
                state=state,
                login_session=login_session,
                errorMsg='Please Login first to Add Movie!',
                )
    elif 'provider' in login_session and login_session['provider'] \
            != 'null':
        state = new_state()
        return render_template('newItem.html', currentPage='new',
                               title='Add New Movie', state=state,
                               login_session=login_session)
    else:
        state = new_state()
        movies = queryAllMovies()
        return render_template(
            'main.html',
            movies=movies,
            currentPage='main',
            state=state,
            login_session=login_session,
            errorMsg='Please Login first to Add Movie!',
            )


# To show movie of different category

@app.route('/movies/category/<string:category>/')
def sortMovies(category):
    movies = session.query(MovieDB).filter_by(category=category).all()
    state = new_state()
    return render_template(
        'main.html',
        movies=movies,
        currentPage='main',
        error='Sorry! No Movie in Database With This Genre :(',
        state=state,
        login_session=login_session)


# To show movie detail

@app.route('/movies/category/<string:category>/<int:movieId>/')
def movieDetail(category, movieId):
    movie = session.query(MovieDB).filter_by(id=movieId,
                                           category=category).first()
    state = new_state()
    if movie:
        return render_template('itemDetail.html', movie=movie,
                               currentPage='detail', state=state,
                               login_session=login_session)
    else:
        return render_template('main.html', currentPage='main',
                               error="""No Movie Found with this Category
                               and Movie Id :(""",
                               state=state,
                               login_session=login_session)


# To edit movie detail

@app.route('/movies/category/<string:category>/<int:movieId>/edit/',
           methods=['GET', 'POST'])
def editMovieDetails(category, movieId):
    movie = session.query(MovieDB).filter_by(id=movieId,
                                           category=category).first()
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            movieName = request.form['movieName']
            movieAuthor = request.form['directorName']
            coverUrl = request.form['movieImage']
            description = request.form['movieDescription']
            movieCategory = request.form['category']
            user_id = check_user().id
            admin_id = check_admin().id

            # check if movie owner is same as logged in user or admin or not

            if movie.user_id == user_id or user_id == admin_id:
                if movieName and movieAuthor and coverUrl and description \
                        and movieCategory:
                    movie.movieName = movieName
                    movie.directorName = movieAuthor
                    movie.coverUrl = coverUrl
                    description = description.replace('\n', '<br>')
                    movie.description = description
                    movie.category = movieCategory
                    session.add(movie)
                    session.commit()
                    return redirect(url_for('movieDetail',
                                    category=movie.category,
                                    movieId=movie.id))
                else:
                    state = new_state()
                    return render_template(
                        'editItem.html',
                        currentPage='edit',
                        title='Edit Movie Details',
                        movie=movie,
                        state=state,
                        login_session=login_session,
                        errorMsg='All Fields are Required!',
                        )
            else:
                state = new_state()
                return render_template(
                    'itemDetail.html',
                    movie=movie,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit movie Details!')
        else:
            state = new_state()
            return render_template(
                'itemDetail.html',
                movie=movie,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Movie Details!',
                )
    elif movie:
        state = new_state()
        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == movie.user_id or user_id == admin_id:
                movie.description = movie.description.replace('<br>', '\n')
                return render_template(
                    'editItem.html',
                    currentPage='edit',
                    title='Edit Movie Details',
                    movie=movie,
                    state=state,
                    login_session=login_session,
                    )
            else:
                return render_template(
                    'itemDetail.html',
                    movie=movie,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit movie Details!')
        else:
            return render_template(
                'itemDetail.html',
                movie=movie,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Movie Details!',
                )
    else:
        state = new_state()
        return render_template('main.html', currentPage='main',
                               error="""Error Editing Movie! No Movie Found
                               with this Category and Movie Id :(""",
                               state=state,
                               login_session=login_session)


# To delete movies

@app.route('/movies/category/<string:category>/<int:movieId>/delete/')
def deleteMovie(category, movieId):
    movie = session.query(MovieDB).filter_by(category=category,
                                           id=movieId).first()
    state = new_state()
    if movie:

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == movie.user_id or user_id == admin_id:
                session.delete(movie)
                session.commit()
                return redirect(url_for('showMovies'))
            else:
                return render_template(
                    'itemDetail.html',
                    movie=movie,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the Owner Can delete the movie'
                    )
        else:
            return render_template(
                'itemDetail.html',
                movie=movie,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Delete the Movie!',
                )
    else:
        return render_template('main.html', currentPage='main',
                               error="""Error Deleting Movie! No Movie Found
                               with this Category and Movie Id :(""",
                               state=state,
                               login_session=login_session)


# JSON Endpoints

@app.route('/movies.json/')
def moviesJSON():
    movies = session.query(MovieDB).all()
    return jsonify(Movies=[movie.serialize for movie in movies])

@app.route('/movies/category/<string:category>.json/')
def movieCategoryJSON(category):
    movies = session.query(MovieDB).filter_by(category=category).all()
    return jsonify(Movies=[movie.serialize for movie in movies])


@app.route('/movies/category/<string:category>/<int:movieId>.json/')
def movieJSON(category, movieId):
    movie = session.query(MovieDB).filter_by(category=category,
                                           id=movieId).first()
    return jsonify(Movie=movie.serialize)


# google signin function

@app.route('/gconnect', methods=['POST'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'),
                               401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain directorization code

    code = request.data
    try:

        # Upgrade the directorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade the
        directorisation code"""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    header = httplib2.Http()
    result = json.loads(header.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = access_token
    login_session['id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION

    login_session['name'] = data['name']
    login_session['img'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    if not check_user():
        createUser()
    return jsonify(name=login_session['name'],
                   email=login_session['email'],
                   img=login_session['img'])


# logout user

@app.route('/logout', methods=['post'])
def logout():

    # Disconnect based on provider

    if login_session.get('provider') == 'google':
        return gdisconnect()
    else:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']

    # Only disconnect a connected user.

    if access_token is None:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['credentials']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'loggedOut'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        # if given token is invalid, unable to revoke token

        response = make_response(json.dumps({'state': 'errorRevoke'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
