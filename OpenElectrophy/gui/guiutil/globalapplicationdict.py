# -*- coding: utf-8 -*-


"""
Author:	Samuel Garcia
Laboratoire de Neurosciences Sensorielles, Comportement, Cognition.
CNRS - UMR5020 - Universite Claude Bernard LYON 1
Equipe logistique et technique
50, avenue Tony Garnier
69366 LYON Cedex 07
FRANCE
sgarcia@olfac.univ-lyon1.fr

License: CeCILL v2 (GPL v2 compatible)

"""


import sys , os
import shutil
import pickle
import user


#------------------------------------------------------------------------------
def get_working_dir(applicationname) :
	if sys.platform =='win32' :
		import win32api
		username = win32api.GetUserName()
		working_dir = os.path.join(win32api.GetEnvironmentVariable('USERPROFILE'),
		'Application data/%s' % applicationname)
	if sys.platform[:5] =='linux' :
		working_dir = os.path.join(os.path.expanduser("~"),'.%s/' % applicationname)
	if sys.platform == 'darwin' :
		working_dir = os.path.join(os.path.expanduser("~"),'.%s/' % applicationname)
	if not(os.path.isdir(working_dir)) :
		os.mkdir(working_dir)
	return working_dir


#------------------------------------------------------------------------------
def get_desktop_dir() :
	if sys.platform =='win32' :
		desktop_dir = os.path.join(user.home , 'Desktop')
	if sys.platform[:5] =='linux' :
		desktop_dir = os.path.join(os.environ['HOME'] , 'Desktop')
	if sys.platform== 'darwin' :
		desktop_dir = os.path.join(os.environ['HOME'] , 'Desktop')
	if not(os.path.isdir(desktop_dir)) :
		os.mkdir(desktop_dir)
	return desktop_dir


#------------------------------------------------------------------------------
class GlobalApplicationDict:
	"""
	Class like dict but with autosaving with pickle
	"""
	#------------------------------------------------------------------------------
	def __init__(self,applicationname = None,
					filename = None):
		self.applicationname = applicationname
		if filename is None:
			working_dir = get_working_dir(applicationname)
			filename = os.path.join(working_dir,'global_application_dict')
		self.filename = filename
		
		if os.path.isfile(self.filename) :
			self.load()
		else :
			self.gdict = { }
			self.save()
			
	
	#------------------------------------------------------------------------------
	def __setitem__(self,key,value):
		self.gdict[key] = value
		self.save()
	
	#------------------------------------------------------------------------------
	def __getitem__(self,key):
		if key in self.gdict:
			return self.gdict[key]
		else :
			return None

	#------------------------------------------------------------------------------
	def update(self, d):
		self.gdict.update(d)
		self.save()


	#------------------------------------------------------------------------------
	def pop(self,key):
		if key in self.gdict:
			v= self.gdict.pop(key)
			self.save()
			return v
		else :
			return None
		
		
	#------------------------------------------------------------------------------
	def load(self) :
		try :
			fid = open(self.filename,'rb')
			self.gdict = pickle.load(fid)
			fid.close()
		except :
			self.gdict = { }
	
	#------------------------------------------------------------------------------
	def save(self) :
		fid = open(self.filename,'wb')
		pickle.dump(self.gdict,fid)
		fid.close()




