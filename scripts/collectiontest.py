import beatsequence as BS
#Create some sequences
a=BS.Sequence(211314)
b=BS.Sequence(31314)
c=BS.Sequence(312114)
#Create matched sequences
matcha=BS.MatchedSequence(a)
matchb=BS.MatchedSequence(b)
matchc=BS.MatchedSequence(c)
#Now create a collection
testcollection=BS.MatchedSequenceCollection()
#add the matches
testcollection.append_attempt(matcha)
testcollection.append_attempt(matchb)
testcollection.append_attempt(matchc)

#go through collection, printing preferred matches (should three)
print"three matches"
for i in testcollection.collection:
    print i.preferred_match.intervals
print "\n"

#now try and add a match that forces matcha to change

matchd=BS.MatchedSequence(c)
testcollection.append_attempt(matchd)
print "extra match, forcing change"
for i in testcollection.collection:
    print i.preferred_match.intervals
print "\n"


#and again, to us all 5 matches

matche=BS.MatchedSequence(c)
matchf=BS.MatchedSequence(c)
matchg=BS.MatchedSequence(c)
testcollection.append_attempt(matche)
testcollection.append_attempt(matchf)
testcollection.append_attempt(matchg)

print "more matches, forcing changes"
for i in testcollection.collection:
    print i.preferred_match.intervals
print "\n"

#finally once more. This time, an error ought to be raised
print "impossible addition, should raise error"
matchh=BS.MatchedSequence(c)
try:
    testcollection.append_attempt(matchh)
except ValueError:
    print "error raised correctly \n"

#check that collection has reverted properly
print "check collection has correctly reverted"
for i in testcollection.collection:
    print i.preferred_match.intervals
