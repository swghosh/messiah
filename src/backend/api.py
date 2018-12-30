#!/usr/bin/python
#-*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, session, redirect, url_for, escape, abort
from flask_cors import CORS, cross_origin
from .db_handler import DBHandler
from .predict import *
import json
import os
import random
import datetime
import pandas as pd
import MySQLdb


CASUALTY_DATA_FILE = "data/random_facts.json"

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = MySQLdb.connect(host="35.200.235.106", user="root", passwd="password77", db="messiah")
cur = db.cursor()

@app.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    """
    Returns the history of disasters for a country/city
    """

    args = ['Country', 'City']
    query = None

    arg = list(request.args.to_dict().keys())[0]

    if arg in args:
        val = request.args.get(arg)
        db_handle = DBHandler()
        query = db_handle.query(arg, val)

    # reducing the length of the response
    if len(query) < 5:
        query = random.sample(query, len(query))
    else:
        query = random.sample(query, 5)

    return jsonify(query)


@app.route('/history_full', methods=['GET'])
@cross_origin()
def get_full_history():
    """
    Returns the history of disasters for a country/city
    """

    args = ['Country', 'City']
    query = None

    arg = list(request.args.to_dict().keys())[0]

    if arg in args:
        val = request.args.get(arg)
        db_handle = DBHandler()
        query = db_handle.query(arg, val)
        
    data=pd.DataFrame(jsonify(query))
    data.columns=['Deaths', 'Date', 'City', 'Country', 'Severity', 'Source', 'Disaster']
    data=data.drop(['City', 'Source'], 1)
    dic = data.to_dict()
    return (dic)


@app.route('/show_random_facts', methods=['GET'])
def show_random_facts():
    #Return a random fact from past years data

    with open(os.path.join(os.path.dirname(__file__), CASUALTY_DATA_FILE)) as f:
        data = json.loads(f.read())

    n = len(data)
    i = random.randint(0, n)
    
    deaths = data[i]['Deaths']
    year = data[i]['Year']
    disaster = data[i]['Type']

    return ("Do you know {deaths} number of people died in {year} from {disaster}?").format(deaths=deaths, year=year, disaster=disaster)


@app.route('/random_facts', methods=['GET'])
@cross_origin()
def get_random_facts():
    """
    Return a random fact from past years data
    """

    with open(os.path.join(os.path.dirname(__file__), CASUALTY_DATA_FILE)) as f:
        data = json.loads(f.read())

    facts = []

    for item in data:
        facts.append([item['Deaths'], item['Year'], item['Type']])

    return jsonify(facts)


@app.route('/predict_eq_mag', methods=['GET'])
def get_eq_mag():
    """
    Predict Earthquake from lattitude, longitude, depth, date
    """

    args = request.args.to_dict()
    lat = args['lat']
    long = args['long']
    depth = args['depth']

    try:
        date = args['date']
    
    except KeyError:
        now = datetime.datetime.now()
        date = '%s/%s/%s' % (now.month, now.day, now.year)



    return str(predict_eq(lat, long, depth, str(date)))

from .users import Users

@app.route('/users/signup', methods=['POST'])
@cross_origin()
def signup():
    try:
        args = request.get_json()
        name = args['name']
        country = args['country']
        username = args['username']
        password = args['password']
        phone = int(args['phone_number'])

        if Users.signup(name, country, username, password, phone):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})

    except:
        return jsonify({'success': False})

@app.route('/')
def index():
    if 'Username' in session:
        username_session = escape(session['Username']).capitalize()
        return render_template('index.html', session_user_name=username_session)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'Username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username_form  = request.form['Username']
        password_form  = request.form['Password']
        cur.execute("SELECT COUNT(1) FROM users WHERE Name = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
        if cur.fetchone()[0]:
            cur.execute("SELECT password FROM users WHERE Name = %s;", [username_form]) # FETCH THE HASHED PASSWORD
            for row in cur.fetchall():
                if password_form.hexdigest() == row[0]:
                    session['Username'] = request.form['Username']
                    return redirect(url_for('index'))
                else:
                    error = "Invalid Credential"
        else:
            error = "Invalid Credential"
    return render_template('Login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('Username', None)
    return redirect(url_for('index'))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)



