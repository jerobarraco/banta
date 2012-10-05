# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import PySide.QtCore as _qc
from PySide import QtCore

import banta.db as _db
import banta.packages as _pack
import banta.utils

class TPayModel(_qc.QAbstractTableModel):
	HEADERS = (
		_qc.QT_TRANSLATE_NOOP("typepay", "Nombre"),
		_qc.QT_TRANSLATE_NOOP("typepay", "Recargo")
	)
	def __init__(self, parent=None):
		_qc.QAbstractTableModel.__init__(self, parent)
		self.tr = banta.utils.unitr(self.trUtf8)

	def rowCount(self, parent=None):
		return len(_db.DB.typePays)

	def columnCount(self, parent=None):
		return 2

	def data(self, index, role=0):
		if not index.isValid():
			return None
		row = index.row()
		if row >= len(_db.DB.typePays):
			return None

		if (role not in (_qc.Qt.DisplayRole, _qc.Qt.EditRole)):
			return None

		col = index.column()
		tp = _db.DB.typePays[row]
		if col == 0:
			return tp.name
		elif col == 1:
			return tp.markup

		return None

	def headerData(self, section=0, orientation=None, role=0):
		if role != _qc.Qt.DisplayRole:
			return None
		if orientation == _qc.Qt.Horizontal:
			return self.tr(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		if index.isValid():
			return  _qc.Qt.ItemIsEditable | _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable #QAbstractItemModel::flags(index) |
		#Is needed in case of a bad index
		return _qc.Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		if index.isValid() and (role == _qc.Qt.EditRole):
			tp = _db.DB.typePays[index.row()]
			if index.column() == 0:
				tp.name = value
			elif index.column() ==1:
				tp.markup = float(value)
			_db.DB.commit()
			self.dataChanged.emit(index, index)
			return True
		return False

	def insertRows(self, position, rows, index=None):
		self.beginInsertRows(_qc.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			_db.DB.typePays.append(_db.models.TypePay(""))
		_db.DB.commit()
		self.endInsertRows()
		return True

	def removeRows(self, position, rows, index=None):
		self.beginRemoveRows(_qc.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			del _db.DB.typePays[position] #when i remove one item, the next takes it index
		_db.DB.commit()
		self.endRemoveRows()
		return True

class TPay(_pack.GenericModule):
	REQUIRES = (_pack.GenericModule.P_ADMIN, )
	NAME = "pay types"
	def __init__(self, app):
		super(TPay, self).__init__(app)
		self.model = TPayModel()
		#this is needed even if the module is not "loaded"
		self.app.window.cb_tpay.setModel(self.model)
		
	def load(self):
		self.dialog = self.app.uiLoader.load(":/data/ui/tpay.ui")
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("Tipos de Pago"))
		self.dialog.v_tpay.setModel(self.model)
		
		self.dialog.bTPNew.clicked.connect(self.new)
		self.dialog.bTPSearch.clicked.connect(self.search)
		self.dialog.bTPDelete.clicked.connect(self.delete)

	@QtCore.Slot()
	def new(self):
		self.model.insertRows(0, 1)

	@QtCore.Slot()
	def search(self):
		#Searches for a TypePay using the name in the gui and selects it on the grid
		#This is not the correct way to search, use the model search function
		text = self.dialog.eTPName.text()
		self.dialog.v_tpay.selectRow(-1)
		for i, tp in enumerate(_db.DB.typePays):
			if text in tp.name.lower():
				self.dialog.v_tpay.selectRow(i)
				break

	@QtCore.Slot()
	def delete(self):
		selected = self.dialog.v_tpay.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.model.removeRows(r, 1)