# -*- coding: utf-8 -*-
"""This is the main script, the entry point"""
#TODO keep code compatible with 3.x
from __future__ import absolute_import, print_function, unicode_literals
import sys
import logging

#Bill list tab title
#Reports, table column header encoding
#3rd party
import PySide
import PySide.QtGui as _qg
import PySide.QtCore as _qc
import PySide.QtUiTools

##for pyinstaller
import zc
import zc.lockfile

#The call to basicConfig() should come before any calls to debug(), info() etc. As it’s intended as a one-off simple configuration facility, only the first call will actually do anything: subsequent calls are effectively no-ops.
#db is needed for loading the config
#to avoid circular reference we should use always "import banta.x.y" (full scope names) never use relative imports
#(like import db or from . import db) ESPECIALLY if we are inside a __init__
#never import anything except a module
from banta import db
#Logger is available after loading the config
logger = logging.getLogger(__name__)

#ours
#import RC before everthing else, so we can use the translations from the resource file
from banta import rc
#from banta import packages
from banta import utils
from banta import packages


class App():
	#A main class for the whole app, it divides the features in several modules
	def __init__(self):
		#Initialize everything
		
		#Qt app itself
		self.app = _qg.QApplication(sys.argv)
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
		logger.info(self.app.tr("Loading ..."))

		#I've decided that is better to have consistence than pain
		_qc.QLocale.setDefault(_qc.QLocale.c())
		#sets a style (which is not the same as stylesheet)
		#the default style (windows) doesn't allow to use transparent background on widgets
		self.app.setStyle("plastique")
		#Some built-in stylesheets
		self.style = 0
		self.styles = ( ":/data/darkorange.qss", ":/data/style.qss",":/data/levelfour.qss", 'user.qss')
		#sets the first stylesheet
		self.changeStyle()
		#uiLoader, load the ui from resources, (careful, a change in .ui file will require to build the resources again)
		self.app.uiLoader = PySide.QtUiTools.QUiLoader()
		self.app.window = self.app.uiLoader.load(":/data/ui/main.ui", None)
		self.app.window.tr = utils.unitr(self.app.window.tr)

		self.app.about = self.app.uiLoader.load(":/data/ui/about.ui", self.app.window)
		self.app.about.setWindowIcon(self.app.window.windowIcon())
		self.app.settings = self.app.uiLoader.load(":/data/ui/settings.ui", self.app.window)
		self.app.settings.setWindowIcon(self.app.window.windowIcon())
		
		#checks the license
		self.checkLicense()		
		#load the modules
		self.loadPackages()
		#Load all the connections (events (signal/slots))
		self.connect()
		
	def checkLicense(self):
		#Licence is going to be removed from the app and business model.
		if db.DB.root['license'] == db.models.LICENSE_FREE:
			status = self.app.window.tr("Usuario no registrado - Considere registrarse para obtener mejor soporte y ayudar a un mejor desarrollo.")
		else:
			status = self.app.window.tr("Usuario registrado - Muchas gracias por contribuir a un mejor software.")
		self.app.window.statusbar.showMessage(status)

	def run(self):
		#Enters the main loop
		self.app.window.showMaximized()
		sys.exit(self.app.exec_())

	def loadTranslation(self, name, path=':/data/trans/'):
		"""Loads a translation file, it must be a ".qm" file
		by default it loads it from resource file
		it only loads ONE translation
		"""
		logger.info("Loading translation '%s' in '%s'"%(name, path))
		trans = _qc.QTranslator()

		if trans.load(name, path):
			self.app.installTranslator(trans)
			self.translators.append(trans)
			logger.info("Translation loaded ok")
			return True
		else:
			logger.error("Couldn't load translator %s"%name)
			return False

	def changeStyle(self):
		#Changes the current style rotating to the next one
		self.setStyle(self.styles[self.style])
		self.style = (self.style +1) % len(self.styles)

	def setStyle(self, filename=None):
		if filename:
			f = _qc.QFile(filename)
			f.open(_qc.QIODevice.ReadOnly or _qc.QIODevice.Text)
			style = _qc.QTextStream(f).readAll()
			self.app.setStyleSheet(style)
		else:
			self.app.setStyleSheet()

	def loadModules(self):
		#First we check the permissions and license
		#Iterate each CLASS in the avail list 
		for av_mod in self.avail:
			#Create an INSTANCE of the module (equivalent to call __init__( )
			mod = av_mod(self.app)
			#We dont check for licenses anymore
			#Only load if we have permissions
			logger.debug( "Available Module %s"%mod.NAME )
			self.app.modules[mod.NAME] = mod
		#Now we load all modules 
		#Do it in different loop so each module can search for other modules
		for mod in self.avail: #so we can retain the load order
			if mod.NAME in self.app.modules:
				logger.debug( "Loading module %s"%mod.NAME )
				try:
					self.app.modules[mod.NAME].load()
				except Exception, e:
					logger.exception( "Failed to load module %s\n%s"%(mod.NAME, str(e)))

	def loadPackages(self):
		#Available packages, order mathers
		self.av_packages = packages.getPackages()
		self.app.packages = {}
		#Here we will save all the loaded modules
		#notice we sav them in self.app so we can pass it to modules itself
		self.app.modules = {}
		#i save them in self.avail just in case there is a module that puts something needed even if it doesnt has permissions
		self.avail = []

		#this for is done in this way to allow some other verification
		for av_pack in self.av_packages:
			self.avail.extend(av_pack.MODULES)
			self.app.packages[av_pack.NAME] = av_pack
		self.loadModules()

	@_qc.Slot(str)
	def siteOpen(self, site="http://www.moongate.com.ar"):
		#os.startfile(site)
		if not _qg.QDesktopServices.openUrl(site):
			_qg.QMessageBox.critical(self.app.window, "Banta", self.app.tr("No se ha podido mostrar la web:\n%s") % site)
		
	def connect(self):
		self.app.aboutToQuit.connect(self.quitting)
		self.app.window.acChangeStyle.triggered.connect(self.changeStyle)
		self.app.window.acAbout.triggered.connect(self.app.about.show)
		self.app.window.acConfig.triggered.connect(self.showSettings)
		self.app.about.sitebt.clicked.connect(self.siteOpen)
		self.app.about.label_3.linkActivated.connect(self.siteOpen)
		self.app.about.label.linkActivated.connect(self.siteOpen)
		self.app.window.l_news.linkActivated.connect(self.siteOpen)
		self.app.window.acAboutQt.triggered.connect(self.app.aboutQt)
		
	@_qc.Slot()
	def showSettings(self):
		if self.app.settings.exec_() == _qg.QDialog.Accepted:
			db.DB.commit()
		else:
			db.DB.abort()

	@_qc.Slot()
	def quitting(self):
		logging.debug("quitting")
		db.CONF.write()
		feed_mod = self.app.modules.get('Feeds')
		if feed_mod: feed_mod.wait()

def run():
	app = App()
	#try:

	if db.CONF.PROFILING:
		import cProfile
		cProfile.runctx('app.run()', globals(), locals(), filename='profile')
	else:
		app.run()
	#except Exception, e:
	#	#log if there's an error with initialization, remember that this will run with no console in windows
	#	logger.exception(str(e).encode('ascii', 'replace'))
	#	print ("i'm sorry, there's been a fatal exception")
	#	raise e

if __name__ == '__main__':
	import os
	print (os.getcwd())