# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
import ZODB.blob

logger = logging.getLogger(__name__)

import datetime
import csv

import PySide.QtCore as _qc
import PySide.QtGui as _qg
import banta.packages as _pack
#cant use full import in a submodule.. probably because the parent module is still loading
import banta.packages.optional.categories as _cats #meaw!
import banta.db as _db
import banta.utils

class ProductDelegate(_qg.QStyledItemDelegate):
	#Handles the edition on the table for each column
	#def __init__(self, parent = None):
	#	_qg.QStyledItemDelegate.__init__(self, parent)

	def createEditor(self, parent, option, index):
		self.initStyleOption(option, index)
		col = index.column()
		editor = None
		if col in (0, 1, 2, 11):
			#Code , internal code, name, descripcion
			editor = _qg.QLineEdit(parent)
		elif col in (3, 4, 5):
			#price, buyprice, stock
			editor = _qg.QDoubleSpinBox(parent)
			editor.setRange(-2147483646, +2147483646)
		elif col == 6:
			#Provider
			editor = _qg.QComboBox(parent)
			#TODO use getmodel.?¿
			editor.setModel(_pack.base.providers.MODEL)
			editor.setModelColumn(1)
		elif col == 7:
			#this little bastar has all the blame
			editor = _qg.QSpinBox(parent)
			editor.setRange(-2147483646, +2147483646)
		elif col == 8:
			#Category
			editor = _qg.QComboBox(parent)
			#todo use getmodel here too maybe..
			#todo problema si categories no esta cargado, test
			editor.setModel(_pack.optional.categories.MODEL)
		elif col == 9:
			#TaxType
			editor = _qg.QComboBox(parent)
			editor.setModel(_pack.optional.type_tax.MODEL)
		elif col == 10:
			#Ingresos Brutos
			editor = _qg.QComboBox(parent)
			editor.addItems(_db.models.Product.IB_NAMES)
		elif col == 12:
			editor = _qg.QLabel()
		#else:
			#Theres a bug in pyside with this and spinboxes
			#Usando setItemDelegateForColumn esto no se hace muy necesario, lo dejo por las dudas.
			#editor = _qg.QStyledItemDelegate.createEditor(self, parent, option, index)
		return editor

	@_qc.Slot()
	def setEditorData(self, editor, index):
		#Sets de data to the editor (current item)
		col = index.column()
		er = _qc.Qt.EditRole
		#Gets the data for the item, in edit mode
		#same as: d = index.model().data(index, _qc.Qt.EditRole)
		d = index.data(er)
		if col in (0, 1, 2, 11):
			editor.setText(d)
		elif col in (3, 4, 5, 7):
			editor.setValue(d)
		elif col in (8, 9, 10):
			#Ingresos Brutos, Category
			#As this comboboxes uses itemindex they share somewhat the same code, so i put them toghether

			#sets the current index (data for this column is just the index)
			#Notice this is the model for products (even on column 5)
			if d:
				editor.setCurrentIndex(d)
		elif col == 6:
			#Provider
			#Not very efficient
			#d is the data in the product model. EditRole returns the provider code.
			#remember that this index belongs to the product list, not to the provider,
			# so we need the code in provider column, which is EditRole

			#Searchs the code in the combo, (which uses the provider model)
			if d< 0: return None
			#BUT findData will look the code "d" in HIS model (providers) using the qt.UserRole (user role is used for this)
			i = editor.findData(d)
			if i< 0: return None
			editor.setCurrentIndex(i)
		elif col == 12:
			editor.setPixmap(_qg.QPixmap(d))


	def setModelData(self, editor, model, index):
		#Set the data from the editor back to the model (usually changed)
		col = index.column()
		er = _qc.Qt.EditRole
		if col in (0, 1, 2, 11):
			model.setData(index, editor.text(), er)
		elif col in (3, 4, 5, 7):
			model.setData(index, editor.value(), er)
		elif col in (8, 9, 10):
			#Ingresos Brutos, Category, Tax Types
			#As this comboboxes uses itemindex they share somewhat the same code, so i put them toghether
			#tells the model to change de data for the item in index, the data is the index of the editor, in editrole
			model.setData(index, editor.currentIndex(), er)
		elif col == 6:
			#Provider
			i = editor.currentIndex()
			#itemData returns the userRole (if i remember well)
			model.setData(index, editor.itemData(i), er)
		elif col == 12:
			fname = _qg.QFileDialog.getOpenFileName(None,
				'Elegir imágen', "",
				"Archivos PNG (*.png);;Archivos JPG (*.jpg);;Todos los archivos (*.*)")[0]

			model.setData(index, fname, er)



class ProductModel(_qc.QAbstractTableModel):
	HEADERS = (
		_qc.QT_TRANSLATE_NOOP('products', "Código"),
		_qc.QT_TRANSLATE_NOOP('products', "Código Externo"),
		_qc.QT_TRANSLATE_NOOP('products', "Nombre"),
		_qc.QT_TRANSLATE_NOOP('products', "Precio"),
		_qc.QT_TRANSLATE_NOOP('products', "Precio de Compra"),
		_qc.QT_TRANSLATE_NOOP('products', 'Stock'),
		_qc.QT_TRANSLATE_NOOP('products', 'Proveedor'),
		_qc.QT_TRANSLATE_NOOP('products', "Unidades por caja"),
		_qc.QT_TRANSLATE_NOOP('products', 'Rubro'),
		_qc.QT_TRANSLATE_NOOP('products', 'Tipo'),
		_qc.QT_TRANSLATE_NOOP('products', 'Ingresos Brutos'),

		_qc.QT_TRANSLATE_NOOP('products', "Descripción"),
		_qc.QT_TRANSLATE_NOOP('products', "Imágen"),
	)
	max_rows = 0
	columns = 13

	def __init__(self, parent = None):
		_qc.QAbstractTableModel.__init__(self, parent)
		self.parent_widget = parent
		self.tr = banta.utils.unitr(self.trUtf8)
		#this might improve speed, but can be dangerous if we dont call __setMaxRows each time the rowcount is changed..
		#for now, that's controlled here in the model
		self._setMaxRows()

	def _setMaxRows(self):
		"""Sets the rowcount in the model
		Is Important to call this function when the quantity of products changes
		(in theory that's well managed using this model for adding/removing rows)
		"""
		self.max_rows =len(_db.DB.products)

	def rowCount(self, parent=None):
		return self.max_rows

	def columnCount(self, parent=None):
		return self.columns

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
			pro = _db.DB.products.values()[row]
			#Create an index setting the "pointer" internal data to the actual Product object
			return self.createIndex(row, col, pro)

	def data(self, index, role=0):
		"""Returns the data for a given index, with a given role.
		This is the (most common) way to get the data from the model.
		index is a QModelIndex created by this object ( self.index(row, col) )
		role which role you need (_qc.Qt.EditRole (for editing) _qc.Qt.DisplayRole (for displaying), etc)
		"""

		if not index.isValid():
			return None

		if role not in (_qc.Qt.DisplayRole, _qc.Qt.EditRole, _qc.Qt.UserRole, _qc.Qt.DecorationRole): #maybe faster, easier to understand, compact
			return None

		#technically faster
		pro = index.internalPointer()
		#_db.DB.abort()
		if role == _qc.Qt.UserRole:
			return pro.code


		col = index.column()

		if col == 12 and (role in( _qc.Qt.DecorationRole, _qc.Qt.EditRole)):
			if pro.thumb:
				im = pro.thumb.open("r")
				img = _qg.QImage()
				img.loadFromData(im.read())
				return img
			else:
				return _qg.QImage("./static/thumb.jpg")

		if role == _qc.Qt.EditRole:
			if col == 9:
				try:
					return _db.DB.type_tax.index(pro.tax_type)
				except:
					return -1
			elif col == 10:
				return pro.ib_type
			elif col == 6:
				#maybe i should return pro.provider but for simplification outside this function i'll hide the complexity here
				#in other databases where you use "indexes" maybe this is more direct
				#so we return the index of the provider in the zodb list
				if not pro.provider:
					return -1
				else:
					return pro.provider.code
			elif col == 8:
				if pro.category is None:
					return -1
				else:
					try:
						#i really hate using trys
						return _db.DB.categories.index(pro.category)
					except:
						return -1
		#Notice there's no else, because some columns are going to return the same value for edit and display role
		if col == 0:
			return pro.code
		elif col == 1:
			return pro.external_code
		elif col == 2:
			return pro.name
		elif col == 3 :
			return pro.price
		elif col == 4:
			return pro.buy_price
		elif col == 5:
			return pro.stock
		elif col == 6 :
			if pro.provider:
				return pro.provider.name
			return None
		elif col == 7:
			return pro.pack_units
		elif col == 8:
			if pro.category:
				return pro.category.name
			return None
		elif col == 9:
			return str(pro.tax_type)
		elif col == 10:
			return pro.IBStr()
		elif col == 11:
			return pro.description
		return None

	def headerData(self, section=0, orientation=None, role=0):
		if role != _qc.Qt.DisplayRole:
			#Careful with this, returning u"" Breaks it
			return None
		if orientation == _qc.Qt.Horizontal:
			return self.tr(self.HEADERS[section])
		else:
			return str(section)

	def flags(self, index=None):
		if index.isValid():
			return	_qc.Qt.ItemIsEditable | _qc.Qt.ItemIsEnabled | _qc.Qt.ItemIsSelectable#QAbstractItemModel::flags(index) |
		return _qc.Qt.ItemIsEnabled

	def setData(self, index=None, value=None, role=0):
		if index.isValid() and (role == _qc.Qt.EditRole):
			#pro = _db.DB.products.values()[index.row()]
			pro = index.internalPointer()
			col = index.column()
			if col == 0:
				#"move" a product in the table
				#check if the code has changed, so it dont delete it accidentally
				if pro.code == value:
					return False
				#also check to NOT replace another product
				if value in _db.DB.products.keys():
					#if the pro.code != value, but value is in the db, then they are 2 different products..
					_qg.QMessageBox.warning(self.parent_widget, "Banta", self.tr("Ya existe un producto con ese código."))
					return False
				#The del must come BEFORE!! there's a chance that the code hasn't changed, in which case it'll end up DELETING the product
				#it should be fixed with the if
				del _db.DB.products[pro.code]
				_db.DB.products[value] = pro
				pro.code = value
			elif col == 1:
				pro.external_code = value
			elif col == 2:
				pro.setName(value)
			elif col == 3:
				pro.price = value
			elif col == 4:
				pro.buy_price = value
			elif col == 5:
				title = self.tr("Modificar Stock")
				#Ask the user for the reason of modification
				while True:
					msg, ok = _qg.QInputDialog.getText(self.parent_widget, title, self.tr("Razón de la modificación:"), _qg.QLineEdit.Normal, "")
					if not ok:
						#cancel button
						return False
					#if there's no message, tries again, until the user cancels or enters a message
					if msg:
						#the quantity is saved as a relative number. #TODO check if the user will prefer a absolute number
						#moves needs to be saved, because of the time key, so they are saved instantly when instantiated, (be careful)
						#so basically the "move" variable means nothing
						move = _db.models.Move(pro, msg, value-pro.stock)
						pro.stock = value
						break
					#endif
				#endwhile
			elif col == 6:
				pro.provider = _db.DB.providers[value]
			elif col == 7:
				pro.pack_units = value
			elif col == 8:
				pro.category = _db.DB.categories[value]
			elif col == 9:
				pro.tax_type = _db.DB.type_tax[value]
			elif col == 10:
				pro.ib_type = value
			elif col == 11:
				pro.description = value
			elif col == 12:
				pro.thumb = ZODB.blob.Blob()
				#open(value, 'rb').write(pro.thumb.open('w')) #horrible
				im = open(value, 'rb')
				with pro.thumb.open("w") as f:
					f.write(im.read())

			#endif
			_db.DB.commit()
			#informs other views of the change
			self.dataChanged.emit(index, index)
			return True
		return False

	def insertRows(self, position, rows, index=None):
		title = self.tr("Nuevo Producto")
		for i in range(rows):
			code, ok = _qg.QInputDialog.getText(self.parent_widget, title, self.tr("Ingrese el código"), _qg.QLineEdit.Normal, "")

			if not ok:
				continue

			if code in _db.DB.products.keys():
				_qg.QMessageBox.warning(self.parent_widget, title, self.tr( "Ya existe un producto con ese código."))
				continue
			#this would be slow, because it'll convert all the keys to a list, also can oly be called after inserting
			#endpos = tuple(zodb.clients.keys()).index(code)
			#this is faster, also, it can be called before inserting. is a little trick, basically we count all the items before
			endpos = len(_db.DB.products.keys(max=code, excludemax=True))
			self.beginInsertRows(_qc.QModelIndex(), endpos, endpos)
			prod = _db.models.Product(code, '-')
			_db.DB.products[prod.code] = prod
			#is important to set the max row before emitting endInsertRow,
			#if not we might get a blank row or an exception
			self._setMaxRows()
			self.endInsertRows()
			position+=1
		_db.DB.commit()
		return True

	def removeRows(self, position, rows, index=None):
		self.beginRemoveRows(_qc.QModelIndex(), position, position+rows-1)
		for i in range(rows):
			key = _db.DB.products.keys()[position]
			del _db.DB.products[key] #when i remove one item, the next takes it index
		_db.DB.commit()
		#VERY MUY IMPORTANT
		#update the max_rows before emitting the endremoverows or we WILL get an exception...
		#because the notified views  will try to update and WILL try to read the removed item
		self._setMaxRows()
		self.endRemoveRows()
		return True

	def endResetModel(self, *args, **kwargs):
		"""When there's a massive change in the model, allow the use of begin/endResetModel
		"""
		#recalculate the maximum rows
		self._setMaxRows()
		_qc.QAbstractTableModel.endResetModel(self, *args, **kwargs)

MODEL = ProductModel()
class Products(_pack.GenericModule):
	REQUIRES = (_pack.GenericModule.P_ADMIN, )
	NAME = 'products'
	#needed for limits delegate. think of a way to solve the delegate crossover stuff and model sharing
	def __init__(self, app):
		super(Products, self).__init__(app)
		self.model = MODEL
		#explanation on providers
		self.model.parent_widget = app.window
		#i use a filteR_mode var just so i don't call the setFilter each time i make a change
		self.filter_mode = -1

	def load(self):
		import banta.packages.base.providers

		#Models
		self.proxy_model = _qg.QSortFilterProxyModel(self.app.window.v_products)
		self.proxy_model.setSourceModel(self.model)
		self.proxy_model.setFilterCaseSensitivity(_qc.Qt.CaseInsensitive)
		#read base/clients to know why is using QueuedConnection
		self.proxy_model.rowsInserted.connect(self.rowInserted, _qc.Qt.QueuedConnection)
		#Makes no sense, keys are strings anyways... this would be usefull for integer keys..
		#self.proxy_model.setSortRole(_qc.Qt.EditRole)
		self.app.window.v_products.setModel(self.proxy_model)
		delegate = ProductDelegate(self.app.window)
		self.app.window.v_products.setItemDelegate(delegate) #i love qt

		self.app.window.cb_billProds.setModel(self.model)
		prov_mod_name = banta.packages.base.providers.Providers.NAME
		prov_model = self.app.modules[prov_mod_name].model
		#be careful because setting the model after the signal is set will trigger the filter

		self.app.window.cb_FilProvider.setModel(prov_model)
		self.app.window.cb_FilProvider.setModelColumn(1)
		self.app.window.cb_FilProvider.setCurrentIndex(-1)
		#Conections
		self.app.window.bProdNew.clicked.connect(self.new)
		self.app.window.bProdDelete.clicked.connect(self.delete)
		self.app.window.bExport.clicked.connect(self.exportProducts)
		self.app.window.bProdClearFilter.clicked.connect(self.clearFilters)
		#this is direct way, but we couldnt filter by another thing i leave it for the record
		#self.app.window.eProdCode.textChanged.connect(self.proxy_model.setFilterWildcard)
		self.app.window.eProdCode.textChanged.connect(self.nameChanged)
		self.app.window.cb_FilProvider.currentIndexChanged.connect(self.providerChanged)

		#self.app.window.v_products.setColumnHidden(3, True)
		#careful! this could be slow!
		#self.app.window.v_products.resizeColumnsToContents()

	@_qc.Slot(str)
	def nameChanged(self, name):
		if self.filter_mode != 0:
			self.proxy_model.setFilterKeyColumn(2)
		self.proxy_model.setFilterWildcard(name)
		self.filter_mode = 0

	@_qc.Slot(int)
	def providerChanged(self, i):
		if i < 0 : 
			return

		if self.filter_mode != 1:
			#the column in the product model for the provider is 5
			self.proxy_model.setFilterKeyColumn(6)
			#We use the EditRole on the product model (which returns the code, not the name) which technically is safer
			self.proxy_model.setFilterRole(_qc.Qt.EditRole)
		model = self.app.window.cb_FilProvider.model()
		#the column for the code in the provider model is 0
		#EditRole returns the code
		code = model.data(model.index(i, 0), _qc.Qt.EditRole)
		self.proxy_model.setFilterWildcard(code)
		self.filter_mode = 1
		
	@_qc.Slot()
	def clearFilters(self):
		self.proxy_model.setFilterKeyColumn(0)
		self.proxy_model.setFilterWildcard(None)
		self.app.window.cb_FilProvider.setCurrentIndex(-1)
		self.app.window.eProdCode.setText("")
		self.filter_mode = -1
		
	@_qc.Slot()
	def new(self):
		self.proxy_model.insertRows(0, 1)

	@_qc.Slot(_qc.QModelIndex, int, int)
	def rowInserted(self, parent, start, end):
		"""This slot gets called when a row is inserted (read new) when a row is inserted, we dont actually know where
		 it gets inserted because keys are sorted, and key bounds position """
		#we could use maptosource but as the index is inserted at the end is coincidently the same
		#in the model and the source
		self.app.window.v_products.selectRow(start)
		sel = self.app.window.v_products.selectedIndexes()
		if sel:
			i = sel[0]
			self.app.window.v_products.scrollTo(i, _qg.QTableView.EnsureVisible)
		#See base/clients.py:rowInserted for more details

	@_qc.Slot()
	def delete(self):
		selected = self.app.window.v_products.selectedIndexes()
		if not selected: return
		r = selected[0].row()
		#NOTICE THE PROXY MODEL!!
		#The view handles different indexes than the real model because is using the proxy
		#So we need to call the actual method on the proxy so it translates the indexes properly
		self.proxy_model.removeRows(r, 1)

	@_qc.Slot()
	def exportProducts(self):
		name =  "banta_products-" +   str( datetime.datetime.now()).replace(":", "_") + ".csv"
		fname = _qg.QFileDialog.getSaveFileName(self.app.window,
			self.app.window.tr('Guardar Reporte'), name,
			self.app.window.tr("Archivos CSV (*.csv);;Todos los archivos (*.*)"),
		)
		#gets the name from the return value
		fname = fname[0]
		if not fname:
			return False
		delimit = ';'.encode('utf-8')
		quote = '"'.encode('utf-8')
		writer = csv.writer(open(fname, 'wb'), delimiter=delimit, quotechar=quote,  quoting=csv.QUOTE_MINIMAL)
		#Write headers
		row = []
		for c in range (self.app.window.v_products.model().columnCount()):
			hi = self.app.window.v_products.model().headerData(c, _qc.Qt.Horizontal, _qc.Qt.DisplayRole)
			row.append( unicode(hi).encode('utf-8'))

		try:
			writer.writerow(row)
		except:
			pass
		self.model.columnCount()

		for r in range(self.app.window.v_products.model().rowCount()):
			row = []
			for c in range(self.app.window.v_products.model().columnCount()):
				index = self.app.window.v_products.model().index(r,c)
				data = self.app.window.v_products.model().data(index, _qc.Qt.DisplayRole)
				#data should ALWAYS be unicode
				#data can be a number or other stuff
				row.append(unicode(data).encode('utf-8'))
			try:
				writer.writerow(row)
			except :
				pass
