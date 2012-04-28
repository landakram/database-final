from random import randint

f = open('/Users/Sam/courses/dbs/database-final/workouts/workouts.sql', 'w')

def inserts5(table, a,b,c,d,e):
	return 'INSERT INTO %s VALUES (%s, %s, %s, %s, %s);' % (table, a, b, c, d, e)

def inserts4(table, a,b,c,d):
	return 'INSERT INTO %s VALUES (%s, %s, %s, %s);' % (table, a, b, c, d)

def inserts3(table, a,b,c):
	return 'INSERT INTO %s VALUES (%s, %s, %s);' % (table, a, b, c)

def inserts2(table, a,b):
	return 'INSERT INTO %s VALUES (%s, %s);' % (table, a, b)

def getDate(m,d):
	ds=['04','11','18','25','04']
	ms=['01','02','03','04','05','06','07','08','09','10','11','12']
	return '\'2012-%s-%s\'' % (ms[m], ds[d])


e_count=0
with open('exercise.txt') as f2:
    try:
        eid = 1
        while True:
            name = f2.next().strip()
            muscle = f2.next().strip()
	    name = '\'%s\'' % name
	    muscle = '\'%s\'' % muscle
	    f.write(inserts2('ExerciseMuscles',name,muscle))
	    f.write('\n')
	    f.write(inserts2('Exercise',eid,name))
	    f.write('\n')
            eid += 1
	    e_count=eid
            f2.next()
    except StopIteration:
        pass

def get5Es():
	es = []
	for i in range(5):
		j = randint(1,21)
		while (j in es):
			j = randint(1,21)
		es.append(j)
	return es

def performance(user, date, reps, ex):
	factor=((user-35) % 15)/3
	max = randint(18,26+factor)*10 - reps*5
	return inserts5("performance",ex,user,date,reps,max)

lazy=[]
wid=0
for i in range(10):
	for j in range(4):
		wid+=1
		date = getDate(i,j)
		f.write(inserts3("Workout", wid, date, i+1))
		f.write("\n")
		for k in range(15):
			uid = i*15 + 36 + k
			if (randint(1,100) <= 90):
				f.write(inserts3("does", wid, uid, date))
				f.write("\n")
			else:
				lazy.append(uid)
		es = get5Es()
		for l in range(5):
			r = randint(3,10)
			f.write(inserts4("consists_of", wid, es[l], randint(2,4), r))
			f.write("\n")
			for m in range(15):
				uid = i*15 + 36 + m
				if (not (uid in lazy)):
					f.write(performance(uid, date, r, es[l]))
					f.write("\n")
		

		


