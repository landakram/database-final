from random import randint 

with open('firsts.txt') as firsts:
    with open('lasts.txt') as lasts:
        for i, line in enumerate(firsts):
            first = line.split()[0].title()
            last = lasts.next().split()[0].title()
            full =  "%s %s" % (first, last)
            # name
            print full
            # email
            print "%s.%s@gmail.com" % (first.lower(), last.lower())
            # password
            print "test1234"
            if i < 10:
                print "Coach"
                # salary
                print randint(40000, 90000)
            elif i < 500:
                print "Athlete"
                # weight in pounds
                print randint(150,250)
                # height in inches
                print randint(65, 80)
            else:
                break
            print ""

