# Bipy functions for the EWDB

from ..gen import *
from ..bipartite_class import *

import urllib
from xml.dom import minidom
import tempfile
import os

def webAsStr(W):
	Wtr = ''	
	for row in W.web:
		for col in row:
			Wtr = Wtr+str(col)+' '
		Wtr = Wtr+'\n'
	return Wtr


def valNode(obj,name):
	content = obj.getElementsByTagName(name)[0].childNodes[0].data
	return content


def getWebsFromDB(cat='all',apk=''):
	ListOfId = []
	url = 'http://bipy.alwaysdata.net/getdatabycat.py?cat='+cat+'&apk='+apk
	infos = urllib.urlopen(url).read()	
	xml = minidom.parseString(infos)
	ids = xml.getElementsByTagName('web')
	
	if len(ids) == 0:
		raise 'No corresponding identifier'
	
	print "Printing data for "+str(len(ids))+" matching record(s)"
	
	print 'ID	NAME		CATEGORY	UTL	LTL'
	for i in ids:
		ListOfId.append(valNode(i,'id'))
		if len(str(valNode(i,'name'))) < 8:
			TabOrNot = '	'
		else:
			TabOrNot = ''
		OutStr = '{0}	{1}{2}	{3}	{4}	{5}'.format(str(valNode(i,'id')),str(valNode(i,'name')),TabOrNot,str(valNode(i,'cat')),str(valNode(i,'utl')),str(valNode(i,'ltl')))
		print OutStr
	
	return 0


def getWebById(id=0,apk=''):
	url = 'http://bipy.alwaysdata.net/getdatabyid.py?id='+str(id)+'&apk='+str(apk)
	infos = urllib.urlopen(url).read()	
	xml = minidom.parseString(infos)
	ids = xml.getElementsByTagName('web')[0]
	#
	f = tempfile.NamedTemporaryFile(delete=False)
	f.write(valNode(ids,'int'))
	f.close()
	web = bipartite(readweb(f.name))
	web.name = valNode(ids,'name')
	if len(valNode(ids,'doi')) > 0:
		bib = {'doi':valNode(ids,'doi')}
		web.ref = ref(bib)
	else:
		if len(valNode(ids,'pmid')) > 0:
			bib = {'pmid':valNode(ids,'pmid')}
			web.ref = ref(bib)
	os.unlink(f.name)
	
	return web


def registerAsContributor(infos,outfile='./EWDB_contribinfos.txt'):
	f = open(outfile, 'w')
	url = 'http://bipy.alwaysdata.net/adduser.py?'+urllib.urlencode(infos)
	infos = urllib.urlopen(url).read()
	xml = minidom.parseString(infos)
	i = xml.getElementsByTagName('contrib')[0]
	#
	print "Thank you "+valNode(i,'rname')+" "+valNode(i,'rsname')+", "
	print "your registration was successful. Please keep all these informations."
	print "They are written in the file "+str(outfile)
	print ""
	if len(valNode(i,'msg')) > 0:
		print valNode(i,'msg')
	print "USERNAME: "+valNode(i,'user')
	f.write("USERNAME: "+valNode(i,'user')+'\n')
	print "PASSWORD: "+valNode(i,'pwd')
	f.write("PASSWORD: "+valNode(i,'pwd')+'\n')
	print "API KEY : "+valNode(i,'apikey')
	f.write("API KEY : "+valNode(i,'apikey')+'\n')
	print "EMAIL   : "+valNode(i,'eml')
	f.write("EMAIL   : "+valNode(i,'eml')+'\n')
	
	return web


def contributeNetwork(bpobj,cat='',utl='',ltl='',desc='',apikey='',public=True):
	
	# Check for references
	rpmid = ''
	rdoi = ''
	rjstor = ''
	if hasattr(bpobj.ref,'pmid'):
		rpmid = bpobj.ref.pmid
	if hasattr(bpobj.ref,'doi'):
		rdoi = bpobj.ref.doi
	if hasattr(bpobj.ref,'jstor'):
		rjstor = bpobj.ref.jstor
	
	if public:
		ispublic = 1
	else:
		ispublic = 0
	
	UrlArgs = {'w':webAsStr(bpobj),
	'n':bpobj.name,
	'c':cat,
	'u':utl,
	'l':ltl,
	'r.d':rdoi,
	'r.p':rpmid,
	'r.j':rjstor,
	'd':desc,
	'apk':apikey,
	'ispublic':ispublic
	}
	
	url = 'http://bipy.alwaysdata.net/addnetwork.py?'+urllib.urlencode(UrlArgs)
	infos = urllib.urlopen(url).read()
	
	getWebsFromDB(cat=cat)
	return 0


def myApiKey(user,pwd):
	cinf = {'u':user,'p':pwd}
	url = 'http://bipy.alwaysdata.net/myapikey.py?'+urllib.urlencode(cinf)
	infos = urllib.urlopen(url).read()	
	xml = minidom.parseString(infos)
	ids = xml.getElementsByTagName('apk')[0]
	apk = valNode(ids,'apikey')
	return apk
