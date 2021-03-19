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


def update_addedby(conn, tt, addedby):
    curs = dbi.dict_cursor(conn)
    addedby = f'''"{addedby}"''' if addedby else "NULL"
    curs.execute(f'UPDATE movie SET addedby = {addedby} where tt = {tt}')
    conn.commit()

def update_title(conn, tt, title):
    curs = dbi.dict_cursor(conn)
    title = f'''"{title}"''' if title else "NULL"
    curs.execute(f'UPDATE movie SET title = {title} where tt = {tt}')
    conn.commit()

def update_release(conn, tt, release):
    curs = dbi.dict_cursor(conn)
    release = f'''"{release}"''' if release else "NULL"
    curs.execute(f'UPDATE movie SET `release` = {release} where tt = {tt}')
    conn.commit()

def update_tt(conn, oldTT, newTT): # last so it doesn't mess other queries
    newTT = int(newTT)
    if not (oldTT == newTT):
        curs = dbi.dict_cursor(conn)
        curs.execute(f'SELECT tt FROM movie WHERE tt = {newTT}')
        newInfo = curs.fetchall()
        if not newInfo:
            curs.execute(f'UPDATE movie SET tt = {newTT} where tt = {oldTT}')
            conn.commit()
            return newTT
    elif oldTT == newTT: # do nothing if they're the same value
        return "Do nothing" 
    return None # newTT != oldTT and newTT already exists in db

def movie(conn, tt):
    '''Finds all attributes of movie with the tt (id) specified'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'select * from movie where tt = {tt}')
    return curs.fetchall()

def dirName(conn, tt):
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT director, name from person inner join movie on \
        (director = nm) where tt = {tt}')
    directorName = curs.fetchall()
    if directorName:
        return directorName
    else:
        return None # no director name displayed

def deleteEntry(conn, tt):
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * from movie where tt = {tt}')
    entry = curs.fetchall()
    if entry:
        curs.execute(f'DELETE from movie where tt = {tt}')
    conn.commit()

def get_incomplete_movies(conn):
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT * from movie where \
        director is NULL or `release` is NULL'
    curs.execute(sql)
    return curs.fetchall()


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