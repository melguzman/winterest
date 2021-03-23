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
import bcrypt
import sys

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def index():
    wemail = session.get('wemail')
    if not wemail:
        print('no session exist')
        if request.method == "GET":
            print('case 1: first visit, just render landing page')
            return render_template('landing.html')
    else:
        return redirect(url_for('home'))

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            wemail = request.form['email']
            passwd = request.form['password']
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''SELECT *
                        FROM userpass
                        WHERE wemail = %s''',
                        [wemail])
            row = curs.fetchone()
            print(row)
            if row is None:
                # Same response as wrong password,
                # so no information about what went wrong
                print("Row is none")
                flash('Login incorrect. Try again or join')
                return redirect( url_for('login'))
            hashed = row['hashed']
            print('database has hashed: {} {}'.format(hashed,type(hashed)))
            print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                    hashed.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
            if hashed2_str == hashed:
                print('they match!')
                flash('successfully logged in as '+ wemail)
                session['index'] = 0
                session['wemail'] = wemail
                return redirect(url_for('home'))
            else:
                flash('Login incorrect. Try again or join')
                return redirect( url_for('index'))
        except Exception as err:
            print("Exception: " + str(err))
            flash('Login incorrect. Try again or join')
            return redirect( url_for('login'))

@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        try:
            conn = dbi.connect()
            curs = dbi.cursor(conn)

            wemail = request.form['email']
            passwd1 = request.form['password1']
            passwd2 = request.form['password2']

            # basic info
            fname = request.form['fname']
            lname = request.form['lname']
            major = request.form['major']
            year = request.form['year']
            country = request.form['country']
            state = request.form['state']
            city = request.form['city']
            onCampus = 'no'

            # MBCode and default oncampus to 'no'
            # highestMBCode = (curs.execute('''SELECT MAX(CAST(MBCode AS int)) AS code FROM MBResults''')) 
            # print(highestMBCode, flush=True)
            # MBCode = int(curs.fetchone()['code']) + 1

            # insert MBCode
            # curs.execute('''INSERT INTO MBResults (MBCode) VALUES (%s)''', [MBCode])
            # conn.commit()

            # insert user account
            curs.execute('''INSERT INTO userAccount (wemail, fname, lname, country, state, city, major, year, onCampus) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', [wemail, fname, lname, country, state, city, major, year, onCampus])
            conn.commit()

            if passwd1 != passwd2:
                flash('Passwords do not match. Try again.')
                return redirect( url_for('signup'))

            hashed = bcrypt.hashpw(passwd1.encode('utf-8'),
                                bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')
            print(passwd1, type(passwd1), hashed, hashed_str)
            try:
                curs.execute('''INSERT INTO userpass(wemail, hashed)
                            VALUES(%s, %s)''',
                            [wemail, hashed_str])
                conn.commit()
            
            except Exception as err:
                flash('That username is taken: {}'.format(repr(err)))
                return redirect(url_for('signup'))

            matches.insertScores(conn, wemail)
            session['index'] = 0
            session['wemail'] = wemail
            return redirect(url_for('interests'))

        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )

@app.route('/pic/<wemail>')
def pic(wemail):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from picfile where wemail = %s''',
        [wemail])
    if numrows == 0:
        flash('No picture for {}'.format(wemail))
        return redirect(url_for('home'))
    row = curs.fetchone()
    return send_from_directory(app.config['UPLOADS'],row['filename'])


@app.route('/interests/', methods = ['GET', 'POST']) 
def interests():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    email = session.get('wemail')
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

        try:
            print("Rendering files")
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(email,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute(
                '''insert into picfile(wemail,filename) values (%s,%s)
                    on duplicate key update filename = %s''',
                [email, filename, filename])
            conn.commit()
            flash('Upload successful')
            return redirect(url_for('home'))

        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return redirect(url_for('interests'))
    else:
        return render_template('interests.html')

@app.route('/logout/', methods = ["POST"])
def logout():
    flash('You successfully logged out. Come back again!')
    resp = make_response(render_template('landing.html'))
    session.pop('wemail', None)
    session.pop('index', None)
    return resp

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
    wemail = session.get('wemail')
    if not wemail:
        flash('You are not logged in. Please log in or sign up!')
        return redirect(url_for('index'))

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
    # see if user has photo:
    photo = userInfo.find_photo(conn, matchEmail)

    # see if the current potential match has already been matched w/ user
    matchStatus = matches.matchExists(conn, wemail, matchEmail)
        
    return render_template('home.html', person = completedMatches, matchStatus = matchStatus,
        currentMatches = currentMatches, emojis = emojis, matchBio = matchBio, currentUserInfo = currentUserInfo,
        photo = photo)

@app.route('/makeMatch/', methods=['POST'])
def makeMatch():
    '''Triggered when user presses the "Match" button on the home page.
    Adds the match pairing to the website'''
    conn = dbi.connect()
    userEmail = session.get('wemail')
    matchEmail = request.form.get('submit')
    matches.setMatched(conn, userEmail, matchEmail)
    return redirect(url_for('home'))

@app.route('/matches/<wemail>', methods=['GET','POST'])
def match(wemail):
    '''Redirects user to a page with matching interactions'''
    userEmail = session.get('wemail')
    if not userEmail:
        flash('Session timed out. Log in again!')
        return redirect(url_for('index'))

    conn = dbi.connect()
    currentUserInfo = profileQueries.find_profile(conn, userEmail)
    info = profileQueries.find_profile(conn, wemail)
    completeInfo = favoritesInformation(info)
    bio = userInfo.getBio(conn, wemail)
    photo = userInfo.find_photo(conn, wemail)
    
    return render_template('matches.html', person = completeInfo, 
    emojis = emojis, personBio = bio, currentUserInfo = currentUserInfo, photo = photo)

@app.route('/next/', methods=['POST'])
def next():
    '''Cycles to the next potential match with the 
    user presses the next button'''
    userEmail = session.get('wemail')
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
    userEmail = session.get('wemail')
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
