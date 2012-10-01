import PyInstaller.hooks.hookutils
from PyInstaller.hooks.hookutils import exec_statement, logger
import os
print "HOOKING"
def hook(mod):
	logger.info('importing %s'%mod)
	#import zope.event
	#mod.event = zope.event
	pth = str(mod.__path__[0])
	
	pth2 = exec_statement("import zope.event; print zope.event.__path__")
	mod.__path__.append(pth2)
	print ("path", pth)
	print ("path2", pth2)
	if os.path.isdir(pth):
	
		# If the user imported setuparg1, this is detected
		# by the hook-wx.lib.pubsub.setuparg1.py hook. That
		# hook sets PyInstaller.hooks.hookutils.wxpubsub
		# to "arg1", and we set the appropriate path here.
		#protocol = getattr(PyInstaller.hooks.hookutils, 'wxpubsub', 'kwargs')
		#logger.info('wx.lib.pubsub: Adding %s protocol path' % protocol)
		#mod.__path__.append(os.path.normpath(os.path.join(pth, protocol)))
		print (pth)
	return mod

	
	