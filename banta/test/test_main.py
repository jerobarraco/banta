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
print_result = None
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
		self.print_results = results
		self.el.quit()

	def close_dialog_yes(self):
		#dialog = app.app.dialog
		dialog = app.activeWindow()
		yes_button= dialog.button(_qg.QMessageBox.Yes)
		_qtt.mouseClick(yes_button, _qc.Qt.LeftButton)
		#_qtt.keyClick(dialog, _qc.Qt.Key_Enter, 0, 10)
		#_qtt.keyClicks(dialog, 's', 0, 10)

	def test_print(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		#set focus on cbclient
		try :
			last_bill = banta.db.DB.bills.maxKey()
		except ValueError: #i dont really like using try/catchs.. but you can use it like this.
			last_bill = 0
		#todo assert client exists
		_qtt.mouseClick(w.cb_clients,  _qc.Qt.LeftButton)
		_qtt.keyClicks( w.cb_clients, "Consumidor\t", 0, 1)
		assert w.lBCliDetail.text() == '[00000000] Consumidor Final (Consumidor Final)'
		self.print_results = None
		self.el = _qc.QEventLoop()
		timer = _qc.QTimer()
		timer.timeout.connect(self.el.quit)
		app.modules['printer'].tprinter.printingFinished.connect(self.printing_finished)
		_qc.QTimer().singleShot(500, self.close_dialog_yes)
		#timer.singleShot(2000, self.close_dialog_yes)
		#sspy = _qc.QSignalSpy(a.modules['printer'].printer_thread, "printingFinished" )
		_qtt.mouseClick( w.bBillPrint, _qc.Qt.LeftButton)
		self.el.exec_()
		#tests that there are results
		assert self.print_results
		#test that there is a possitive result
		assert self.print_results[0]
		#test for a saved bill
		assert last_bill < banta.db.DB.bills.maxKey()
		assert self.print_results[1].idn == banta.db.DB.bills.maxKey()
		global print_results
		#for the mostrarFacturas
		print_resutls = self.print_results
		#checks exceptions
		e = EXCEPTIONS
		assert not e


	def test_printA(self):
		pass

	#···· CLIENT
	def test_newClient(self):
		global EXCEPTIONS, w
		EXCEPTIONS = 0
		_qtt.mouseClick(w.bCliNew,  _qc.Qt.LeftButton)
		#gets the last client
		#checks the selection is correct
		mod = w.v_clients.model()
		r = mod.rowCount()
		idx = mod.index(r-1, 1)
		idn = idx.data(_qc.Qt.UserRole)
		assert idn > -1
		#check existence
		assert idn in banta.db.DB.clients

		name = idx.data()
		assert name == 'Nuevo cliente'
		mod.setData(idx, """Juan\n\t\rMocho""")
		name = idx.data()
		assert name == "Juan   Mocho"

		e = EXCEPTIONS
		assert not e

	def test_delClient(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		t_cli = 'Juan   Mocho'
		#assert t_cli in banta.db.DB.clients
		#is better to use the model() from the view, because it could change, in this case the model is
		#a proxy model, so be carefull not to mix db indexes with view indexes
		cli_mod = w.v_clients.model()
		i_start = cli_mod.index(0, 1)
		#hit =-1 on purpose
		matches = cli_mod.match(i_start, _qc.Qt.EditRole, t_cli, -1)
		assert (len(matches))

		i = matches[0]
		c = cli_mod.data(i, _qc.Qt.EditRole)
		assert t_cli == c
		idn = cli_mod.data(i, _qc.Qt.UserRole)
		w.v_clients.selectionModel().clearSelection()
		w.v_clients.selectRow(i.row())
		w.v_clients.scrollTo(i)

		_qtt.mouseClick(w.bCliDelete,  _qc.Qt.LeftButton)
		assert idn not in banta.db.DB.clients
		e = EXCEPTIONS
		assert not e

	def test_billChangeProduct(self):
		pass

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
		#assertions are lazy so we need to copy the value
		e = EXCEPTIONS
		assert not e

	def test_delProduct(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		tp_code = 'test11'
		#test previous existance
		assert tp_code in banta.db.DB.products

		#test search
		mod = w.v_products.model()
		i_start = mod.index(0, 0)
		#hit =-1 on purpose
		matches = mod.match(i_start, _qc.Qt.UserRole, tp_code, -1)
		assert (len(matches))

		#test getting data
		i = matches[0]
		p = mod.data(i, _qc.Qt.EditRole)
		assert tp_code == p

		#test deletion
		#selects it
		w.v_products.selectionModel().clearSelection()
		w.v_products.selectRow(i.row())
		w.v_products.scrollTo(i)
		#deletes it like a user (tests bindings, and stuff)
		_qtt.mouseClick(w.bProdDelete,  _qc.Qt.LeftButton)
		#checks non-existance
		assert tp_code not in banta.db.DB.products
		e = EXCEPTIONS
		#check exceptions
		assert not e

	#### PRODUCT
	def test_newProvider(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		tp_code = 'test11'
		def __enterProvider():
			dialog = app.activeWindow()
			#note tpcode
			dialog.setTextValue(tp_code)
			_qtt.keyClick(dialog, _qc.Qt.Key_Enter)

		if tp_code in banta.db.DB.providers:
			del banta.db.DB.providers[tp_code]

		_qc.QTimer().singleShot(200, __enterProvider)
		_qtt.mouseClick(w.bProvNew,  _qc.Qt.LeftButton)
		assert tp_code in banta.db.DB.providers
		#assertions are lazy so we need to copy the value
		e = EXCEPTIONS
		if e:
			import traceback
			traceback.print_last()
		assert not e

	def test_delProvider(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		code = 'test11'
		#test previous existance
		assert code in banta.db.DB.providers

		#test search
		mod = w.vProviders.model()
		i_start = mod.index(0, 0)
		#hit =-1 on purpose
		matches = mod.match(i_start, _qc.Qt.UserRole, code, -1)
		assert (len(matches))

		#test getting data
		i = matches[0]
		p = i.data(_qc.Qt.EditRole)
		#p = mod.data(i, _qc.Qt.EditRole)
		assert code == p

		#test deletion
		#selects it
		w.vProviders.selectionModel().clearSelection()
		w.vProviders.selectRow(i.row())
		w.vProviders.scrollTo(i)
		#deletes it like a user (tests bindings, and stuff)
		_qtt.mouseClick(w.bProvDelete, _qc.Qt.LeftButton)
		#checks non-existance
		assert code not in banta.db.DB.providers
		e = EXCEPTIONS
		#check exceptions
		assert not e

	def test_mostrarFacturas(self):
		global EXCEPTIONS
		EXCEPTIONS = 0
		#(asumes it printed)
		success, bill, number, error = self.print_results
		assert bill.idn #the id for the bill
		#in theory the dateedits shows the current month, so the bill should show up by default
		_qtt.mouseClick(w.bProvDelete, _qc.Qt.LeftButton)
		bill_mod = app.modules['bill list']
		#bill_mod.tBList.
		e = EXCEPTIONS
		#check exceptions
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
hpk @ freenode.net/#pylib
"""