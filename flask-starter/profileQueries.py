from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)
import cs304dbi as dbi # fix dbi name

'''**************** Queries for getting info ****************'''

def find_profile(conn, wemail):
    '''Returns the info associated with a given wemail'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * FROM userAccount WHERE wemail =\
         {wemail}')
    person = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the demographics
    if len(person) != 0:
        return curs.fetchall()
    return "No user by that name yet"

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

'''**************** Queries for changing tables ****************'''

############ INSERT, UPDATE User Profile

def insert_profile(conn, wemail, fname, lname, country,
            state, city, MBCode, major, year, onCampus):
    '''Takes new user's initial inputs and adds them into the table'''
    # assumption: user MUST input all categories 
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * FROM userAccount WHERE wemail = {wemail}')
    checkUser = curs.fetchall()
    # if account for this user doesn't already exist, we will add them to
    # the userAccounts table
    if len(checkDem) == 0: 
        curs.execute(f'INSERT INTO userAccount (wemail, fname, lname, country,
            state, city, MBCode, major, year, onCampus) \
            VALUES ({wemail}, {fname}, {lname}, {country}, \
            {state}, {city}, {MBCode}, {major}, {year}, {onCmpus})')
    conn.commit()

def update_profile(conn, wemail, fname, lname, country,
            state, city, MBCode, major, year, onCampus): 
    '''Takes user's changed inputs for their profile and updates the
    profile accordingly'''

    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL" # i think i can just get rid of these but idk

    curs.execute(f'UPDATE userAccount SET fname = {fname} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET lname = {lname} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET country = {country} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET state = {state} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET city = {city} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET MBCode = {MBCode} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET major = {major} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET year = {year} \
        WHERE wemail = {wemail}')
    curs.execute(f'UPDATE userAccount SET year = {onCampus} \
        WHERE wemail = {wemail}')

    conn.commit()

def delete_profile(conn, wemail):
    '''Deletes a user profile given their ID'''
    curs = dbi.dict_cursor(conn)
    wemail = f'''"{wemail}"''' if wemail else "NULL"
    user = find_profile(conn, wemail)
    if len(user) != 0:
        curs.execute(f'DELETE FROM userAccount WHERE wemail = {wemail}')


if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
