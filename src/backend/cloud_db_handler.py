import os
import json
from mysql.connector import errorcode

DB_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'databaseConfig.json')
print(DB_CONFIG_PATH)
with open(DB_CONFIG_PATH) as config:
    DB_CREDS = json.loads(
        config.read()
    )['db']
print(DB_CREDS)

from mysql import connector
from mysql.connector import Error

db = connector.connect(**DB_CREDS)

def signup(name,country,username,password,phone_no):
    try:
        sql_query='INSERT INTO users VALUES ("%s", "%s", "%s", "%s", %d)' % (name, country, username, password, phone_no)
        db.cursor().execute(sql_query)
        return True
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return False



    
def login(username, password):
    sql_query='SELECT Username, Password FROM users where Username = +"' + username + '"'
    cursor=db.cursor()
    cursor.execute(sql_query)
    for (f1,f2) in cursor:
        print(f1, f2)
        if(f2==password):
            return True
    return False


# test only code
if __name__ == '__main__':
    cursor = db.cursor()
    sql_query = 'SELECT * FROM disasters LIMIT 5'
    cursor.execute(sql_query)
    for row in cursor:
        print(row)
