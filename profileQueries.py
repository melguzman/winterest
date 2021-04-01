from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
from threading import Lock # threading & locking
app = Flask(__name__)
import cs304dbi as dbi 

'''**************** Queries for getting info ****************'''

def find_meeting(conn, meetingID):
    '''Returns the meeting info associated with a given meetingID'''
    curs = dbi.dict_cursor(conn)
    curs.execute('SELECT * FROM meeting WHERE meetingID = %s', 
    [meetingID])
    return curs.fetchone()

def find_all_meetings(conn, wemail):
    '''Returns all meetings associated with a given wemail'''
    curs = dbi.dict_cursor(conn)
    curs.execute('SELECT * FROM meeting WHERE wemail = %s or wemail2 = %s', 
    [wemail, wemail])
    return curs.fetchall()

def find_profile(conn, wemail):
    '''Returns the info associated with a given wemail'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM userAccount WHERE wemail =
         %s''', [wemail])
    person = curs.fetchone()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the demographics
    if len(person) != 0:
        return person
    return "No user by that name yet"

def find_profile_v2(conn, wemail):
    '''Returns the info associated with a given wemail'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM userAccount WHERE wemail =
         %s''', [wemail])
    person = curs.fetchone()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the demographics
    if person != None:
        return person
    return None

def find_person(conn, name):
    '''Gives all the people who match part of a given name'''
    curs = dbi.dict_cursor(conn)
    name = name.split()
    if len(name) == 1: #just first name provided
        curs.execute('''select fname, wemail, year from userAccount
            where fname like %s''', ['%' + name[0] + '%']) 
    else:
        curs.execute('''select fname, lname, wemail, year from userAccount
            where fname like %s and lname like %s''', ['%' + name[0] + '%', '%' + name[-1] + '%']) 
    return curs.fetchall()

def find_dem(conn, wemail):
    '''Returns a user's demographic information; singular row returned'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT country, state, city FROM userAccount 
            WHERE wemail = %s''', [wemail])
    demographics = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the demographics
    if len(demographics) != 0:
        return demographics
    return "No demographics input yet"

def find_phoneNum(conn, wemail):
    '''Returns a user's phone number'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT phoneNumber FROM contact WHERE 
        wemail = %s''', [wemail])
    return curs.fetchall()

def find_contacts(conn, wemail):
    '''Returns user's available contact information as a
    list of dictionaries'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM contact WHERE
        wemail = %s''', [wemail])
    return curs.fetchall()

'''**************** Queries for changing tables ****************'''

############ INSERT, UPDATE User Profile

def insert_profile(conn, wemail, fname, lname, country,
            state, city, major, year, onCampus): #got rid of password and MBCode
    '''Takes new user's initial inputs and adds them into the table'''
    # assumption: user MUST input all categories 
    curs = dbi.dict_cursor(conn)
    #lock = Lock()
    #lock.acquire()
    curs.execute('''lock tables userAccount read''')
    curs.execute('''SELECT * FROM userAccount WHERE wemail = %s''', [wemail])
    checkUser = curs.fetchall()
    curs.execute('''unlock tables''')
    # if account for this user doesn't already exist, we will add them to
    # the userAccounts table
    if len(checkUser) == 0: 
        curs.execute('''lock tables userAccount write''')
        curs.execute('''INSERT INTO userAccount (wemail, fname, lname, country, 
            state, city, major, year, onCampus) VALUES (%s, %s, %s, %s, 
            %s, %s, %s, %s, %s)''', 
            [wemail, fname, lname, country, state, city, major, year, onCampus])
        curs.execute('''unlock tables''')
    conn.commit()
    #lock.release()

def update_profile(conn, wemail, fname, lname, country,
            state, city, major, year, onCampus): #got rid of password
    '''Takes user's changed inputs for their profile and updates the
    profile accordingly'''

    curs = dbi.dict_cursor(conn)
    #lock = Lock()
    #lock.acquire()
    curs.execute('''lock tables userAccount write''')
    #curs.execute('''UPDATE userAccount SET password = %s 
         #WHERE wemail = %s''', [password, wemail]) 
    curs.execute('''UPDATE userAccount SET fname = %s 
        WHERE wemail = %s''', [fname, wemail])
    curs.execute('''UPDATE userAccount SET lname = %s
        WHERE wemail = %s''', [lname, wemail])
    curs.execute('''UPDATE userAccount SET country = %s
        WHERE wemail = %s''', [country, wemail])
    curs.execute('''UPDATE userAccount SET state = %s
        WHERE wemail = %s''', [state, wemail])
    curs.execute('''UPDATE userAccount SET city = %s
        WHERE wemail = %s''', [city, wemail])
    #curs.execute('''UPDATE userAccount SET MBCode = %s
        #WHERE wemail = %s''', [MBCode, wemail])
    curs.execute('''UPDATE userAccount SET major = %s
        WHERE wemail = %s''', [major, wemail])
    curs.execute('''UPDATE userAccount SET year = %s
        WHERE wemail = %s''', [year, wemail])
    curs.execute('''UPDATE userAccount SET onCampus = %s
        WHERE wemail = %s''', [onCampus, wemail])
    curs.execute('''unlock tables''')

    conn.commit()
    #lock.release()

def delete_profile(conn, wemail):
    '''Deletes a user profile given their ID'''
    curs = dbi.dict_cursor(conn)
    user = find_profile(conn, wemail)
    if len(user) != 0:
        curs.execute('''lock tables userAccount write''')
        curs.execute('''DELETE FROM userAccount WHERE wemail = %s''', [wemail])
        curs.execute('''unlock tables''')

    conn.commit()

############ INSERT, UPDATE User Profile

def insert_contact(conn, wemail, phoneNumber, handle, url, platform):
    '''Takes new user's contact information (phone number and info
    about most used social medial platform) so others can reach out
    Note: users can only insert one row of their contact information''' 

    curs = dbi.dict_cursor(conn)
    # curs.execute('''lock tables contact read''')
    # curs.execute('''SELECT * FROM contact WHERE wemail = %s''', [wemail])
    # checkContact = curs.fetchall()
    # curs.execute('''unlock tables''')
    # if contact for this user doesn't already exist, we will add their info to
    # the contact table
    # if len(checkContact) == 0: 
    curs.execute('''lock tables contact write''')
    curs.execute('''INSERT INTO contact (wemail, phoneNumber, 
            handle, url, platform) VALUES (%s, %s, %s, %s, %s)''', 
            [wemail, phoneNumber, handle, url, platform])
    curs.execute('''unlock tables''')
    conn.commit()

def update_contact(conn, wemail, phoneNumber, handle, url, platform): 
    '''Takes user's changed inputs for their contacts and updates the
    profile accordingly'''

    curs = dbi.dict_cursor(conn)

    curs.execute('''lock tables contact write''')
    curs.execute('''UPDATE contact SET phoneNumber = %s
        WHERE wemail = %s''', [phoneNumber, wemail])
    curs.execute('''UPDATE contact SET handle = %s
        WHERE wemail = %s''', [handle, wemail])
    curs.execute('''UPDATE contact SET url = %s
        WHERE wemail = %s''', [url, wemail])
    curs.execute('''UPDATE contact SET platform = %s
        WHERE wemail = %s''', [platform, wemail])
    curs.execute('''unlock tables''')

    conn.commit()

def update_social(conn, wemail, url, platform): 
    '''Takes user's changed inputs for their contacts and updates the
    profile accordingly'''

    curs = dbi.dict_cursor(conn)

    curs.execute('''lock tables contact write''')
    curs.execute('''UPDATE contact SET url = %s
        WHERE wemail = %s and platform = %s''', [url, wemail, platform])
    curs.execute('''unlock tables''')

    conn.commit()

def update_phone(conn, wemail, phoneNumber): 
    '''Takes user's changed inputs for their contacts and updates the
    profile accordingly'''

    curs = dbi.dict_cursor(conn)

    curs.execute('''lock tables contact write''')
    curs.execute('''UPDATE contact SET phoneNumber = %s
        WHERE wemail = %s''', [phoneNumber, wemail])
    curs.execute('''unlock tables''')

    conn.commit()



def delete_contact(conn, wemail):
    '''Deletes a user's contact information given their wemail'''
    curs = dbi.dict_cursor(conn)
    phone = find_phoneNum(conn, wemail)
    if len(phone) != 0:
        curs.execute('''lock tables contact write''')
        curs.execute('''DELETE FROM contact WHERE wemail = %s''', [wemail])
        curs.execute('''unlock tables''')
    conn.commit()

############ INSERT, DELETE Meetings
def insert_meeting(conn, wemail, wemail2, what, type,
            location, time, date, notes): #got rid of password and MBCode
    '''Creates a meeting using info'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''lock tables meeting write''')
    curs.execute('''INSERT INTO meeting (meetingID, wemail, wemail2, what, 
        type, location, time, date, notes) VALUES (null, %s, %s, %s, %s, 
        %s, %s, %s, %s)''', 
        [wemail, wemail2, what, type, location, time, date, notes])
    curs.execute('''unlock tables''')
    conn.commit()

def delete_meeting(conn, meetingID):
    '''Deletes a meeting given the meetingID'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''lock tables meeting write''')
    curs.execute('''DELETE FROM meeting WHERE meetingID = %s''', [meetingID])
    curs.execute('''unlock tables''')
    conn.commit()

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    #print(find_profile(conn, 'aEstrada'))
    #print(find_dem(conn, 'aEstrada'))
    #print(find_phoneNum(conn, 'aEstrada'))
    #insert_profile(conn, 'mTuzman', 'Melisa', 'Tuzman', 'USA',
            #'CA', 'Bellflower', 'Data Science', 2020, 'no')
    #update_profile(conn, 'mTuzman', 'Melisa', 'Tuzman', 'USA',
            #'CA', 'Los Angeles', 'Data Science', 2020, 'no')
    #delete_profile(conn, 'mTuzman')
    #insert_contact(conn, 'mTuzman', 703, 'somehandle11', 'someurlq', 'facebook')
    #update_contact(conn, 'mTuzman', 703, 'somehandle11', 'someurlq', 'instagram')
    #delete_contact(conn, 'mTuzman')
    
