## LP-BRIM modularity in bipartite webs
#TODO: this is taking forever because it require a bipartite object
from ..null import *
from ..mainfuncs import *
import numpy as np
from scipy.weave import inline

def mostFrequent(L):
    """
    Finds the most frequent item of an array
    """
    uVal = uniquify(L)
    np.random.shuffle(uVal)
    cnt = {}
    for u in uVal:
        cnt[u] = 0
    for l in L:
        cnt[l] += 1
    return max(cnt, key=cnt.get)

def Qbip_c(W,gg,gh):
    """
    A C implementation of the Qbip function
    Not working at this time
    """
    ggc = map(int,np.copy(gg))
    ghc = map(int,np.copy(gh))
    adj = adjacency(W)
    nt = len(W)
    nb = len(W[0])
    nl = int(np.sum(adj))
    gen = generality(W)
    vul = vulnerability(W)
    code = """
    int i, j, Pos;
    float ModNul, DiffProb;
    float tQ = 0.0;
    for(i = 0; i < nt; i++)
    {
        for(j = 0; j < nb; j++)
        {
            Pos = (i * nb) + j;
            if (ggc[i] == ghc[j])
            {
                ModNul = (float)(gen[i] * vul[j]) / (float)nl;
                DiffProb = (float)adj[Pos] - (float)ModNul;
                tQ += DiffProb;
            }
        }
    }
    return_val = tQ;
    """
    res = inline(code, ['nt','nb','ggc','ghc','nl','gen','vul','adj'], headers = ['<math.h>','<string.h>'], compiler = 'gcc')
    return res / nl

def Qbip(W,gg,gh):
    """
    Bipartite modularity sensu Barber
    Good candidate for a C version
    """
    adj = adjacency(W)
    gen = generality(W)
    vul = vulnerability(W)
    tQ = 0.0
    for i in xrange(len(W)):
        for j in xrange(len(W[0])):
            if gg[i] == gh[j]:
                tQ += (adj[i][j] - (gen[i]*vul[j])/float(np.sum(adj)))
    return tQ / float(np.sum(adj))


## LP method
def LP(W,q_c):
    """
    LABEL PROPAGATION method
    """
    if q_c:
        qfunc = Qbip_c
    else:
        qfunc = Qbip
    OptimStep = 0
    w = adjacency(W) ## This version of modularity is BINARY
    # Community objects
    g = []
    # Each LTL species is assigned a random label
    losp = len(W[0])
    upsp = len(W)
    h = np.arange(losp)
    np.random.shuffle(h)
    # First round of UTL species label propagation
    for i in xrange(upsp):
        # We get a void object to get neighboring labels
        vNL = []
        for j in xrange(losp):
            if w[i][j] == 1:
                # In case of interaction, the label of the interacting
                # LTL species is considered to be neighboring
                vNL.append(h[j])
        # We then add the most common label
        g.append(mostFrequent(vNL))
    # We calculate basal modularity
    refBip = qfunc(W,g,h)
    oriBip = -1
    # Then go on to optimize
    # The LP procedure stops whenever the modularity stops increasing
    while oriBip < refBip:
        oriBip = refBip
        # We propagate the UTL species labels
        # The order of the nodes being updated
        # is choosen at random
        jOrder = range(losp)
        random.shuffle(jOrder)
        for j in jOrder:
            # We get a void object to get neighboring labels
            vNL = []
            for i in xrange(upsp):
                if w[i][j] == 1:
                    # In case of interaction, the label of the interacting
                    # LTL species is considered to be neighboring
                    vNL.append(g[i])
            # We then add the most common label
            h[j] = mostFrequent(vNL)
        # We propagate the LTL species labels
        # The order of the nodes being updated
        # is choosen at random
        iOrder = range(upsp)
        random.shuffle(iOrder)
        for i in iOrder:
            # We get a void object to get neighboring labels
            vNL = []
            for j in xrange(losp):
                if w[i][j] == 1:
                    # In case of interaction, the label of the interacting
                    # LTL species is considered to be neighboring
                    vNL.append(h[j])
            # We then add the most common label
            g[i] = mostFrequent(vNL)
        # We then recalculate the modularity
        refBip = qfunc(W,g,h)
        OptimStep += 1
    # Once we are OUTSIDE the loop (the modularity is stabilized)
    # we return the current Qbip and the community partition
    return [refBip,g,h]


## Create the R and T matrix from a partition
def getRTfp(tg,th):
    ug = uniquify(tg)
    uh = uniquify(th)
    c = len(ug)
    # Build matrices
    R = np.zeros((len(tg),c))
    T = np.zeros((len(th),c))
    # Fill matrices
    for comm in xrange(c):
        for row in xrange(len(tg)):
            if ug[comm] == tg[row]:
                R[row][comm] = 1
        for row in xrange(len(th)):
            if uh[comm] == th[row]:
                T[row][comm] = 1
    return [R,T]


## Gets a module vector from a module matrix
def getCVfromCM(cm):
    cv = []
    for i in xrange(len(cm)):
        for j in xrange(len(cm[0])):
            if cm[i][j] == 1:
                cv.append((j+1))
    return cv

def BRIM(W,part,q_c):
    if q_c:
        qfunc = Qbip_c
    else:
        qfunc = Qbip
    import numpy as np
    # part is an object returned by LP
    ig = part[1]
    ih = part[2]
    iQbip = part[0]
    initPart = getRTfp(ig,ih)
    R = initPart[0]
    T = initPart[1]
    nc = len(R[0])
    # do the B matrix
    B = np.copy(adjacency(W))
    upsp = len(B)
    losp = len(B[0])
    gen = generality(B)
    vul = vulnerability(B)
    for i in xrange(upsp):
        for j in xrange(losp):
                B[i][j] -= (gen[i]*vul[j])/float(np.sum(B))
    # begin BRIM optimization
    refQbip = -1
    while refQbip < iQbip:
        refQbip = iQbip
        # Step 1 : BT
        BT = np.dot(B,T)
        for i in xrange(len(BT)):
            for k in xrange(nc):
                if BT[i][k] == max(BT[i]):
                    R[i][k] = 1
                else:
                    R[i][k] = 0
        # Step 2 : BR
        BR = np.dot(B.T,R)
        for i in xrange(len(BR)):
            for k in xrange(nc):
                if BR[i][k] == max(BR[i]):
                    T[i][k] = 1
                else:
                    T[i][k] = 0
        ng = getCVfromCM(R)
        nh = getCVfromCM(T)
        iQbip = qfunc(W,ng,nh)
    return [iQbip,ng,nh]


## Single LPBRIM Run
def LPBRIM(W,q_c):
    import scipy as sp
    import numpy as np
    LPpart = LP(W,q_c)
    BRIMpart = BRIM(W,LPpart,q_c)
    Q = BRIMpart[0]
    Nmod = len(uniquify(BRIMpart[1]))
    TopPart = BRIMpart[1]
    BotPart = BRIMpart[2]
    out = [Q,Nmod,TopPart,BotPart]
    return out

#TODO: findModules should calculate the necessary data and pass it to other functions
def findModules(W,reps=10,outstep=5,step_print=False,q_c=False):
    topmod = 0
    out = [0,0,0,0]
    if (reps >= 100) & step_print:
        print "Done	Best Q	Best M"
        print "----------------------"
    nstep = outstep
    for repl in range(reps):
        run = LPBRIM(W,q_c)
        if run[0] > topmod:
            topmod = run[0]
            out = run
        if reps >= 100:
            if ((repl/float(reps))*100 >= nstep) & step_print:
                print"{0}%	{1} 	{2}".format(str(nstep), str(out[0]), str(out[1]))
                nstep += outstep
#	print 'Found '+str(out[1])+' modules with Qbip of '+str(topmod)
    if (reps >= 100)& step_print:
        print "----------------------"
        print"{0}%	{1}	{2}".format(str(100),str(out[0]), str(out[1]))
        print "----------------------"
    return out

def Qr(w,mod):
    """
    Returns the realized modularity, to be described in a future
    paper
    """
    if mod[0] == 0:
        return 0
    else :
        adj = adjacency(w)
        Nint = 0
        for i in xrange(len(w)):
            for j in xrange(len(w[0])):

                if adj[i][j] == 1:
                    if mod[2][i] == mod[3][j]:
                        Nint += 1
        realized = Nint/float(np.sum(adj))
        return realized


## Separate modules
def splitWeb(W,mod,path='.',prefix='web_',ext='web',minU=3,minL=3):
    if mod[1] == 0:
        np.savetxt(path+'/'+prefix+'full.'+ext,W.web,delimiter=' ')
    else:
        # We start with the modules
        g = mod[2]
        h = mod[3]
        uMod = uniquify(g)
        for mod in uMod:
            # For each module
            nUp = 0
            nLo = 0
            for i in g:
                if i == mod:
                    nUp += 1
            for i in h:
                if i == mod:
                    nLo += 1
            nWeb = np.zeros((nUp,nLo))
            cRow = -1
            for i in range(W.upsp):
                cCol = -1
                if g[i] == mod:
                    cRow += 1
                    for j in range(W.losp):
                        if h[j] ==mod:
                            cCol +=1
                            nWeb[cRow][cCol] = W.web[i][j]
            if nUp >= minU:
                if nLo >= minL:
                    np.savetxt(path+'/'+prefix+str(mod)+'.'+ext,nWeb,delimiter=' ')
    return 0


## All sub webs as mini_bipartite
def subWebs(W):
    ExtractedModules = []
    # We start with the modules
    g = W.modules.up_modules
    h = W.modules.low_modules
    uMod = uniquify(g)
    for mod in uMod:
        # For each module
        nUp = 0
        nLo = 0
        for i in g:
            if i == mod:
                nUp += 1
        for i in h:
            if i == mod:
                nLo += 1
        nWeb = np.zeros((nUp,nLo))
        cRow = -1
        for i in range(W.upsp):
            cCol = -1
            if g[i] == mod:
                cRow += 1
                for j in range(W.losp):
                    if h[j] ==mod:
                        cCol +=1
                        nWeb[cRow][cCol] = W.web[i][j]
        ExtractedModules.append(nWeb)
    return ExtractedModules



## END OF FILE