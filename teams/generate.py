def mascot(name, mascot):
    print 'INSERT INTO TeamMascot VALUES ("%s", "%s");' % (name, mascot) 

def team(tid, name, hometown):
    print 'INSERT INTO Team VALUES (%s, "%s", "%s");' % (tid, name, hometown) 
    
f1 = open('mascots.txt')
f2 = open('hometowns.txt')
mascots = [line.strip() for line in f1 if line.strip() != ""]
towns = [line.strip() for line in f2 if line.strip() != ""]
f1.close()
f2.close()

for m in mascots:
    mascot('%ss' % m, m)

c = 0
while len(mascots) < 35:
    mascots.append(mascots[c])
    c += 1

c = 0
while len(towns) < 35:
    towns.append(towns[c])
    c += 1

for i, (m, t) in enumerate(zip(mascots, towns)):
    team(i+1, '%ss'%m, t)
    
     
    




