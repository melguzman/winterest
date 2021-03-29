from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
from threading import Lock # threading & locking

app = Flask(__name__)

import cs304dbi as dbi
import userInfoQueries
import scoreQueries
import userInfoQueries
import profileQueries

'''Global Variables'''
lock = Lock()

def insertScores(conn, wemail):
    '''Inserts initial match scores into every person in the databases's 
    matches table. This should be done as soon as the person's account is 
    created, without the user having to recallibrate their matches manually,
    works given the current user's wemail.'''
    curs = dbi.dict_cursor(conn)
    lock.acquire() # lock the system as we insert the user's scores
    if profileQueries.find_scores(conn, wemail):
        # in the case the user is already in the db and has scores, we do not need
        # to do this
        lock.release()
        return False

    curs.execute('SELECT wemail from userAccount') # gives every person in database
    allUsers = curs.fetchall() # assuming allUsers is a list of dicts

    # loop through every user and insert into their database
    for user in allUsers:
        #print(user)
        emailID = user['wemail']
        if emailID != wemail: # don't do this for the users themselves
            score = scoreQueries.matchScore(conn, emailID, wemail)

            # insert current user wemail to emailID row
            curs.execute('''INSERT INTO matches_scored (wemail, wemail2, score, 
            isMatched) VALUES (%s, %s, %s, "no")''', [wemail, emailID, score])

            # insert emailID to current user wemail row
            curs.execute('''INSERT INTO matches_scored (wemail, wemail2, score, 
            isMatched) VALUES (%s, %s, %s, "no")''', [emailID, wemail, score])
    lock.release()
    conn.commit()
    return "User's initial scores have been added to the database"

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
            curs.execute('''UPDATE matches_scored SET score = %s WHERE wemail 
                 = %s and wemail2 = %s''', [score, wemail, emailID])

            # update emailID to current user wemail row
            curs.execute('''UPDATE matches_scored SET score = %s WHERE wemail 
                 = %s and wemail2 = %s''', [score, emailID, wemail])

    conn.commit()

def generatePotentialMatches(conn, wemail): 
    '''Generates the matches for the current user given their wemail.
    Sorted by highest matching score to lowest matching score.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM matches_scored WHERE wemail = %s
        ORDER BY score DESC''', [wemail])
    return curs.fetchall() # returns table of matches

def generatePotentialInfo(conn, wemail):
    '''Generates the matches and all of their information for the 
    current user given their wemail. Sorted by highest matching score 
    to lowest matching score.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT userAccount.* FROM matches_scored 
        INNER JOIN userAccount ON (matches_scored.wemail2 = userAccount.wemail) 
        WHERE matches_scored.wemail = %s
        ORDER BY score DESC''', [wemail])
    return curs.fetchall()

def setMatched(conn, wemail, wemail2):
    '''Takes current user and their matched person's info and updates
    both of their matched status accordingly; wemail is the current user,
    wemail2 is the matched person'''
    curs = dbi.dict_cursor(conn)
        # update matching status for user's row
    curs.execute('''UPDATE matches_scored SET isMatched = "yes" WHERE wemail 
        = %s and wemail2 = %s''', [wemail, wemail2])

        # update matching status for matched person's row
    curs.execute('''UPDATE matches_scored SET isMatched = "yes" WHERE wemail 
        = %s and wemail2 = %s''', [wemail2, wemail])
    conn.commit()

def unMatch(conn, wemail, wemail2):
    '''Takes current user and their old matched person's info and updates
    both of their matched status to NO; wemail is the current user,
    wemail2 is the matched person'''
    curs = dbi.dict_cursor(conn)
        # update matching status for user's row
    curs.execute('''UPDATE matches_scored SET isMatched = "no" WHERE wemail 
        = %s and wemail2 = %s''', [wemail, wemail2])

        # update matching status for old matched person's row
    curs.execute('''UPDATE matches_scored SET isMatched = "no" WHERE wemail 
        = %s and wemail2 = %s''', [wemail2, wemail])
    conn.commit()

# def getMatches(conn, wemail):
#     '''Returns the information of the people the user has matched with,
#     given the user's wemail'''
#     curs = dbi.dict_cursor(conn)
#     curs.execute('''SELECT b.wemail, b.fname, b.lname, b.year 
#     FROM userAccount as a INNER JOIN matches_scored m ON (m.wemail 
#     = a.wemail) INNER JOIN userAccount as b ON (m.wemail2 = b.wemail) 
#     WHERE m.isMatched = "yes" and m.wemail = %s''', [wemail]) 
#     return curs.fetchall()
def getMatches(conn, userEmail): 
    '''Gets all of the user's matches only under a two sided match'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT wemail, fname, lname, year FROM userAccount 
        WHERE wemail <> %s''', [userEmail])
    people = curs.fetchall()
    
    twoSidedMatching = []
    for person in people: 
        userSideMatching = matchExists(conn, userEmail, person['wemail'])
        personSideMatching = matchExists(conn, person['wemail'], userEmail)
        if (len(userSideMatching) > 0) and (len(personSideMatching) > 0):
            twoSidedMatching.append(person)
    return twoSidedMatching

def getOneSidedMatches(conn, userEmail): 
    '''Returns the information of all the people that clicked match with 
    the user but the user had not clicked matched with yet (one sided match)'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select wemail, fname, lname, year from userAccount 
        where wemail in (select wemail from matches_scored where 
        wemail2 = %s and isMatched = 'yes')''', [userEmail])
    possibleOneSided = curs.fetchall()
    #print('possibleOneSided')
    #print(possibleOneSided)
    twoSidedMatches = getMatches(conn, userEmail) 
    #print('twoSidedMatches')
    #print(twoSidedMatches)
    oneSidedMatches = []
    
    #print(len(twoSidedMatches))
    #if there are two sided matches, check that oneSidedMatches does not exist in that set
    if len(twoSidedMatches) > 0: 
        for oneSDMatch in possibleOneSided: #maybe better way, but works well
            for twoSDMatch in twoSidedMatches:
                if oneSDMatch != twoSDMatch:
                    oneSidedMatches.append(oneSDMatch) #extract and return only one sided matches
    else: #no two sided matches
        return possibleOneSided #could be 0 or more

    return oneSidedMatches #could be 0 or more

def setOneSDMatch(conn, wemail, wemail2): #one sided
    '''Takes current user and their matched person's info and updates
    only user's matched status; wemail is the current user,
    wemail2 is the matched person'''
    curs = dbi.dict_cursor(conn)
        # update matching status for user's row
    curs.execute('''UPDATE matches_scored SET isMatched = "yes" WHERE wemail 
        = %s and wemail2 = %s''', [wemail, wemail2])
    conn.commit()

def matchExists(conn, wemail, wemail2):
    '''Checks if a match exists between two people'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM matches_scored 
    WHERE (wemail = %s  AND wemail2 = %s) AND isMatched = "yes"''', [wemail, wemail2]) 
    return curs.fetchall()

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    #insertScores(conn, 'aEstrada')
    #updateScores(conn, 'aEstrada')
    #print(generatePotentialMatches(conn, 'aEstrada'))
    #print(generatePotentialInfo(conn, 'aEstrada'))
    #setMatched(conn, 'aEstrada', 'gPortill')
    #setMatched(conn, 'aEstrada', 'eRamos')
    #print(matchExists(conn, 'aEstrada', 'eRamos'))
    #print(getMatches(conn, 'mguzman2'))
    #curs = dbi.dict_cursor(conn)
