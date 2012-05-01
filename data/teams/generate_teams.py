def mascot(name, mascot):
    print 'INSERT INTO TeamMascot VALUES ("%s", "%s");' % (name, mascot) 

def team(tid, name, hometown):
    print 'INSERT INTO Team VALUES (%s, "%s", "%s");' % (tid, name, hometown) 
    
f1 = open('mascots.txt')
f2 = open('hometowns.txt')
f3 = open('schools.txt')
mascots = [line.strip() for line in f1 if line.strip() != ""]
towns = [line.strip() for line in f2 if line.strip() != ""]
schools = [line.strip() for line in f3 if line.strip() != ""]
f1.close()
f2.close()
f3.close()

for i, (m, s) in enumerate(zip(mascots, schools)):
    mascot('%s College' % s,'%ss'% m)

c = 0
while len(schools) < 35:
    schools.append(schools[c])
    c += 1

c = 0
while len(towns) < 35:
    towns.append(towns[c])
    c += 1

for i, (s, t) in enumerate(zip(schools, towns)):
    team(i+1, '%s College' % s, t)
    
     
    




