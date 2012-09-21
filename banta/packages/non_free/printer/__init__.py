# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
from PySide import QtCore, QtGui

from banta.packages import GenericModule
from banta.packages.base import bills
from banta.db.models import LICENSES_NOT_FREE

import banta.db as _db
import banta.utils
#Create a separate class that will handle the actual printing
class ThreadPrinter(QtCore.QObject):
	#Emited to update the status when printing
	statusChanged = QtCore.Signal(str)
	#emited when the printing is done, even if it ended with errors. (look at onPrintingFinish @ bills.py to see the meaning)
	printingFinished = QtCore.Signal(list)
	def __init__(self, app, printer, *args, **kwargs):
		super(ThreadPrinter, self).__init__(*args, **kwargs)
		self.app = app
		self._printer = None
		#cache the values so we dont retain any zodb object here
		self._speed = printer.SPEEDS[printer.speed]
		self._brand = printer.brand
		self._device = str(printer.device)
		self._model = printer.model
		#TODO implement this (option in settings called "Stay connected to the printer" that forces that the printer is created only once)
		self._persistent = False #self._persistent = printer.persistent

	def _getPrinter(self):
		#if the printer is persistent, return it
		if self._printer:
			return self._printer

		printer = None
		#get's the speed
		try:
			#check the brand
			if self._brand == _db.models.Printer.BRAND_HASAR:
				#import the related module
				from packages.non_free.printer.hasarPrinter import HasarPrinter
				#creates an instance of the printer and returns it
				printer = HasarPrinter(deviceFile=self._device, speed=self._speed, model = self._model)
			elif self._brand == _db.models.Printer.BRAND_EPSON:
				from packages.non_free.printer.epsonPrinter import EpsonPrinter
				printer = EpsonPrinter(deviceFile=self._device, speed=self._speed, model = self._model)
		except Exception as e:
			emsg = str(e).decode('utf-8', 'ignore')
			msg = self.tr("No se ha podido conectar con la impresora\n{0}").format(emsg)
			#QtGui.QMessageBox.critical(None, self.tr("Impresión Fallida: "), msg )
			logger.error(msg)

		if self._persistent :
			self._printer = printer
		return printer

	@QtCore.Slot()
	def cancel(self):
		printer = self._getPrinter()
		if printer is None: return
		printer.cancelDocument()
		logger.debug("cancelling bill")

	@QtCore.Slot()
	def dailyCloseZ(self):
		printer = self._getPrinter()
		if printer is None: return
		ret = printer.dailyClose(printer.DAILY_CLOSE_Z)
		logger.debug("daily close z: %s"% ret)

	@QtCore.Slot()
	def closePrinter(self):
		"""just in case"""
		if self._printer :
			self._printer.close()
		del self._printer
		self._printer = None

	@QtCore.Slot(object)
	#Passing the bill object is kinda dangerous, because zodb is not thread safe. so we shouldnt modify it here
	def printBill(self, bill):
		#this S$%& is dangerous!
		#if ANYTHING happens, a printingFinished must be emited, or the other thread will stay waiting.. which sucks
		printer = None
		try:
			self.statusChanged.emit("Conectando con la impresora")
			printer = self._getPrinter()
			cli = bill.client
			doc_type_code = getattr(printer, DOC_TYPE_ATTRS[cli.doc_type], ' ')
			tax_type_code = getattr(printer, IVA_TYPE_ATTRS[cli.tax_type], ' ')

			#Checks the type of the bill.
			#This defines what function and with what parameters is called on the printer device interface

			btype = bill.btype
			doc = cli.code.encode('ascii', 'ignore')
			#I wanted to translate this strings. but .. we cant use app in this thread, also, there's no reason to translate this
			#fiscal printers are only argentinean
			self.statusChanged.emit("Abriendo el documento")
			if btype in (bill.TYPE_A, bill.TYPE_B):
				if btype == bill.TYPE_A:
					letter = 'A'
				else:
					letter = 'B'
				printer.openBillTicket(letter, cli.name, cli.address, doc, doc_type_code, tax_type_code)
			elif btype == bill.TYPE_C:
				#Tickets are only for Monotributists, be carefull with this.
				printer.openTicket()
			elif btype in ( bill.TYPE_NOTA_CRED_A , bill.TYPE_NOTA_CRED_B):
				letter = ((btype== bill.TYPE_NOTA_CRED_A) and 'A' ) or 'B' #same as the if before, but more compact
				#TODO add reference
				# type, name, address, doc, docType, ivaType, reference="NC"
				printer.openBillCreditTicket(letter, cli.name, cli.address, doc, doc_type_code, tax_type_code)
			elif btype in (bill.TYPE_NOTA_DEB_A, bill.TYPE_NOTA_DEB_B ):
				letter = ((btype== bill.TYPE_NOTA_DEB_A) and 'A' ) or 'B'
				#type, name, address, doc, docType, ivaType
				printer.openDebitNoteTicket(letter, cli.name, cli.address, doc, doc_type_code, tax_type_code )
			else:
				self.printingFinished.emit(
					(False, bill, -1, 'Tipo de factura incorrecto')
				)
				return False #who cares about our result anyway but RETURN IS IMPORTANT!

			for i in bill.items:
				printer.addItem(i.description, i.quantity, i.unit_price, i.tax*100)
				self.statusChanged.emit("Imprimiendo item: %s"%i.description)
			#si no ponemos descuento posiblemente la impresion en factura A ande en la 320,si es asi, entonces tener cuidado
			#, discount=i.discount*100, discountDescription="descuento" << la impresora no toma el descuento..
			self.statusChanged.emit("Agregando pagos")
			printer.addPayment(bill.ptype and bill.ptype.name or "Efectivo", bill.total)
			self.statusChanged.emit("Cerrando factura")
			number = printer.closeDocument()

			self.statusChanged.emit("Documento impreso correctamente")
			self.printingFinished.emit( (True, bill, int(number), '') )
		except Exception, e:
			#Something GROOSSS just happend, gotta notify the other thread!
			self.printingFinished.emit( (False, bill, -1, str(e)) )
		finally:
			if (not self._persistent )and printer:
				printer.close()

#The purpose of this module is to connect the threadedprinter with the bill, and also set some stuff.
class Printer(GenericModule):
	NAME = "Printer"
	LICENSES = LICENSES_NOT_FREE
	def __init__(self, app):
		super(Printer, self).__init__(app)

	def load(self):
		self.app.window.acCancelPrinter.setVisible(True)
		#settings (maybe i should create another module for this?)
		self.dialog = self.app.uiLoader.load(":/data/ui/settings_printer.ui", self.app.settings.tabWidget)
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("Impresora"))
		printer = _db.DB.printer
		self.dialog.cbBrands.addItems(printer.BRAND_NAMES)
		speed_texts = map(str, printer.SPEEDS)
		self.dialog.cbSpeed.addItems(speed_texts)
		#TODO poner el currentIndex en -1 en los demas combobox al crearlo/vaciarlo, arregla el probleam de la signal not emmited
		#todo use .clear AND TEST!
		self.dialog.cbBrands.setCurrentIndex(-1)
		self.dialog.cbBrands.currentIndexChanged.connect(self.brandChanged)
		
		#loads printer data into the form
		#show data from current config
		self.dialog.cbBrands.setCurrentIndex(printer.brand)
		self.dialog.device.setText(printer.device)
		self.dialog.cbSpeed.setCurrentIndex(printer.speed)
		#order DO mathers, because previous function emits currentIndexChanged that calls brandChanged that fills this combo
		self.dialog.cbModels.setCurrentIndex(printer.model)
		#connect the rest of the slots
		self.dialog.cbModels.currentIndexChanged.connect(self.modelChanged)
		self.dialog.device.editingFinished.connect(self.deviceChanged)
		self.dialog.cbSpeed.currentIndexChanged.connect(self.speedChanged)

		#creates the threaded printing which could be run in the same thread also
		#create another thread
		self.printer_thread = QtCore.QThread()
		##force the other thread to quit when is finished (something not happening i think)
		#self.printer_thread.finished.connect(self.printer_thread.quit)
		#forces the other thread to quit when the app is about to quit
		self.app.aboutToQuit.connect(self.printer_thread.quit)

		#now we create the threadedprinter (the object that will actually print the stuff)
		self.tprinter = ThreadPrinter(self.app, printer)#pass the printer
		#and put it in the other thread
		self.tprinter.moveToThread(self.printer_thread)
		#and connect the stuff
		self.app.window.acCloseZ.triggered.connect(self.tprinter.dailyCloseZ)
		self.app.window.acCancelPrinter.triggered.connect(self.tprinter.cancel)
		#now we try to get the bill module
		bill_mod = self.app.modules.get(bills.Bills.NAME, None)
		if bill_mod:
			#and connect all the signals required for a correct printing
			#It must be done here, to retain sanity. the tprinter object is local to this module,
			#also the most logic thing is to make this module resposable for printing stuff
			#to print with the fiscal printer
			bill_mod.startPrinting.connect(self.tprinter.printBill)#, QtCore.Qt.DirectConnection) careful with this
			#to print a draft on the normal printer
			bill_mod.startPrintingDraft.connect(self.printDraft)

			#when the printing finishes we must tell the bill module, because saving the bill happens there
			#because we shouldnt touch zodb objects in other threads
			self.tprinter.printingFinished.connect(bill_mod.onPrintingFinish)
			#this signal is emitted to inform about the progress
			self.tprinter.statusChanged.connect(self.app.window.statusbar.showMessage)
		#When everythin is set, we start running the thread :)
		self.printer_thread.start()

	#Too bad we cant put this in the other thread because it uses Widgets so it belongs to the main thread
	@QtCore.Slot(object)
	def printDraft(self, bill):
		printer = QtGui.QPrinter()
		printer.setPrintProgram("Banta")
		print_diag = QtGui.QPrintDialog(printer)
		if print_diag.exec_() != QtGui.QDialog.Accepted:
			self.tprinter.printingFinished.emit(
				(False, bill, -1, '')
			)
			return
		def printList(p, pr, list, col_width):
			bottom = 0
			r = QtCore.QRect(pr)
			for i in list:
				r.setRight(r.left()+col_width)
				br = p.drawText(r, QtCore.Qt.TextWordWrap, i)
				r.setLeft(r.left()+col_width)
				bottom = max(br.bottom(), bottom)
			pr.setTop(bottom+10)
			return
		p=None
		try:
			raise Exception("alskd")
			p = QtGui.QPainter()
			p.begin(printer)
			pr = QtCore.QRect(printer.pageRect())
			#br = QtCore.QRect(printer.pageRect())
			pr.setLeft(pr.left()+20)
			#hader
			msgs = [u'Fecha y Hora', u'CUIT/DNI', u'Nombre', u'Direccion']
			col_width = pr.width()/len(msgs)
			printList(p, pr, msgs, col_width)

			msgs = map( unicode,
				( QtCore.QDateTime(bill.date).toString(), bill.client.code, bill.client.name , bill.client.address )
			)
			printList(p, pr, msgs, col_width)
			pr.setTop(pr.top()+20)
			p.drawLine(pr.left(), pr.top(),pr.right(), pr.top() )
			pr.setTop(pr.top()+20)

			#item header
			msgs = [u'Cantidad', u'Descripcion', u'Precio Unitario', u'IVA', u'Importe']
			col_width = pr.width()/len(msgs)
			printList(p, pr, msgs, col_width)
			#items
			for i in bill.items:
				if pr.top()>=pr.bottom()-100:
					printer.newPage()
					pr.setTop(printer.pageRect().top()+20)
				items = map(unicode, ( i.quantity, i.description, i.unit_price, i.tax_total, i.price))
				printList(p, pr, items, col_width)
			#This was not in the documentation, i've spent lots of time searching the solution
			#Too god i've developed a good sense of "hunch"
			pr.setTop(pr.top()+20)
			items = (u"Iva $%s"%bill.tax, u"Total $%s"%bill.total)
			printList(p, pr, items, col_width)
			pr.setTop(pr.top()+20)
			p.drawLine(pr.left(), pr.top(), pr.right(), pr.top() )
			pr.setTop(pr.top()+20)
			printList(p, pr, [u'Presupuesto generado con Banta. MoonGate.com.ar'], pr.width() )
			self.tprinter.printingFinished.emit( (True, bill, -1, '') )
		except Exception, e:
			#Something GROOSSS just happend, gotta notify the other thread!
			self.tprinter.printingFinished.emit( (False, bill, -1, str(e)) )
		finally:
			if p: p.end()


	### All this below are for the Config
	@QtCore.Slot(int)
	def brandChanged(self, i):
		"""
		Updates the models when the brand changes
		"""
		#this sets the current index to -1 
		self.dialog.cbModels.clear() 
		if i == 0:
			from banta.packages.non_free.printer.hasarPrinter import HasarPrinter
			models = HasarPrinter.MODEL_NAMES
		else:
			from banta.packages.non_free.printer.epsonPrinter import EpsonPrinter
			models = list (EpsonPrinter.MODEL_NAMES)
		self.dialog.cbModels.addItems(models)
		_db.DB.printer.brand = i
		
	@QtCore.Slot(int)
	def modelChanged(self, i):
		_db.DB.printer.model = i
	
	@QtCore.Slot()
	def deviceChanged(self):
		#editingFinished dont pass any value...
		_db.DB.printer.device = self.dialog.device.text()
	
	@QtCore.Slot(int)
	def speedChanged(self, speed):
		_db.DB.printer.speed = speed
		
DOC_TYPE_ATTRS=(
	'DOC_TYPE_CUIT',
	'DOC_TYPE_LIBRETA_ENROLAMIENTO',
	'DOC_TYPE_LIBRETA_CIVICA',
	'DOC_TYPE_DNI',
	'DOC_TYPE_PASAPORTE',
	'DOC_TYPE_CEDULA',
	'DOC_TYPE_SIN_CALIFICADOR'
)

IVA_TYPE_ATTRS =(
	'IVA_TYPE_CONSUMIDOR_FINAL',
	'IVA_TYPE_RESPONSABLE_INSCRIPTO',
	'IVA_TYPE_RESPONSABLE_NO_INSCRIPTO',
	'IVA_TYPE_EXENTO',
	'IVA_TYPE_NO_RESPONSABLE',
	'IVA_TYPE_RESPONSABLE_NO_INSCRIPTO_BIENES_DE_USO',
	'IVA_TYPE_RESPONSABLE_MONOTRIBUTO',
	'IVA_TYPE_MONOTRIBUTISTA_SOCIAL',
	'IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL',
	'IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL_SOCIAL',
	'IVA_TYPE_NO_CATEGORIZADO'
)