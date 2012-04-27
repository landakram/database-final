import MySQLdb as mysql
from flask import (Flask, g, request, session, render_template, redirect, 
                   url_for, flash)

from functools import wraps

app = Flask(__name__)
app.config.from_object('settings')


# Decorator for view functions. Checks whether there is a user_id in the 
# current session. If not, redirects to login page. If so, runs the view 
# function.
def login_required(f):
    @wraps(f)
    def dec_fn(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return dec_fn

@app.route('/')
def index():
    # user is not logged in
    if not session.get('user_id'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'] 
    password = request.form['password']
    cursor = g.db.cursor()
    cursor.execute('SELECT name FROM User WHERE email = %s AND password = %s',
                   (email, password))
    # if one user was found, then this is that user
    if int(cursor.rowcount) == 1:
        user = cursor.fetchone()
        # fetch uid
        session['user_id'] = user[0]
        flash('You were logged in successfully.', 'success')
        return redirect(url_for('index'))
    # either 0 or more than one (which really shouldn't happen)
    else:
        flash('Your email and password wasn\'t found.', 'error')
        return redirect(url_for('index'))



@app.before_request
def before_request():
    g.db = mysql.connect(host = app.config['DB_HOST'], 
                         db = app.config['DB_NAME'],
                         user = app.config['DB_USER'],
                         passwd = app.config['DB_PASSWORD'])

@app.teardown_request
def teardown_request(exception):
    g.db.close()
