# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
EXCEPTIONS = 0

def my_excepthook(type, value, tback):
	# log the exception here
	# then call the default handler
	global EXCEPTIONS
	EXCEPTIONS+=1
	sys.__excepthook__(type, value, tback)

sys.excepthook = my_excepthook

import py.test

from PySide.QtTest import QTest as _qtt
import PySide.QtCore as _qc
import PySide.QtGui as _qg
import banta

app = None
w = None

def setup_module(module):
	global app, w
	if app is None:
		app = banta.App()
		w = app.window
		w.showMaximized()

def teardown_module(module):
	app.exit()

class TestBanta:
	#####LOADS
	i = 0
	b = 0

	def test_loads(self):
		global app
		assert app is not None
		assert isinstance(app, banta.App)
		assert banta.db.DB.printer is not None
		k = banta.db.updates.UPDATES.keys()
		k.sort()
		assert banta.db.DB.root['version'] == k[-1] +1

	#########PRINT
	@_qc.Slot(list)
	def printing_finished (self, results):
		self.results = results
		self.el.quit()

	def close_dialog_yes(self):
		#dialog = app.app.dialog
		dialog = app.activeWindow()
		yes_button= dialog.button(_qg.QMessageBox.Yes)
		_qtt.mouseClick(yes_button, _qc.Qt.LeftButton)
		#_qtt.keyClick(dialog, _qc.Qt.Key_Enter, 0, 10)
		#_qtt.keyClicks(dialog, 's', 0, 10)

	def test_print(self):
		#set focus on cbclient
		_qtt.mouseClick(w.cb_clients,  _qc.Qt.LeftButton)
		_qtt.keyClicks( w.cb_clients, "00000000\t", 0, 1)
		assert w.lBCliDetail.text() == '[00000000] Consumidor Final (Consumidor Final)'
		self.results = None
		self.el = _qc.QEventLoop()
		timer = _qc.QTimer()
		timer.timeout.connect(self.el.quit)
		app.modules['printer'].tprinter.printingFinished.connect(self.printing_finished)
		_qc.QTimer().singleShot(500, self.close_dialog_yes)
		#timer.singleShot(2000, self.close_dialog_yes)
		#sspy = _qc.QSignalSpy(a.modules['printer'].printer_thread, "printingFinished" )
		_qtt.mouseClick( w.bBillPrint, _qc.Qt.LeftButton)
		self.el.exec_()
		assert self.results
		assert self.results[0]
		#todo check if bill gets saved

	def test_printA(self):
		assert 0

	#···· CLIENT
	def _enterNewClient(self):
		dialog = app.activeWindow()
		dialog.setTextValue('testing')
		#_qtt.keyClicks(dialog, "testing")
		_qtt.keyClick(dialog, _qc.Qt.Key_Enter)
		#yes_button = dialog.button(_qg.QMessageBox.Yes)
		#_qtt.mouseClick(yes_button, _qc.Qt.LeftButton)
		#_qtt.keyClick(dialog, _qc.Qt.Key_Enter, 0, 10)
		#dialog.accept() #also does it

	def test_newClient(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		if 'testing' in banta.db.DB.clients:
			print("YA HABIA UN CLIENTE")
			del banta.db.DB.clients['testing']
		_qc.QTimer().singleShot(200, self._enterNewClient)
		_qtt.mouseClick(w.bCliNew,  _qc.Qt.LeftButton)
		assert 'testing' in banta.db.DB.clients
		del banta.db.DB.clients['testing']
		e = EXCEPTIONS
		assert not e


	def test_changeProduct(self):
		assert 0

	#### PRODUCT
	def test_newProduct(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		tp_code = 'test11'
		def __enterProduct():
			dialog = app.activeWindow()
			#note tpcode
			dialog.setTextValue(tp_code)
			#_qtt.keyClicks(dialog, "testing")
			_qtt.keyClick(dialog, _qc.Qt.Key_Enter)


		if tp_code in banta.db.DB.products:
			del banta.db.DB.products[tp_code]

		_qc.QTimer().singleShot(200, __enterProduct)
		_qtt.mouseClick(w.bProdNew,  _qc.Qt.LeftButton)
		assert tp_code in banta.db.DB.products
		del banta.db.DB.products[tp_code]
		#assertions are lazy so we need to copy the value
		e = EXCEPTIONS
		assert not e


	def setup_method(self, method):
		pass

	@classmethod
	def setup_class(cls):
		""" setup any state specific to the execution of the given class (which
		usually contains tests).
		"""
		pass

	@classmethod
	def teardown_class(cls):
		""" teardown any state that was previously setup with a call to
		setup_class.
		"""
		pass


	def setup_method(self, method):

		""" setup any state tied to the execution of the given method in a
		class. setup_method is invoked for every test method of a class.
		"""
		pass
	def teardown_method(self, method):
		""" teardown any state that was previously setup with a setup_method
		call.
		"""

		pass


thanks = """ Thanks to:
ntome @ freenode.net
"""