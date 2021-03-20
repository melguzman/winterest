from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi # figure out which dbi to use
# import cs304dbi_sqlite3 as dbi

import userInfoQueries
import profileQueries

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
            pass
        elif kind == 'signup':
            fname = request.form['fname']
            lname = request.form['lname']
            major = request.form['major']
            year = request.form['year']
            country = request.form['country']
            state = request.form['state']
            city = request.form['city']
            MBCode = 'NULL'
            onCampus = 'NULL'

            conn = dbi.connect()

            #profileQueries.insert_profile(conn, email, fname, lname, country, state, city, 'NULL', major, year, 'NULL')

            curs = dbi.dict_cursor(conn)
            curs.execute('INSERT INTO userAccount (wemail, fname, lname, country, state, city, MBCode, major, year, onCampus, password) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (email, fname, lname, country, state, city, MBCode, major, year, onCampus, password))
            #flash('Signup successful!')
            return '<h1>SUCCESS</h1>'
            #curs.execute('''insert into userAccount (wemail, password, fname, lname, major, year, country, state, city, onCampus, MBCode) 
            #values ('szeamer', 'password', 'Silvia', 'Zeamer', 'MAS', '2021', 'US', 'TX', 'Austin', NULL, NULL);')'''
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
