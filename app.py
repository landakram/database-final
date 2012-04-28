import MySQLdb as mysql
from flask import (Flask, g, request, session, render_template, redirect, 
                   url_for, flash)
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

app = Flask(__name__)
app.config.from_object('settings')
app.config['DEBUG'] = True


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
    cursor.execute('SELECT uid, name, password FROM User WHERE email = %s',
                   (email, ))
    # if one user was found, then this is that user
    if int(cursor.rowcount) == 1:
        user = cursor.fetchone()
        # we check the password against the hash stored in the db
        if check_password_hash(user[2], password):
            # fetch uid
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash('You were logged in successfully.', 'success')
            return redirect(url_for('index'))
    # either 0 or more than one (which really shouldn't happen)
    flash('Your email and password wasn\'t found.', 'error')
    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user_type = request.form['type'].lower()
    cursor = g.db.cursor()
    # first check if user with email address already exists
    cursor.execute('SELECT * FROM User WHERE email = %s', (email,))
    # if any user was found, then cannot register with that email
    if int(cursor.rowcount) != 0:
        flash('That email address is already taken.', 'error')
        return redirect(url_for('index'))

    uid = 0

    print user_type
    if user_type == 'athlete':
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        cursor.execute('INSERT INTO User(name, email, password) VALUES(%s, %s, %s)', 
                    (name, email, generate_password_hash(password)))
        uid = cursor.lastrowid
        cursor.execute('INSERT INTO Athlete VALUES(%s, %s, %s)',
                    (uid, height, weight))
        print "HELLOOO"
    elif user_type == 'coach':
        salary = float(request.form['salary'])

        cursor.execute('INSERT INTO User(name, email, password) VALUES(%s, %s, %s)', 
                    (name, email, generate_password_hash(password)))
        uid = cursor.lastrowid
        cursor.execute('INSERT INTO Coach VALUES(%s, %s)', (uid, salary))
    g.db.commit()

    session['user_id'] = uid
    session['user_name'] = name
    flash('You were successfully registered and logged in.', 'success')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    try:
        session.pop('user_id')
        session.pop('user_name')
    except KeyError:
        pass
    finally:
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


if __name__ == '__main__':
    app.run()

