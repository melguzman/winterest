from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import userInfoQueries
import scoreQueries

def insertScores(conn, wemail):
    '''Inserts initial match scores into every person in the databases's 
    matches table. This should be done as soon as the person's account is 
    created, without the user having to recallibrate their matches manually,
    works given the current user's wemail.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('SELECT wemail from userAccount') # gives every person in database
    allUsers = curs.fetchall() # assuming allUsers is a list of dicts

    # loop through every user and insert into their database
    for user in allUsers:
        emailID = user['wemail']
        if emailID != wemail: # don't do this for the users themselves
            score = scoreQueries.matchScore(conn, emailID, wemail)

            # insert current user wemail to emailID row
            curs.execute(f'INSERT INTO matches_scored (wemail, wemail2, score, \
            isMatched) VALUES ("{wemail}", "{emailID}", "{score}", "no")')

            # insert emailID to current user wemail row
            curs.execute(f'INSERT INTO matches_scored (wemail, wemail2, score, \
            isMatched) VALUES ("{emailID}", "{wemail}", "{score}", "no")')
            

def updateScores(conn, wemail):
    '''Only used if the current user updates their profile,
    works given the current user's wemail. '''
    curs = dbi.dict_cursor(conn)
    curs.execute('SELECT wemail from userAccount') # gives every person in database
    allUsers = curs.fetchall() # assuming allUsers is a list of dicts

    # loop through every user and update their score with current user
    for user in allUsers:
        emailID = user['wemail']
        if emailID != wemail: # don't do this for the users themselves
            score = scoreQueries.matchScore(conn, emailID, wemail)

            # update current user wemail to emailID row
            curs.execute(f'UPDATE matches_scored SET score = "{score}" WHERE wemail \
                 = "{wemail}" and wemail2 = "{emailID}"')

            # update emailID to current user wemail row
            curs.execute(f'UPDATE matches_scored SET score = "{score}" WHERE wemail \
                 = "{emailID}" and wemail2 = "{wemail}"')

def generatePotentialMatches(conn, wemail): 
    '''Generates the matches for the current user given their wemail.
    Sorted by highest matching score to lowest matching score.'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * FROM matches_scored WHERE wemail = "{wemail}" \
        ORDER BY score DESC')
    return curs.fetchall() # returns table of matches

<<<<<<< HEAD
def isMatched(conn, wemail, wemail2):
=======
def generatePotentialInfo(conn, wemail):
    '''Generates the matches and all of their information for the 
    current user given their wemail. Sorted by highest matching score 
    to lowest matching score.'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT userAccount.* FROM matches_scored \
        INNER JOIN userAccount ON (matches_scored.wemail2 = userAccount.wemail) \
        WHERE matches_scored.wemail = "{wemail}" \
        ORDER BY score DESC')
    return curs.fetchall()

def setMatched(conn, wemail, wemail2):
>>>>>>> c96cbdb8676b7b5f79153ce0a9e1d2ebab82d8eb
    '''Takes current user and their matched person's info and updates
    both of their matched status accordingly; wemail is the current user,
    wemail2 is the matched person'''
    curs = dbi.dict_cursor(conn)
        # update matching status for user's row
    curs.execute(f'UPDATE matches_scored SET isMatched = "yes" WHERE wemail \
        = "{wemail}" and wemail2 = "{wemail2}"')

        # update matching status for matched person's row
    curs.execute(f'UPDATE matches_scored SET isMatched = "yes" WHERE wemail \
        = "{wemail2}" and wemail2 = "{wemail}"')
    return curs.fetchall()

def getMatches(conn, wemail):
    '''Returns the information of the people the user has matched with,
    given the user's wemail'''
    curs = dbi.dict_cursor(conn)
<<<<<<< HEAD
    curs.execute(f'''SELECT b.wemail, b.fname, b.lname, b.year
    FROM userAccount as a INNER JOIN matches_scored m ON (m.wemail \
    = a.wemail) INNER JOIN userAccount as b ON (m.wemail2 = b.wemail)
    WHERE m.isMatched = "yes" and m.wemail = {wemail}''') 
=======
    curs.execute(f'SELECT b.wemail, b.fname, b.lname, b.year \
    FROM userAccount as a INNER JOIN matches_scored m ON (m.wemail \
    = a.wemail) INNER JOIN userAccount as b ON (m.wemail2 = b.wemail) \
    WHERE m.isMatched = "yes" and m.wemail = "{wemail}"') 
    return curs.fetchall()
>>>>>>> c96cbdb8676b7b5f79153ce0a9e1d2ebab82d8eb

def matchExists(conn, wemail, wemail2):
    '''Checks if a match exists between two people'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * FROM matches_scores \
    WHERE wemail = "{wemail}" AND wemail2 = "{wemail}" AND isMatched = "yes"') 
    return curs.fetchall()


if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    insertScores(conn, 'aEstrada')
    #curs = dbi.dict_cursor(conn)
