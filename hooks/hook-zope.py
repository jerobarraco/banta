import PyInstaller.hooks.hookutils
from PyInstaller.hooks.hookutils import exec_statement, logger
import os
print "HOOKING"
def hook(mod):
	logger.info( 'importing %s' % mod)
	#import zope.event
	#mod.event = zope.event
	pth = str(mod.__path__[0])
	
	try:
		import zope.event
		mod.event = zope.event
	except :
		pass
	try:
		import zope.transaction
		mod.transaction = zope.transaction
	except:
		pass
	pth2 = exec_statement("import zope.event; print zope.event.__path__")
	print ("path2", pth2)
	
	mod.__path__.append(pth2)
	print mod.__path__
	return mod
