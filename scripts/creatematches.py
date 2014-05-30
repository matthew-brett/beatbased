#!/bin/env python
'''Creates as many matches as possible for metric sequences, with 5-7 intervals'''

import beatsequence as BS

#First, create a list of all combinations of intervals, taking those which add up to 12
print "calculating possible combinations"
S=[]
for length in range(5,10):
    L=[4 for n in range(length)]
    for i in BS.valueperm(L):
        #work out total, gp to next if not 12
        total=0
        for n in i:
            total+=n
        if total!=12:continue
        i.sort()
        if i not in S:
            print "added",i
            S.append(i)

#now run the match creator on S:
for i in S:
    BS.getmatches(i,debug=True)
    print i,"completed"

i=raw_input("Finished. Press enter to close")
