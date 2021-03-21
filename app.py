from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi # figure out which dbi to use
# import cs304dbi_sqlite3 as dbi

import userInfoQueries
import matchingQueries as mq
import makeMatchesQueries as matches
import random

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
    return render_template('landing.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/signup/')
def signup():
    return render_template('signup.html')

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
                session['wemail'] = email
                return redirect(url_for('home'))
            else:
                return '<h1>FAILURE</h1>'

        elif kind == 'signup':
            fname = request.form['fname']
            lname = request.form['lname']
            major = request.form['major']
            year = request.form['year']
            country = request.form['country']
            state = request.form['state']
            city = request.form['city']
            MBCode = '5'
            onCampus = 'no'

            conn = dbi.connect()

            curs = dbi.dict_cursor(conn)
            curs.execute('''INSERT INTO MBResults (MBCode) VALUES (%s)''', [MBCode])
            curs.execute('''INSERT INTO userAccount (wemail, fname, lname, country, state, city, MBCode, major, year, onCampus, password) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', [email, fname, lname, country, state, city, MBCode, major, year, onCampus, password])
            conn.commit()
            session['wemail'] = email
            return redirect(url_for('home'))
            
    return '<h1>NOTHING HAPPENED</h1>'




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

def favoritesInformation(peopleDict):
    conn = dbi.connect()
    temp = peopleDict
    for aDict in peopleDict:
        favs = mq.getFavorites(conn, peopleDict['wemail']) # Get list of dictionaries for each fav.
        temp['favorites'] = favs
    return temp

@app.route('/home/', methods=['GET','POST'])
def home():
    # get user's email
    conn = dbi.connect()
    wemail = session.get('wemail', 'jl4')
    index = session.get('index', 0)
    matchStatus = False
    emojis = {'album': '💿', 'song': '🎵', 'artist': '👩‍🎨', 'book': '📘', 
    'movie': '🎬', 'color': '🎨', 'emoji': '😜', 'food': '🍔', 'restaurant': '🍕',
    'game': '👾'}

    # get a user's current matching
    currentMatches = mq.getMatches(conn, wemail)
    # get list of potential matches (list of dictionaries)
    potentialMatches = matches.generateMatches(conn, wemail)
    # add a favorites key with a list of interests as it's value for each user
    completedMatches = favoritesInformation(potentialMatches)
    # grab potential user via index (one place they are in the carosel)
    potentialMatch = potentialMatches[index]
    matchEmail = potentialMatch['wemail']

    # see if the current potential match has already been matched w/ user
    matchStatus = mq.isMatched(wemail, matchEmail)

    if request.method == 'POST':
        # User pressed match button, so match two of them together
        matchEmail = request.form.get('submit')
        mq.insertMatches(wemail, matchEmail)
        
    return render_template('home.html', person = potentialMatch, matchStatus = matchStatus,
        currentMatches = currentMatches, emojis = emojis)
    
@app.route('/match/', methods=['POST'])
def match():
    userEmail = session['username']
    matchEmail = request.form.get('submit')
    mq.insertMatches(wemail, matchEmail)
    return redirect(url_for('home'))

@app.route('/next/', methods=['POST'])
def next():
    wemail = session.get('wemail')
    index = session.get('index')
    potentialMatches = matches.generateMatches(conn, wemail)

    if (index == (len(potentialMatches) - 1)):
        session['index'] = 0
    else:
        session['index'] = session['index'] + 1
    return redirect(url_for('home'))

@app.route('/back/', methods=['POST'])
def back():
    wemail = session.get('wemail')
    index = session.get('index')
    potentialMatches = matches.generateMatches(conn, wemail)

    if (index == 0):
        session['index'] = len(potentialMatches) - 1
    else:
        session['index'] = session['index'] - 1
    return redirect(url_for('home'))


@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        # maybe PUT?
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html')


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
