from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
from threading import Lock # threading & locking
app = Flask(__name__)

from datetime import datetime
import cs304dbi as dbi # figure out which dbi to use
# import cs304dbi_sqlite3 as dbi

import userInfoQueries as userInfo
import profileQueries
import makeMatchesQueries as matches
import insertFakeData
import random
import bcrypt
import sys
import time

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
            return render_template('landing.html', page_title="Landing")
    else:
        return redirect(url_for('home'))

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    '''Routing function for when peole log in'''
    if request.method == 'GET':
        return render_template('login.html', page_title="Login")
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
            if row is None:
                # Same response as wrong password,
                # so no information about what went wrong
                print("Row is none")
                flash('Login incorrect. Try again or join')
                return redirect( url_for('login'))
            hashed = row['hashed']
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                    hashed.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            if hashed2_str == hashed:
                flash('successfully logged in as '+ wemail)
                session['index'] = 0
                session['wemail'] = wemail
                return redirect(url_for('home'))
            else:
                flash('Login incorrect. Try again or sign up')
                return redirect( url_for('index'))
        except Exception as err:
            print("Exception: " + str(err))
            flash('Login incorrect. Try again or sign up')
            return redirect( url_for('login'))

@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
    '''Routing function for when people sign up. 
    This is the first page of the onboarding process'''
    if request.method == 'GET':
        return render_template('signup.html', page_title="Signup")
    else:
        try:
            conn = dbi.connect()
            curs = dbi.cursor(conn)
            
            # grab email and passwords
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
            onCampus = request.form['onCampus']

            # insert user account
            profileQueries.insert_profile(conn, wemail, fname, lname, country, state, city, major, year, onCampus)

            # check if the passwords match and if so, 
            # continue to add them to the user pass table
            if passwd1 != passwd2:
                flash('Passwords do not match. Try again.')
                return redirect( url_for('signup'))

            hashed = bcrypt.hashpw(passwd1.encode('utf-8'),
                                bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')
            print(passwd1, type(passwd1), hashed, hashed_str)
            try:
                curs.execute('''lock tables userpass write''')
                curs.execute('''INSERT INTO userpass(wemail, hashed)
                            VALUES(%s, %s)''',
                            [wemail, hashed_str])
                curs.execute('''unlock tables''')
                conn.commit()
            
            # In the case the username is taken
            except Exception as err:
                flash('That username is taken: {}'.format(repr(err)))
                return redirect(url_for('signup'))

            # Generate a list of potential matches for the user (ordered)
            matches.insertScores(conn, wemail)

            # Add a session 'index' that keeps track of their scroll position
            # for the carousel
            session['index'] = 0
            # Add a session for the email so we can remember the user
            session['wemail'] = wemail
            return redirect(url_for('interests'))

        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )

@app.route('/pic/<wemail>')
def pic(wemail):
    '''Loads images, which are used on all pages (home,
    matches, and user profile'''
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
    '''Interests is the second half of the onboarding process.
    Users are asked for the interests (favorites) and contact
    information. We will be making the favorites customizable 
    for the beta version'''
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
        userInfo.insert_favorites(conn, email, book, 'book')
        userInfo.insert_favorites(conn, email, album, 'song')
        userInfo.insert_favorites(conn, email, color, 'color')

        #insert user's bio
        curs.execute('''lock tables bio write''')
        curs.execute('''INSERT INTO bio (wemail, bio) VALUES (%s, %s)''', [email, bio])
        curs.execute('''unlock tables''')
        conn.commit()

        #insert contact information
        social1_type = request.form['contact-type1'] 
        social2_type = request.form['contact-type2']
        if (social1_type == 'Text'): 
            social1_value = request.form['phonenumber1']
            profileQueries.insert_contact(conn, email, social1_value, None, None, social1_type)
        else: # for Instagram/Faceobok, which hold links
            # Two cases were necessary since the inputs held different values
            social1_value = request.form['social-url1']
            profileQueries.insert_contact(conn, email, None, None, social1_value, social1_type)

        # check if someone entered a second contact method
        social2_social = request.form['social-url2']
        social2_number = request.form['phonenumber2']
        if (social2_social != '') or (social2_number != ''):
            if (social2_type == 'Text'):
                profileQueries.insert_contact(conn, email, social2_number, None, None, social2_type)
            else:
                profileQueries.insert_contact(conn, email, None, None, social2_social, social2_type)

        try:
            # Uploading the image
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(email,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''lock tables picfile write''')
            curs.execute(
                '''insert into picfile(wemail,filename) values (%s,%s)
                    on duplicate key update filename = %s''',
                [email, filename, filename])
            curs.execute('''unlock tables''')
            conn.commit()
            flash('Upload successful')
            return redirect(url_for('home'))

        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return redirect(url_for('interests'))
    else:
        return render_template('interests.html', page_title="Signup")

@app.route('/logout/', methods = ["POST"])
def logout():
    '''Logout option when the user chooses to log out'''
    flash('You successfully logged out. Come back again!')
    resp = make_response(render_template('landing.html', page_title="Landing"))
    session.pop('wemail', None)
    session.pop('index', None)
    return resp

@app.route('/faq/')
def faq():
    '''Routes to the FAQ page, which contains information about Winterest'''
    return render_template('faq.html', page_title = 'Winterest FAQ')

def favoritesInformation(personDict):
    '''Takes a dictionary and adds a favorite key and favorite info in 
    a form of a list of dictionaries as the value'''
    conn = dbi.connect()
    email = personDict['wemail']
    favs = userInfo.find_favorites(conn, email) # Get list of dictionaries for each fav.
    personDict['favorites'] = favs # Add key value pair to the dictionary
    return personDict

# Emojis dictionary that associates a 'favorite' with an emoji. This will
# be important in the Beta version, when interests can be customized
emojis = {'album': '💿', 'song': '🎵', 'artist': '👩‍🎨', 'book': '📘', 
    'movie': '🎬', 'color': '🎨', 'emoji': '😜', 'food': '🍔', 'restaurant': '🍕',
    'game': '👾'}

@app.route('/home/', methods=['GET','POST'])
def home():
    '''This is the home page of the website that houses matching
    interactions. This page allows users to display potential matches
    and their current matches'''
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
    # get a user's one sided matchings
    oneSidedMatching = matches.getOneSidedMatches(conn, wemail) #addeddddddddddddddddddddddddddd
    # get list of potential matches emails (list of dictionaries) 
    potentialMatches = matches.generatePotentialInfo(conn, wemail)
    # grab potential user via index (one place they are in the carosel)
    potentialMatch = potentialMatches[index]  # this is a dictionary!
    # add a favorites key with a list of interests as its value for each user
    completedMatches = favoritesInformation(potentialMatch)
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
        currentMatches = currentMatches, oneSidedMatches = oneSidedMatching, emojis = emojis, 
        matchBio = matchBio, currentUserInfo = currentUserInfo,
        photo = photo, page_title="Home") #adddedddddddddddddddddd

@app.route('/makeMatch/<location>', methods=['POST'])
def makeMatch(location):
    '''Triggered when user presses the "Match" button on the home page.
    Adds the match pairing to the website'''
    conn = dbi.connect()
    userEmail = session.get('wemail')
    matchEmail = request.form.get('submit')
    #matches.setMatched(conn, userEmail, matchEmail)
    #return redirect(url_for('home'))
    
    #check if one sided match already exists
    #print("Does one sided exist?")
    #print(matches.matchExists(conn, matchEmail, userEmail))
    if matches.matchExists(conn, matchEmail, userEmail): #works perfect
        #print("worked")
        matches.setMatched(conn, userEmail, matchEmail) #updated both so two sided match
    else:
        matches.setOneSDMatch(conn, userEmail, matchEmail) #intially one sided

    if location == "home":
        return redirect(url_for('home'))
    else:
        return redirect(url_for('match', wemail=matchEmail))

@app.route('/deleteMatch/', methods=['POST'])
def deleteMatch():
    '''Triggered when user presses the "unMatch" button on the home page.
    Gets rid of match pairing from the website'''
    conn = dbi.connect()
    userEmail = session.get('wemail')
    matchEmail = request.form.get('submit')
    #design decision: if one side unmatches, completey unmatch
    matches.unMatch(conn, userEmail, matchEmail)
    return redirect(url_for('home'))

@app.route('/matches/<wemail>', methods=['GET','POST'])
def match(wemail):
    '''Redirects user to a page with matching interactions'''
    session['currentMatchee'] = wemail
    userEmail = session.get('wemail')
    if not userEmail:
        flash('Session timed out. Log in again!')
        return redirect(url_for('index'))

    # grabbing basic info and photos for the match page
    conn = dbi.connect()
    currentUserInfo = profileQueries.find_profile(conn, userEmail)
    info = profileQueries.find_profile(conn, wemail)
    completeInfo = favoritesInformation(info)
    bio = userInfo.getBio(conn, wemail)
    photo = userInfo.find_photo(conn, wemail)
    contacts = profileQueries.find_contacts(conn, wemail)

    #check if this person is a one sided match
    oneSidedMatchStatus = (len(matches.matchExists(conn, wemail, userEmail)) > 0) \
                        and (len(matches.matchExists(conn, userEmail, wemail)) == 0)

    # Add any upcoming meetings
    meetings = profileQueries.find_all_meetings(conn, wemail)
    
    return render_template('matches.html', person = completeInfo, 
        oneSDMatchStatus = oneSidedMatchStatus, emojis = emojis, personBio = bio, 
        currentUserInfo = currentUserInfo, photo = photo, meetings = meetings, 
        contacts=contacts, page_title=completeInfo["fname"] + "'s Profile") #addeddddddddddddd

@app.route('/profile/', methods=['GET','POST'])
def profile():
    '''Displays the current user's profile'''
    userEmail = session.get('wemail')
    if not userEmail:
        flash('Session timed out. Log in again!')
        return redirect(url_for('index'))

    conn = dbi.connect()
    info = profileQueries.find_profile(conn, userEmail)
    completeInfo = favoritesInformation(info)
    bio = userInfo.getBio(conn, userEmail)
    photo = userInfo.find_photo(conn, userEmail)
    contacts = profileQueries.find_contacts(conn, userEmail)
    # Add any upcoming meetings
    meetings = profileQueries.find_all_meetings(conn, userEmail)
    
    return render_template('profile.html', person = completeInfo, 
        emojis = emojis, personBio = bio, photo = photo, meetings = meetings, 
        contacts=contacts, page_title=info["fname"] + "'s Profile") #addeddddddddddddd


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

@app.route('/scheduleMeeting/<wemail>', methods=['POST'])
def scheduleMeeting(wemail):
    '''Schedules a meeting with two users (triggered when users
    press schedule'''
    # Grab meeting logistics from the schedule form
    userEmail = session.get('wemail')
    matchEmail = wemail
    what = request.form['schedule-what']
    where = request.form['schedule-where']
    location = request.form['schedule-location']
    when = request.form['schedule-when']
    notes = request.form['notes']

    # Extract information from the time input
    dateAndTime = when.split('T')
    strippedDate = dateAndTime[0]
    strippedTime = dateAndTime[1]
    dateObject = datetime.strptime(strippedDate, "%Y-%m-%d")
    formatedDate = formatDate(dateObject)
    formatedTime = timeConvert(strippedTime)

    conn = dbi.connect()
    curs = dbi.cursor(conn)

    # Insert information info table
    profileQueries.insert_meeting(conn, userEmail, matchEmail, what, where,
            location, formatedTime, formatedDate, notes)

    meetings = profileQueries.find_all_meetings(conn, wemail)

    # Example outputs: study in-person Clapp 2021-03-29T18:40 hi
    return redirect(url_for('match', wemail=wemail, meetings=meetings))

@app.route('/deleteMeeting/', methods=['POST'])
def deleteMeeting():
    '''Deletes a meeting between two people'''
    conn = dbi.connect()
    current = session.get('currentMatchee')
    meetingID = request.form['deleteMeeting']
    print(meetingID, current)
    profileQueries.delete_meeting(conn, meetingID)
    return redirect(url_for('match', wemail=current))

def timeConvert(inputTime):
    '''Formats the time into this format: 7:00pm EST'''
    newTime = datetime.strptime(inputTime,'%H:%M').strftime('%I:%M %p')
    return newTime + " " + time.tzname[0]

def formatDate(date):
    '''Formats the date into this format: Thursday, May 23'''
    dayOfWeek = date.strftime("%A")
    month = date.strftime("%B")
    day = date.strftime("%d")
    return "{}, {} {}".format(dayOfWeek, month, day)

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
