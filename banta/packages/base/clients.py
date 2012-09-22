# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
#TODO refactor imports
from PySide.QtCore import QAbstractTableModel, Qt
from PySide import QtCore, QtGui
from PySide.QtCore import QT_TRANSLATE_NOOP
from banta.packages import GenericModule
import banta.utils
import banta.db as _db

class ClientDelegate(QtGui.QStyledItemDelegate):
	def __init__(self, parent = None):
		QtGui.QStyledItemDelegate.__init__(self, parent)

	def createEditor(self, parent, option, index):
		self.initStyleOption(option, index)
		col = index.column()
		if col == 3:
			editor = QtGui.QComboBox(parent)
			editor.addItems(_db.models.Client.TAX_NAMES)
			return editor
		elif col == 4:
			editor = QtGui.QComboBox(parent)
			editor.addItems(_db.models.Client.DOC_NAMES)
			return editor
		elif col == 5:
			editor = QtGui.QComboBox(parent)
			editor.addItems(_db.models.Client.IB_NAMES)
			return editor
		else:
			return super(ClientDelegate, self).createEditor(parent, option, index)

	def setEditorData(self, editor, index):
		#Sets de dat to the editor (current item)
		if index.column() in (3, 4, 5):#columns 3, 4, 5 works the same
			#Gets the data for the item, in edit mode
			d = index.data(Qt.EditRole)
			#same as
			#d = index.model().data(index, Qt.EditRole)
			#sets the current index (data for this column is just the index)
			editor.setCurrentIndex(d)
		else:
			super(ClientDelegate, self).setEditorData(editor, index)

	def setModelData(self, editor, model, index):
		#Set the data from the editor back to the model (usually changed)
		if index.column() in (3,4,5):
			#tells the model to change de data for the item in index, the data is the index of the editor, in editrole
			model.setData(index, editor.currentIndex(), Qt.EditRole)
		else:
			super(ClientDelegate, self).setModelData(editor, model, index)
			#QtGui.QStyledItemDelegate.setModelData(editor, model, index)

class ClientModel(QAbstractTableModel):
	HEADERS = (
		QT_TRANSLATE_NOOP('clients', "DNI/CUIT/CUIL"),
		QT_TRANSLATE_NOOP('clients', "Nombre"),
		QT_TRANSLATE_NOOP('clients', "Dirección"),
		QT_TRANSLATE_NOOP('clients', "Tipo Iva"),
		QT_TRANSLATE_NOOP('clients', "Tipo Documento"),
		QT_TRANSLATE_NOOP('clients', "Ingresos Brutos"),
		QT_TRANSLATE_NOOP('clients', "Saldo")
	)
	def __init__(self, parent=None):
		QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)

	def rowCount(self, parent=None):
		#todo use max_rows
		return len(_db.DB.clients)

	def columnCount(self, parent=None):
		return 7

	def index(self, row, col, parent=None):
		"""Creates an index for someone OUTSIDE the model with improved speed"""
		#it redefines the base function, which creates a simple index. Indexes created through this function includes the actual
		#object in index.internalPointer that way, calling .data in the same index several times, will require less time
		#This makes the whole app some seconds faster (on a low end pc and 3K products) but requires a little more RAM (in theory)
		#reads the item from the db
		#The .internalPointer should NOT be used outside THIS MODEL (in theory)
		if (row<0) or (col<0) or (row >= len(_db.DB.clients)):
			return self.createIndex(row, col)#returns an invalid index
		else:
			pro = _db.DB.clients.values()[row]
			return self.createIndex(row, col, pro)

	def data(self, index, role=0):
		if not index.isValid():
			return None

		#userRole is for searchign in the combobox (for other model)
		if role not in (Qt.DisplayRole, Qt.EditRole, Qt.UserRole): #maybe faster, easier to understand, compact
			return None

		#technically faster
		cli = index.internalPointer()
		col = index.column()
		#Most probably is a display role
		if role == Qt.DisplayRole:
			if col == 0:
				return cli.code
			elif col ==1:
				return cli.name
			elif col == 2:
				return cli.address
			elif col == 3:
				return  cli.taxStr()
			elif col == 4:
				return cli.docStr()
			elif col == 5:
				return cli.IBStr()
			elif col == 6:
				return cli.balance
			else:
				return None
		#2nd probably a edit role
		elif role == Qt.EditRole:
			if col == 0:
				return cli.code
			elif col == 1:
				return cli.name
			elif col == 2:
				return cli.address
			elif col == 3 :
				return cli.tax_type
			elif col == 4:
				return cli.doc_type
			elif col == 5:
				return cli.ib_type
			elif col == 6:
				return cli.balance
		elif role == Qt.UserRole:#User role is usually for searching
			return cli.code
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
			#if index.column() == 0 :
			#	return  Qt.ItemIsEnabled | Qt.ItemIsSelectable
			return  Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		if index.isValid() and (role == Qt.EditRole):
			#dangerous
			cli = index.internalPointer()
			col = index.column()
			if col == 0:
				#"move" a client in the table
				#check if the code has changed, so it dont delete it accidentally
				if cli.code == value:
					return False
				#also check to NOT replace another product
				if value in _db.DB.clients.keys():
					#if the pro.code != value, but value is in the db, then they are 2 different products..
					QtGui.QMessageBox.warning(self.parent_widget, "Banta", self.tr("Ya existe un cliente con ese código."))
					return False
				#The del must come BEFORE!! there's a chance that the code hasn't changed, in which case it'll end up DELETING the product
				#it should be fixed with the if
				del _db.DB.clients[cli.code]
				cli.code = value
				_db.DB.clients[value] = cli
			elif col ==1:
				cli.name = value
			elif col ==2:
				cli.address = value
			elif col == 3:
				cli.tax_type = value
			elif col == 4:
				cli.doc_type = value
			elif col == 5:
				cli.ib_type = value
			elif col == 6:
				cli.balance = value
			_db.DB.commit()
			return True
		return False

	def insertRows(self, position, rows, index=None):
		for i in range(rows):
			code, ok = QtGui.QInputDialog.getText(self.parent_widget, self.tr("Nuevo Cliente"),
				self.tr("Ingrese el DNI/CUIT/CUIL"), QtGui.QLineEdit.Normal, "")
			if not ok:
				return False
			if code in _db.DB.clients.keys():
				QtGui.QMessageBox.information(self.parent_widget, self.tr("Nuevo Cliente"),
					self.tr( "Ya existe un cliente con ese código."))
				return False
			#this would be slow, because it'll convert all the keys to a list, also can oly be called after inserting
			#endpos = tuple(_db.DB.clients.keys()).index(code)
			#this is faster, also, it can be called before inserting. is a little trick, basically we count all the items before
			endpos = len(_db.DB.clients.keys(max=code, excludemax=True))
			self.beginInsertRows(QtCore.QModelIndex(), endpos, endpos)
			cli = _db.models.Client(code, "-")
			_db.DB.clients[cli.code] = cli
			self.endInsertRows()
			position+=1
		_db.DB.commit()
		return True

	def removeRows(self, position, rows, index=None):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			#i use values and c.code in case .keys() return the items in different order
			c = _db.DB.clients.values()[position]
			del _db.DB.clients[c.code] #when i remove one item, the next takes it index
		_db.DB.commit()
		self.endRemoveRows()
		return True

	def addItem(self, tpay=None):
		#Todo implement??
		pass
	pass

class Clients(GenericModule):
	REQUIRES = (GenericModule.P_ADMIN, )
	NAME = 'Clients'
	def __init__(self, app):
		super(Clients, self).__init__(app)
		self.model = ClientModel(self.app.window)
		#self.app.window.v_clients.setModel(self.model)
		self.app.window.cb_clients.setModel(self.model)
		self.proxy_model = QtGui.QSortFilterProxyModel(self.app.window.v_clients)
		self.proxy_model.setSourceModel(self.model)
		self.proxy_model.setFilterKeyColumn(1)
		self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
		#This is important so when a row is inserted, it is selected, so the client dont have to scroll 300000 items
		# to change the basic info of a new (and blank) item (so it has no name either)
		self.proxy_model.rowsInserted.connect(self.rowInserted)
		self.app.window.v_clients.setModel(self.proxy_model)

		delegate = ClientDelegate(self.app.window)
		self.app.window.v_clients.setItemDelegate(delegate) #i love qt
		#self.window.v_clients.setItemDelegateForColumn(3, delegate) #i love qt
		#self.window.v_clients.setItemDelegateForColumn(4, delegate) #i love qt
		#self.window.v_clients.setItemDelegateForColumn(5, delegate) #i love qt
		self.app.window.bCliNew.clicked.connect(self.new)
		self.app.window.bCliDelete.clicked.connect(self.delete)
		self.app.window.eCliCode.textChanged.connect(self.proxy_model.setFilterWildcard)
		self.app.window.bClientAccount.setVisible(False)

	@QtCore.Slot()
	def new(self):
		#new instances are inserted in whatever place they get, keys are sorted.. so it doesnt matter
		self.model.insertRows(0, 1)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def rowInserted(self, parent, start, end):
		"""This slot gets called when a row is inserted (read new) when a row is inserted, we dont actually know where
		 it gets inserted because keys are sorted, and key bounds position """

		self.app.window.v_clients.selectRow(start)
		i = self.app.window.v_clients.selectedIndexes()[0]
		self.app.window.v_clients.scrollTo(i)

	@QtCore.Slot()
	def delete(self):
		selected = self.app.window.v_clients.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.proxy_model.removeRows(r, 1)