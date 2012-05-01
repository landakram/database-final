import MySQLdb as mysql
from flask import (Flask, g, request, session, render_template, redirect, 
                   url_for, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

from datetime import datetime

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

    uid = session['user_id']
    if session['user_type'] == 'coach':
        return redirect(url_for('coach_info', uid=uid))
    elif session['user_type'] == 'athlete':
        return redirect(url_for('athlete_info', uid=uid))


@app.route('/coach/<int:uid>')
@login_required
def coach_info(uid):
    cursor = g.db.cursor()

    cursor.execute("""SELECT C.tid, T.name FROM coaches C, Team T
                    WHERE C.uid=%s AND C.tid=T.tid""", (uid,))
    teams = cursor.fetchall()

    if uid == session['user_id']:
        cursor.execute('SELECT salary FROM Coach WHERE uid = %s', (uid,))
        salary = cursor.fetchone()[0]
    else:
        salary = None
    
    return render_template('coach.html', salary=salary, teams=teams, uid=uid)


@app.route('/team/<int:tid>')
@login_required
def team_info(tid):
    cursor = g.db.cursor()
    cursor.execute("""SELECT T.name, T.hometown, S.name 
                      FROM Team T, Sport S, plays P
                      WHERE T.tid = %s AND S.sid = P.sid  """, 
                      (tid,))
    team = cursor.fetchone()
    cursor.execute("""SELECT U.uid, M.number, U.name, M.position
                      FROM User U, member_of M
                      WHERE M.tid = %s AND M.uid = U.uid
                      ORDER BY M.number""", (tid,))
    members = cursor.fetchall()

    cursor.execute('SELECT uid FROM coaches WHERE tid = %s', (tid,)) 
    uid = cursor.fetchone()[0]

    current_coach = True if uid == session['user_id'] else False

    cursor.execute("""SELECT wid, date_assigned 
                      FROM Workout 
                      WHERE uid=%s AND tid=%s
                      ORDER BY date_assigned DESC
                      LIMIT 5""", 
                  (session['user_id'], tid))

    workouts = cursor.fetchall()

    return render_template('team.html', team=team, 
                                        members=members,    
                                        current_coach=current_coach,
                                        workouts=workouts,
                                        tid=tid)

@app.route('/team/<int:tid>/workout/create')
@login_required
def create_workout(tid):
    cursor = g.db.cursor()
    cursor.execute('SELECT uid FROM coaches WHERE tid = %s AND uid=%s', 
                   (tid, session['user_id'])) 
    if int(cursor.rowcount) == 0:
        flash('You don\'t have permission to do that', 'error')
        return redirect(url_for('team_info', tid=tid))

    cursor.execute('SELECT DISTINCT muscle_group FROM ExerciseMuscles')
    muscles = cursor.fetchall()
    print muscles

    return render_template('create.html', muscles=muscles, tid=tid)

@app.route('/team/<int:tid>/workout/submit', methods=['POST'])
@login_required
def submit_workout(tid):
    cursor = g.db.cursor()
    cursor.execute('SELECT uid FROM coaches WHERE tid = %s AND uid=%s', 
                   (tid, session['user_id'])) 
    if int(cursor.rowcount) == 0:
        return jsonify(error='You don\'t have permission to create a workout for this team')
    
    print request.form['workout[0][exercise]']

    cursor.execute('INSERT INTO Workout(tid, date_assigned, uid) VALUES (%s, %s, %s)',
                    (tid, datetime.now(), session['user_id']))
    
    wid = cursor.lastrowid

    for i in range(len(request.form)/3):
        cursor.execute('SELECT eid FROM Exercise WHERE name=%s',
                        (request.form['workout[%d][exercise]'%i]))
        eid = cursor.fetchone()[0]
        sets = request.form['workout[%d][sets]'%i]
        reps = request.form['workout[%d][reps]'%i]
        cursor.execute('INSERT INTO consists_of VALUES (%s, %s, %s, %s)',
                        (wid, eid, sets, reps))

    g.db.commit()
    return jsonify(success=True)


@app.route('/team/<int:tid>/workout/<int:wid>')
@login_required
def workout_info(tid, wid):
    cursor = g.db.cursor()
    cursor.execute('SELECT date_assigned FROM Workout WHERE wid=%s',(wid,))
    date = cursor.fetchall()[0][0]
    cursor.execute("""SELECT E.eid, E.name, C.sets, C.reps
                      FROM Exercise E, consists_of C 
                      WHERE C.wid = %s AND E.eid = C.eid""", (wid,))
    exercises = cursor.fetchall()

    cursor.callproc("TeamProgress", (tid,wid))
    members = cursor.fetchall()

    return render_template('workout.html', exercises=exercises, 
                                           members=members, 
                                           date=date,
                                           wid=wid)

@app.route('/exercises')
def exercises():
    muscle = request.args.get('muscle')
    cursor = g.db.cursor()
    if muscle == 'any':
        cursor.execute('SELECT name FROM ExerciseMuscles')
    else:
        cursor.execute('SELECT name FROM ExerciseMuscles WHERE muscle_group=%s',
                    (muscle,))
    e = map(lambda (a,) : a, list(cursor.fetchall()))
    return jsonify(exercises=e)


@app.route('/athlete/<int:uid>/workout/<int:wid>')
@login_required
def athlete_performance(uid, wid):
    cursor = g.db.cursor()
    cursor.execute('SELECT U.uid, U.name FROM User U WHERE U.uid = %s', (uid,))
    user = cursor.fetchone()
    if user[0] == session['user_id']:
        is_self = True
    else:
        is_self = False

    cursor.execute('SELECT date_assigned FROM Workout WHERE wid=%s',(wid,))
    date = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM does D WHERE D.uid=%s AND D.wid=%s',
                    (uid,wid))
    # athlete has not completed workout
    if cursor.rowcount == 0:
        completed = False
        cursor.execute("""SELECT E.name, C.reps, E.eid
                        FROM Exercise E, consists_of C
                        WHERE C.wid = %s AND E.eid = C.eid""",
                        (wid, ))
        exercises = cursor.fetchall()
    else: 
        completed = True
        cursor.execute("""SELECT E.name, P.max_weight
                        FROM Exercise E, performance P
                        WHERE P.uid = %s AND P.wid = %s AND E.eid = P.eid""",
                        (uid, wid))
        exercises = cursor.fetchall()

    # get tid for link to teams workout page
    cursor.execute('SELECT tid FROM Workout WHERE wid=%s', (wid,))
    tid = cursor.fetchone()[0]

    return render_template('performance.html', user=user,
                           exercises=exercises, date=date, tid=tid,
                           wid=wid, is_self=is_self, completed=completed)


@app.route('/athlete/<int:uid>')
@login_required
def athlete_info(uid):
    cursor = g.db.cursor()
    # get general info about athlete
    cursor.execute("""SELECT U.name, A.height, A.weight 
                      FROM User U, Athlete A 
                      WHERE U.uid = A.uid AND U.uid = %s""", (uid,))
    athlete = cursor.fetchone()

    cursor.execute("""SELECT M.tid, T.name FROM member_of M, Team T
                        WHERE M.uid=%s AND M.tid=T.tid""", (uid,))
    teams = cursor.fetchall()

    workouts=[]
    for team in teams:
        tid=team[0]

        cursor.execute("""SELECT wid, date_assigned 
                      FROM Workout 
                      WHERE tid=%s
                      ORDER BY date_assigned DESC
                      LIMIT 5""", 
                  (tid,))
        workouts= cursor.fetchall()
    

    return render_template('athlete.html', 
                            uid=uid,
                            athlete=athlete, 
                            teams=teams, 
                            workouts=workouts)


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
            cursor.execute('SELECT salary FROM Coach WHERE uid = %s', (user[0]))
            # if not a coach, then we have an athlete
            if int(cursor.rowcount == 0):
                session['user_type'] = 'athlete'
            else:
                session['user_type'] = 'coach'
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
    if user_type == 'athlete':
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        cursor.execute('INSERT INTO User(name, email, password) VALUES(%s, %s, %s)', 
                    (name, email, generate_password_hash(password)))
        uid = cursor.lastrowid
        cursor.execute('INSERT INTO Athlete VALUES(%s, %s, %s)',
                    (uid, height, weight))
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

@app.route('/input/<int:wid>', methods=['POST'])
def input(wid):
    cursor = g.db.cursor()
    uid=session['user_id']
    cursor.execute('SELECT E.eid FROM consists_of E WHERE E.wid=%s',(wid,))
    eids = cursor.fetchall()
    for eid in eids:
        reps=int(request.form['reps%s' % eid])
        weight=int(request.form['max%s' % eid])
        cursor.execute('INSERT INTO performance VALUES (%s, %s, %s, %s, %s)', (eid[0], uid, wid, reps, weight))
    cursor.execute('INSERT INTO does VALUES (%s, %s, %s)', (wid,uid,datetime.now()))
    g.db.commit()    
    return redirect(url_for('athlete_performance',uid=uid,wid=wid))


@app.route('/logout')
def logout():
    try:
        session.pop('user_id')
        session.pop('user_name')
        session.pop('user_type')
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

