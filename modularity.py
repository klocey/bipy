from bipy import *

print "Reading the network file..."
print ""

w = bipartite(readweb('modular.web'),t=False)
prettyprint(w.web)

print ""
print "The modular network was hand-made"
print "so that we expect 3 modules"
print ""
#w = bipartite(readweb('demo.web'),t=True)
modulinfo = findModules(w,50) # Needs a number of replicates

# The following line prints a web grouped by modules
# the 'col' option is currently buggy and should not be used
plotModules(w,modulinfo,filename='web_by_modules',col=False)
# compare with the result of the function printing it by degree
plotMatrix(w,filename='web_by_degree',asnest=True)