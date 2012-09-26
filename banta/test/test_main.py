# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import py.test

from PySide.QtTest import QTest as _qtt
import PySide.QtCore as _qc

import banta

app = None
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
		_qtt.mouseClick( w.bBillPrint, _qc.Qt.LeftButton)
		sspy = _qc.QSignalSpy(a.modules['printer'].printer_thread, "printingFinished" )
		el = _qc.QEventLoop()
		el.exec_()
		"""
	145	    QTimer timer;
	146	    connect(&timer, SIGNAL(timeout()), &eventLoop, SLOT(quit()));
		timer.start(5000);
166	    eventLoop.exec();
167
168	    QCOMPARE(changedSpy.count(), 1);
169	    QCOMPARE(changedSpy.at(0).count(), 1);
170
171	    QString fileName = changedSpy.at(0).at(0).toString();
172	    QCOMPARE(fileName, testFile.fileName());
173
174	    changedSpy.clear();"""

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
	print (module)
	
def teardown_module(module):
	print (module)


thanks = """ Thanks to:
ntome @ freenode.net
"""