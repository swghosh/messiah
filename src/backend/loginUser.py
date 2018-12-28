from flask_login import current_user, login_user
from app.models import User

@app.route('/login', methods=['GET','POST'])
def login:
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        users = users.query.filter_by(Username=form.Username.data).first()
        if users is None or not users.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(users, remember=form.remember_me.data)
        return redirect(url_for('index')) 
    return render_template('Login.html', title='Login', form=form)
   