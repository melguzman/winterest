from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import userInfoQueries

'''**************** Queries for creating match score ****************'''
''' Scoring algorithm is built in this file '''

def matchScore(conn, wemail, wemail2):
    '''Gives a match score between two given users'''
    curs = dbi.dict_cursor(conn)

    if wemail == wemail2:
        return 'Cannot match with self'
    
    curs.execute(f'SELECT major, city, state, country, onCampus, personality, \
                favorites.itemType, favorites.name FROM userAccount INNER \
                JOIN MBResults using (MBCode) INNER JOIN favorites USING \
                (wemail) INNER JOIN loveLanguages using (wemail) \
                WHERE wemail = {wemail}')

    firstInfo = curs.fetchall()

    if len(firstInfo) == 0:
        return 'No possible match here'
    firstPerson = firstInfo[0] # assumes firstInfo is a list of one dictionary

    curs.execute(f'SELECT major, city, state, country, onCampus, personality, \
                FROM userAccount INNER JOIN MBResults using (MBCode) \
                INNER JOIN favorites USING (wemail) INNER JOIN loveLanguages \
                using (wemail) WHERE wemail = {wemail2}')
    
    secondInfo = curs.fetchall()

    if len(secondInfo) == 0:
        return 'No possible match here'
    secondPerson = secondInfo[0] # assumes secondInfo is a list of one dictionary

    score = 0

    # all of these MUST be filled out by the user, otherwise alg breaks
    if secondPerson['major'] == firstPerson['major']:
        score += 1
    if secondPerson['city'] == firstPerson['city']:
        score += 1
    if secondPerson['state'] == firstPerson['state']:
        score += 1
    if secondPerson['country'] == firstPerson['country']:
        score += 1
    if secondPerson['onCampus'] == firstPerson['onCampus']:
        score += 1
    if secondPerson['personality'] == firstPerson['personality']:
        score += 1
    score += matchScore_LL # add in score from love languages
    score += matchScore_favorites # add in score from favorites

    return score

def matchScore_LL(conn, wemail, wemail2):
    # assumes that firstFaves and secondFaves is a list of dictionaries
    # debug accordingly
    firstLLs = userInfoQueries.find_favorites(conn, wemail)
    secondLLs = userInfoQueries.find_favorites(conn, wemail2)

    score = 0
    if not firstLLs or not secondLLs:
        return score
    for langDict in firstLLs:
        language = langDict['language']
        for langDict2 in secondLLs:
            if langDict2['language'] == language:
                score += 1
    return score 

def matchScore_favorites(conn, wemail, wemail2):
    # assumes that firstFaves and secondFaves is a list of dictionaries
    # debug accordingly
    firstFaves = userInfoQueries.find_favorites(conn, wemail)
    secondFaves = userInfoQueries.find_favorites(conn, wemail2)

    score = 0
    if not firstFaves or not secondFaves:
        return score
    for faveDict in firstFaves:
        fave1 = faveDict['name'].lower()
        fave1Type = faveDict['itemType']
        for faveDict2 in secondFaves:
            fave2 = faveDict2['name'].lower()
            fave2Type = faveDict2['itemType']
            if fave1 == fave2 and fave1Type == fave2Type:
                score += 1
    return score  

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)