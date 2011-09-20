from .gen import *
from .nul import *
from .nes import *
from .spe import *
from .mod import *

from getref import *
from mainfuncs import *

import tkFileDialog

class bipartite:
	## This class defines a bipartite object with all structural infos
	def __init__ (self,web,t=False):
		# Read the matrix
		if t:
			web = web.T
		self.web = web
		# General infos
		self.upsp = len(self.web)
		self.losp = len(self.web[0])
		self.size = self.upsp * self.losp
		# Connectance
		self.adjacency = adjacency(self.web)
		self.nlink = linknum(self.web)
		self.connectance = self.nlink / float(self.size)
		# Specificity and all
		self.generality = generality(web)
		self.vulnerability = vulnerability(web)
		self.specificity = specificity(web)
		self.rr = RR(web)
		self.ssi = ssi(web)
		self.mperf = meanperf(web,novoid=True)
		self.bperf = HighLink(web)
		# Nestedness
		NODF = nodf(web)
		self.nodf = NODF[0]
		self.nodf_up = NODF[2]
		self.nodf_low = NODF[1]
		# Placeholder for modularity
		self.modules = ''
		# Placeholder for references
		self.ref = []
		# Placeholder for species names
		self.upnames = range(self.upsp)
		self.lonames = range(self.losp)
		# For the name
		self.name = ''
		
	## Species-level function
	def specieslevel(self,modreps=100):
		# Create a filename
		if self.name != '':
			filename = self.name+'_species.txt'
		else:
			filename = 'web_species.txt'
		# Check the modules
		if self.modules == '':
			self.modules = modules(self,reps=modreps)
		# Loop on the species
		f = open(filename, 'w')
		f.write('SPEC\tLEVEL\tDEGREE\tSPE\tSSI\tMOD\n')
		for i in range(self.upsp):
			f.write(str(self.upnames[i])+'\tTOP\t'+str(self.generality[i])+'\t'+str(self.specificity[i])+'\t'+str(self.ssi[i])+'\t'+str(self.modules.up_modules[i])+'\n')
		for i in range(self.losp):
			f.write(str(self.lonames[i])+'\tBOTTOM\t'+str(self.vulnerability[i])+'\tNA\tNA\t'+str(self.modules.low_modules[i])+'\n')
		f.close()
		# Return the data
		print 'Species-level data saved to '+filename
		return 0
		
	## Network-level function
	def networklevel(self,modreps=50,nullreps=100,fun=null2):
		# Create a filename
		if self.name != '':
			filename = self.name+'_network.txt'
		else:
			filename = 'web_network.txt'
		# Check the modules
		if self.modules == '':
			self.modules = modules(self,reps=modreps)
		# Print the data
		f = open(filename, 'w')
		f.write('NAME\t'+self.name+'\n')
		f.write('SIZE\t'+str(self.size)+'\n')
		f.write('UP_SP\t'+str(self.upsp)+'\n')
		f.write('LO_SP\t'+str(self.losp)+'\n')
		f.write('CONN\t'+str(self.connectance)+'\n')
		f.write('NODF\t'+str(self.nodf)+'\n')
		f.write('NODF_UP\t'+str(self.nodf_up)+'\n')
		f.write('NODF_LO\t'+str(self.nodf_low)+'\n')
		f.write('QBIP\t'+str(self.modules.Q)+'\n')
		f.write('NMOD\t'+str(self.modules.N)+'\n')
		f.write('QR\t'+str(self.modules.Qr)+'\n')
		f.close()
		# Return the data
		print 'Network-level data saved to '+filename
		return 0
	


class modules:
	## A class for the modules
	def __init__(self,w,reps=100):
		modinfos = findModules(w,reps=reps)
		self.Q = modinfos[0]
		self.N = modinfos[1]
		self.up_modules = modinfos[2]
		self.low_modules = modinfos[3]
		if self.Q > 0:
			self.Qr = Qr(w,modinfos)
		else:
			self.Qr = 1
	


class ref:
	## This class defines references for a dataset
	## Fallback order is
	##		1 DOI
	##		2 PMID
	##		3 JSTOR stable url
	def __init__ (self,infos):
		self.link = ''
		self.fulltext = 'Unable to retrieve citation info'
		if infos.has_key('doi'):
			self.doi = infos['doi']
			self.link_doi = "http://dx.doi.org/"+str(self.doi)
			self.fulltext = text_citation(get_citation(self.doi))
			self.link = self.link_doi
		if infos.has_key('pmid'):
			self.pmid = infos['pmid']
			self.link_pubmed = "http://www.ncbi.nlm.nih.gov/pubmed/"+str(self.pmid)
			self.fulltext = text_citation(get_citation(self.pmid))
			self.link = self.link_pubmed
		if infos.has_key('jstor'):
			self.jstor = infos['jstor']
			self.link_jstor = "http://www.jstor.org/pss/"+str(self.jstor)
			self.link = self.link_jstor
		if self.link == '':
			self.link = ' (no link available)'


def loadweb(file='',t=False):
	if file == '':
		filename = tkFileDialog.askopenfilename()
	else:
		filename = file
	# Read the web
	w = bipartite(readweb(filename),t=t)
	return w
