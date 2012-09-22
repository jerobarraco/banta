# -*- coding: utf-8 -*-
import py.test
import banta
from PySide.QtTest import QTest as _qtt
import PySide.QtCore
app =None
w = None

class TestBanta:
	def test_loads(self):
		global app
		assert app is not None
		assert isinstance(app, banta.App)
		assert banta.db.DB.printer is not None
		k = banta.db.updates.UPDATES.keys()
		k.sort()
		assert banta.db.DB.root['version'] == k[-1] +1
		w.showMaximized()
		
	def test_print(self):
		_qtt.keyClicks( w.cb_clients, "00000000\t", 0, 10)
		assert w.lBCliDetail.text() == '[00000000] Consumidor Final (Consumidor Final)'
		_qtt.mouseClick( w.bBillPrint, PySide.QtCore.Qt.LeftButton)
	@classmethod
	def setup_class(cls):
		""" setup any state specific to the execution of the given class (which
		usually contains tests).
		"""
		global app, w
		app = banta.App()
		w = app.app.window
		
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
		
def setup_module(module):
	print module
	
def teardown_module(module):
	print module