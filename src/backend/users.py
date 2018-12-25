import os
from urllib.parse import urlparse

# retreive database credentials
# from environment variable
DATABASE_URL = os.environ['MYSQL_DATABASE_URL']
dbUrl = urlparse(DATABASE_URL)
DB_CREDS = {
    'user': dbUrl.username,
    'password': dbUrl.password,
    'host': dbUrl.hostname,
    'database': dbUrl.path[1:]
}

from mysql import connector
from mysql.connector import Error
from mysql.connector import OperationalError
from mysql.connector import errorcode

import jwt
from datetime import datetime, timedelta

TRESHOLD = 2 # in days

# retreive token secret key
# from environment variable
SECRET_KEY = os.environ['TOKEN_SECRET_KEY']

class DatabaseHandler:
    db = None

    def __init__(self):
        self.connect()
    
    def connect(self):
        try:
            self.db = connector.connect(**DB_CREDS)
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
    
    def query(self, sql, params = None):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, params)
            self.db.commit()
        except (AttributeError, OperationalError):
            self.connect()
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
        return cursor

    def close(self):
        self.db.close()

class Users:
    @staticmethod
    def is_valid_username(username):
        sql_query = 'SELECT Username FROM users where Username = %s'
        db_handle = DatabaseHandler()
        cursor = db_handle.query(sql_query, (username,))
        (val1,) = cursor.fetchone()
        db_handle.close()
        return val1 == username

    @staticmethod
    def is_valid_user(username, password):
        sql_query = 'SELECT Username, Password FROM users WHERE Username = %s'
        db_handle = DatabaseHandler()
        cursor = db_handle.query(sql_query, (username, password))
        (val1, val2) = cursor.fetchone()
        db_handle.close()
        return val2 == password

    @staticmethod
    def signup(name, country, username, password, phone_no):
        sql_query = 'INSERT INTO users (Name, Country, Username, Password, Phone_Number) VALUES (%s, %s, %s, %s, %s)'
        db_handle = DatabaseHandler()
        try:
            db_handle.query(sql_query, (name, country, username, password, phone_no))
        except:
            flag = False
        else:
            flag = True
        finally:
            db_handle.close()
        return flag

    @staticmethod
    def get_user_details(username):
        sql_query = 'SELECT Name, Country, Phone_Number FROM users WHERE username = %s'
        db_handle = DatabaseHandler()
        cursor = db_handle.query(sql_query, (username,))
        (name, country, phone) = cursor.fetchone()
        db_handle.close()
        return {
            'username': username,
            'name': name,
            'country': country,
            'phone_number': phone
        }

    @staticmethod
    def generate_access_token(username, password):
        if Users.is_valid_user(username, password):
            web_token = {
                'iat': datetime.utcnow(),
                'aud': username,
                'exp': datetime.utcnow() + timedelta(days = TRESHOLD)
            }
            return jwt.encode(web_token, SECRET_KEY)
        else:
            return None

    @staticmethod
    def is_valid_access_token(token, username):
        if Users.is_valid_username(username):
            try:
                web_token = jwt.decode(token, SECRET_KEY, audience = username)
            # in case of signature error
            # or in case of audience mismatch error
            # or in case of token expired error
            except:
                return False
            else:
                return True
        else:
            return False
