from bipy import *

print "Reading a remote file on NCEAS server"
print ""

ResUrl = "http://www.nceas.ucsb.edu/interactionweb/data/host_parasite/text_matrices/aishihik_p.txt"

#rw = readRemoteWeb(ResUrl,True,True)
#prettyprint(sortbydegree(rw.web))

readFromSql(1)