import os
import json

DB_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'databaseConfig.json')
with open(DB_CONFIG_PATH) as config:
    DB_CREDS = json.loads(
        config.read()
    )['db']

from mysql import connector
from mysql.connector import Error

db = connector.connect(host = DB_CREDS['host'], user = DB_CREDS['username'],
                       password = DB_CREDS['password'], database = DB_CREDS['database'])

# test only code 
if __name__ == '__main__':
    cursor = db.cursor()
    sql_query = 'SELECT * FROM disasters LIMIT 5'
    cursor.execute(sql_query)
    for row in cursor:
        print(row)

db.close()