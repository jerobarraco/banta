# -*- coding: utf-8 -*-
""" Module for listing bills
"""
#TODO this could be a "report" (??) (at this moment cant be a report because:
# 1) need double click to reopen a bill, 2) when exporting it asks to purge drafts
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
import datetime
import csv
import banta.packages as _pack
import PySide.QtCore as _qc
import PySide.QtGui as _qg


import banta.db as _db
import banta.utils

REQUIRES = list()
LICENSES = ()

class BillList(_pack.GenericModule):
	REQUIRES = (_pack.GenericModule.P_ADMIN, )
	NAME = "bill list"
	def __init__(self, app):
		super(BillList, self).__init__(app)

	def load (self):
		self.widget = self.app.uiLoader.load(":/data/ui/bill_list.ui")
		self.app.window.tabWidget.addTab(self.widget, self.app.window.tr("Lista de Facturas"))

		month_start, today, month_end = banta.utils.currentMonthDates()
		self.widget.dBListMin.setDate(month_start)
		self.widget.dBListMax.setDate(month_end)

		self.widget.bBListShow.clicked.connect(self.show)
		self.widget.bExportDraft.clicked.connect(self.exportDrafts)
		self.widget.tBList.doubleClicked.connect(self.showBill)
		
	@_qc.Slot()
	def exportDrafts(self):
		#TODO purge drafts with a menu action
		"""Exports DRAFTS from the bill list, also deleting them"""

		#ensure we dont work with uncommited data
		_db.DB.commit()

		name = "banta_bills-" + str( datetime.datetime.now()).replace(":", "_") + ".csv"
		#file = codecs.open(name, "wb",'utf-8')#dont even care for thsi...
		#writer = banta.utils.UnicodeCSVWriter(file,delimiter=';', quotechar='"',  quoting=csv.QUOTE_MINIMAL)
		#this too must be encoded, otherway it'll say that they must be exactly one character big
		delimit = ';'.encode('utf-8')
		quote = '"'.encode('utf-8')
		writer = csv.writer(open(name, 'wb'), delimiter=delimit, quotechar=quote, quoting=csv.QUOTE_MINIMAL)

		ret = _qg.QMessageBox.question(self.app.window, self.app.window.tr("Banta - Exportar"),
			self.app.window.tr('¿Desea eliminar los presupuestos?') ,
			_qg.QMessageBox.Yes | _qg.QMessageBox.No,
			_qg.QMessageBox.No
		)
		delete = (ret == _qg.QMessageBox.Yes)

		tmin, tmax = banta.utils.getTimesFromFilters(self.widget.dBListMin, self.widget.dBListMax )
		#Write headers
		row = []
		for c in range (self.widget.tBList.columnCount()):
			hi = self.widget.tBList.horizontalHeaderItem(c)
			row.append(hi.text().encode('utf-8'))
		try:
			writer.writerow(row)
		except:
			pass
		#looks like i cant delete on the fly WHEN USING MIN AND MAX! so i need to store the keys to be deleted and delete them later
		#if the list is too big, it could mean problems
		to_delete = []
		#_db.DB.bills.values()[:] doesnt work
		for bill in _db.DB.bills.values(min= tmin, max=tmax):
			#Documentation on python says that the data is "stringified" using str() so no need to call it here
			#I have NO idea why the csv writer tries to convert stuff to Ascii even when the file is open with codecs...
			#Only solution is to decode stuff to ascii.. this in python 3 will be easier...

			d =( bill.time, bill.number, bill.date, bill.TYPE_NAMES[bill.btype].encode('utf-8', 'replace'),
				bill.client.name.encode('utf-8', 'replace'), bill.tax, bill.total, len(bill.items), bill.strPrinted(),
				bill.user and bill.user.name.encode('utf-8', 'replace')
			)
			try:
				writer.writerow(d)
				if delete and not bill.printed:
					#If the user wants to delete a bill and the bill is a draft
					#then is stored for deletion
					#this is inside the try, so if there's an exception while trying to write, it wont get deleted
					to_delete.append(bill.time)
			except:
				pass

		for k in to_delete:
			del _db.DB.bills[k]

		if to_delete:
			#only commit if we've deleted something
			_db.DB.commit("system", "drafts exported and purged")
		logger.info("Draft exported correctly, %s registries deleted from db"%len(to_delete))

	@_qc.Slot()
	def show(self):
		tb = self.widget.tBList
		tb.setRowCount(0)
		total = 0.0
		tax_total = 0.0
		tmin, tmax = banta.utils.getTimesFromFilters(self.widget.dBListMin, self.widget.dBListMax )
		for b in _db.DB.bills.values(min = tmin, max = tmax):
			r = tb.rowCount()
			tb.setRowCount(r+1)
			total += b.total
			tax_total += b.tax
			#we convert the DateTime to QDateTime to use Qt's translation system
			#TODO solve the "problem" of a null user (¿?)
			texts = (str(b.time), str(b.number), _qc.QDateTime(b.date).toString(), b.TYPE_NAMES[b.btype],
							 b.client.name, str(b.tax), str(b.total) , str(len(b.items)),
							 b.strPrinted(), b.user and b.user.name
			)
			#notice len(b.items) != sum ([q for b.items.quantity])
			for c, t in enumerate(texts):
				tb.setItem(r, c, _qg.QTableWidgetItem(t))
		self.app.window.statusbar.showMessage("Total $%s (IVA %s)"%(total,tax_total))
		#just to test
		#self.app.modules['bills'].printDraft(zodb.bills[zodb.bills.keys()[-1]])

	@_qc.Slot(_qc.QModelIndex)
	def showBill(self, mi):
		row = mi.row()
		code = int(self.widget.tBList.item(row, 0).text())
		b = _db.DB.bills[code].copy()
		self.app.modules['bills'].showBill(b)
