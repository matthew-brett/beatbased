#!/bin/env python
'''
Classes and functions for analyzing and selecting sequences
according to beat properties

Author: Sam Burnand
'''

import random
import copy

def totalsort(x,y):
    '''function for sorting lists of integers by the totals'''
    xtotal=0
    ytotal=0
    for n in x:
        xtotal+=n
    for n in y:
        ytotal+=n
    return xtotal-ytotal

def valueperm(maxlist):
    """returns a list of all the possible permutations, given a list
    of maximum values"""
    L=[1 for i in range(len(maxlist))]
    S=[]
    i=0
    while i<=len(maxlist)-1:
            if L[i]==maxlist[i]:i+=1
            else:
                S.append(L[:])
                L[i]+=1
                L[:i]=[1 for n in range(i)]
                i=0
    S.append(maxlist[:])
    S.sort(totalsort)
    return S

def findmatches(i):
    """returns a MatchedSequenceCollection with as many metric re-arrangements
    of the interval set as possible, 
    along with their matched complex sequences
    
    finds all matches, but can be extremely slow"""
    seq=Sequence(i)
    msc = MatchedSequenceCollection()
    #find all the metric possibilities
    for s in seq.all_metric():
        ms = MatchedSequence(s)
        # Add this match to match collection, if any matches found 
        if ms.matches:
            try:
                msc.append_attempt(ms)
            except ValueError:
                continue
    #write results to a file
    filename="outputsequences/"+seq.__str__()+".txt"
    f=open(filename, "wt")
    for i,m in enumerate(msc.collection):
        f.write("%s : %s ; boi=%s\n" %
        (m.target_sequence, m.preferred_match, m.boilist[m.preferred_match_no]))
    f.close()
    return msc

def getmatches(i,debug=False):
    """works in a similar way to findmatches, but checks less carefully for
    possible combinations. Much faster"""
    seq=Sequence(i)
    if debug:print"Checking:",seq
    metrics=[]
    for n in seq.all_metric():
        metrics.append(n)
    if debug:print len(metrics),"metric sequences found"
    allcomplex=[]
    #create a list for results, the indices of which will match those of the metric sequence
    results=[]
    #A similar list, for beats of interest
    boi=[]
    for i in range(len(metrics)):
        results.append(0)
        boi.append(0)
    for i,s in enumerate(metrics):
        if debug:print "finding complex matches for",s
        matched,bois=s.matched_complex()
        for b,m in enumerate(matched):
            if m.intervals not in allcomplex:
                allcomplex.append(m.intervals)
                results[i]=m
                boi[i]=bois[b]
                break         
    if debug:print"Results:"
    if debug:
        for i,p in enumerate(metrics):
            if results[i]!=0:print p.intervals,":",\
                    results[i].intervals," beat of interest:",boi[i]
            else: print p.intervals,": None found"
    if metrics:
        filename="outputsequences/"+seq.__str__()+".txt"
        f=open(filename, "wt")
        for i,p in enumerate(metrics):
            if results[i]:
                f.write("%s:%s;%s\n" %
                        (p.__str__(), results[i].__str__(), boi[i]))
        f.close()
    
def permIter(seq):
    """Given some sequence 'seq', returns an iterator that gives
    all permutations of that sequence.
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/105962
    """
    ## Base case
    if len(seq) == 1:
        yield(seq)
        raise StopIteration

    ## Inductive case
    for i in range(len(seq)):
        element_slice = seq[i:i+1]
        rest_iter = permIter(seq[:i] + seq[i+1:])
        for rest in rest_iter:
            yield(element_slice + rest)
    raise StopIteration

def calculate_beatscore(onsets, basegroup, upbeat):
    """gives a score based on how frequently onsets
    appear in groups of basegroup"""
    #calculate number of beats, counting an incomplete last beat as a 
    #full beat, not including the first onset
    L=onsets[upbeat:]
    beatno=len(L)/basegroup
    if len(L)%basegroup==0:beatno-=1   
    if beatno<1:raise ValueError, "Sequence too short to correctly analyse"
    beats = -1
    # Inevitable first onset brings beats to 0
    for i, o in enumerate(L):
        if o and i % basegroup == 0:
            beats+=1
    return 1.0*beats/beatno

def beat_metrics(onsets, beatfunc=calculate_beatscore, debug=False):
    """ Returns beatscore, basegroup and upbeat values, 
    depending on how the sequence best groups (based on beatscores)"""
    # grouping in g with upbeat of u
    s=0
    for g in range(4,2,-1):
        for u in range(g):
            if onsets[u]:
                p=beatfunc(onsets, g, u)
                if p>s:
                    s=p
                    basegroup=g
                    upbeat=u
    # now set beatscore as best score
    beatscore=int(round(s*100,2))*1.0/100
    #subtract 0.1 for the presence of an upbeat
    if upbeat>0:beatscore-=0.1
    #check for upbeats of 3 in groups of 4, and upbeats of 2 in groups of 3
    #subtracting a further 0.1 from score if present
    if upbeat==basegroup-1:beatscore-=0.1
    #check for confusing upbeat, and suptract 0.1 from beatscore if present
    if upbeat==0:
        if onsets[1] and not onsets[2]:beatscore-=0.1
    if debug:
        print "Score of",beatscore,", grouping in", basegroup,\
              ", upbeat of",upbeat
    return beatscore, basegroup, upbeat

class Sequence(object):
    ''' Class for sequences of intervals '''
    def __init__(self, sequence_def, beatfunc = beat_metrics, debug=False):
        ''' Initializes sequence from seqence_def

        sequence def can be one of:
        onset definition - sequence of ones and zeros indicating
          presence / absence of onset for each base interval
          e.g [1, 1, 0, 0, 1, 0]
        interval definition - sequence of numbers from 1-Inf specifying
          the time to the next onset e.g [1, 3, 2] 
        Definitions can be lists, or strings, or integers.
        
        By definition, sequences start with an onset, so an intial
        onset of 0 is illegal

        >>> a = Sequence([1, 3, 2])
        >>> 
        '''
        self.beatfunc = beatfunc
        self.debug = debug
        self._initialize(sequence_def)

    def set_onsets(self, onsets):
        self._initialize(onsets, 'onsets')
    def get_onsets(self):
        return self._onsets
    onsets = property(get_onsets, 
                      set_onsets, 
                      None, 
                      'get/set onsets');

    def set_intervals(self, intervals):
        self._initialize(intervals, 'intervals')
    def get_intervals(self):
        return self._intervals
    intervals = property(get_intervals, 
                        set_intervals, 
                        None, 
                        'get/set intervals');
    
    def get_beatscore(self):
        return self._beatscore
    beatscore=property(get_beatscore,None,None,'get beatscore')

    def get_upbeat(self):
        return self._upbeat
    upbeat=property(get_upbeat,None,None,'get upbeat')

    def get_basegroup(self):
        return self._basegroup
    basegroup=property(get_basegroup,None,None,'get basegroup')

    def _intervals_to_onsets(self, intervals):
        ''' Convert intervals to onsets '''
        onsets = []
        for e in intervals:
            onsets += [1] + [0]*(e-1)
        return onsets

    def _onsets_to_intervals(self, onsets):
        ''' Convert onsets to intervals '''
        if not onsets:
            return onsets
        if onsets[0] == 0:
            raise ValueError, 'Sequence must start with onset'
        intervals = []
        for onset in onsets:
            if onset == 1:
                intervals.append(1)
            elif onset == 0 :
                intervals[-1]+=1
            else:
                raise ValueError, 'Must be 0 or 1 onsets'
        return intervals

    def all_permutations(self):
        ''' returns a list of all the possible permutations of the sequence

        Caches result, only invalidated by onset, interval get/set
        '''
        if self._all_permutations is None:
            L = []
            S = []
            for intervals in permIter(self.intervals):
                if intervals not in L:
                    L.append(intervals)
                    S.append(Sequence(intervals))
            self._all_permutations = S
        return self._all_permutations

    def _initialize(self, sequence_def, def_type=None):
        ''' Sets onsets, intervals,  beatscore, basegroup and upbeat attributes, '''

        ''' Allow def to be int, long or string - proc to list '''
        if isinstance(sequence_def, (int, long)):
            sequence_def = str(sequence_def)
        if isinstance(sequence_def, basestring):
            sequence_def = [int(e) for e in list(sequence_def)]
        if def_type is None:
            if 0 in sequence_def: # must be onsets, or 1s only sequence
                def_type = 'onsets'
            else:
                def_type = 'intervals'
        if def_type == 'intervals':
            self._intervals = sequence_def
            self._onsets = self._intervals_to_onsets(sequence_def)
        elif def_type == 'onsets':
            if len(sequence_def) and sequence_def[0] == 0:
                raise ValueError, 'Onsets must start with 1'
            self._onsets = sequence_def
            self._intervals = self._onsets_to_intervals(sequence_def)
        else:
            raise ValueError, 'Strange sequence definition %s' % def_type

        # Clear cached variables for lazy loading
        self._all_permutations = None
        self._all_metric = None
        self._matched_complex = None

        # Calculate beatscore etc
        self._beatscore, self._basegroup, self._upbeat = self.beatfunc(
            self.onsets)

    def all_metric(self,basegroup=4,upbeat=0):
        """returns a list of all possible re-arrangements of the sequence
        which form a perfect metrically grouped sequence"""
        if self._all_metric:
            return self._all_metric
        L=self.all_permutations()
        S=[]
        for i in L:
            if i.beatscore==1.0 and i.basegroup==basegroup \
                   and i.upbeat==upbeat and i.extra_exclude()==False:
                S.append(i)
        self._all_metric = S
        return S
    def extra_exclude(self):
        """returns true if the sequence meets one of a few extra criteria for
        exclusion from the metric simples"""
        exclude=False
        #check for 13s and 121s
        for i in range(0,12,4):
            if self.onsets[i:i+4]==[1,1,0,1]:exclude=True
            if self.onsets[i:i+4]==[1,1,0,0]:exclude=True
        #check for repeated 'bars' of 4
        if self.onsets[0:4]==self.onsets[4:8] or \
                self.onsets[4:8]==self.onsets[8:12]:exclude=True
        return exclude

    def matched_complex(self,bois=[9,5],threshold=0.8):
        """returns a list of sequences with a beatscore lower than or 
        equal to threshold, re-arrangements of the given sequence, 
        which match the given sequence around the beat of interest (boi)"""
        if self._matched_complex:
            return self._matched_complex, self._boilist
        L=self.all_permutations()
        S=[]
        boidict={}
        for boi in bois:
            if boi<=4 or boi>=(len(self.onsets)-1):raise ValueError , \
                "beat of interest invalid for sequence"
            for i in L:
                if i.onsets[boi-4:boi+2]==self.onsets[boi-4:boi+2] \
                        and i.beatscore<=threshold:
                    S.append(i)
                    boidict[i]=boi
        S.sort(lambda x, y: cmp(x.beatscore, y.beatscore))
        boilist=[]
        for i in S:
            boilist.append(boidict[i])

        if self.debug:
            if len(S)>0:print "Best one:",S[0].intervals,"\n",len(S),"found"
            else: print "None found"
        self._matched_complex = S
        self._boilist=boilist
        return S, boilist

    def wrong_version(self,debug=False):
        """returns another sequence which differs from the input by
        joining two intervals, and splitting one interval into two.
        metric/complex is preserved"""
        #loop until one is found which fits criteria
        found=False
        num=0 # used to raise an error if too many loops occur
        while found==False:
            num+=1
            if num>=1000:raise ValueError,"no possible wrong version"
            newsequence=Sequence(self.intervals[:])
            #choose random position to join
            pos=random.randint(0,len(newsequence.intervals)-3)
            if debug:print "position:",pos
            newinterval=newsequence.intervals[pos]+newsequence.intervals[pos+1]
            if newinterval>4:continue # don't make intervals greater than 4
            newsequence.intervals[pos:pos+2]=[newinterval]
            if debug:print "join gives:",newsequence
            #now a random split
            pos=random.randint(0,len(newsequence.intervals)-1)
            if debug:print "split at:",pos
            n=newsequence.intervals[pos]
            if n==1:continue # can't split a 1
            split=random.randint(1,n-1)
            split1=n-split
            split2=n-split1
            if debug:print "splitting",n,"to",split1,"and",split2
            newsequence.intervals[pos]=split1
            if debug:print newsequence
            newsequence.intervals[pos+1:pos+1]=[split2]
            #now check that new sequence is similar to self (but not same)
            if debug:print newsequence
            if debug:print self.intervals
            found=True
            if newsequence.intervals==self.intervals:found=False
            if self.beatscore==1.0 and newsequence.beatscore!=1.0:found=False
            if self.beatscore<=0.8 and newsequence.beatscore>0.8:found=False
        return newsequence

    def __str__(self):
        intervalstring=""
        for i in self.intervals:
            intervalstring+=str(i)
        return intervalstring

class MatchedSequence(object):
    def __init__(self, target_sequence):
        self.target_sequence = target_sequence
        self.matches, self.boilist = target_sequence.matched_complex()
        self._preferred_match_no = 0

    def get_preferred_match(self):
        return self.matches[self._preferred_match_no]
    def get_preferred_match_no(self):
        return self._preferred_match_no
    def set_preferred_match_no(self,value):
        self._preferred_match_no=value
    preferred_match = property(get_preferred_match)
    preferred_match_no=property(get_preferred_match_no,set_preferred_match_no)

    def to_next_match(self):
        if self._preferred_match_no >= len(self.matches)-1:
            raise ValueError, 'Ran out of matches, leaving as was'
        self._preferred_match_no += 1
        
    def to_previous_match(self):
        if self._preferred_match_no <= 0:
            raise ValueError, 'Ran out of matches, leaving as was'
        self._preferred_match_no -= 1

    def to_first_match(self):
        self._preferred_match_no=0


class MatchedSequenceCollection(object):
    ''' Collection of previously matched sequences '''
    def __init__(self, matched_seq_list=None):
        if matched_seq_list is None:
            matched_seq_list = []
        self.collection = matched_seq_list
        
    def append_attempt(self,mseq):
        #make fallback copy
        collection_copy=copy.deepcopy(self.collection)
        #add new sequence
        self.collection.append(mseq)
        #create list of how many matches each has
        totalmatcheslist=[]
        for i in self.collection:
            totalmatcheslist.append(len(i.matches))
        #go through these possibilites, check for duplicates
        for matcheslist in valueperm(totalmatcheslist):
            #set the preferred matches to those corresponding to this set
            for i,m in enumerate(matcheslist):
                self.collection[i].preferred_match_no=m-1
            #now check for duplicates
            failure=False
            checklist=[]
            for match in self.collection:
                if match.preferred_match.intervals not in checklist:
                    checklist.append(match.preferred_match.intervals)
                else:
                    failure=True
                    break
            if failure==True:
                continue
            else: 
                break
        #if ends naturally, not possible to add it in, so revert to copy
        #and raise an error
        else:
            self.collection=collection_copy
            raise ValueError, "Can't be put in"





