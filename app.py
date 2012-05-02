import MySQLdb as mysql
from flask import (Flask, g, request, session, render_template, redirect, 
                   url_for, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

from datetime import datetime

# setup our Flask application
app = Flask(__name__)
app.config.from_object('settings')
app.config['DEBUG'] = True

# 
# Athletics Organizer
# Authors: Mark Hudnall and Sam Konowitch
# Emails: mhh02009@mymail.pomona.edu, sk032009@mymail.pomona.edu
# 

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

# The index. If a user is not logged in, then we prompt them to log in or 
# register. If they are logged in, we check their user type and redirect them
# appropriately.
@app.route('/')
def index():
    # user is not logged in
    if not session.get('user_id'):
        # open a cursor to the database
        cursor = g.db.cursor()
        cursor.execute("""SELECT T.tid, T.school, S.name FROM Team T, plays P, Sport S
                        WHERE T.tid = P.tid AND P.sid = S.sid 
                        ORDER BY T.school""")
        teams = cursor.fetchall()
        return render_template('login.html', teams=teams)

    uid = session['user_id']
    if session['user_type'] == 'coach':
        return redirect(url_for('coach_info', uid=uid))
    elif session['user_type'] == 'athlete':
        return redirect(url_for('athlete_info', uid=uid))

### Coach views ###

# Displays information about a coach including teams coached.
@app.route('/coach/<int:uid>')
@login_required
def coach_info(uid):
    cursor = g.db.cursor()

    cursor.execute("""SELECT C.tid, T.school FROM coaches C, Team T
                    WHERE C.uid=%s AND C.tid=T.tid""", (uid,))
    teams = cursor.fetchall()

    # if we are requesting our own page, then we want to show them the salary
    if uid == session['user_id']:
        cursor.execute('SELECT salary FROM Coach WHERE uid = %s', (uid,))
        salary = cursor.fetchone()[0]
    # otherwise, that is privileged information
    else:
        salary = None
    
    return render_template('coach.html', salary=salary, teams=teams, uid=uid)


### Team views ###

# Displays information about a team, like the team roster. If you are the 
# coach of this team, then displays the recent workouts and allows you to 
# create a new workout
@app.route('/team/<int:tid>')
@login_required
def team_info(tid):
    cursor = g.db.cursor()
    # general team information
    cursor.execute("""SELECT T.school, T.hometown, S.name 
                      FROM Team T, Sport S, plays P
                      WHERE T.tid = %s AND S.sid = P.sid  """, 
                      (tid,))
    team = cursor.fetchone()
    cursor.execute('SELECT mascot FROM TeamMascot WHERE school=%s',
                    (team[0],))
    mascot = cursor.fetchone()[0]

    # get members of the team
    cursor.execute("""SELECT U.uid, M.number, U.name, M.position
                      FROM User U, member_of M
                      WHERE M.tid = %s AND M.uid = U.uid
                      ORDER BY M.number""", (tid,))
    members = cursor.fetchall()

    cursor.execute('SELECT uid FROM coaches WHERE tid = %s', (tid,)) 
    # The cursor always returns tuples, so for a single value we just unpack
    # it
    coaches = map(lambda (x,) : x, list(cursor.fetchall()))

    # If multiple coaches, we want them all to be able to see the workouts
    current_coach = True if session['user_id'] in coaches else False

    cursor.execute("""SELECT wid, date_assigned 
                      FROM Workout 
                      WHERE tid=%s
                      ORDER BY date_assigned DESC
                      LIMIT 5""", 
                  (tid))

    workouts = cursor.fetchall()

    return render_template('team.html', team=team, 
                                        members=members,    
                                        current_coach=current_coach,
                                        workouts=workouts, mascot=mascot,
                                        tid=tid)

# Allows a coach to create a workout for a given team.
@app.route('/team/<int:tid>/workout/create')
@login_required
def create_workout(tid):
    cursor = g.db.cursor()
    cursor.execute('SELECT uid FROM coaches WHERE tid = %s AND uid=%s', 
                   (tid, session['user_id'])) 
    # if the coach does not coach this team, we do not want them to be
    # able to create workouts for them, so we redirect.
    if int(cursor.rowcount) == 0:
        flash('You don\'t have permission to do that', 'error')
        return redirect(url_for('team_info', tid=tid))

    cursor.execute('SELECT DISTINCT muscle_group FROM ExerciseMuscles')
    muscles = cursor.fetchall()
    print muscles

    return render_template('create.html', muscles=muscles, tid=tid)

# Endpoint for workout form submission. This is actually called asynchronously
# from the workout creation endpoint.
@app.route('/team/<int:tid>/workout/submit', methods=['POST'])
@login_required
def submit_workout(tid):
    cursor = g.db.cursor()
    cursor.execute('SELECT uid FROM coaches WHERE tid = %s AND uid=%s', 
                   (tid, session['user_id'])) 
    # if the coach does not coach this team, we do not want them to be
    # able to create workouts for them, so we redirect.
    if int(cursor.rowcount) == 0:
        return jsonify(error='You don\'t have permission to create a workout for this team')
    
    #print request.form['workout[0][exercise]']

    cursor.execute('INSERT INTO Workout(tid, date_assigned, uid) VALUES (%s, %s, %s)',
                    (tid, datetime.now(), session['user_id']))
    
    # since Workout ids are auto incremented, we get the wid for the one we just created
    wid = cursor.lastrowid

    # associate the exercises with the newly created workout
    for i in range(len(request.form)/3):
        cursor.execute('SELECT eid FROM Exercise WHERE name=%s',
                        (request.form['workout[%d][exercise]'%i]))
        eid = cursor.fetchone()[0]
        sets = request.form['workout[%d][sets]'%i]
        reps = request.form['workout[%d][reps]'%i]
        cursor.execute('INSERT INTO consists_of VALUES (%s, %s, %s, %s)',
                        (wid, eid, sets, reps))

    # commit the transaction
    g.db.commit()
    return jsonify(success=True)


# Displays the exercises in the workout. Also uses a stored procedure
# to determine which members on the team have and have not completed the workout
@app.route('/team/<int:tid>/workout/<int:wid>')
@login_required
def workout_info(tid, wid):
    cursor = g.db.cursor()
    cursor.execute('SELECT date_assigned FROM Workout WHERE wid=%s',(wid,))
    date = cursor.fetchall()[0][0]

    # get the exercises associated with this workout
    cursor.execute("""SELECT E.eid, E.name, C.sets, C.reps
                      FROM Exercise E, consists_of C 
                      WHERE C.wid = %s AND E.eid = C.eid""", (wid,))
    exercises = cursor.fetchall()

    # call the stored procedure. See schema.sql for details
    cursor.callproc("TeamProgress", (tid,wid))
    members = cursor.fetchall()

    return render_template('workout.html', exercises=exercises, 
                                           members=members, 
                                           date=date,
                                           wid=wid)

# This endpoint is used by the workout creation view. It is called 
# asynchronously using ajax. Given a muscle group, it returns all exercise
# names associated with that muscle group.
@app.route('/exercises')
def exercises():
    muscle = request.args.get('muscle')
    cursor = g.db.cursor()
    # if they select any, then we just return all exercises
    if muscle == 'any':
        cursor.execute('SELECT name FROM ExerciseMuscles')
    else:
        cursor.execute('SELECT name FROM ExerciseMuscles WHERE muscle_group=%s',
                    (muscle,))
    # unpack the tuple
    e = map(lambda (a,) : a, list(cursor.fetchall()))
    # jsonify serializes the list and returns it with a json mimetype
    return jsonify(exercises=e)

### Athlete views ###

# Shows an athlete's performance for a given workout
@app.route('/athlete/<int:uid>/workout/<int:wid>')
@login_required
def athlete_performance(uid, wid):
    cursor = g.db.cursor()
    # get general info about the user
    cursor.execute('SELECT U.uid, U.name FROM User U WHERE U.uid = %s', (uid,))
    user = cursor.fetchone()
    # if it's the current user, we make note of that. This variable is used
    # in the template to decide whether to allow input
    if user[0] == session['user_id']:
        is_self = True
    else:
        is_self = False

    cursor.execute('SELECT date_assigned FROM Workout WHERE wid=%s',(wid,))
    date = cursor.fetchone()[0]

    # essentially used to see whether the athlete has completed the workout
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
        # if completed, we query the performance table instead
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


# General information about an athlete
@app.route('/athlete/<int:uid>')
@login_required
def athlete_info(uid):
    cursor = g.db.cursor()
    # get general info about athlete
    cursor.execute("""SELECT U.name, A.height, A.weight 
                      FROM User U, Athlete A 
                      WHERE U.uid = A.uid AND U.uid = %s""", (uid,))
    athlete = cursor.fetchone()

    cursor.execute("""SELECT M.tid, T.school FROM member_of M, Team T
                        WHERE M.uid=%s AND M.tid=T.tid""", (uid,))
    teams = cursor.fetchall()

    workouts=[]
    # get recent workouts
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


# Endpoint for performance form submission
@app.route('/input/<int:wid>', methods=['POST'])
@login_required
def input(wid):
    cursor = g.db.cursor()
    uid = session['user_id']
    cursor.execute('SELECT E.eid FROM consists_of E WHERE E.wid=%s',(wid,))
    eids = cursor.fetchall()
    # loops through form submission and inserts into performance table
    for eid in eids:
        reps=int(request.form['reps%s' % eid])
        weight=int(request.form['max%s' % eid])
        cursor.execute('INSERT INTO performance VALUES (%s, %s, %s, %s, %s)', (eid[0], uid, wid, reps, weight))
    cursor.execute('INSERT INTO does VALUES (%s, %s, %s)', (wid,uid,datetime.now()))
    g.db.commit()    
    return redirect(url_for('athlete_performance',uid=uid,wid=wid))

### General User Views ###

# Endpoint for login form submission
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


# Registers a user
@app.route('/register', methods=['POST'])
def register():
    # Grab the information from the request body
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user_type = request.form['type'].lower()
    tid = int(request.form['team'])
    cursor = g.db.cursor()
    # first check if user with email address already exists
    cursor.execute('SELECT * FROM User WHERE email = %s', (email,))
    # if any user was found, then cannot register with that email
    if int(cursor.rowcount) != 0:
        flash('That email address is already taken.', 'error')
        return redirect(url_for('index'))

    uid = 0
    # if the user is an athlete, then we insert them into the Athletes table
    # and put them on a team, as well as insert them into the User table
    if user_type == 'athlete':
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        cursor.execute('INSERT INTO User(name, email, password) VALUES(%s, %s, %s)', 
                    (name, email, generate_password_hash(password)))
        uid = cursor.lastrowid
        cursor.execute('INSERT INTO Athlete VALUES(%s, %s, %s)',
                    (uid, height, weight))
        cursor.execute('INSERT INTO member_of VALUES(%s, %s, "Bench", NextTeamNumber(%s))',
                        (uid, tid, tid))
    # if the user is a coach, then we insert them into the Coach table
    # and have them coach a team, as well as insert them into the User table
    elif user_type == 'coach':
        salary = float(request.form['salary'])

        cursor.execute('INSERT INTO User(name, email, password) VALUES(%s, %s, %s)', 
                    (name, email, generate_password_hash(password)))
        uid = cursor.lastrowid
        cursor.execute('INSERT INTO Coach VALUES(%s, %s)', (uid, salary))
        cursor.execute('INSERT INTO coaches VALUES(%s, %s, %s)',
                        (uid, tid, datetime.now()))
    # commit the transaction
    g.db.commit()

    # set the cookies
    session['user_id'] = uid
    session['user_name'] = name
    session['user_type'] = user_type
    flash('You were successfully registered and logged in.', 'success')
    return redirect(url_for('index'))


# Logs a user out. We do this by deleting the session cookies that contain 
# currently logged in users information.
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

# This function is run before every request. It connects to the database
# and stores the connection on the "g" object, which is available for
# the lifetime of a request.
@app.before_request
def before_request():
    g.db = mysql.connect(host = app.config['DB_HOST'], 
                         db = app.config['DB_NAME'],
                         user = app.config['DB_USER'],
                         passwd = app.config['DB_PASSWORD'])

# Closes the database connection after a request finishes
@app.teardown_request
def teardown_request(exception):
    g.db.close()


if __name__ == '__main__':
    app.run()

