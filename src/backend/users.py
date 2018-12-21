import os
import json

DB_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'databaseConfig.json')
with open(DB_CONFIG_PATH) as config:
    DB_CREDS = json.loads(
        config.read()
    )['db']

from mysql import connector
from mysql.connector import Error
from mysql.connector import errorcode

db = connector.connect(**DB_CREDS)

def auto_reconnect(func):
    global db
    if db.is_connected == False:
        db = connector.connect(**DB_CREDS)
    return func

@auto_reconnect
def signup(name,country,username,password,phone_no):
    try:
        sql_query='INSERT INTO users VALUES (%s, %s, %s, %s, %d)'
        data = (name, country, username, password, phone_no)
        # use of data seperately will save from sql injection
        db.cursor().execute(sql_query, data)
        return True
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return False

@auto_reconnect 
def is_valid_user(username, password):
    # use of data seperately will save from sql injection
    sql_query='SELECT Username, Password FROM users where Username = %s'
    cursor = db.cursor()
    cursor.execute(sql_query, (username,))
    for (f1,f2) in cursor:
        if(f2==password):
            return True
    return False

@auto_reconnect
def is_valid_username(username):
    # use of data seperately will save from sql injection
    sql_query='SELECT Username FROM users where Username = %s'
    cursor = db.cursor()
    cursor.execute(sql_query, (username,))
    for (f1,) in cursor:
        if f1 == username:
            return True
    return False

import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'kwocmessiah18'
TRESHOLD = 2 # in days

def generate_access_token(username, password):
    if is_valid_user(username, password):
        web_token = {
            'iat': datetime.utcnow(),
            'aud': username,
            'exp': datetime.utcnow() + timedelta(days = TRESHOLD)
        }
        return jwt.encode(web_token, SECRET_KEY)
    else:
        return None

def is_valid_access_token(token, username):
    if is_valid_username(username):
        web_token = jwt.decode(token, SECRET_KEY, audience = username)
        return True
    else:
        return False
