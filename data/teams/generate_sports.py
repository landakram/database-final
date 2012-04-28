
sports = [
("Football", "Fall"),
("Basketball", "Winter"),
("Baseball", "Spring"),
("Soccer", "Fall"),
("Water Polo", "Fall"),
("Track", "Spring"),
("Cross Country", "Fall"),
("Swimming", "Winter"),
("Rugby", "Spring"),
("Tennis", "Summer")
]

def circular(lst):
    i = 0
    while True:
        yield lst[i]
        i = (i + 1) % len(lst)

#s = circular(seasons)

def insert_sports((name, season)):
    print 'INSERT INTO SportSeason VALUES ("%s", "%s");' % (name, season) 
    print 'INSERT INTO Sport VALUES ("%s");' % (name) 

def insert_plays(team_id, sport_id):
    print 'INSERT INTO plays VALUES (%s, %s);' % (sport_id, team_id) 

def insert_member_of(uid, tid):
    print 'INSERT INTO member_of VALUES (%s, %s);' % (uid, tid) 

def insert_coaches(uid, tid):
    print 'INSERT INTO coaches VALUES (%s, %s);' % (uid, tid) 

if __name__ == '__main__':
    # create sports
    map(insert_sports, sports)
    # put athletes on teams
    tid = circular(range(1, 36))
    for uid in range(11, 501):
        insert_member_of(uid, tid.next())
    # match teams with sports, match coaches with teams
    sid = circular(range(1,11))
    cs = circular(range(1,11))
    for tid in range(1, 36):
        insert_plays(tid, sid.next())
        insert_coaches(cs.next(), tid)


    
    
