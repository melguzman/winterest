from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import csv 

def insertDataToTables(conn,csvFile):
    '''Extracts data on fake users and inserts their information to tables
    in database'''
    curs = dbi.dict_cursor(conn)
    fields = [] 
    rows = []
    fieldsDict = {}
    # reading csv file 
    with open(csvFile, 'r') as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
      
        # getting field names from first row 
        fields = next(csvreader) 
        index = 0
        for field in fields:
            #print(field)
            fieldsDict[field] = index
            index += 1

        #insert data into respective tables for a fake user one at a time
        for row in csvreader:
            #insert data into MBResults
            # curs.execute(f'insert into MBResults(MBCode,personality,role) \
            # values("{row[fieldsDict["MBCode"]]}","{row[fieldsDict["personality"]]}",\
            # "{row[fieldsDict["role"]]}")')
            # conn.commit()

            #insert data into userAccount
            curs.execute('''insert into userAccount(wemail,fname,lname,major,year,
                country,state,city,onCampus) values(%s,%s, %s, %s, %s, %s, %s, %s, %s)''', 
                [row[fieldsDict["wemail"]], row[fieldsDict["fname"]], row[fieldsDict["lname"]], 
                row[fieldsDict["major"]], row[fieldsDict["year"]], row[fieldsDict["country"]], 
                row[fieldsDict["state"]], row[fieldsDict["city"]], row[fieldsDict["onCampus"]]])
            conn.commit()

            #insert data into contact
            curs.execute('''insert into contact(wemail,phoneNumber,handle,url,platform) 
                values(%s, %s, %s, %s, %s)''', [row[fieldsDict["wemail"]], 
                row[fieldsDict["phoneNumber"]], row[fieldsDict["handle"]], row[fieldsDict["url"]], 
                row[fieldsDict["platform"]]])
            conn.commit()

            #insert data into professionalInterests
            curs.execute('''insert into professionalInterests(wemail,industry,dreamJob) 
                values(%s,%s,%s)''', [row[fieldsDict["wemail"]], row[fieldsDict["industry"]], 
                row[fieldsDict["dreamJob"]]])
            conn.commit()

            #insert data into favorites
            curs.execute('''insert into favorites(wemail,name,itemType) 
                values(%s, %s, %s)''', [row[fieldsDict["wemail"]], row[fieldsDict["name"]], 
                row[fieldsDict["itemType"]]])
            conn.commit()

            #insert data into loveLanguages
            curs.execute('''insert into loveLanguages(wemail,langNum,language) 
                values(%s, %s, %s)''', [row[fieldsDict["wemail"]], row[fieldsDict["langNum"]], 
                row[fieldsDict["language"]]])
            conn.commit()

            #insert data into picfile
            curs.execute('''insert into picfile(wemail,filename) 
                values(%s, %s)''', [row[fieldsDict["wemail"]], row[fieldsDict["filename"]]])
            conn.commit()



if __name__ == '__main__':
    dbi.cache_cnf()
    csvFile = "users.csv"
    db_to_use = 'wellesleymatch_db' 
    dbi.use(db_to_use)
    conn = dbi.connect()
    insertDataToTables(conn,csvFile)
