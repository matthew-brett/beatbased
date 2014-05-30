#!/bin/env python
"""Goes through output file from joinfiles, and creates wrong versions of each sequence"""

import beatsequence as BS

inputfile=open("outputsequences/output.txt","rt")
outputfile=open("outputsequences/wrongversions.txt","wt")
#go past first two irrelevant lines
inputfile.readline()
inputfile.readline()
allwrongs=[]
num=0
while 1==1:
    s=inputfile.readline()
    if s=="\n":break
    s=s[:s.find("\n")]
    seq=BS.Sequence(s)
    while 1==1:
        wrongversion=seq.wrong_version()
        if wrongversion not in allwrongs:
            allwrongs.append(wrongversion)
            num+=1
            print "wrong version added",num
            break
print "outputting"
#write these to output file
outputfile.write("Metric wrong versions\n\n")
for i in allwrongs:
    outputfile.write(i.__str__()+"\n")
#go through two more irrelevant lines
inputfile.readline()
inputfile.readline()
allwrongs=[]
print "moved on to complex"
while 1==1:
    s=inputfile.readline()
    if s=="\n":break
    s=s[:s.find("\n")]
    seq=BS.Sequence(s)
    while 1==1:
        wrongversion=seq.wrong_version()
        if wrongversion not in allwrongs:
            allwrongs.append(wrongversion)
            num+=1
            print "wrong version added",seq
            break
#write these to output file
print "outputting"
outputfile.write("\nComplex wrong versions\n\n")
for i in allwrongs:
    outputfile.write(i.__str__()+"\n")
print "output done"
outputfile.close()

    
    
    

