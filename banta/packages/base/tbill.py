# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import PySide.QtCore as _qc
import banta.packages as _pack
import banta.db.models as _mods
import banta.utils

class TBillModel(_qc.QAbstractTableModel):
	HEADERS = (
		_qc.QT_TRANSLATE_NOOP('typebill', "Nombre"),
	)
	def __init__(self, parent=None):
		_qc.QAbstractTableModel.__init__(self, parent)
		self.tr = banta.utils.unitr(self.trUtf8)

	def rowCount(self, parent=None):
		return len(_mods.Bill.TYPE_NAMES)

	def columnCount(self, parent=None):
		return 1

	def data(self, index, role=0):
		if not index.isValid():
			return None
		r = index.row()
		if r >= len(_mods.Bill.TYPE_NAMES):
			return None

		if (role == _qc.Qt.DisplayRole) or (role == _qc.Qt.EditRole):
			if index.column() == 0:
				return _mods.Bill.TYPE_NAMES[r]

		return None

	def headerData(self, section=0, orientation=None, role=0):
		if role != _qc.Qt.DisplayRole:
			return None
		if orientation == _qc.Qt.Horizontal:
			return self.trUtf8(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		if index.isValid():
			return  _qc.Qt.ItemIsEditable | _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return None #_qc.Qt.ItemIsEnabled

class TBill(_pack.GenericModule):
	REQUIRES = (_pack.GenericModule.P_ADMIN, )
	NAME = 'bill_types'
	def load(self):
		self.model = TBillModel()
		self.app.window.cb_tbill.setModel(self.model)
