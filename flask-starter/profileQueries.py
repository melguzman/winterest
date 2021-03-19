from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)
import cs304dbi as dbi # fix dbi name

def insert_demographics(conn, wemail, country, state, city):
    # assumption: user MUST input all categories 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT country FROM userAccount WHERE wemail = {wemail}')
    checkDem = curs.fetchall()
    # if list of demographics by said wemail doesn't exist
    if len(checkDem) == 0: 
        curs.execute(f'INSERT INTO userAccount (wemail, country, state, city) \
                VALUES ({wemail}, {country}, {state}, {city})')
        conn.commit()

def update_demographics(conn, wemail, country, state, city): 
    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE userAccount SET country = {country} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET state = {state} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET city = {city} \
        WHERE wemail = {wemail}')
    conn.commit()

def insert_professionalInterests(conn, wemail, industry, dreamJob):
    # assumption: user MUST input all categories 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT wemail FROM professionalInterests INNER \
        JOIN professionalInterests USING (wemail) WHERE \
        wemail = {wemail}')
    checkInt = curs.fetchall()
    # if list of professional interests by said wemail doesn't exist
    if len(checkInt) == 0: 
        curs.execute(f'INSERT INTO professionalInterests (wemail, \
            industry, dreamJob) VALUES ({wemail}, {industry}, \
            {dreamJob})')
        conn.commit()

def update_professionalInterests(conn, wemail, industry, dreamJob):
    # update professional interests list
    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE professionalInterests SET industry = {industry} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE professionalInterests SET dreamJob = {dreamJob} \
        WHERE wemail = {wemail}')
    conn.commit()

def insert_professionalInterests(conn, wemail, industry, dreamJob):
    # assumption: user MUST input all categories 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT wemail FROM professionalInterests INNER \
        JOIN professionalInterests USING (wemail) WHERE \
        wemail = {wemail}')
    checkInt = curs.fetchall()
    # if list of professional interests by said wemail doesn't exist
    if len(checkInt) == 0: 
        curs.execute(f'INSERT INTO professionalInterests (wemail, \
            industry, dreamJob) VALUES ({wemail}, {industry}, \
                {dreamJob})')
        conn.commit()

def update_professionalInterests(conn, wemail, industry, dreamJob):
    # update professional interests list 
    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE professionalInterests SET industry = {industry} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE professionalInterests SET dreamJob = {dreamJob} \
        WHERE wemail = {wemail}')
    conn.commit()



if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('sk1_db')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    """ insert_movie(conn, 8648, 'Wick', 1818)
    curs.execute(f'SELECT * from movie where tt = 8648')
    print(curs.fetchone())
    #deleteEntry(conn, 8648)
    #print(curs.fetchone())
    curs.execute(f'SELECT * from movie where tt = 2')
    print(curs.fetchone()) """

    #print(get_incomplete_movies(conn))