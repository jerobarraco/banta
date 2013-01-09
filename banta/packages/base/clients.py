# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

import PySide.QtCore as _qc
import PySide.QtGui as _qg

import banta.utils
import banta.db as _db
import banta.packages as _pkg

class ClientDelegate(_qg.QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		self.initStyleOption(option, index)
		col = index.column()
		editor = None
		if col in (0, 1, 2):
			editor = _qg.QLineEdit(parent)
		elif col == 3:
			editor = _qg.QComboBox(parent)
			editor.addItems(_db.models.Client.TAX_NAMES)
		elif col == 4:
			editor = _qg.QComboBox(parent)
			editor.addItems(_db.models.Client.DOC_NAMES)
		elif col == 5:
			editor = _qg.QComboBox(parent)
			editor.addItems(_db.models.Client.IB_NAMES)
		elif col == 6:
			editor = _qg.QDoubleSpinBox(parent)
			editor.setRange(-2147483646, +2147483646)
		#else:
			#bug
			#return super(ClientDelegate, self).createEditor(parent, option, index)
		return editor

	def setEditorData(self, editor, index):
		#Sets de dat to the editor (current item)
		col = index.column()
		#Gets the data for the item, in edit mode
		d = index.data(_qc.Qt.EditRole)
		#same as
		#d = index.model().data(index, _qc.Qt.EditRole)
		if col in (0, 1, 2):
			editor.setText(d)
		elif col in (3, 4, 5):#columns 3, 4, 5 works the same
			#sets the current index (data for this column is just the index)
			editor.setCurrentIndex(d)
		elif col == 6:
			editor.setValue(d)
		#else:
		#	super(ClientDelegate, self).setEditorData(editor, index)

	def setModelData(self, editor, model, index):
		#Set the data from the editor back to the model (usually changed)
		col = index.column()
		data = None
		if col in (0, 1, 2):
			data = editor.text()
		elif col in (3,4,5):
			#tells the model to change de data for the item in index, the data is the index of the editor, in editrole
			data = 	editor.currentIndex()
		elif col == 6:
			data = editor.value()
		#else:
			#super(ClientDelegate, self).setModelData(editor, model, index)
			#_qg.QStyledItemDelegate.setModelData(editor, model, index)
		model.setData(index, data, _qc.Qt.EditRole)

class ClientModel(_qc.QAbstractTableModel):
	HEADERS = (
		_qc.QT_TRANSLATE_NOOP('clients', "DNI/CUIT/CUIL"),
		_qc.QT_TRANSLATE_NOOP('clients', "Nombre"),
		_qc.QT_TRANSLATE_NOOP('clients', "Dirección"),
		_qc.QT_TRANSLATE_NOOP('clients', "Tipo Iva"),
		_qc.QT_TRANSLATE_NOOP('clients', "Tipo Documento"),
		_qc.QT_TRANSLATE_NOOP('clients', "Ingresos Brutos"),
		_qc.QT_TRANSLATE_NOOP('clients', "Saldo")
	)
	max_rows = 0
	def __init__(self, parent=None):
		_qc.QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)
		self._setMaxRows()

	def _setMaxRows(self):
		"""Sets the rowcount in the model depending on the license, clamping if the actual rowcount is larger
		that way the data is preserved when the license expires
		Is Important to call this function when the quantity of products changes
		(in theory that's well managed using this model for adding/removing rows)
		"""
		self.max_rows = len(_db.DB.clients)

	def rowCount(self, parent=None):
		return self.max_rows

	def columnCount(self, parent=None):
		return 7

	def index(self, row, col, parent=None):
		"""Creates an index for someone OUTSIDE the model with improved speed"""
		#it redefines the base function, which creates a simple index. Indexes created through this function includes the actual
		#object in index.internalPointer that way, calling .data in the same index several times, will require less time
		#This makes the whole app some seconds faster (on a low end pc and 3K products) but requires a little more RAM (in theory)
		#reads the item from the db
		#The .internalPointer should NOT be used outside THIS MODEL (in theory)
		if (row<0) or (col<0) or (row >= self.max_rows):
			return self.createIndex(row, col)#returns an invalid index
		else:
			pro = _db.DB.clients.values()[row]
			return self.createIndex(row, col, pro)

	def data(self, index, role=0):
		if not index.isValid():
			return None

		#userRole is for searchign in the combobox (for other model)
		if role not in (_qc.Qt.DisplayRole, _qc.Qt.EditRole, _qc.Qt.UserRole): #maybe faster, easier to understand, compact
			return None

		#technically faster
		cli = index.internalPointer()

		#User role is usually for searching
		#so we put it outside to speed up a little, it could slow down if search is not common
		if role == _qc.Qt.UserRole:
			#idn is the internal identifier for a client stored in the clients vector (IOBtree)
			#there will be "casual" clients without a valid idn (-1)
			#as this model is made to handle clients that arent casual, is ok to asume we'll use valid idns
			return cli.idn
		#actually calling index.column is slow, so we avoid it in case we only wanted the userrrole
		col = index.column()
		#Most probably is a display role
		if role == _qc.Qt.DisplayRole:
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
		elif role == _qc.Qt.EditRole:
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
			#if index.column() == 0 :
			#	return  _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable
			return  _qc.Qt.ItemIsEditable | _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return _qc.Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		if index.isValid() and (role == _qc.Qt.EditRole):
			#dangerous
			cli = index.internalPointer()
			col = index.column()
			if col == 0:
				#code is not a KEY field anymore, most of this checks are useless now
				cli.code = value
			elif col ==1:
				cli.setName(value)
			elif col ==2:
				cli.setAddress(value)
			elif col == 3:
				cli.tax_type = value
			elif col == 4:
				cli.doc_type = value
			elif col == 5:
				cli.ib_type = value
			elif col == 6:
				cli.balance = value
			_db.DB.commit()
			self.dataChanged.emit(index, index)
			return True
		return False

	def insertRows(self, position, rows, index=None):
		for i in range(rows):
			#Now the code in the client is a serial id. so it'll always gets inserted on the bottom
			endpos = len(_db.DB.clients)
			self.beginInsertRows(_qc.QModelIndex(), endpos, endpos)
			#we put a useful name for the client, so the user can find it easily
			cli = _db.models.Client('',  self.tr("Nuevo cliente") )
			self._setMaxRows()
			self.endInsertRows()
			position+=1
		_db.DB.commit()
		return True

	def removeRows(self, position, rows, index=None):
		self.beginRemoveRows(_qc.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			#i use values and c.code in case .keys() return the items in different order
			c = _db.DB.clients.values()[position]
			#when i remove one item, the next takes it index
			del _db.DB.clients[c.idn]
		_db.DB.commit()
		#important
		self._setMaxRows()
		self.endRemoveRows()
		return True

	def endResetModel(self, *args, **kwargs):
		self._setMaxRows()
		_qc.QAbstractTableModel.endResetModel(self, *args, **kwargs)

class Clients(_pkg.GenericModule):
	REQUIRES = (_pkg.GenericModule.P_ADMIN, )
	NAME = 'clients'
	def __init__(self, app):
		super(Clients, self).__init__(app)
		self.model = ClientModel(self.app.window)
		#self.app.window.v_clients.setModel(self.model)
		self.app.window.cb_clients.setModel(self.model)
		self.proxy_model = _qg.QSortFilterProxyModel(self.app.window.v_clients)
		self.proxy_model.setSourceModel(self.model)
		self.proxy_model.setFilterKeyColumn(1)
		self.proxy_model.setFilterCaseSensitivity(_qc.Qt.CaseInsensitive)
		#This is important so when a row is inserted, it is selected, so the client dont have to scroll 300000 items
		# to change the basic info of a new (and blank) item (so it has no name either)
		#There's a small problem using this singal to update the view. QueuedConnection might solve it
		self.proxy_model.rowsInserted.connect(self.rowInserted, _qc.Qt.QueuedConnection)
		self.app.window.v_clients.setModel(self.proxy_model)

		delegate = ClientDelegate(self.app.window)
		self.app.window.v_clients.setItemDelegate(delegate) #i love qt
		#self.window.v_clients.setItemDelegateForColumn(3, delegate) #i love qt
		#self.window.v_clients.setItemDelegateForColumn(4, delegate) #i love qt
		#self.window.v_clients.setItemDelegateForColumn(5, delegate) #i love qt
		self.app.window.bCliNew.clicked.connect(self.new)
		self.app.window.bCliDelete.clicked.connect(self.delete)
		self.app.window.eCliCode.textChanged.connect(self.proxy_model.setFilterWildcard)

	@_qc.Slot()
	def new(self):
		#new instances are inserted in whatever place they get, keys are sorted.. so it doesnt matter
		self.model.insertRows(0, 1)

	@_qc.Slot(_qc.QModelIndex, int, int)
	def rowInserted(self, parent, start, end):
		"""This slot gets called when a row is inserted (read new) when a row is inserted, we dont actually know where
		 it gets inserted because keys are sorted, and key bounds position """
		#selects the new client
		self.app.window.v_clients.selectRow(start)
		sel = self.app.window.v_clients.selectedIndexes()
		#we need the "if sel" because of the nature of QueuedConnection, when this module
		#is being tested, it will call rowInserted in the wrong moment
		if sel:
			#gets the index of the selected row
			i = sel[0]
			#scrolls to it
			self.app.window.v_clients.scrollTo(i, _qg.QTableView.EnsureVisible)
		#self.app.window.v_clients.scrollToBottom()
		#_qc.QTimer().singleShot(100, lambda i=i: self.app.window.v_clients.scrollTo(i))
		#The signal connected to this function is the same as the signal used to insert the item in the view
		#so we have a race-situation with the view, that ends up not scrolling.
		#for that we've changed the connection to this slot as a QueuedConnection, if that fails
		#we'll have to go back to the timmer solution
		#Thanks to Avaris @ irc.freenode.net/#pyside


	@_qc.Slot()
	def delete(self):
		selected = self.app.window.v_clients.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		self.proxy_model.removeRows(r, 1)