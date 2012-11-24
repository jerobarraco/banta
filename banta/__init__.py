# -*- coding: utf-8 -*-
"""This is the main script, the entry point"""
#TODO keep code compatible with 3.x
from __future__ import absolute_import, print_function, unicode_literals
import sys
import logging

__version__ = '1.19'

#3rd party
##for pyinstaller
import PySide
import PySide.QtGui as _qg
import PySide.QtCore as _qc
import PySide.QtUiTools

#db is needed for loading the config
#to avoid circular reference we should use always "import banta.x.y" (full scope names) never use relative imports
#(like import db or from . import db) ESPECIALLY if we are inside a __init__
#never import anything except a module
from banta import db
#The call to basicConfig() should come before any calls to debug(), info() etc.
# As it’s intended as a one-off simple configuration facility, only the first call will actually do anything:
# subsequent calls are effectively no-ops.

#Logger is available after loading the config which is loaded on the db
logger = logging.getLogger(__name__)

#ours
#import RC before everthing else, so we can use the translations from the resource file
from banta import rc
from banta import utils
from banta import packages

#TODO subclass qapplication
class App(_qg.QApplication):
	#A main class for the whole app, it divides the features in several modules

	#this doesnt work, it only catch c++ exceptions
	#"def notify(self, rec, ev):
	#	try:
	#		return _qg.QApplication.notify(self, rec, ev)
	#	except:
	#		print ('Gotcha', e)
	#		return False

	def __init__(self):
		#Initialize everything
		super(App, self).__init__(sys.argv)
		#Qt app itself
		#self.app = _qg.QApplication(sys.argv)
		#Before creating the translators we tell Qt how strings are encoded (the fact that Qt has this functions makes it awesome)
		self.codec = _qc.QTextCodec.codecForName("UTF-8")
		#CodecForTr is maybe the most important, it affects string stored in translations, as well as string constants in the source
		#that's being translated. otherway we need to use trUtf8 in code.
		#(Also important to set the CODECFORTR in the qt project from where translations are generated
		#(read the documentation on pyside)
		_qc.QTextCodec.setCodecForTr(self.codec)
		_qc.QTextCodec.setCodecForCStrings(self.codec)
		_qc.QTextCodec.setCodecForLocale(self.codec)
		self.translators = []
		#loads all the translations
		locale = _qc.QLocale.system().name()
		for tr_name in ( locale, 'qt_'+locale):
			if not self.loadTranslation(tr_name):
				new_tr_name = tr_name.rsplit('_', 1)[0]#If en_GB doesnt load, try to load en
				self.loadTranslation(new_tr_name)

		#print(QtCore.QTextCodec.codecForCStrings().name())
		#test the translation
		#dont use unicode
		logger.info(self.tr("Loading ...".encode('utf-8')))

		#I've decided that is better to have consistence than pain
		_qc.QLocale.setDefault(_qc.QLocale.c())
		#sets a style (which is not the same as stylesheet)
		#the default style (windows) doesn't allow to use transparent background on widgets
		self.setStyle("plastique")
		#Some built-in stylesheets
		self.style = 0
		self.styles = ( ":/data/darkorange.qss", ":/data/style.qss",":/data/levelfour.qss", 'user.qss')
		#sets the first stylesheet
		self.changeStyle()
		#uiLoader, load the ui from resources, (careful, a change in .ui file will require to build the resources again)
		self.uiLoader = PySide.QtUiTools.QUiLoader()
		self.window = self.uiLoader.load(":/data/ui/main.ui", None)
		self.window.tr = utils.unitr(self.window.trUtf8)

		self.about = self.uiLoader.load(":/data/ui/about.ui", self.window)
		self.about.setWindowIcon(self.window.windowIcon())
		self.settings = self.uiLoader.load(":/data/ui/settings.ui", self.window)
		self.settings.setWindowIcon(self.window.windowIcon())
		
		#checks the license
		self.checkLicense()		
		#load the modules
		self.loadPackages()
		#Load all the connections (events (signal/slots))
		self.connectStuff()
		
	def checkLicense(self):
		#Licence is going to be removed from the app and business model.
		status = self.window.tr ("Banta versión %s listo.")
		status %= __version__
		if db.DB.root['license'] == db.models.LICENSE_FREE:
			status += " " + self.window.tr("Usuario no registrado. Considere registrarse para obtener mejor soporte y contribuir a un mejor producto.")
		else:
			status += " " + self.window.tr("Usuario registrado. Muchas gracias por contribuir a un mejor producto.")
		self.window.statusbar.showMessage(status)

	def run(self):
		#Enters the main loop
		self.window.showMaximized()
		return self.exec_()

	def loadTranslation(self, name, path=':/data/trans/'):
		"""Loads a translation file, it must be a ".qm" file
		by default it loads it from resource file
		it only loads ONE translation
		"""
		logger.info("Loading translation '%s' in '%s'"%(name, path))
		trans = _qc.QTranslator()

		if trans.load(name, path):
			self.installTranslator(trans)
			self.translators.append(trans)
			logger.info("Translation loaded ok")
			return True
		else:
			logger.error("Couldn't load translator %s"%name)
			return False

	def changeStyle(self):
		#Changes the current style rotating to the next one
		self.loadStyleSheet(self.styles[self.style])
		self.style = (self.style +1) % len(self.styles)

	def loadStyleSheet(self, filename=None):
		style = ""
		if filename:
			f = _qc.QFile(filename)
			f.open(_qc.QIODevice.ReadOnly or _qc.QIODevice.Text)
			style = _qc.QTextStream(f).readAll()
		self.setStyleSheet(style)
	#setStyle and setStyleSheet are method of qApplication
	def loadModules(self):
		#First we check the permissions and license
		#Iterate each CLASS in the avail list 
		for av_mod in self.avail:
			#Create an INSTANCE of the module (equivalent to call __init__( )
			mod = av_mod(self)
			#We dont check for licenses anymore
			#Only load if we have permissions
			logger.debug( "Available Module %s"%mod.NAME )
			self.modules[mod.NAME] = mod
		#Now we load all modules 
		#Do it in different loop so each module can search for other modules
		for mod in self.avail: #so we can retain the load order
			name = mod.NAME
			if name in db.CONF.DISABLED_MODULES:
				logger.debug("About to load module '%s' but it is disabled from banta.cfg" %name)
			elif name in self.modules:
				logger.debug( "Loading module %s"%mod.NAME )
				try:
					self.modules[mod.NAME].load()
				except Exception, e:
					logger.exception( "Failed to load module %s\n%s"%(mod.NAME, str(e)))

	def loadPackages(self):
		#Available packages, order mathers
		self.av_packages = packages.getPackages()
		self.packages = {}
		#Here we will save all the loaded modules
		#notice we sav them in self.app so we can pass it to modules itself
		self.modules = {}
		#i save them in self.avail just in case there is a module that puts something needed even if it doesnt has permissions
		self.avail = []

		#this for is done in this way to allow some other verification
		for av_pack in self.av_packages:
			self.avail.extend(av_pack.MODULES)
			self.packages[av_pack.NAME] = av_pack
		self.loadModules()

	@_qc.Slot(str)
	def siteOpen(self, site="http://www.moongate.com.ar"):
		#os.startfile(site)
		if not _qg.QDesktopServices.openUrl(site):
			_qg.QMessageBox.critical(self.app.window, "Banta", self.app.tr("No se ha podido mostrar la web:\n%s") % site)
		
	def connectStuff(self):
		self.aboutToQuit.connect(self.quitting)
		self.window.acChangeStyle.triggered.connect(self.changeStyle)
		self.window.acAbout.triggered.connect(self.about.show)
		self.window.acConfig.triggered.connect(self.showSettings)
		self.about.sitebt.clicked.connect(self.siteOpen)
		self.about.label_3.linkActivated.connect(self.siteOpen)
		self.about.label.linkActivated.connect(self.siteOpen)
		self.window.l_news.linkActivated.connect(self.siteOpen)
		self.window.acAboutQt.triggered.connect(self.aboutQt)
		
	@_qc.Slot()
	def showSettings(self):
		if self.settings.exec_() == _qg.QDialog.Accepted:
			db.DB.commit()
		else:
			db.DB.abort()

	@_qc.Slot()
	def quitting(self):
		logging.debug("quitting")
		db.CONF.write()
		feed_mod = self.modules.get('Feeds')
		if feed_mod: feed_mod.wait()

def runApp():
	app = App()
	if db.CONF.PROFILING:
		import cProfile
		cProfile.runctx('app.run()', globals(), locals(), filename='profile')
	else:
		return app.run()

def runWrapped():
	try:
		return runApp()
	except Exception, e:
		import traceback
		#log if there's an error with initialization, remember that this will run with no console in windows
		logger.exception(str(e).encode('ascii', 'replace'))
		print ("i'm sorry, there's been a fatal exception")
		traceback.print_exc()
		raise e

def run():
	if db.CONF.DEBUG:
		return runApp()
	else:
		return runWrapped()

if __name__=='__main__':
	sys.exit(run())