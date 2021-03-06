# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
import csv
import PySide.QtCore as _qc
import PySide.QtGui as _qg
import banta.packages as _pkg
import banta.db as _db

#TODO move imports to the utils module


class CSVImports(_pkg.GenericModule):
	REQUIRES = (_pkg.GenericModule.P_ADMIN, )
	NAME = "csvimports"
	#Theres no license restriction because we want EVERYBODY to use our soft, so we'll give as much as possible to make that happen
	def load(self):
		self.app.window.acImportProducts.triggered.connect(self.importProducts)
		self.app.window.acImportClients.triggered.connect(self.importClients)
		self.app.window.acImportProviders.triggered.connect(self.importProviders)

	@_qc.Slot()
	def importProducts(self):
		"""Handles importing data from a csv file"""
		#this is the MODULE for products
		#this is the MODEL for products
		msg = self.app.window.tr("""Elija un archivo .csv cuyas columnas sean:
Código, Nombre, Precio, Stock, Tipo de Iva [0, 1 o 2], Código de Proveedor""")
		_qg.QMessageBox.information(self.app.window, "Banta", msg)
		#open a file
		fname = _qg.QFileDialog.getOpenFileName(self.app.window,
			self.app.window.tr('Abrir archivo'), "",
			self.app.window.tr("Archivos CSV (*.csv);;Todos los archivos (*.*)")
		)
		#gets the name from the return value
		fname = fname[0]
		if not fname:
			return False

		f = open(fname, 'rb')
		#creates a csv reader
		delim = ';'.encode('ascii')
		quote = '"'.encode('ascii')
		reader = csv.reader(f, delimiter=delim, quotechar=quote )
		updated = discarded = inserted = 0
		#gets the (qt) MODEL for products using the MODULE for product
		mod_name = _pkg.base.products.Products.NAME
		prod_model = self.app.modules[mod_name].model
		#starts to reset the model (invalidate all views)
		#Documentation says we shouuld try to use begin* and end* if possible. and it is possible
		prod_model.beginResetModel()
		try:
			#iterate the lines
			for art  in reader:
				#read the columns (carefull, the columns must be this, not 1 more , not 1 less)
				code = art and art.pop(0) or None
				name = art and art.pop(0) or ""
				price = art and art.pop(0) or "0"
				stock = art and art.pop(0) or "0"
				tax_type = art and art.pop(0) or "0"
				prov = art and art.pop(0) or ""
				#try to read from utf

				if name:
					#is important to decode first, otherway logger will crash
					name = name.decode('utf-8', 'replace')
				else:
					name = ""

				if not code:
					#logs incorrect lines
					logger.info("Invalid code for product (%s)"%(name))
					discarded +=1
					continue

				code = code.decode('utf-8', 'replace')


				#tries to parse the data
				#todo create a function for safe_get_float
				try:		price = float(price)
				except: price = 0.0

				try: 		stock = float(stock)
				except: stock = 0.0

				try:		tax_type = int(tax_type)
				except: tax_type = 1

				#if the code exists, then we take the product from the db
				if code in _db.DB.products:
					prod = _db.DB.products[code]
					#and increases the acum
					updated +=1
				else:
					#if not , we create it
					prod = _db.models.Product(code)
					_db.DB.products[code] = prod
					inserted +=1
				#sets the data. If the item already existed, then, values are updated (use with care)
				prod.name = name
				prod.price = price
				prod.stock = stock
				prod.tax_type = tax_type
				#checks if the provider exists
				if prov in _db.DB.providers:
					#and sets it
					prod.provider = _db.DB.providers[prov]
			#COMMIT ONLY WHEN WE FINISHED IMPORTING!!!!
			#if not the db will increase dramatically
			_db.DB.commit('user', 'product import')
			msg = self.app.window.tr("""%s productos agregados\n%s modificados\n%s descartados por código incorrecto""")
			msg = msg%(inserted, updated, discarded)
			logger.info(msg)
			_qg.QMessageBox.information(self.app.window, "Banta", msg)
		except Exception, e:
			#if something goes wrong, we have to rollback.. sorry, everyitem not commited was lost...
			_db.DB.abort()
			#and tell the admin
			logger.exception(e)
			#and the user (though they wont understand anything)
			_qg.QMessageBox.critical(self.app.window, "Banta", self.app.window.tr("Ha ocurrido un error:\n%s")% e.message)
		#and after all (even if it commited or rolled-back) we finish resetting the model.
		#best to leave this outside, because once we call begin, we must allways call end

		prod_model.endResetModel()

	@_qc.Slot()
	def importClients(self):
		"""Handles importing data from a csv file"""
		#this is the MODULE for clients needed to reset the model
		#this is the MODEL for products
		msg = u"Elija un archivo .csv cuyas columnas sean:\n Código, Nombre, Dirección, Tipo de Iva\n"
		msg += u"\tTipos de iva:"
		for t in enumerate(_db.models.Client.TAX_NAMES):
			msg += u"\n\t%s\t%s"%t

		_qg.QMessageBox.information(self.app.window, "Banta", msg)
		#open a file
		fname = _qg.QFileDialog.getOpenFileName(self.app.window,
			self.app.window.tr('Abrir archivo'), "",
			self.app.window.tr("Archivos CSV (*.csv);;Todos los archivos (*.*)")
		)
		#gets the name from the return value
		fname = fname[0]
		if not fname:
			return False

		f = open(fname, 'rb')
		#creates a csv reader
		delim = ';'.encode('ascii')
		quote = '"'.encode('ascii')
		reader = csv.reader(f, delimiter=delim, quotechar=quote)
		updated = discarded = inserted = 0
		#gets the (qt) MODEL for products using the MODULE for product
		mod_name = _pkg.base.clients.Clients.NAME
		model = self.app.modules[mod_name].model
		#starts to reset the model (invalidate all views)
		#Documentation says we shouuld try to use begin* and end* if possible. and it is possible
		model.beginResetModel()
		try:
			#iterate the lines
			for cli in reader:
				#read the columns (carefull, the columns must be this, not 1 more , not 1 less)
				#read carefully, checks if there is a colum, then try to get the value, else sets a default
				code = cli and cli.pop(0) or '' #cli.pop(0) if cli else ""
				name = cli and cli.pop(0) or ''
				address = cli and cli.pop(0) or ''
				tax_type = cli and cli.pop(0) or '0'#if this is not an int, then exception

				if name:
					name = name.decode('utf-8', 'replace')
				else:
					name = ""

				if not code:
					logger.info("Invalid code for (%s)"%(name))
					discarded +=1
					continue

				#Decode
				code = code.decode('utf-8', 'replace')
				address = address.decode('utf-8', 'replace')

				try:		tax_type = int(tax_type)
				except: tax_type = 0

				#Petruccio asked to use the same CUIT for different clients, thus, making this into nonsense
				"""if code in _db.DB.clients:
					cli = _db.DB.clients[code]
					updated +=1
				else:
					cli = _db.models.Client(code)
					_db.DB.clients[code] = cli
					inserted +=1"""
				#Creates a new client
				#automatically saves in the db
				cli = _db.models.Client(code, name=name, address=address, tax_type=tax_type)
				inserted +=1
			#COMMIT ONLY WHEN WE FINISHED IMPORTING!!!!
			#if not the db will increase dramatically
			msg = self.app.window.tr("""%s clientes agregados\n%s modificados\n%s descartados por código incorrecto""")
			msg = msg%(inserted, updated, discarded)
			logger.info(msg)
			_qg.QMessageBox.information(self.app.window, "Banta", msg)
			_db.DB.commit('', 'client import')
		except Exception, e:
			#if something goes wrong, we have to rollback.. sorry, everyitem not commited was lost...
			_db.DB.abort()
			#and tell the admin
			logger.exception(e)
			#and the user (though they wont understand anything)
			_qg.QMessageBox.critical(self.app.window, "Banta", self.app.tr("Ha ocurrido un error:\n%s")% e.message)
		#and after all (even if it commited or rolled-back) we finish resetting the model.
		#best to leave this outside, because once we call begin, we must allways call end
		model.endResetModel()

	@_qc.Slot()
	def importProviders(self):
		"""Handles importing data from a csv file"""
		#this is the MODULE for clients needed to reset the model
		#this is the MODEL for products
		msg = u"Elija un archivo .csv cuyas columnas sean:\n Código (CUIT), Nombre, Dirección, Teléfono, Mail\n"
		_qg.QMessageBox.information(self.app.window, "Banta", msg)
		#open a file
		fname = _qg.QFileDialog.getOpenFileName(self.app.window,
			self.app.window.tr('Abrir archivo'), "",
			self.app.window.tr("Archivos CSV (*.csv);;Todos los archivos (*.*)")
		)
		#gets the name from the return value
		fname = fname[0]
		if not fname:
			return False

		f = open(fname, 'rb')
		delim = ';'.encode('ascii')
		quote = '"'.encode('ascii')
		#creates a csv reader
		reader = csv.reader(f, delimiter=delim, quotechar=quote)
		updated = discarded = inserted = 0
		#gets the (qt) MODEL for products using the MODULE for product
		mod_name = _pkg.base.providers.Providers.NAME
		model = self.app.modules[mod_name].model
		#starts to reset the model (invalidate all views)
		#Documentation says we shouuld try to use begin* and end* if possible. and it is possible
		model.beginResetModel()
		try:
			for prov in reader:
				code = prov and prov.pop(0) or ""
				name = prov and prov.pop(0) or ""
				address = prov and prov.pop(0) or ""
				phone = prov and prov.pop(0) or ""
				mail = prov and prov.pop(0) or ""

				if name:
					name = name.decode('utf-8', 'replace')
				else:
					name = ""

				if not code:
					logger.debug("Invalid code for (%s)"%(name))
					discarded +=1
					continue

				code = code.decode('utf-8', 'replace')
				address = address.decode('utf-8', 'replace')
				phone = phone.decode('utf-8', 'replace')
				mail = mail.decode('utf-8', 'replace')

				if code in _db.DB.providers:
					pro = _db.DB.providers[code]
					updated +=1
				else:
					pro = _db.models.Provider(code)
					_db.DB.providers[code] = pro
					inserted +=1

				pro.name = name
				pro.address = address
				pro.phone = phone
				pro.mail = mail

			msg = self.app.window.tr("""%s proveedores agregados\n%s modificados\n%s descartados por código incorrecto""")
			msg = msg%(inserted, updated, discarded)
			logger.info(msg)
			_qg.QMessageBox.information(self.app.window, "Banta", msg)
			_db.DB.commit('', 'providers import')
		except Exception, e:
			#if something goes wrong, we have to rollback.. sorry, everyitem not commited was lost...
			_db.DB.abort()
			#and tell the admin
			logger.exception(e)
			#and the user (though they wont understand anything)
			_qg.QMessageBox.critical(self.app.window, "Banta", self.app.tr("Ha ocurrido un error:\n%s")% e.message)
		#and after all (even if it commited or rolled-back) we finish resetting the model.
		#best to leave this outside, because once we call begin, we must allways call end
		model.endResetModel()