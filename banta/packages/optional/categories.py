# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

import PySide.QtCore as _qc
import PySide.QtGui as _qg

import banta.packages as _pack
import banta.db as _db
import banta.utils

class CategoryModel(_qc.QAbstractTableModel):
	HEADERS = (
		_qc.QT_TRANSLATE_NOOP("categories", "Nombre"),
	)
	def __init__(self, parent=None):
		_qc.QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)

	def rowCount(self, parent=None):
		return len(_db.DB.categories)

	def columnCount(self, *args, **kwargs):
		return 1

	def data(self, index, role= 0):
		if not index.isValid():
			return None

		if (role not in (_qc.Qt.DisplayRole, _qc.Qt.EditRole)):
			return None

		row = index.row()
		if row >= len(_db.DB.categories):
			return None

		col = index.column()
		cat = _db.DB.categories[row]
		if col == 0:
			return cat.name

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
			return  _qc.Qt.ItemIsEditable | _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable
		#Is needed in case of a bad index
		return _qc.Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		if index.isValid() and (role == _qc.Qt.EditRole):
			cat = _db.DB.categories[index.row()]
			col = index.column()
			if col == 0:
				cat.name = value
			_db.DB.commit()
			self.dataChanged.emit(index, index)
			return True
		return False

	def insertRows(self, position, rows, index=None):
		for i in range(rows):
			name, ok = _qg.QInputDialog.getText(self.parent_widget,
				self.tr("Rubros"),
				self.tr("Ingrese el nombre del rubro"),	_qg.QLineEdit.Normal, "")

			if not ok:
				return False

			self.beginInsertRows(_qc.QModelIndex(), position, position)
			cat = _db.models.Category(name)
			#zodb.categories is a PersistentList, so we can append and insert items by their position (like a normal Array)
			#this will probably change later, because is not a LazyLoading array..
			_db.DB.categories.insert(position, cat)
			self.endInsertRows()
			position += 1
		_db.DB.commit()

	def removeRows(self, position, rows, index = None):
		self.beginRemoveRows(_qc.QModelIndex(), position, position + rows - 1)

		for i in range(rows):
			_db.DB.categories.pop(position)
		_db.DB.commit()
		self.endRemoveRows()
		return True

#TODO put the model inside the Categories class, and add a function called getModel
MODEL =  CategoryModel()

class Categories(_pack.GenericModule):
	REQUIRES = (_pack.GenericModule.P_ADMIN, )
	NAME = "categories"
	def __init__(self, app):
		super(Categories, self).__init__(app)
		self.model = MODEL
		self.model.parent_widget = app.window

	def load(self):
		self.dialog = self.app.uiLoader.load(":/data/ui/categories.ui")
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("Rubros"))
		self.dialog.v_categories.setModel(self.model)
		
		self.dialog.bCatNew.clicked.connect(self.new)
		self.dialog.bCatDelete.clicked.connect(self.delete)
		self.dialog.bCatSearch.clicked.connect(self.search)

	def getModel(self):
		return self.model

	@_qc.Slot()
	def new(self):
		self.model.insertRows(0, 1)

	@_qc.Slot()
	def delete(self):
		selected = self.dialog.v_categories.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.model.removeRows(r, 1)

	@_qc.Slot()
	def search(self):
		#Searches for a TypePay using the name in the gui and selects it on the grid
		text = self.dialog.eCatName.text()
		self.dialog.v_categories.selectRow(-1)
		for i, cat in enumerate(_db.DB.categories):
			if text in cat.name.lower():
				self.dialog.v_categories.selectRow(i)
				break