from random import randint

f = open('/Users/Sam/courses/dbs/database-final/workouts/workouts.sql', 'w')

def inserts3(table, a,b,c):
	return 'INSERT INTO %s VALUES (%s, %s, %s);' % (table, a, b, c)

def inserts2(table, a,b):
	return 'INSERT INTO %s VALUES (%s, %s);' % (table, a, b)

def getDate(m,d):
	if (m==0):
		return '\'%s-%s-2012\'' % ('Jan',(7*d+4))
	elif (m==1):
		return '\'%s-%s-2012\'' % ('Feb',(7*d+4))
	elif (m==2):
		return '\'%s-%s-2012\'' % ('Mar',(7*d+4))
	elif (m==3):
		return '\'%s-%s-2012\'' % ('Apr',(7*d+4))
	elif (m==4):
		return '\'%s-%s-2012\'' % ('May',(7*d+4))
	elif (m==5):
		return '\'%s-%s-2012\'' % ('Jun',(7*d+4))
	elif (m==6):
		return '\'%s-%s-2012\'' % ('Jul',(7*d+4))
	elif (m==7):
		return '\'%s-%s-2012\'' % ('Aug',(7*d+4))
	elif (m==8):
		return '\'%s-%s-2012\'' % ('Sep',(7*d+4))
	else :
		return '\'%s-%s-2012\'' % ('Oct',(7*d+4))
e_count=0
with open('exercise.txt') as f2:
    try:
        eid = 1
        while True:
            name = f2.next().strip()
            muscle = f2.next().strip()
	    f.write(inserts2('ExerciseMuscles',name,muscle))
	    f.write('\n')
	    f.write(inserts2('Exercise',eid,name))
	    f.write('\n')
            eid += 1
	    e_count=eid
            f2.next()
    except StopIteration:
        pass

wid=0
for i in range(10):
	for j in range(4):
		wid+=1
		date = getDate(i,j)
		f.write(inserts3("Workout", wid, date, i+1))
		f.write("\n")

		

		


