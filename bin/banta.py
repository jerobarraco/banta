#! python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys, os

if __name__=='__main__':
	#python will set the path of the current script thats baaaaaaad
	#as this file is inside the banta module, setting the path inside here will create problems when
	#loading the module.
	#on the other side we want banta to be executed in another path, so the database and the settings
	#are stored in whichever directory is ran from. allowing several different versions to run
	print (os.getcwd())
	sys.path[0] = os.getcwd()
	#sys.path.insert(0, os.getcwd())
	import banta
	banta.run()
