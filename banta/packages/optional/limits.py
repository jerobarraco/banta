# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
logger = logging.getLogger(__name__)
import itertools

import PySide.QtCore as _qc
import PySide.QtGui as _qg
#cant import a submodule
import banta.utils
import banta.packages as _pack
import banta.db as _db

class LimitDelegate(_qg.QStyledItemDelegate):
	#Handles the edition on the table for each column
	def createEditor(self, parent, option, index):
		self.initStyleOption(option, index)
		col = index.column()
		editor = None
		if col == 0:
			editor = _qg.QComboBox(parent)
			editor.setModel(_pack.base.products.MODEL)
			editor.setModelColumn(0)
		elif col in (1, 2):
			editor = _qg.QDoubleSpinBox(parent)

		#else:
		#	#Usando setItemDelegateForColumn esto no se hace muy necesario, lo dejo por las dudas.
		#	return _qg.QStyledItemDelegate.createEditor(self, parent, option, index)
		return editor

	def setEditorData(self, editor, index):
		#Sets de data to the editor (current item)
		col = index.column()
		d = index.data(_qc.Qt.EditRole)
		if col == 0:
			#d is Product code
			#Searchs the code in the combo, (which uses the provider model)
			if d< 0: return None
			#BUT findData will look the code "d" in HIS model (products) using the qt.UserRole (user role is used for this)
			i = editor.findData(d)
			if i< 0: return None
			editor.setCurrentIndex(i)
		elif col in (1, 2):
			editor.setValue(d)
		#else:
		#	_qg.QStyledItemDelegate.setEditorData(self, editor, index)

	def setModelData(self, editor, model, index):
		#Set the data from the editor back to the model (usually changed)
		col = index.column()
		data = None
		if col == 0:
			i = editor.currentIndex()
			data = editor.itemData(i)
		elif col in (1, 2):
			data = editor.value()

			#model.setData(index, editor.itemData(i), _qc.Qt.EditRole)
		#else:
		#	_qg.QStyledItemDelegate.setModelData(self, editor, model, index)
		model.setData(index, data, _qc.Qt.EditRole)

class LimitModel(_qc.QAbstractTableModel):
	HEADERS = (#el encode es UNICAMENTE para el tr
		_qc.QT_TRANSLATE_NOOP("limits", "Producto"),
		_qc.QT_TRANSLATE_NOOP("limits", "Cantidad"),
		_qc.QT_TRANSLATE_NOOP("limits", "Monto"),
	)
	columns = 3
	def __init__(self, parent=None):
		_qc.QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)

	def rowCount(self, parent=None):
		return len(_db.DB.limits)

	def columnCount(self, parent=None):
		return self.columns

	def data(self, index, role=0):
		"""Returns the data for an item
		The role indicates which type of data should be returned
		Accepts the UserRole because products uses this model too. so it works on findData"""
		if not index.isValid():
			return None

		if role not in (_qc.Qt.DisplayRole, _qc.Qt.EditRole):
			return None

		row = index.row()
		col = index.column()

		if (row >= self.rowCount()):
			return None

		lim = _db.DB.limits[row]

		if col == 0:
			if lim.product is None:
				return None
			if role == _qc.Qt.DisplayRole:
				return lim.product.name
			else:
				return lim.product.code

		elif col == 1:
			return lim.quantity
		elif col == 2:
			return lim.amount
		return None

	def headerData(self, section=0, orientation=None, role=0):
		"""Returns the data for each header"""
		if role != _qc.Qt.DisplayRole:
			return None
		if orientation == _qc.Qt.Horizontal:
			return self.tr(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		"""Returns the flag for each item"""
		if index.isValid():
			return	_qc.Qt.ItemIsEditable | _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return None #Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		"""Sets the data of a item.
		Returns True|False """

		if index.isValid() and (role == _qc.Qt.EditRole):
			lim = _db.DB.limits[index.row()]
			col = index.column()
			if col == 0:
				lim.product = _db.DB.products[value]
			elif col == 1:
				lim.quantity = value
			elif col == 2:
				lim.amount = value
			_db.DB.commit()
			return True
		return False

	def insertRows(self, position, rows, index=None):
		for i in range(rows):
			self.beginInsertRows(_qc.QModelIndex(), position, position)
			lim = _db.models.Limit()
			_db.DB.limits.append(lim)
			self.endInsertRows()
			position+=1
		_db.DB.commit()
		return True

	def removeRows(self, position, rows, index=None):
		self.beginRemoveRows(_qc.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			del _db.DB.limits[position] 
			#when i remove one item, the next takes it index
		_db.DB.commit()
		self.endRemoveRows()
		return True

class LimitCheck():
	prod_code = None
	quantity = 0
	amount = 0
	def __init__(self, limit):
		self.prod_code = limit.product.code
		self.limit = limit

	def addQuantity(self, quant):
		if self.limit.quantity:
			self.quantity += quant
			return self.quantity <= self.limit.quantity
		return True

	def exQuantity(self):
		"""Returns the remaining quantity"""
		return self.quantity - self.limit.quantity

	def addAmount(self, amount):
		if self.limit.amount:#check if it's not 0
			self.amount += amount
			return self.amount <= self.limit.amount
		return True

	def exAmount(self):
		return self.amount - self.limit.amount

class Limits(_pack.GenericModule):
	NAME = "Limits"
	def __init__(self, app):
		super(Limits, self).__init__(app)
		self.model = LimitModel(app.window)

	def load(self):
		self.dialog = self.app.uiLoader.load(":/data/ui/limits.ui", self.app.settings.tabWidget)
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("Límites"))
		self.dialog.v_limits.setModel(self.model)
		self.dialog.v_limits.setItemDelegate(LimitDelegate()) #i love qt
		self.dialog.bLimNew.clicked.connect(self.new)
		self.dialog.bLimDelete.clicked.connect(self.delete)
		bill_mod_name = _pack.base.bills.Bills.NAME
		self.bill_mod = self.app.modules[bill_mod_name]
		self.app.window.acBillPrint.triggered.disconnect()#self.bill_mod.saveBill
		self.app.window.acBillPrint.triggered.connect(self.saveBill)

	@_qc.Slot()
	def saveBill(self):
		error_msg = self.overLimits()
		if error_msg:
			_qg.QMessageBox.critical(self.app.window, "Banta", error_msg)
		else:
			self.bill_mod.printBill()

	def overLimits(self):
		"""Checks all the limits!
		returns a string with an error message (if any)"""
		#obtains the dates for current month, and convert it to ints
		tmin, today, tmax = map(banta.utils.dateTimeToInt, banta.utils.currentMonthDates())
		#creates a dictionary of all the limits
		checks = dict([
			#for each limit, it creates a LimitCheck and uses the product code as the key
			(lim.product.code, LimitCheck(lim))
			for lim in _db.DB.limits ])

		over_quant_msg = self.dialog.tr(
				("Se ha excedido en la cantidad permitida para el producto código %s." +
					"\nExceso de %s unidad(es)."
				)
		)
		over_amount_msg = self.dialog.tr(
			("Se ha excedido en el monto permitido para el producto código %s." +
			"\nExceso de $%s.")
		)

		client = self.bill_mod.bill.client
		#make sure we check the current bill.
		#this chains both iterables, this way it saves up memory by not converting to list
		bills = itertools.chain([self.bill_mod.bill], _db.DB.bills.values(min = tmin, max = tmax) )
		for b in bills:
			if client == b.client:
				for i in b.items:
					#tries to get a limit for the current item
					lim = checks.get(i.product.code)
					if lim:
						if not lim.addQuantity(i.quantity):
							return over_quant_msg % (lim.prod_code, lim.exQuantity())
						if not lim.addAmount(i.price):
							return over_amount_msg % (lim.prod_code, lim.exAmount())
		return None

	@_qc.Slot()
	def new(self):
		self.model.insertRows(0, 1)

	@_qc.Slot()
	def delete(self):
		selected = self.dialog.v_limits.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.model.removeRows(r, 1)