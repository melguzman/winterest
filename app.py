from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi # figure out which dbi to use
# import cs304dbi_sqlite3 as dbi

import userInfoQueries as userInfo
import profileQueries
import makeMatchesQueries as matches
import insertFakeData
import random
import sys

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    wemail = request.cookies.get('wemail')
    if not wemail:
        print('no cookie set')
        if request.method == "GET":
            print('case 1: first visit, just render landing page')
            return render_template('landing.html')
    else:
        return redirect(url_for('home'))

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/signup/')
def signup():
    return render_template('signup.html')

@app.route('/interests/', methods = ['GET', 'POST']) 
def interests():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    email = request.cookies.get('wemail')
    #interests
    if request.method == 'POST':
        book = request.form['book']
        album = request.form['song']
        color = request.form['color']
        bio = request.form['bio']

        #insert interests
        curs.execute('''INSERT INTO favorites (wemail, name, itemType) VALUES (%s, %s, %s)''', [email, book, 'book'])
        conn.commit()
        curs.execute('''INSERT INTO favorites (wemail, name, itemType) VALUES (%s, %s, %s)''', [email, album, 'song'])
        conn.commit()
        curs.execute('''INSERT INTO favorites (wemail, name, itemType) VALUES (%s, %s, %s)''', [email, color, 'color'])
        conn.commit()
        curs.execute('''INSERT INTO bio (wemail, bio) VALUES (%s, %s)''', [email, bio])
        conn.commit()
        return redirect(url_for('home'))
    else:
        return render_template('interests.html')

@app.route('/authenticate/<kind>', methods = ['GET', 'POST']) 
def authenticate(kind):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if kind == 'login':
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''SELECT * FROM userAccount WHERE wemail = %s AND password = %s''', [email, password])
            if len(curs.fetchall()) == 1:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('wemail', email)
                return resp
            else:
                flash("Incorrect information. Try again?")
                return render_template('landing.html')

        elif kind == 'signup':
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)

            #basic info
            fname = request.form['fname']
            lname = request.form['lname']
            major = request.form['major']
            year = request.form['year']
            country = request.form['country']
            state = request.form['state']
            city = request.form['city']

            #MBCode and default oncampus to 'no'
            highestMBCode = (curs.execute('''SELECT MAX(CAST(MBCode AS int)) AS code FROM MBResults''')) 
            print(highestMBCode, flush=True)
            MBCode = int(curs.fetchone()['code']) + 1
            onCampus = 'no'

            #insert MBCode
            curs.execute('''INSERT INTO MBResults (MBCode) VALUES (%s)''', [MBCode])
            conn.commit()

            #insert user account
            curs.execute('''INSERT INTO userAccount (wemail, fname, lname, country, state, city, MBCode, major, year, onCampus, password) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', [email, fname, lname, country, state, city, MBCode, major, year, onCampus, password])
            conn.commit()

            matches.insertScores(conn, email)

        #set wemail
        session['index'] = 0
        resp = make_response(redirect(url_for('interests')))
        resp.set_cookie('wemail', email)
        return resp

    flash ("Error during authentication. Try again.") 
    return redirect(url_for("landing.html"))

@app.route('/faq/')
def faq():
    return render_template('faq.html', page_title = 'Winterest FAQ')

@app.route('/demographics/', methods = ["GET", "POST"])
def demographics():
    if request.method == 'GET':
        return render_template('demographics.html', title ='Fill out your demographics:')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

def favoritesInformation(personDict):
    '''Takes a dictionary and adds a favorite key and favorite info in 
    a form of a list of dictionaries as the value'''
    conn = dbi.connect()
    temp = personDict
    email = personDict['wemail']
    favs = userInfo.find_favorites(conn, email) # Get list of dictionaries for each fav.
    temp['favorites'] = favs # Add key value pair to the dictionary
    return temp

emojis = {'album': '💿', 'song': '🎵', 'artist': '👩‍🎨', 'book': '📘', 
    'movie': '🎬', 'color': '🎨', 'emoji': '😜', 'food': '🍔', 'restaurant': '🍕',
    'game': '👾'}

@app.route('/home/', methods=['GET','POST'])
def home():
    # grab wemail from cookie
    wemail = request.cookies.get('wemail')
    if not wemail:
        flash('You are not logged in. Please log in or sign up!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # User wants to logout
        if "logout" in request.form: 
                flash('You successfully logged out. Come back again!')
                resp = make_response(
                    render_template('landing.html'))
                resp.set_cookie('wemail', '', expires=0)
                session.pop('index', None)
                # resp.set_cookie('index', '', expires=0)
                return resp

    conn = dbi.connect()

    currentUserInfo = profileQueries.find_profile(conn, wemail)

    # get index from current carousel
    index = session.get('index', 0) 

    # get a user's current matching
    currentMatches = matches.getMatches(conn, wemail)
    # get list of potential matches emails (list of dictionaries) 
    potentialMatches = matches.generatePotentialInfo(conn, wemail)
    # grab potential user via index (one place they are in the carosel)
    potentialMatch = potentialMatches[index]  # this is a dictionary!
    # add a favorites key with a list of interests as its value for each user
    completedMatches = favoritesInformation(potentialMatch)
    print("Completed matches: " + str(completedMatches))
    # get that user's info as a list with one dictionary in it
    matchEmail = potentialMatch['wemail']
    # get potential user's bio
    matchBio = userInfo.getBio(conn, matchEmail)
    if not (matchBio):
        matchBio = []

    # see if the current potential match has already been matched w/ user
    matchStatus = matches.matchExists(conn, wemail, matchEmail)
        
    return render_template('home.html', person = completedMatches, matchStatus = matchStatus,
        currentMatches = currentMatches, emojis = emojis, matchBio = matchBio, currentUserInfo = currentUserInfo)

@app.route('/makeMatch/', methods=['POST'])
def makeMatch():
    '''Triggered when user presses the "Match" button on the home page.
    Adds the match pairing to the website'''
    conn = dbi.connect()
    userEmail = request.cookies.get('wemail')
    matchEmail = request.form.get('submit')
    matches.setMatched(conn, userEmail, matchEmail)
    return redirect(url_for('home'))

@app.route('/matches/<wemail>', methods=['GET','POST'])
def match(wemail):
    '''Redirects user to a page with matching interactions'''
    userEmail = request.cookies.get('wemail')
    if not userEmail:
        flash('Session timed out. Log in again!')
        return redirect(url_for('index'))

    conn = dbi.connect()
    currentUserInfo = profileQueries.find_profile(conn, userEmail)
    info = profileQueries.find_profile(conn, wemail)
    completeInfo = favoritesInformation(info)
    bio = userInfo.getBio(conn, wemail)
    
    return render_template('matches.html', person = completeInfo, emojis = emojis, personBio = bio, currentUserInfo = currentUserInfo)

@app.route('/next/', methods=['POST'])
def next():
    '''Cycles to the next potential match with the 
    user presses the next button'''
    userEmail = request.cookies.get('wemail')
    if not userEmail:
        flash('Session timed out. Log in again!')
        return redirect(url_for('index'))

    conn = dbi.connect()
    index = session.get('index', 0)
    potentialMatches = matches.generatePotentialInfo(conn, userEmail)

    if (index == (len(potentialMatches) - 1)):
        session['index'] = 0
    else:
        session['index'] = index + 1
    return redirect(url_for('home'))

@app.route('/back/', methods=['POST'])
def back():
    '''Cycles to the previous potential match with the 
    user presses the back button'''
    userEmail = request.cookies.get('wemail')
    if not userEmail:
        flash('Session timed out. Log in again!')
        return redirect(url_for('index'))

    conn = dbi.connect()
    index = session.get('index', 0)
    potentialMatches = matches.generatePotentialInfo(conn, userEmail)

    if (index == 0):
        session['index'] = len(potentialMatches) - 1
    else:
        session['index'] = index - 1
    return redirect(url_for('home'))


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'wellesleymatch_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
