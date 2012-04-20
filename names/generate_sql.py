def user(name, email, password):
    print 'INSERT INTO User VALUES ("%s", "%s", "%s");' % (name, email, password) 

def coach(uid, salary):
    print 'INSERT INTO Coach VALUES (%s, %s);' % (uid, salary) 

def athlete(uid, weight, height):
    print 'INSERT INTO Athlete VALUES (%s, %s, %s);' % (uid, height, weight) 


with open('everyone.txt') as f:
    try:
        uid = 1
        while True:
            name = f.next().strip()
            email = f.next().strip()
            pw = f.next().strip()
            role = f.next().strip()
            user(name, email, pw)
            if role == 'Coach':
                sal = f.next().strip()
                coach(uid, sal)
            else:
                weight = f.next().strip()
                height = f.next().strip()
                athlete(uid, weight, height)
            uid += 1
            f.next()

    except StopIteration:
        pass

