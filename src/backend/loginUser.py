from flask import Flask, session, redirect, url_for, escape, request, render_template
import MySQLdb

app = Flask(__name__)

db = MySQLdb.connect(host="35.200.235.106", user="root", passwd="password77", db="messiah")
cur = db.cursor()

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

