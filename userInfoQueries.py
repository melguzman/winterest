from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
from threading import Lock # threading & locking
app = Flask(__name__)

import cs304dbi as dbi
import scoreQueries

'''**************** Queries for getting info ****************'''

def find_profInt(conn, wemail):
    '''Returns a user's professional interest information; singular
    row returned'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM professionalInterests
        WHERE wemail = %s''', [wemail])
    profInt = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the professional interests
    if len(profInt) != 0:
        return profInt
    return "No professional interests input yet"

def find_photo(conn, wemail):
    '''Returns the user's image; singular
    row returned'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM picfile
        WHERE wemail = %s''', [wemail])
    return curs.fetchone()

def find_favorites(conn, wemail):
    '''Returns a user's favorites things and their respective genres; will be 
    multiple rows'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM favorites
        WHERE wemail = %s''', [wemail])
    return curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns their favorite things and the respective genres
    

def find_person_LLs(conn, wemail):
    '''Returns all of user's love languages; 3 rows returned'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM loveLanguages 
        WHERE wemail = %s''', [wemail])
    LLInt = curs.fetchall()
    # returns a string in the case where the person has not filled info out
    # otherwise, returns the love languages
    if len(LLInt) != 0:
        return LLInt

# def find_MB_info(conn, MBCode):
#     '''Takes a user's MBCode and uses it to generate their personality
#     information and role in society as per the Myers-Briggs test.'''
#     curs = dbi.dict_cursor(conn)
#     curs.execute(f'SELECT personality, role FROM MBResults WHERE \
#                 MBResults.MBCode = "{MBCode}"')
#     MBVals = curs.fetchall()
#     if len(MBVals) != 0:
#         return MBVals
#     return "No MB code input yet"

def getBio(conn, userEmail):
    '''Returns a user's bio'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT bio FROM bio WHERE wemail = %s''', [userEmail]) 
    return curs.fetchone()



'''**************** Queries for changing tables ****************'''

############ INSERT, UPDATE Professional Interests

def insert_professionalInterests(conn, wemail, industry, dreamJob):
    '''Takes user's initial inputs for their professional interests and
    inserts them into the table. Can have one input per professional interest
    column.'''

    # assumption: user MUST have an input for ALL categories 
    curs = dbi.dict_cursor(conn)

    curs.execute('''SELECT wemail FROM professionalInterests WHERE 
        wemail = %s''', [wemail])
    checkInt = curs.fetchall()
    # if list of professional interests by said wemail doesn't exist,
    # we will insert a new row into the table for this person
    if len(checkInt) == 0: 
        curs.execute('''INSERT INTO professionalInterests (wemail, 
            industry, dreamJob) VALUES (%s, %s, %s)''', 
            [wemail, industry, dreamJob])
        conn.commit()

def update_professionalInterests(conn, wemail, industry, dreamJob):
    '''Takes user's changed inputs for their professional interests and
    updates them.'''

    curs = dbi.dict_cursor(conn)
    curs.execute('''UPDATE professionalInterests SET industry = %s
                WHERE wemail = %s''', [industry, wemail]) 
    curs.execute('''UPDATE professionalInterests SET dreamJob = %s
        WHERE wemail = %s''', [dreamJob, wemail]) 
    conn.commit()

############ INSERT, UPDATE Favorite and Genres

def insert_favorites(conn, wemail, name, itemType):
    '''Takes user's inputs for their favorite things and their respective 
    genres.'''

    # assumption: user MUST have a favorite of each genre listed 
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO favorites (wemail, name, itemType) 
        VALUES (%s, %s, %s)''', [wemail, name, itemType])
    conn.commit()

def update_favorites(conn, wemail, name, itemType):
    '''Takes user's changed inputs for their favorite genres and
    updates them. Assumes 1 to 1 ratio between itemType and favorite
    thing'''

    # update favorite and genres info 
    curs = dbi.dict_cursor(conn)
    curs.execute('''UPDATE favorites SET name = %s
        WHERE itemType = %s and wemail = %s''', [name, itemType, wemail]) 
    curs.execute('''UPDATE favorites SET itemType = %s
        WHERE name = %s and wemail = %s''', [itemType, name, wemail]) 
    conn.commit()
    

############ INSERT, UPDATE Love languages

def insert_top3_LL(conn, wemail, language, langNum):
    '''Takes user's inputs for a love language and inserts it into the
    table. We assume that the user inputs their top 3 languages (all of
    equal weight). Only occurs if the user is filling these out for 
    the first time. Must be called thrice, once for each language.'''

    # assumption: user MUST have 3 LLs
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO loveLanguages (wemail, language, langNum) 
        VALUES (%s, %s, %s)''', [wemail, language, langNum])
    conn.commit()

def update_top3_lang(conn, wemail, language, langNum):
    '''Takes user's changed inputs for one of their love languages. Updates
    with new top 3 languages for user. Can be called thrice every time a user
    makes an update, essentially updating all three languages even if any of
    them remain the same for simplicity's sake'''

    # update love languages info 
    curs = dbi.dict_cursor(conn)
    curs.execute('''UPDATE loveLanguages SET language = %s
        WHERE wemail = %s and langNum = %s''', [language, wemail, langNum])
    curs.execute('''commit''')
    conn.commit()


############ INSERT Myers-Briggs test results

# def insert_Myers_Briggs_table(conn,MBCode): #needs to be used first
#     '''Takes inputs from user's Myers-Briggs test results.
#     Inserts the user's code from the test results into the database.'''

#     curs = dbi.dict_cursor(conn)
#     curs.execute(f'INSERT INTO MBResults (MBCode) \
#         VALUES ("{MBCode}")')
#     conn.commit()


# def insert_Myers_Briggs(conn, wemail, MBCode): #then use function second
#     '''Takes inputs from user based off of their Myers-Briggs test results.
#     Inserts the user's code from the test results into the database.'''

#     curs = dbi.dict_cursor(conn)
#     curs.execute(f'UPDATE userAccount SET MBCode = "{MBCode}" \
#         where wemail = "{wemail}"')
#     conn.commit()


if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('wellesleymatch_db')
    conn = dbi.connect()
    #print(find_profInt(conn, 'aEstrada'))
    #print(find_person_LLs(conn, 'gPortillo'))
    #print(find_MB_info(conn, 2)) #aEstrada
    #print(getBio(conn, 'mPap'))
    #insert_professionalInterests(conn, 'cat', 'Government', 'International Affairs')
    #update_professionalInterests(conn, 'cat', 'Education', 'Teacher')
    #insert_favorites(conn, 'aEstrada', 'Malo', 'album')
    #update_favorites(conn, 'aEstrada', 'Azteca', 'album')
    #insert_top3_LL(conn, 'mPap', 'service', '2')
    #update_top3_lang(conn, 'mPap', 'affirmation', '1')

    #insert_Myers_Briggs_table(conn,'1')
    #insert_Myers_Briggs(conn, 'mTuzman', '1')
    #curs = dbi.dict_cursor(conn)
