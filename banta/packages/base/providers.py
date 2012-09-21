# -*- coding: utf-8 -*-
#TODO refactor code
from __future__ import absolute_import, print_function, unicode_literals
from PySide.QtCore import QAbstractTableModel, Qt, QT_TRANSLATE_NOOP
from PySide import QtCore, QtGui
from banta.packages.generic import GenericModule

import banta.db as _db
import banta.utils

class ProviderModel(QAbstractTableModel):
	HEADERS = (
		QT_TRANSLATE_NOOP("providers", "Código"),
		QT_TRANSLATE_NOOP("providers", "Nombre"),
		QT_TRANSLATE_NOOP("providers", "Dirección"),
		QT_TRANSLATE_NOOP("providers", 'Teléfono'),
		QT_TRANSLATE_NOOP("providers", 'Correo')
	)
	columns = 5
	def __init__(self, parent=None):
		QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)

	def rowCount(self, parent=None):
		return len(_db.DB.providers)

	def columnCount(self, parent=None):
		return self.columns

	def data(self, index, role=0):
		"""Returns the data for an item
		The role indicates which type of data should be returned
		Accepts the UserRole because products uses this model too. so it works on findData"""
		if not index.isValid():
			return None

		if role not in (Qt.DisplayRole, Qt.EditRole, Qt.UserRole):
			return None

		row = index.row()
		col = index.column()

		if (row >= len(_db.DB.providers)):
			return None

		pro = _db.DB.providers.values()[row]

		if (role == Qt.UserRole) or col == 0:
			#If the rol is UserRole returns the code. I'm not sure this is the optimal way, but i understood that from the doc
			return pro.code
		elif col == 1:
			return pro.name
		elif col == 2:
			return pro.address
		elif col == 3:
			return pro.phone
		elif col == 4:
			return pro.mail
		return None

	def headerData(self, section=0, orientation=None, role=0):
		"""Returns the data for each header"""
		if role != Qt.DisplayRole:
			return None
		if orientation == Qt.Horizontal:
			return self.tr(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		#Returns the flag for each item

		if index.isValid():
			#We only let edit fields that arent the column 0 (code)
			if index.column() == 0 :
				return	Qt.ItemIsEnabled | Qt.ItemIsSelectable
			return	Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return None #Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		"""Sets the data of a item.
		Returns True|False """

		if index.isValid() and (role == Qt.EditRole):
			pro = _db.DB.providers.values()[index.row()]
			col = index.column()
			if col == 0:
				return False
			elif col == 1:
				pro.name = value
			elif col == 2:
				pro.address = value
			elif col == 3:
				pro.phone = value
			elif col == 4:
				pro.mail = value
			_db.DB.commit()
			return True
		return False

	def insertRows(self, position, rows, index=None):
		for i in range(rows):
			code, ok = QtGui.QInputDialog.getText(self.parent_widget, self.tr("Nuevo Proveedor"),
				self.tr("Ingrese el código"), QtGui.QLineEdit.Normal, "")
			if not ok:
				return False
			self.beginInsertRows(QtCore.QModelIndex(), position, position)
			prov = _db.models.Provider(code)
			_db.DB.providers[prov.code] = prov
			self.endInsertRows()
			position+=1
		_db.DB.commit()
		return True

	def removeRows(self, position, rows, index=None):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			#I use .values() and c.code in case .keys() return the items in different order
			c = _db.DB.providers.values()[position]
			del _db.DB.providers[c.code] #when i remove one item, the next takes it index
		_db.DB.commit()
		self.endRemoveRows()
		return True

#Needed on product delegate
MODEL = ProviderModel()
class Providers(GenericModule):
	REQUIRES = (GenericModule.P_ADMIN, )
	NAME = 'Providers'
	def __init__(self, app):
		super(Providers, self).__init__(app)
		self.model = MODEL

	def load(self):
		self.app.window.vProviders.setModel(self.model)
		self.app.window.bProvNew.clicked.connect(self.new)
		self.app.window.bProvSearch.clicked.connect(self.search)
		self.app.window.bProvDelete.clicked.connect(self.delete)

	@QtCore.Slot()
	def new(self):
		self.model.insertRows(0, 1)

	@QtCore.Slot()
	def search(self):
		text = self.app.window.eProvName.text().lower()#case insensitive
		self.app.window.vProviders.selectRow(-1)
		for i, pro in enumerate(_db.DB.providers.values()):
			if text in pro.name.lower():
				self.app.window.vProviders.selectRow(i)
				break

	@QtCore.Slot()
	def delete(self):
		selected = self.app.window.vProviders.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.model.removeRows(r, 1)