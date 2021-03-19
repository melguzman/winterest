from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)
import cs304dbi as dbi # fix dbi name

'''**************** Queries for getting info ****************'''

def find_dem(conn, wemail):
    '''Returns a user's demographic information; singular row returned'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT country, state, city FROM userAccount WHERE wemail =\
         {wemail}')
    demographics = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the demographics
    if len(demographics) != 0:
        return curs.fetchall()
    return "No demographics input yet"

def find_profInt(conn, wemail):
    '''Returns a user's professional interest information; singular
    row returned'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * FROM professionalInterests\
        WHERE wemail = {wemail}')
    profInt = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the professional interests
    if len(profInt) != 0:
        return curs.fetchall()
    return "No professional intersts input yet"

def find_favorites(conn, wemail):
    '''Returns a user's favorites things and their respective genres; will be 
    multiple rows'''
    curs.execute(f'SELECT * FROM favorites\
        WHERE wemail = {wemail}')
    genreInt = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the professional interests
    if len(genreInt) != 0:
        return curs.fetchall()
    return "No favorite genres input yet"

def find_person_LLs(conn, wemail):
    '''Returns all of user's love languages; 3 rows returned'''
    curs.execute(f'SELECT * FROM loveLanguages \
        WHERE wemail = {wemail}')
    LLInt = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the professional interests
    if len(LLInt) != 0:
        return curs.fetchall()
    return "No LLs input yet"


'''**************** Queries for changing tables ****************'''

############ INSERT, UPDATE, DELETE Demographics

def insert_demographics(conn, wemail, country, state, city):
    '''Takes user's initial inputs for their demographics and
    inserts them into the table.'''

    # assumption: user MUST input all categories 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT country FROM userAccount WHERE wemail = {wemail}')
    checkDem = curs.fetchall()
    # if list of demographics by said wemail doesn't exist,
    # we will insert a new row into the table for this person
    if len(checkDem) == 0: 
        curs.execute(f'INSERT INTO userAccount (wemail, country, state, city) \
                VALUES ({wemail}, {country}, {state}, {city})')
        conn.commit()

def update_demographics(conn, wemail, country, state, city): 
    '''Takes user's changed inputs for their demographics and
    updates them.'''
    
    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE userAccount SET country = {country} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET state = {state} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET city = {city} \
        WHERE wemail = {wemail}')
    conn.commit()

############ INSERT, UPDATE, DELETE Professional Intersets

def insert_professionalInterests(conn, wemail, industry, dreamJob):
    '''Takes user's initial inputs for their professional interests and
    inserts them into the table. Can have one input per professional interest
    column.'''

    # assumption: user MUST have an input for ALL categories 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT wemail FROM professionalInterests WHERE \
        wemail = {wemail}')
    checkInt = curs.fetchall()
    # if list of professional interests by said wemail doesn't exist,
    # we will insert a new row into the table for this person
    if len(checkInt) == 0: 
        curs.execute(f'INSERT INTO professionalInterests (wemail, \
            industry, dreamJob) VALUES ({wemail}, {industry}, \
            {dreamJob})')
        conn.commit()

def update_professionalInterests(conn, wemail, industry, dreamJob):
    '''Takes user's changed inputs for their professional interests and
    updates them.'''

    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE professionalInterests SET industry = {industry} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE professionalInterests SET dreamJob = {dreamJob} \
        WHERE wemail = {wemail}')
    conn.commit()

############ INSERT, UPDATE, DELETE Favorite and Genres

def insert_favorites(conn, wemail, name, itemType):
    '''Takes user's inputs for their favorite things and their respective 
    genres.'''

    # assumption: user MUST have a favorite of each genre listed 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'INSERT INTO favorites (wemail, name, itemType) \
        VALUES ({wemail}, {name}, {itemType})')
    conn.commit()

def update_favorites(conn, wemail, name, itemType):
    '''Takes user's changed inputs for their favorite genres and
    updates them. Assumes 1 to 1 ratio between itemType and favorite
    thing'''

    # update favorite and genres info 
    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE favorites SET name = {name} \
        WHERE itemType = {itemType}')
    curs.execute(f'UPDATE favorites SET itemType = {itemType} \
        WHERE name = {name}')
    conn.commit()

############ INSERT, UPDATE, DELETE Love languages

def insert_top3_LL(conn, wemail, language, langNum):
    '''Takes user's inputs for a love language and inserts it into the
    table. We assume that the user inputs their top 3 languages (all of
    equal weight). Only occurs if the user is filling these out for 
    the first time. Must be called thrice, once for each language.'''

    # assumption: user MUST have 3 LLs
    curs = dbi.dict_cursor(conn)
    curs.execute(f'INSERT INTO loveLanguages (wemail, language, langNum) \
        VALUES ({wemail}, {language}, {langNum})')
    conn.commit()

def update_top3_lang(conn, wemail, language, langNum):
    '''Takes user's changed inputs for one of their love languages. Updates
    with new top 3 languages for user. Can be called thrice every time a user
    makes an update, essentially updating all three languages even if any of
    them remain the same for simplicity's sake'''

    # update love languages info 
    curs = dbi.dict_cursor(conn)

    wemail = f'''"{wemail}"''' if wemail else "NULL"
    curs.execute(f'UPDATE loveLanguages SET language = {language} \
        WHERE wemail = {wemail} and langNum = {langNum}')
    conn.commit()

############ INSERT, DELETE Myers-Briggs test results

# can add update but I don't really feel it's needed bc doesn't usually change

def insert_LL(conn, wemail, rank, language):
    '''Takes inputs from user based off of their Myers-Briggs test results.
    Inserts the user's results into the database'''

    curs = dbi.dict_cursor(conn)
    # if list of professional interests by said wemail doesn't exist
    curs.execute(f'INSERT INTO loveLanguages (wemail, name, type) \
        VALUES ({wemail}, {rank}, {language})')
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