from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi

#need to change naming of variables to stay consistent with table
def userInfo_forMentorMatching(conn, userEmail):
    '''Collect needed information of user to match for a mentor'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select major, city, state, country, industry, dreamJob \
                  from userAccount inner join professionalInterests where wemail = %s', [userEmail])
    reurn curs.fetchall()

def getPossibleMenotrMatchings(conn, userIndustry, userDreamJob):
    '''Collect all eligible people who the user could meet as a possible mentor. Eligible here means
        that a person is either in an industry that the user is interested in or has a job that is the
        dream job of the user'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from userAccount inner join professionalInterests using (wemail) \
    where industry = %s or dreamJob = %s',[userIndustry, userDreamJob]) #need to check if sql works
    return curs.fetchall()

#check if you can have so many inner joins
def userInfo_forFriendMatching(conn, userEmail): 
    '''Collect needed information of user to match for a friend'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select major, city, state, country, onCampus, industry, dreamJob, \
                  personality, type.genre, name.genre, type.favorite, name.favorite, \
                  classCode from userAccount inner join professionalInterests using (wemail)\
                  inner join myersBriggs using (wemail) inner join genres using (wemail) \
                  inner join favorites using (wemail) inner join classes using (wemail) \
                  where wemail = %s', [userEmail])
    return curs.fetchall()

#later will be changed so meets certains requirements for friend matching as the group sees fit
def getPossibleFriendMatchings(conn):
    '''Collect all people and their traits that a user could meet as a friend'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select major, city, state, country, onCampus, personality, type.genre, \
                  name.genre, type.favorite, name.favorite, classCode, industry, dreamJob \
                  from userAccount inner join professionalInterests using (wemail) \
                  inner join myersBriggs using (wemail) inner join genres using (wemail) \
                  inner join favorites using (wemail) inner join classes using (wemail)')
    return curs.fetchall()

def userInfo_forRomanticMatching(conn, userEmail): 
    '''Collect needed information of user to match for a romantic relationship'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select major, city, state, country, onCampus, industry, dreamJob, \
                  personality, type.genre, name.genre, type.favorite, name.favorite, \
                  language from userAccount inner join professionalInterests using (wemail)\
                  inner join myersBriggs using (wemail) inner join genres using (wemail) \
                  inner join favorites using (wemail) \
                  inner join loveLanguages using (wemail) where wemail = %s', [userEmail])
    reurn curs.fetchall()

#later will be changed so meets certains requirements for romantic matching as the group sees fit
def getPossibleRomanceMatchings(conn):
    '''Collect all people and their traits that a user could meet as a romantic partner'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select major, city, state, country, onCampus, personality, language, \
                  type.genre, name.genre, type.favorite, name.favorite from userAccount \
                  inner join myersBriggs using (wemail) inner join genres using (wemail) \
                  inner join favorites using (wemail) inner join loveLanguages using (wemail)')
    return curs.fetchall()