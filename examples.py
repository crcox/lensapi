import pickle
import numpy

def aslist(x):
    if isinstance(x, basestring):
        return [x]
    else:
        return x

def lowerlist(x):
    try:
        x = [x.lower()]
    except AttributeError:
        x = [e.lower() for e in x]
    return x

def writeheader(f, header):
    for k,v in header.items():
        line = '{k}: {v}\n'.format(k=k,v=v)
        f.write(line)
    f.write(';\n\n')

def writeex(f, name, freq, inputs, targets):
    ISET = []
    [ISET.extend(t.keys()) for t in inputs]
    ISET = sorted(list(set(ISET)))

    TSET = []
    [TSET.extend(t.keys()) for t in targets]
    TSET = sorted(list(set(TSET)))

    name = 'name: {w}\n'.format(w=name)
    freq = 'freq: {f}\n'.format(f=freq)
    nevents = '{e}\n'.format(e=len(inputs))
    f.write(name)
    f.write(freq)
    f.write(nevents)

    # Loop over events
    for e,(inp,trg) in enumerate(zip(inputs,targets)):
        # loop over groups
        line='[{e}] I:\n'.format(e=e)
        f.write(line)

        for grp in ISET:
            if grp == 'context':
                continue
            val,rep = inp[grp]
            if isinstance(val,basestring):
                line='\t({g}Input)\n'.format(g=grp.title())
            elif val == 0:
                line='\t({g}Input)\n'.format(g=grp.title())
            else:
                line='\t({g}Input) {r}\n'.format(g=grp.title(),r=' '.join([str(x) for x in rep]))
            f.write(line)

        if 'context' in inp.keys():
            line='\t({g}) {r}\n'.format(g='context',r=' '.join([str(x) for x in inp['context']]))
            f.write(line)

        line='[{e}] T:\n'.format(e=e)
        f.write(line)
        for grp in TSET:
            val,rep = trg[grp]
            if isinstance(val,basestring):
                line='\t({g}Output)\n'.format(g=grp.title())
            elif val == 0:
                line='\t({g}Output)\n'.format(g=grp.title())
            else:
                line='\t({g}Output) {r}\n'.format(g=grp.title(),r=' '.join([str(x) for x in rep]))
            f.write(line)
    f.write(';\n')

def buildinput(STIM, events, inputs, context, ISET=None):
    return buildex(STIM, events, inputs, context, layer='input', TYPES=ISET)

def buildtarget(STIM, events, targets, context, TSET=None):
    return buildex(STIM, events, targets, context, layer='target', TYPES=TSET)

def buildex(STIM, events, patterns, context, layer, TYPES=None):
    # Compose master lists of input and target types, across all phases.
    # These lists will be forced into alphabetical order to impose stable
    # representational structure across different models (i.e., when both
    # phon and sem inputs are used, phon units are ALWAYS prior to sem
    # units in the input pattern, because of the order imposed at this
    # step.
    if TYPES is None:
        TYPES = [v.keys()[0] if isinstance(v,dict)
                else v for v in patterns.values()]

    # Check if the input type is a dictionary, which means it is a
    # type: data pair. For example, a pair of sem: warmstart is an
    # instruction to fill the semantic units with the data in the
    # warmstart field. If it is NOT a dictionary, format it to be
    # one so that the data are of consistent structure throughout.
    patterns_master = patterns.copy()
    patterns = {}
    for k,v in patterns_master.items():
        if isinstance(v, dict):
            patterns[k] = v
        else:
            patterns[k] = {v:v}

    REPS = []
    # Each event will use some subset of the unit/pattern types. The first
    # step will be to subset the pattern list so it only includes what the
    # event calls for. Then we will loop over the TYPES (ie, ISET or TSET as
    # the case may be) and build up the input/output pattern in the appropriate
    # order.
    for i,event_ in enumerate(events):
        maps = {patterns[k].keys()[0]:patterns[k].values()[0]
                for k in event_.keys()
                if k in patterns.keys()}
        vals = {patterns[k].keys()[0]:event_[k]
                for k in event_.keys()
                if k in patterns.keys()}

        repd = {}
        for type_ in TYPES:
            # First check if type_ is used in this event during this phase
            if type_ in maps.keys():
                # Next, check if the value assigned to the event is numeric
                datacode = maps[type_]
                try:
                    rep = STIM[datacode].tolist()
                except AttributeError:
                    rep = STIM[datacode]

                try:
                    val = vals[type_] + 0 # TypeError if not numeric
                except TypeError:
                    val = 0 # placeholder---will take on value at write stage

                try:
                    # Flatten the phon representation (including
                    # disambiguiating homophone units, if they exist)
                    rep = [u
                            for sublist in rep
                            for u in sublist]
                except TypeError:
                    rep = [u for u in rep]

                rep = (vals[type_],rep)

            else:
                # If the type_ is not used in this event during this phase,
                # insert an all-zeros version of the rep as a place holder.
                try:
                    rep = STIM[type_].tolist()
                except AttributeError:
                    rep = STIM[type_]

                try:
                    # Flatten the phon representation (including
                    # disambiguiating homophone units)
                    rep = [0 for sublist in rep for u in sublist]
                except TypeError:
                    # sem reps are not nested
                    rep = [0 for u in rep]

                if layer == 'target':
                    rep = ('-',rep)
                else:
                    rep = (0,rep)

            repd[type_] = rep

        if layer == 'input':
            if context is None:
                contextUnit = False
            elif context == 'AAE':
                contextUnit = [1]
            else:
                contextUnit = [0]

            if contextUnit:
                repd['context'] = contextUnit

        REPS.append(repd)

    return REPS


def disambiguate(STIM,HOMO):
    from math import ceil,log
    # Compute max number of homophones for any single phonological
    # represenation
    maxn = []
    for h in HOMO.values():
        maxn.append(max([len(words) for words in h.values()]))
    maxn = max(maxn)

    # Compute the number of bits needed to represent an integer large
    # enough to enumerate nmax homophones
    # 2^nunits = nmax
    # so:
    nunits = log(nmax,2)
    nunits = int(ceil(nunits))

    # Compose format string for integer-->binary conversion
    fmt = '{{i:0{n}b}}'.format(n=nunits)

    # Add nunits to every phonological representation
    for key,D in STIM.items():
        for word, d in D.items():
            STIM[key][word].phon.append([0]*nunits)

    # Increment bits to enumerate each homophone
    for key,homo in HOMO.items():
        for words in homo.items():
            for i,w in enumerate(words):
                binstr = fmt.format(i=i)
                binpat = [int(b) for b in binstr]
                # Homo-units are always in the last slot
                STIM[key][w]['phon'][-1] = binpat
    return STIM

def stimdist(STIM,type_,method='cityblock'):
    """ Generate a dictionary that records the distance of each word to
    every other word. Distances are in ascending order, and the words
    associated with each distance are in the same order."""
    import scipy.spatial.distance
    import operator

    def selectAllDist(dist,j):
        N = len(dist)
        n = (1 + numpy.sqrt(1+(8*N))) / 2
        i = numpy.array(range(n))
        del i[j]
        ix = N - ((i**2 - i) / 2) + (j-i-1)
        return dist[ix]

    # All sets have the same semantics, so any will do.
    key = STIM.keys()[0]
    words = STIM[key].keys()
    n = len(words)
    reps = numpy.array([STIM[key][w][type_] for w in words])
    dist = scipy.spatial.distance.pdist(reps,method)
    dist = scipy.spatial.distance.squareform(dist)
    DIST = {}
    for i,w in enumerate(words):
        ix = [j for j in xrange(n) if not j == i]
        d = sorted(zip(dist[i,ix],ix,[words[j] for j in ix]),key=operator.itemgetter(0))
        DIST[w] = {'words': [x[2] for x in d],'dist': [x[0] for x in d]}

    return DIST

def warmstart(STIM,DIST,type_,newfield,knn=0,radius=0):
    import itertools

    if not isinstance(type_,basestring):
        print "'type_' must be a string"
        raise TypeError
    if not isinstance(newfield,basestring):
        print "'newfield' must be a string"
        raise TypeError

    # knn and radius are mutually exclusive
    if knn > 0:
        for key,D in STIM.items():
            for word, d in D.items():
                dist = DIST[word]
                words = dist['words'][0:knn]
                semreps = numpy.array([D[w][type_] for w in words])
                meanrep = numpy.mean(semreps,0)
                STIM[key][word][newfield] = meanrep

    elif radius > 0:
        for key,D in STIM.items():
            for word, d in D.items():
                dist = DIST[word]
                words = [dist['words'][i] for i,d in enumerate(dist['dist']) if d < radius]
                semreps = numpy.array([D[w][type_] for w in words])
                meanrep = numpy.mean(semreps,0)
                STIM[key][word][newfield] = meanrep

    return STIM
