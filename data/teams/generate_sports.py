from random import choice

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

position = ["Forward", "Center", "Back", "Left", "Right", "Goalie"]

days = map(str, range(1,31))
months = ['01','02','03','04','05','06','07','08','09','10','11','12']
years = ['2011', '2010', '2009', '2008']

def circular(lst):
    i = 0
    while True:
        yield lst[i]
        i = (i + 1) % len(lst)

def numbers(lst):
    i = 1
    j = 0 
    while True:
        while j < len(lst):
            j += 1
            yield i
        i += 1
        j = 0

#s = circular(seasons)

def insert_sports((name, season)):
    print 'INSERT INTO SportSeason VALUES ("%s", "%s");' % (name, season) 
    print 'INSERT INTO Sport(name) VALUES ("%s");' % (name) 

def insert_plays(team_id, sport_id):
    print 'INSERT INTO plays VALUES (%s, %s);' % (sport_id, team_id) 

def insert_member_of(uid, tid, number, pos):
    print 'INSERT INTO member_of VALUES (%s, %s, "%s", %s);' % (uid, tid,
                                                                pos, number) 

def insert_coaches(uid, tid):
    date = '%s-%s-%s' % (choice(years), choice(months), choice(days))
    print 'INSERT INTO coaches VALUES (%s, %s, "%s");' % (uid, tid, date) 

if __name__ == '__main__':
    # create sports
    map(insert_sports, sports)
    # put athletes on teams
    tid = circular(range(1, 36))
    team_numbers = numbers(range(1,36))
    pos = circular(position)
    for uid in range(11, 501):
        insert_member_of(uid, tid.next(), team_numbers.next(), pos.next())
    # match teams with sports, match coaches with teams
    sid = circular(range(1,11))
    cs = circular(range(1,11))
    for tid in range(1, 36):
        insert_plays(tid, sid.next())
        insert_coaches(cs.next(), tid)


    
    
