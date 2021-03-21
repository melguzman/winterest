from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import csv 

def insertDataToTables(conn,filename):
    '''Extracts data on fake users and inserts their information to tables
    in database'''
    curs = dbi.dict_cursor(conn)
    fields = [] 
    rows = []
    fieldsDict = {}
    # reading csv file 
    with open(filename, 'r') as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
      
        # getting field names from first row 
        fields = next(csvreader) 
        index = 0
        for field in fields:
            fieldsDict[field] = index
            index += 1

        #insert data into respective tables for a fake user one at a time
        for row in csvreader:
            #insert data into MBResults
            curs.execute(f'insert into MBResults(MBCode,personality,role) \
            values({row[fieldsDict["MBCode"]]},{row[fieldsDict["personality"]]},\
            {row[fieldsDict["role"]]})')
            conn.commit()

            #insert data into userAccount
            curs.execute(f'insert into userAccount(wemail,password,fname,lname,major,year,\
            country,state,city,onCampus,MBCode) values({row[fieldsDict["wemail"]]},\
            {row[fieldsDict["password"]]},{row[fieldsDict["fname"]]},\
            {row[fieldsDict["lname"]]},{row[fieldsDict["major"]]}, {row[fieldsDict["year"]]},\
            {row[fieldsDict["country"]]},{row[fieldsDict["state"]]}, {row[fieldsDict["city"]]},\
            {row[fieldsDict["onCampus"]]},{row[fieldsDict["MBCode"]]})')
            conn.commit()

            #insert data into contact
            curs.execute(f'insert into contact(wemail,phoneNumber,handle,url,platform) \
            values({row[fieldsDict["wemail"]]},{row[fieldsDict["phoneNumber"]]},\
            {row[fieldsDict["handle"]]}, {row[fieldsDict["url"]]}, \
            {row[fieldsDict["platform"]]})')
            conn.commit()

            #insert data into professionalInterests
            curs.execute(f'insert into professionalInterests(wemail,industry,dreamJob) \
            values({row[fieldsDict["wemail"]]},{row[fieldsDict["industry"]]},\
            {row[fieldsDict["dreamJob"]]})')
            conn.commit()

            #insert data into favorites
            curs.execute(f'insert into favorites(wemail,name,itemType) \
            values({row[fieldsDict["wemail"]]},{row[fieldsDict["name"]]},\
            {row[fieldsDict["itemType"]]})')
            conn.commit()

            #insert data into loveLanguages
            curs.execute(f'insert into loveLanguages(wemail,langNum,language) \
            values({row[fieldsDict["wemail"]]},{row[fieldsDict["langNum"]]},\
            {row[fieldsDict["language"]]})')
            conn.commit()

            #insert data into bio
            curs.execute(f'insert into bio(wemail,bioID,bio) \
            values({row[fieldsDict["wemail"]]},{row[fieldsDict["bioID"]]},\
            {row[fieldsDict["bio"]]})')
            conn.commit()


def getIceBreaker():
    '''Randomly returns an ice breaker'''
    iceBreakers = ["Two Truths and One Lie", 
                    "How are you feeling today?", 
                    "Get the weirdest thing in your room, then bring it back to show",
                    "Highlight of the month?",
                    "Failure of the month?",
                    "Play three rounds of Never Have I Ever",
                    "Virtual wine tasting!",
                    "What’s the last picture that you took?",
                    "If you inherited or won a million dollars, what’s\
          the very first thing you would do with the money?"]
    pick = random.randint(0, len(iceBreaker)-1)
    return iceBreaker[pick]