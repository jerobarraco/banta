# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
logger = logging.getLogger(__name__)

import PySide.QtCore as _qc
import PySide.QtGui as _qg
import banta.db as _db
import banta.packages as _pkg
import banta.utils

#This module will handle most of the stuff for a bill
#Also it need to expose the signals and slots required by the printer module
#QObject is needed for signals
class Bills( _qc.QObject, _pkg.GenericModule):
	REQUIRES = (_pkg.GenericModule.P_SELL, )
	NAME = "bills"
	#Tries to print a bill
	startPrinting = _qc.Signal(object)
	startPrintingDraft = _qc.Signal(object)
	#License is taken from the generic module, by default is for every license
	def __init__(self, app, *args, **kwargs):
		super(Bills, self).__init__()
		self.app = app
		#Basic db instances we need for working
		#they get created when a new bill is created. when loading a new bill is created
		self.bill = None
		self.item = None

	def load(self):
		#caches the window
		w = self.app.window
		# connections
		## actions
		w.acItemAdd.triggered.connect(self.itemAdd)
		w.acItemDelete.triggered.connect(self.itemDelete)
		w.acBillNew.triggered.connect(self.new)
		w.acBillPrint.triggered.connect(self.printBill)
		w.acSaveDraft.triggered.connect(self.printDraft)
		w.acChangeClientSearch.triggered.connect(self.changeClientSearch)

		## Buttons
		w.bBillAdd.setDefaultAction(w.acItemAdd)
		w.bBillNew.setDefaultAction(w.acBillNew)
		w.bBillDelete.setDefaultAction(w.acItemDelete)
		w.bBillPrint.setDefaultAction(w.acBillPrint)
		w.bDraft.setDefaultAction(w.acSaveDraft)
		w.bChangeType.setDefaultAction(w.acChangeClientSearch)

		#w.chBProdReducible.stateChanged.connect(self.prodReducibleChanged)

		## combos
		w.cb_tbill.currentIndexChanged.connect(self.typeChanged)
		w.cb_tpay.currentIndexChanged.connect(self.payChanged)
		w.cb_billProds.currentIndexChanged.connect(self.prodChanged)
		w.cb_clients.currentIndexChanged.connect(self.clientChanged)
		w.cb_billUser.currentIndexChanged.connect(self.userChanged)
		w.eProdDetail.editingFinished.connect(self.prodDetailChanged)
		w.cb_billIva.setModel(_pkg.optional.type_tax.MODEL)
		w.cb_billIva.currentIndexChanged.connect(self.taxChanged)
		#So the label clears when the user inputs another client, this will make sure they select the correct one.
		#(notice that is still possible that SOME client is assigned to the bill but the interface wont show it)
		w.cb_clients.editTextChanged.connect(w.lBCliDetail.clear)

		#this is for the barcodeScanner, because i cant find a proper way to configure them (barcode scanners in general)
		#i use returnpressed instead of editingFinished because that way i can leave the combobox, eitherway when i leave
		#itemAdd will be called and set the focus back to the combo
		#lineEdit() is only available for editable comboboxes
		w.cb_billProds.lineEdit().returnPressed.connect(self.itemAdd)
		w.eProdDetail.returnPressed.connect(self.itemAdd)
		v = _qg.QTableView()#Todo think to do this same to products
		v.setSelectionMode(_qg.QTableView.SingleSelection)
		v.setSelectionBehavior(_qg.QTableView.SelectRows)
		w.cb_clients.setView(v)
		#hides the columns that aren't needed
		#another way using the horizontal header.
		#must be done AFTER setting the view to cb_clients. otherway it wont hide them
		#h = v.horizontalHeader()
		for c in (2,4,5,6):
			#h.hideSection(c)
			v.setColumnHidden(c, True)

		#petruccio says that normally the client comes with his NAME not his CODE
		#though is way more prone to errors...
		w.cb_clients.setModelColumn(1)

		w.eBProdQuant.valueChanged.connect(self.prodQuantChanged)
		#example of how to set a locale for just one widget
		#w.eBProdMarkup.setLocale(_qc.QLocale.c())
		w.dsPrice.valueChanged.connect(self.priceChanged)
		#setting the first item, will also trigger the signal, that's exactly what i want, it will set a default value
		#to the objects
		#order matters
		#Trigger a new bill, so lots of stuff will set up
		w.acBillNew.trigger()
		self.loadNewClientDialog()

	def loadNewClientDialog(self):
		self.dialog = self.app.uiLoader.load(":/data/ui/temp_client.ui", self.app.window)
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.dialog.setWindowIcon(self.app.window.windowIcon())
		self.dialog.setWindowTitle(self.dialog.tr('Nuevo cliente casual'))
		self.app.window.bNewCasualClient.setDefaultAction(self.app.window.acNewCasualClient)
		self.app.window.acNewCasualClient.triggered.connect(self.newCasualClient)
		self.dialog.cbTaxType.addItems(_db.models.Client.TAX_NAMES)
		self.dialog.cbCodeType.addItems(_db.models.Client.DOC_NAMES)
		self.dialog.cbIBType.addItems(_db.models.Client.IB_NAMES)

	@_qc.Slot(float)
	def priceChanged(self, value):
		"""When the price changes, set the price to the current item."""		
		#stores in the base_price of the current item, NOT in the product. because this is temporal (for this sale). 
		#is for overriding the normal price
		self.item.base_price = value
		self.updateItem()

	@_qc.Slot()
	def prodDetailChanged(self):
		if not self.item: 
			return
		text = self.app.window.eProdDetail.text()
		self.item.description = text
		#notice the text is not saved until we do a commit to the database, but thats ok
		#it'll be crazy to commit on each call, since this function
		#is called for each keypress (and zodb saves each version of each object) the database will increase too much and slow things down
		#but either way is an item that's not in a bill , it doesnt matter. (neither the bill) (so only commit BEFORE printing)
		#actually Qt signal editingFinished calls a few tiems,

	@_qc.Slot(int)
	def userChanged(self, i):
		"""Called when the user of a bill changes"""
		if i == -1 :
			return
		self.bill.user = _db.DB.users[i]

	@_qc.Slot(int)
	def clientChanged(self, i):
		"""Called when the client is changed on the cb"""
		if i == -1 :
			return

		code = self.app.window.cb_clients.itemData(i, _qc.Qt.UserRole)
		client = _db.DB.clients[code]
		self.setClient(client)
		return

	@_qc.Slot()
	def changeClientSearch(self):
		col = self.app.window.cb_clients.modelColumn()
		if (col==1):
			col = 0
			text = self.app.window.tr("Código del cliente")
		else:
			col = 1
			text = self.app.window.tr("Nombre del cliente")
		self.app.window.cb_clients.setModelColumn(col)
		self.app.window.lBClient.setText(text)

	@_qc.Slot()
	def printDraft(self):
		ret = self._askToPrint(True)
		if ret == _qg.QMessageBox.Cancel:
			return #nothing to do here...

		#Print if the user wants to
		if ret == _qg.QMessageBox.Yes:
			self.bill.calculate()
			self.startPrintingDraft.emit(self.bill)
			self.app.window.acBillNew.trigger()
		else:
			#if he doesnt want to print, he will want to save it so..
			self.onPrintingFinish((True, self.bill, -1, ''))
			#we gotta save the bill anyway so..

	@_qc.Slot()
	def printBill(self):
		if self._askToPrint(False) == _qg.QMessageBox.Yes:
			if self.bill.printed: #Shouldnt happen because now bills are being copied. but i leave it for a while.
				#TODO add an attribute for drafts and fiscals ¿?
				_qg.QMessageBox.information(self.app.window, self.app.window.tr("Banta - Imprimir"),
					self.app.window.tr("Esta factura ya ha sido impresa."))
				return False

			#read following comment
			self.bill.calculate()
			self.startPrinting.emit(self.bill)
			#starts a new bill just to be safe that the users doesnt modify the bill while is being printed,
			#this will make unnecesary to show a blocking dialog, which also allows the user to do faster his stuffs and
			#check other stuff on the database at the same time
			#We should be carefull that the user doesnt modify a object that could cause a problem with the other thread
			#That's why we calculate here. because most values are calculated ones, not the directs ones from the product
			self.app.window.acBillNew.trigger()
			#Trigger new bill? the user could modify the current bill while printing!!!
			# (should use a dialog to avoid that?)

	def _askToPrint(self, draft=False):
		if not self.bill.client :
			_qg.QMessageBox.information(self.app.window, self.app.window.tr("Banta - Imprimir"),
				self.app.window.tr("No se ha indicado el cliente"))
			return _qg.QMessageBox.Cancel

		options = _qg.QMessageBox.Yes | _qg.QMessageBox.Cancel
		if draft:
			#Theres no sense in saying "i dont want to print" if he hitted the fiscal print
			options |=  _qg.QMessageBox.No

		msgBox = _qg.QMessageBox(
			_qg.QMessageBox.Question, self.app.window.tr("Banta - Imprimir"), self.app.window.tr('¿Desea imprimir?'),
			options, self.app.window
		)
		msgBox.setDefaultButton(_qg.QMessageBox.Cancel)
		#we store it on app for tests
		self.app.dialog = msgBox
		ret = self.app.dialog.exec_()
		return ret

	@_qc.Slot(list)
	def onPrintingFinish(self, result):
		"""slot for when the printer finishes printing something,
		returns a tuple with the information
		 types: (bool, _db.models.bill, int)
			values: (success, original bill object, bill number(if <0 then is a draft), error string (if any))
		"""
		if len(result) != 4: return
		success, bill, number, error = result
		#When the bill is closed, it's also commited, so we close it after it's printed
		#when a bill is closed is added to the db, so be careful
		#if there's an exception in any of the prints, the bill wont close, the db wont commit and a new bill wont be created
		if success:
			if number>= 0: #-1 is a draft or error
				bill.number = number
				bill.printed = True
			bill.close()
			_db.DB.commit()
			#we also want to start a new bill (if the user hasent created a new one)
			if bill == self.bill :
				self.app.window.acBillNew.trigger()
		else:
			msg = str(error).decode('utf-8', 'ignore')
			msg = self.app.window.tr("No se ha podido realizar la impresión\n{0}\n¿Desea volver a editar la factura?\nSi elige NO, la factura NO se guardará.").format(msg)
			logger.error(msg)
			ret = _qg.QMessageBox.question(self.app.window, self.app.window.tr("Impresión Fallida "), msg,
				_qg.QMessageBox.Yes | _qg.QMessageBox.No, _qg.QMessageBox.Yes
			)
			if ret == _qg.QMessageBox.Yes:
				self.showBill(bill)

	@_qc.Slot(int)
	def typeChanged(self, i):
		if i<0:
			self.bill.tax = 0.0
			self.bill.number = 0
		else:
			#Todo show message if (i not in client.getPossibleBillTypes)
			self.bill.setTypeBill(i)
		self.showInfo()

	@_qc.Slot(int)
	def payChanged(self, i):
		if i<0:
			return
		tp = _db.DB.typePays[i]
		self.bill.setTypePay(tp)
		self.item.markup = self.bill.markup
		#This should recalculate the items and the bill totals
		self.showInfo()
		self.updateItem()
		self.updateAllItems()

	@_qc.Slot(int)
	def prodChanged(self, i):
		if i == -1 : 
			self.app.window.dsPrice.setValue(0.0)
			self.app.window.eBProdQuant.setValue(0.0)
			self.app.window.eProdDetail.setText("")
			#self.app.window.chBProdReducible.setChecked(False)
			self.app.window.cb_billIva.setCurrentIndex(0)
			return

		code = self.app.window.cb_billProds.itemData(i, _qc.Qt.UserRole)
		prod = _db.DB.products[code]
		self.item.setProduct(prod)
		self.app.window.dsPrice.setValue(prod.price)
		self.app.window.eProdDetail.setText(self.item.description)
		try:
			tax_index = _db.DB.type_tax.index(prod.tax_type)
		except:
			tax_index = 0

		self.app.window.cb_billIva.setCurrentIndex(tax_index)
		#self.app.window.chBProdReducible.setChecked(self.item.reducible)
		self.updateItem()

	@_qc.Slot(float)
	def prodQuantChanged(self, quant):
		self.item.setQuantity(quant)
		input("aslkd")
		#self.updateItem()

	#@_qc.Slot(int)
	#def prodReducibleChanged(self, val):
	#	self.item.reducible = bool(val)
	#	self.updateItem()

	@_qc.Slot(int)
	def taxChanged(self, val):
		if val < 0:
			return
		self.item.tax_type = _db.DB.type_tax[val]
		self.updateItem()

	@_qc.Slot()
	def itemAdd(self):
		"""Adds an item to the current bill. And does	all the critical logic related to it"""
		self.app.window.eBProdQuant.setFocus()

		if self.item.product is None:
			self.app.window.statusbar.showMessage( self.app.window.tr("Debe seleccionar un producto."))
			return

		if self.bill.addItem(self.item):
			r = self.app.window.tb_bill.rowCount()
			self.app.window.tb_bill.setRowCount(r+1)
			i = self.item
			i.calculate()
			#Create a list of the texts (columns) to take advantage of enumerate
			texts = (
				i.product.code, i.description, str(i.base_price), str(i.quantity),
				str(i.markup), str(i.net_price), str(i.tax_total), str(i.price)
			)
			for c, t in enumerate(texts):
				#use enumerate index to control the column
				self.app.window.tb_bill.setItem(r, c, _qg.QTableWidgetItem(t))

		#important, otherwise the same instance will be overwritten and bill.addItem will return false
		self.item = _db.models.Item(markup=self.bill.markup)
		#dont use .clear it'll delete every product
		self.app.window.cb_billProds.setCurrentIndex(-1)
		self.app.window.eBProdQuant.setValue(1)
		self.app.window.dsPrice.setValue(0.0)
		self.updateItem()
		self.showInfo()
				
	@_qc.Slot()
	def itemDelete(self):
		"""Removes an item from the bill"""
		r = self.app.window.tb_bill.currentRow()
		if r < 0 : return
		self.bill.delItem(r)
		self.app.window.tb_bill.removeRow(r)
		self.showInfo()

	@_qc.Slot()
	def new(self):
		"""Creates a new BILL"""
		self.bill = _db.models.Bill()
		if not self.item: self.item = _db.models.Item()
		self.app.window.tb_bill.setRowCount(0)
		self.app.window.cb_tbill.setCurrentIndex(-1)
		self.app.window.cb_clients.setCurrentIndex(-1)
		self.app.window.cb_tpay.setCurrentIndex(0)
		self.app.window.cb_billProds.setCurrentIndex(-1)
		self.app.window.lBCliDetail.setText("")
		#forces to re-set the user on the new bill.. using the current index we allow to create several bills
		# using the same user and not having to change the combobox each time
		self.app.window.cb_billUser.currentIndexChanged.emit(self.app.window.cb_billUser.currentIndex())
		#force the re-set of the pay type
		self.app.window.cb_tpay.currentIndexChanged.emit(0)
		self.showInfo()

	@_qc.Slot()
	def newCasualClient(self):
		"""Creates a new Client for a temporary use (one shot/one buy)
		The idea of this is not to bloat the client list with one-time shoppers
		"""
		d = self.dialog
		d.eName.setText("")
		d.eCode.setText("")
		d.eAddress.setText("")
		#When we have a one-shot buyer, the probabilities says he'll be using his DNI (National ID)
		d.cbCodeType.setCurrentIndex(_db.models.Client.DOC_DNI)
		#And most probably a Final Consumer
		d.cbTaxType.setCurrentIndex(_db.models.Client.TAX_CONSUMIDOR_FINAL)
		#most probably
		d.cbIBType.setCurrentIndex(_db.models.Client.IB_UNREGISTERED)
		if d.exec_() != _qg.QDialog.Accepted:
			return
		#gets the data
		name = d.eName.text()
		code = d.eCode.text()
		address = d.eAddress.text()
		t_code = d.cbCodeType.currentIndex()
		t_tax = d.cbTaxType.currentIndex()
		t_ib = d.cbIBType.currentIndex()
		#Instantiate a new client with the correct data
		c = _db.models.Client(code, name, address, t_code, t_tax, t_ib, save=False)
		#sets the client to the current bill (Performs sone validation and secondary effects)
		self.setClient(c)

	def showInfo(self):
		"""Updates the info for the bill"""
		self.bill.calculate()
		w = self.app.window
		w.lBillSubtotalA.setText(str(self.bill.subtotal))
		w.lBillTax.setText(str(self.bill.tax))
		w.lBillTotal.setText(str(self.bill.total))
		w.lBillNumber.setText(str(self.bill.number))

	def updateItem(self):
		"""Updates the info for the current item"""
		self.item.calculate()
		p = self.item.price
		self.app.window.lBItemTotal.setText(str(p))

	def updateAllItems(self):
		"""Updates the info for the items added to the bill. mostly affected by stuff like TypePay change and Client change..
		(notice that the "current" item is not updated, for that, use updateItem)
		recalculate indicates when is needed to recalculate the items.
		 Normally is false when we are reloading a saved bill
		"""
		self.app.window.tb_bill.setRowCount(len(self.bill.items))
		for r, i in enumerate(self.bill.items):
			#we avoid recalculating the a printed bill unless is totally safe
			if not self.bill.printed:
				i.calculate()
			texts = (
				i.product.code, i.description, str(i.base_price), str(i.quantity),
				str(i.markup), str(i.net_price), str(i.tax_total), str(i.price)
			)
			for c, t in enumerate(texts):
				#use enumerate index to control the column
				self.app.window.tb_bill.setItem(r, c, _qg.QTableWidgetItem(t))

	def showBill(self, bill):
		"""This function sets a bill as the current, and loads all its info.
		Used from bill_list
		bill param is a bill object from the database or _db.models.Bill
		"""

		#order matters because of signals.  we have to be extra carefull here, one change can make lots of errors
		#disabling all signals might be a reasonable solution, but when we  have more time.
		#because it will require to disconnect and reconnect the pertinent signals

		#first we set the current bill, otherway another bill object might be modified, and in the extrange case that we
		#are showing 2 saved bills (one after the other) the first bill might get changed, and then persisted
		self.bill = bill
		#now the typeBill must be set, because the client changes this if is wrong,
		#luckly this one is easier
		self.app.window.cb_tbill.setCurrentIndex(self.bill.btype)

		if self.bill.ptype is not None:
			tp = self.app.window.cb_tpay
			i = tp.findText(self.bill.ptype.name)
			if i>-1:
				tp.setCurrentIndex(i)
		else:
			#TODO set a default
			#TODO check when does this happens, why does it happens and solve it
			#looks like it happens after i load a saved bill
			print (self.bill.ptype)
			print ("NO PAYMENT TYPE SET!")

		#mi = self.app.window.cb_clients.model().match(None, Qt.EditRole, )
		cb = self.app.window.cb_clients
		code = bill.client.code
		i = cb.findData(code)

		if i>-1:
			#doing this actually emit the currentIndexChanged, that actually re-sets the client to the bill, so be carefull
			cb.setCurrentIndex(i)
			#client will trigger a tbill change if the tbill is not correct

		self.app.window.tabWidget.setCurrentIndex(0)
		self.showInfo()
		self.updateAllItems()

	def setClient(self, client):
		"Sets a client to the current bill"
		_info="""The client can be a existing client in the database or a new one
		Look at the beauty of zodb, we can assign a new instance without having to
		put it on the clients tree. Using a correct logic in the code this will
		make everything run as expected without any drawback.
		"""
		if not self.bill:
			#TODO check why this happens on load
			return
		self.bill.setClient(client)
		d = (client.code, client.name, client.taxStr())
		self.app.window.lBCliDetail.setText("[%s] %s (%s)"%d)
		#this code is too simplistic
		bill_types = client.getPossibleBillTypes()
		#we use the cb_tbill to check the current billtype to ensure visual concordance
		cbt = self.app.window.cb_tbill.currentIndex()
		if cbt not in bill_types:
			#the index is the same as the bill_type, so the next line is ok,
			#if the bill_types changes we should use the model correctly.
			self.app.window.cb_tbill.setCurrentIndex(bill_types[0]) #this will trigger self.bill.setTBill
		#update the client's exempt situation
		#True if the client is exempt from tax
		#TODO if we use this line below more than once, add as function in models.Client.isExempt()
		client_exempt = (client.tax_type == client.TAX_EXENTO)
		#sets the current item (we never know if the user will change the client after modifying a item)
		self.item.client_exempt = client_exempt

		for i, item in enumerate(self.bill.items):
			item.client_exempt = client_exempt
		#we need to update all items because the client might change his exempt status
		self.updateItem()
		self.updateAllItems()


