from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import random
import userInfoQueries

def getPossibleMentorMatchings(conn, userIndustry, userDreamJob):
    '''Collect all eligible people who the user could meet as a 
    possible mentor. Eligible here means that a person is either 
    in an industry that the user is interested in or has a job that 
    is the dream job of the user'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from userAccount inner join professionalInterests \
    using (wemail) where industry = %s or dreamJob = %s',[userIndustry, userDreamJob]) 
    return curs.fetchall()

#later will be changed so meets certains requirements for friend matching as the group sees fit
def getPossibleFriendMatchings(conn, userFavType, userFav):
    '''Collect all people and their traits that a user could meet as a friend'''
    curs = dbi.dict_cursor(conn) 
    curs.execute('select major, city, state, country, onCampus, personality, \
                  favorites.itemType, favorites.name, industry, dreamJob \
                  from userAccount inner join professionalInterests \
                  using (wemail) inner join MBResults using (MBCode) inner \
                  join favorites using (wemail) where favorites.itemType = %s \
                  and favorites.name = %s', [userFavType, userFav])
    return curs.fetchall()

#later will be changed so meets certains requirements for romantic matching as the group sees fit
def getPossibleRomanceMatchings(conn, userLoveLanguage, userFavType, userFav): 
    '''Collect all people and their traits that a user could meet as a romantic partner'''
    curs = dbi.dict_cursor(conn) 
    curs.execute('select major, city, state, country, onCampus, personality, language, \
                  favorites.itemType, favorites.name from userAccount \
                  inner join MBResults using (MBCode) \
                  inner join favorites using (wemail) inner join loveLanguages using (wemail) \
                  where language = %s and favorites.itemType = %s \
                  and favorites.name = %s', [userLoveLanguage, userFavType, userFav])
    return curs.fetchall()

def getIceBreaker():
    '''Randomly returns an ice breaker'''
    iceBreakers = ["Two Truths and One Lie", 
                    "How are you feeling today?", 
                    "Get the weirdest thing in your room, then bring it back to show".
                    "Highlight of the month?",
                    "Failure of the month?",
                    "Play three rounds of Never Have I Ever",
                    "Virtual wine tasting!",
                    "What’s the last picture that you took?"]
    pick = random.randint(0, len(iceBreaker)-1)
    return iceBreaker[pick]
