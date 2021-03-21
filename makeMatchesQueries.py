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
    created, without the user having to recallibrate their matches manually.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('SELECT wemail from userAccount') # gives every person in database
    allUsers = curs.fetchall() # assuming allUsers is a list of dicts

    # loop through every user and insert into their database
    for user in allUsers:
        emailID = user['wemail']
        if emailID != wemail: # don't do this for the users themselves
            score = scoreQueries.matchScore(conn, emailID, wemail)

            # insert current user wemail to emailID row
            curs.execute(f'INSERT INTO matches_scored (wemail, wemail2, score) \
            VALUES ({wemail}, {emailID}, {score})')

            # insert emailID to current user wemail row
            curs.execute(f'INSERT INTO matches_scored (wemail, wemail2, score) \
            VALUES ({emailID}, {wemail}, {score})')
            

def updateScores(conn, wemail):
    '''Only used if the user updates their profile. '''
    curs = dbi.dict_cursor(conn)
    curs.execute('SELECT wemail from userAccount') # gives every person in database
    allUsers = curs.fetchall() # assuming allUsers is a list of dicts

    # loop through every user and update their score with current user
    for user in allUsers:
        emailID = user['wemail']
        if emailID != wemail: # don't do this for the users themselves
            score = scoreQueries.matchScore(conn, emailID, wemail)

            # update current user wemail to emailID row
            curs.execute(f'UPDATE matches_scored SET score = {score} WHERE wemail \
                 = {wemail} and wemail2 = {emailID}')

            # update emailID to current user wemail row
            curs.execute(f'UPDATE matches_scored SET score = {score} WHERE wemail \
                 = {emailID} and wemail2 = {wemail}')

def generateMatches(conn, wemail):
    '''Generates the matches for the current user given their wemail.
    Sorted by highest matching score to lowest matching score.'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT * FROM matches_scored WHERE wemail = {wemail} \
        ORDER BY score DESC')
    return curs.fetchall() # returns table of matches

def generateMatchesInfo(conn, wemail):
    '''Generates the matches for the current user given their wemail.
    Sorted by highest matching score to lowest matching score.'''
    curs = dbi.dict_cursor(conn)
    curs.execute(f'SELECT userAccount.* FROM matches_scored 
        INNER JOIN userAccount ON (matches_scored.wemail2 = userAccount.wemail) 
        WHERE matches_scored.wemail = {wemail} \
        ORDER BY score DESC')
    return curs.fetchall()

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)