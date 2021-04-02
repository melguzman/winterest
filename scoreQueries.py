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
    
    curs.execute('''SELECT major, city, state, country, onCampus, 
                favorites.itemType, favorites.name FROM userAccount INNER 
                JOIN favorites USING 
                (wemail) INNER JOIN loveLanguages using (wemail) 
                WHERE wemail = %s''', [wemail])

    firstInfo = curs.fetchall()

    if len(firstInfo) == 0:
        return 'No possible match here'
    firstPerson = firstInfo[0] # assumes firstInfo is a list of one dictionary

    curs.execute('''SELECT major, city, state, country, onCampus 
                FROM userAccount INNER JOIN favorites USING (wemail) INNER JOIN loveLanguages 
                using (wemail) WHERE wemail = %s''', [wemail2])
    
    secondInfo = curs.fetchall()

    if len(secondInfo) == 0:
        return 'No possible match here'
    secondPerson = secondInfo[0] # assumes secondInfo is a list of one dictionary

    score = 0

    #in case information that was not filled in somehow still passes throuh
    
    if secondPerson.get('major', -1) == firstPerson.get('major', -2):
        score += 1
    if secondPerson.get('city', -1) == firstPerson.get('city', -2):
        score += 1
    if secondPerson.get('state', -1) == firstPerson.get('state', -2):
        score += 1
    if secondPerson.get('country', -1) == firstPerson.get('country', -2):
        score += 1
    if secondPerson.get('onCampus', -1) == firstPerson.get('onCampus', -2):
        score += 1

    score += matchScore_LL(conn, wemail, wemail2) # add in score from love languages
    score += matchScore_favorites(conn,wemail,wemail2) # add in score from favorites

    return score

def matchScore_LL(conn, wemail, wemail2):
    # assumes that firstFaves and secondFaves is a list of dictionaries
    firstLLs = userInfoQueries.find_person_LLs(conn, wemail)
    secondLLs = userInfoQueries.find_person_LLs(conn, wemail2)

    score = 0
    if not firstLLs or not secondLLs:
        return score

    #handles case in which users can have more than 1 love language
    for langDict in firstLLs: 
        language = langDict['language']
        for langDict2 in secondLLs: 
            if langDict2['language'] == language:
                score += 1
    return score 

def matchScore_favorites(conn, wemail, wemail2):
    # assumes that firstFaves and secondFaves is a list of dictionaries
    firstFaves = userInfoQueries.find_favorites(conn, wemail)
    secondFaves = userInfoQueries.find_favorites(conn, wemail2)

    score = 0
    if not firstFaves or not secondFaves:
        return score

    #handles case in which users can have more than 1 favorite item
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
    #print(matchScore(conn, 'aEstrada', 'aEstrada'))
    #print(matchScore(conn, 'aEstrada', 'eRamos'))
    #print(matchScore_LL(conn, 'gPortill', 'eRamos'))
    #print(matchScore_favorites(conn, 'mPap', 'eRamos'))
    #curs = dbi.dict_cursor(conn)
