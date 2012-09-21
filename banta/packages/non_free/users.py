# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from PySide.QtCore import QAbstractTableModel, Qt
from PySide import QtCore, QtGui
from PySide.QtCore import QT_TRANSLATE_NOOP
import logging

from banta.packages import GenericModule
from banta.db.models import LICENSES_NOT_FREE
from banta.db.models import User
import banta.db as _db
import banta.utils
#from db.models import User
logger = logging.getLogger(__name__)
#TODO solve the problem of the unset user on a free license
class UserModel(QAbstractTableModel):
	HEADERS = (
		QT_TRANSLATE_NOOP('users', "Nombre"),
	)
	
	def __init__(self, parent=None):
		QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)
		
	def rowCount(self, parent=None):
		return len(_db.DB.users)

	def columnCount(self, parent=None):
		return 1

	def data(self, index, role=0):
		if not index.isValid():
			return None
		#cache the row
		row = index.row()
		if (row >= len(_db.DB.users)):
			return None

		if (role not in (Qt.DisplayRole, Qt.EditRole)):
			return None
		#cache the user
		user = _db.DB.users[row]
		#cache the col
		col = index.column()
		if col == 0 :
			return user.name

		return None

	def headerData(self, section=0, orientation=None, role=0):
		if role != Qt.DisplayRole:
			return None
		if orientation == Qt.Horizontal:
			return self.tr(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		if index.isValid():
			return  Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		if index.isValid() and (role == Qt.EditRole):
			user = _db.DB.users[index.row()]
			col = index.column()
			if col == 0:
				user.name = value

			_db.DB.commit()
			return True
		return False

	def insertRows(self, position, rows, index=None):
		for i in range(rows):
			name, ok = QtGui.QInputDialog.getText(self.parent_widget,
				self.tr("Usuarios"), self.tr("Ingrese el nombre del usuario"),	QtGui.QLineEdit.Normal, "")
			
			if not ok:
				return False
			
			#end = len(_db.DB.users)
			self.beginInsertRows(QtCore.QModelIndex(), position, position)
			user = User(name)
			#zodb.users is a PersistentList , so we can append and insert items by their position (like a normal Array)
			#this will probably change later, because is not a LazyLoading array..
			_db.DB.users.insert(position, user)
			self.endInsertRows()
			position += 1
		_db.DB.commit()
			
	def removeRows(self, position, rows, index = None):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
		
		for i in range(rows):
			_db.DB.users.pop(position)
		_db.DB.commit()
		self.endRemoveRows()
		return True

class Users (GenericModule):
	REQUIRES = (GenericModule.P_ADMIN,)
	NAME = "Users"
	LICENSES = LICENSES_NOT_FREE
	def __init__(self, app):
		super(Users, self).__init__(app)
		#We create the Model here in case is needed in another module
		self.model = UserModel(self.app.window)
		self.app.window.cb_billUser.setEnabled(False)
		self.app.window.cb_billUser.setModel(self.model)

	def load(self):
		self.dialog = self.app.uiLoader.load(":/data/ui/users.ui")
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("Usuarios"))
		self.dialog.v_users.setModel(self.model)
		self.app.window.cb_billUser.setEnabled(True)
		self.dialog.bUNew.clicked.connect(self.new)
		self.dialog.bUSearch.clicked.connect(self.search)
		self.dialog.bUDelete.clicked.connect(self.delete)

	@QtCore.Slot()
	def new(self):
		self.model.insertRows(0, 1)

	@QtCore.Slot()
	def search(self):
		#Searches for a User using the name in the gui and selects it on the grid
		text = self.dialog.eUName.text()
		self.dialog.v_users.selectRow(-1)
		for i, user in enumerate(_db.DB.users):
			if text in user.name.lower():
				self.dialog.v_users.selectRow(i)
				break

	@QtCore.Slot()
	def delete(self):
		selected = self.dialog.v_users.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.model.removeRows(r, 1)