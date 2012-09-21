# -*- coding: utf-8 -*-
# TODO refactor the imports
from __future__ import absolute_import, print_function, unicode_literals
from PySide.QtCore import QAbstractTableModel, Qt
from PySide import QtCore, QtGui

from banta.packages.generic import GenericModule
import banta.db.models as _mods

class TBillModel(QAbstractTableModel):
	#TODO delete other columns
	#TODO: translate

	HEADERS = (	"Nombre", "IVA", "Actual")
	def __init__(self, parent=None):
		QAbstractTableModel.__init__(self, parent)

	def rowCount(self, parent=None):
		return len(_mods.Bill.TYPE_NAMES)

	def columnCount(self, parent=None):
		return 1

	def data(self, index, role=0):
		if not index.isValid():
			return None

		if index.row() >= len(_mods.Bill.TYPE_NAMES) or index.row() < 0:
			return None

		if (role == Qt.DisplayRole) or (role == Qt.EditRole):
			name = _mods.Bill.TYPE_NAMES[index.row()]
			pair = (name, 0.0, 0)
			return pair[index.column()]
		else:
			return None

	def headerData(self, section=0, orientation=None, role=0):
		if role != Qt.DisplayRole:
			return None
		if orientation == Qt.Horizontal:
			return self.trUtf8(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		if index.isValid():
			return  Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return None #Qt.ItemIsEnabled

class TBill(GenericModule):
	REQUIRES = (GenericModule.P_ADMIN, )
	NAME = 'Bill Types'
	def load(self):
		self.model = TBillModel()
		self.app.window.cb_tbill.setModel(self.model)
