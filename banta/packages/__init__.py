# -*- coding: utf-8 -*-
"""
Packages are different than modules, the idea is to make possible to coexists different setups for different clients.
Every package contains a list of its modules, so the main script can load those modules without more changes,
retaining the control on stuff like user permission and license.

Notice that license types only HIDES data and methods to the user, it NEVER deletes nor fails to create certain stuff.
This is an important strategy.
"""
from __future__ import absolute_import, print_function, unicode_literals
import banta.db.models as _mods
note="""
Notice that this module doesn't import any other module (ie, .base, .non_free, etc)
that's on purpose, to 
a) keep detachment and allow a faster load time, 
b) allow not to load or include a module that can't be loaded for some weird reason 
(platform specific dependency, bug, etc)
c) allow to load modules on runtime, after being packaged (with pyinstaller)


Note b: after some quick test i've found out that using modules instead of using classes can be 3 times
quicker... 
and modules and packages arent really "classes" because we wont have many instances. Instead we should
ONLY have 1 instance. Also typing the full path to a class is kinda bothersome ie:
banta.packages.base.BasePackage , banta.packages.base.bills.Bills , also looks repetitive.
so, i'll move to a module approach.
so these both classes are useless   
"""

class GenericPackage():
	#list of modules to load, must be a CLASS object for a GenericModule descendant
	MODULES = list()
	#Name of the package
	NAME = ""

	def __init__(self, app):
		#Initialization stuff
		self.app = app

	def load(self):
		#load stuff
		pass

class GenericModule(object):
	REQUIRES = tuple()
	NAME = "-"
	#Defaults to all license types
	LICENSES = _mods.LICENSES_ALL
	#Permissions
	P_ADMIN = 0
	P_SELL  = 1

	def __init__(self, app, *args, **kwargs):
		"""Initializes the module
		Only initialize what's needed always even if the module is not available"""
		self.app = app

	def load(self):
		"""Loads the module
		this is only called if the module being loaded"""
		pass

def getPackages():
	"""This function will search for new packages and list them.
	returns a list of packages.
	"""
	from banta.packages import base, optional
	packs = [base, optional]

	import banta.db
	if banta.db.CONF.EXPERIMANTAL:
		from banta.packages import experimental
		packs.append(experimental)
		
	return packs