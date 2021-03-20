from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
    
def getMatches(conn, userEmail):
    '''Returns a person's matches in a list of dictionaries'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select b.wemail, b.fname, b.lname, b.year
    from userAccountas a inner join matches on (matches.wemail = a.wemail)
    inner join userAccount b on (matches.wemail2 = b.wemail)
    where a.wemail = %s''', [userEmail]) 
    return curs.fetchall()

def insertMatches(conn, userEmail, matchEmail):
    '''Inserts a matching pair'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO matches (wemail, wemail2)
            VALUES (%s, %s)''', [userEmail, matchEmail]) 
    conn.commit()

def getFavorites(conn, userEmail): 
    '''Returns a person's favorites'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select wemail, name, itemType 
    from favorites inner join userAccount using (wemail)
    where userAccount.wemail = %s''', [userEmail]) 
    return curs.fetchall()

def userInfo_forMentorMatching(conn, userEmail):
    '''Collect needed information of user to match for a mentor'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select major, city, state, country, industry, dreamJob \
                  from userAccount inner join professionalInterests using \
                  (wemail) where userAccount.wemail = %s', [userEmail])
    return curs.fetchall()

def getPossibleMentorMatchings(conn, userIndustry, userDreamJob):
    '''Collect all eligible people who the user could meet as a 
    possible mentor. Eligible here means that a person is either 
    in an industry that the user is interested in or has a job that 
    is the dream job of the user'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from userAccount inner join professionalInterests \
    using (wemail) where industry = %s or dreamJob = %s',[userIndustry, userDreamJob]) 
    return curs.fetchall()

def userInfo_forFriendMatching(conn, userEmail): 
    '''Collect needed information of user to match for a friend'''
    curs = dbi.dict_cursor(conn) #notes: favorites and languages are multiple 
    curs.execute('select major, city, state, country, onCampus, industry, dreamJob, \
                  personality, favorites.itemType, favorites.name \
                  from userAccount inner join professionalInterests using (wemail)\
                  inner join MBResults using (MBCode) \
                  inner join favorites using (wemail) \
                  where userAccount.wemail = %s', [userEmail])
    return curs.fetchall()

#later will be changed so meets certains requirements for friend matching as the group sees fit
def getPossibleFriendMatchings(conn, userFavType, userFav):
    '''Collect all people and their traits that a user could meet as a friend'''
    curs = dbi.dict_cursor(conn) 
    curs.execute('select major, city, state, country, onCampus, personality, \
                  favorites.itemType, favorites.name, industry, dreamJob \
                  from userAccount inner join professionalInterests using (wemail) \
                  inner join MBResults using (MBCode) inner join favorites using (wemail) \
                  where favorites.itemType = %s and favorites.name = %s', [userFavType, userFav])
    return curs.fetchall()

def userInfo_forRomanticMatching(conn, userEmail): 
    '''Collect needed information of user to match for a romantic relationship'''
    curs = dbi.dict_cursor(conn)  #notes: favorites and languages are multiple 
    curs.execute('select major, city, state, country, onCampus, industry, dreamJob, \
                personality, favorites.itemType, favorites.name, \
                language from userAccount inner join professionalInterests using (wemail)\
                inner join MBResults using (MBCode) \
                inner join favorites using (wemail) \
                inner join loveLanguages using (wemail) where userAccount.wemail = %s', [userEmail])
    return curs.fetchall()

#later will be changed so meets certains requirements for romantic matching as the group sees fit
def getPossibleRomanceMatchings(conn, userLoveLanguage, userFavType, userFav): 
    '''Collect all people and their traits that a user could meet as a romantic partner'''
    curs = dbi.dict_cursor(conn) 
    curs.execute('select major, city, state, country, onCampus, personality, language, \
                  favorites.itemType, favorites.name from userAccount \
                  inner join MBResults using (MBCode) \
                  inner join favorites using (wemail) inner join loveLanguages using (wemail) \
                  where language = %s and favorites.itemType = %s and favorites.name = %s', [userLoveLanguage, userFavType, userFav])
    return curs.fetchall()
    