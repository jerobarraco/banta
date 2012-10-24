# -*- coding: utf-8 -*-
"""This module contains the data-models used in the rest of the software

Considering the MVC model, is NOT nice to import this module DIRECTLY to a GUI-related code. (or the class into gui code)
It should be imported in a controller. Using _instances_ of objects from this module in code from the GUI is ok (and adviced).
(or using constants from gui code)
"""
from __future__ import absolute_import, unicode_literals, print_function
import datetime
import decimal
#4 decimal places precition
decimal.getcontext().prec = 4

import persistent as _per
#DO NOT IMPORT DB or DB.CNX or DB.ZODB DIRECTLY HERE!

#Constants
#license types
LICENSE_FREE = 0
LICENSE_BASIC = 1
LICENSE_POWER = 2
LICENSE_ADVANCED = 3
LICENSES_ALL = (LICENSE_FREE, LICENSE_BASIC, LICENSE_POWER, LICENSE_ADVANCED)
LICENSES_NOT_FREE = (LICENSE_BASIC, LICENSE_POWER, LICENSE_ADVANCED)
LICENSES_NOT_BASIC = (LICENSE_POWER, LICENSE_ADVANCED)
#This could be stored in the settings
TAX_MAX = 0.21
TAX_REDUCED = 0.105
#DO NOT IMPORT DB or DB.CNX or DB.ZODB DIRECTLY HERE!

#DO NOT IMPORT DB or DB.CNX or DB.ZODB DIRECTLY HERE!

class Product(_per.Persistent):
	"""Each of the product in the store.
	It can have stock, or not. It can be available or not.
	It just store the properties for each product (like a 'class' for real products)
	"""
	name = ""
	code = ""
	#External/Provider code
	external_code = ""
	#sold price, SOLD price
	price = 0.0
	#Price at which is (usually) bought
	buy_price = 0.0
	ib_type = 0
	prod_type = 0
	#Available stock
	stock = 0
	#Units PER (bought) Package (box)
	pack_units = 1
	#provider
	provider = None
	#category
	#Better if it can be none.. specially on the free version
	category = None
	#Minimum stock before warning 
	#min_stock = 0 #later, needs View and Controller
	#Constants for type of product, it defines the tax it to be charged (depends on other crappy stuff)
	description = ""
	TYPE_EXEMPT = 0
	TYPE_SELL_GOOD = 1
	TYPE_USE_GOOD = 2
	TYPE_NAMES = (
		'Exento (0%)',
		'Bien de cambio (' + str(int(TAX_MAX*100))+'%)',
		'Bien de uso (' + str(int(TAX_REDUCED*100))+'%)',
	)
	#Consts for Brute Income (Ingresos Brutos), defines what will be charged (depends on other stuff)
	IB_NOT_EXEMPT = 0
	IB_EXEMPT = 1
	IB_NAMES = ('Exento', 'No Exento')

	def __init__(self, code, name="", price=0.0, stock=0, tax_type=0):
		_per.Persistent.__init__(self)
		self.code = code
		self.name = name
		self.price = price
		self.stock = stock
		self.tax_type = tax_type

	def IBStr(self):
		return self.IB_NAMES[self.ib_type]

	def typeStr(self):
		return self.TYPE_NAMES[self.tax_type]

	def __str__(self):
		return "[%s] $%s %s"%(self.code, self.price, self.name)
	pass

class Item(_per.Persistent):
	"""Represents an item in a bill.
	it is related to a product, BUT for historical reasons (ask nande) 
	the product data needed to form a bill, must be duplicated and stored SEPARATEDLY"""
	product = None
	#price per unit as the product in that date
	base_price=0.0
	#CALCULATED price per unit, including markup but without tax
	unit_price = 0.0
	#CALCULATED total price with tax (calculated with item.calculate())
	price = 0.0
	#CALCULATED net_price without tax (calculated with item.calculate())
	net_price = 0.0
	quantity = 1
	#CALCULATED tax percentaje, calculated by calculateTax
	tax = TAX_MAX
	#CALCULATED total tax charged for the item
	tax_total = 0.0
	description = ""
	reducible = False
	#A percentaje that the owner charges over the price of a product
	#Sets the markup of a item, that is when the owner decides to charge an overprice or make a discount (negative markup)
	#markup is a percentaje
	markup = 0.0
	#Tells wether the client is exempt or not
	client_exempt  = False
	def __init__(self, product=None, quant=1, markup=0.0, client_exempt=False):
		_per.Persistent.__init__(self)
		self.markup = markup
		self.client_exempt = client_exempt
		if product:
			self.setProduct(product)
		self.setQuantity(quant)

	def setProduct(self, product):
		self.product = product
		#this values need duplication because the client might want to change the default values 
		#also to allow the use of generic products

		self.unit_price =  self.base_price = product.price
		self.description = product.name
		self.reducible = (self.product.tax_type == self.product.TYPE_USE_GOOD)

	def setQuantity(self, quant):
		self.quantity = quant

	def calculateTax(self):
		"""Calculates the tax for this item
		it depends on :
		Product, and client_exempt
		sets self.tax for the corresponding tax for this item
		"""
		#i use another variable just for clarity
		#"self.product and" will prevent checking when there's no product set
		prod_exempt = self.product and (self.product.tax_type == self.product.TYPE_EXEMPT)

		if self.client_exempt or prod_exempt:
			self.tax = 0.0
		elif self.reducible:
			self.tax = TAX_REDUCED
		else:
			self.tax = TAX_MAX

	def calculate(self):
		"""Calculates the total
		and other values.
		self.price is the total price of the item (including tax)
		self.tax_total is the total ammount of tax in the price (not a percentaje)
		self.net_price is the total price without tax
		"""
		self.calculateTax()
		#round( ,4) rounds the item to 4 digits, is needed because printers dont process more then 4 digits
		self.unit_price = round(self.base_price, 4) * (1+self.markup)
		self.price = (self.unit_price * self.quantity)

		if self.tax > 0.0 :
			#theres always an easy way in python
			self.net_price = round(self.price/(1+self.tax) , 4)
			self.tax_total = self.price - self.net_price
		else:
			self.net_price = self.price
			self.tax_total = 0.0
		return self.price

class TypePay(_per.Persistent):
	name = ''
	markup = 0.0
	def __init__(self, name, markup=0.0):
		_per.Persistent.__init__(self)
		self.name = name
		self.markup = markup

	def __str__(self):
		return "%s - %s%%" % (self.name, self.markup*100)

class Client(_per.Persistent):
	"""Class for the Clients"""
	#Constants for identification
	DOC_CUIT = 0
	DOC_LIBRETA_ENROLAMIENTO = 1
	DOC_LIBRETA_CIVICA = 2
	DOC_DNI = 3
	DOC_PASAPORTE = 4
	DOC_CEDULA = 5
	DOC_SIN_CALIFICADOR = 6
	DOC_NAMES = (
		"CUIT", "Libreta de Enrolamiento", "Libreta Cívica", "DNI",
		"Pasaporte", "Cédula" , "Sin Calificador"
	)
	
	#Constants for Tax information related to the client
	TAX_CONSUMIDOR_FINAL = 0
	TAX_RESPONSABLE_INSCRIPTO = 1
	TAX_RESPONSABLE_NO_INSCRIPTO = 2
	TAX_EXENTO = 3
	TAX_NO_RESPONSABLE = 4
	TAX_RESPONSABLE_NO_INSCRIPTO_BIENES_DE_USO = 5
	TAX_RESPONSABLE_MONOTRIBUTO = 6
	TAX_MONOTRIBUTO = 7
	TAX_MONOTRIBUTISTA_SOCIAL = 8
	TAX_PEQUENIO_CONTRIBUYENTE_EVENTUAL = 9
	TAX_PEQUENIO_CONTRIBUYENTE_EVENTUAL_SOCIAL = 10
	TAX_NO_CATEGORIZADO = 11
	TAX_NAMES = (
		"Consumidor Final", "Responsable Inscripto", "Responsable no Inscripto", "Exento", "No Responsable",
		"Responsable No Inscripto Bienes de Uso", "Responsable Monotributo", "Monotributo",
		"Monotributista Social", "Pequeño Contribuyente Eventual", "Pequeño Contribuyente Eventual Social",
		"No categorizado"
	)

	#Constants for Ingresos Brutos (Brute Income) for the client (This is argentinean AFAIK)
	IB_UNREGISTERED = 0
	IB_REGISTERED = 1
	IB_EXEMPT = 2
	IB_NAMES = ('No registrado', 'Registrado', 'Exento')

	idn = -1
	#great, you can have two peoples with the same code in this country, ain't it bad?
	name = ""
	code = ""
	address = ""
	#TAX (Iva)
	tax_type = 0
	#Documento (A.K.A. ID)
	doc_type = 0
	#Ingresos Brutos
	ib_type = 0
	##ACCOUNTING
	#stores the debt (or credit if negative)
	balance = 0.0
	def __init__(self, code, name="", address="", doc_type=DOC_SIN_CALIFICADOR, tax_type=TAX_CONSUMIDOR_FINAL,
							 ib_type=IB_UNREGISTERED):
		_per.Persistent.__init__(self)
		self.name = name
		self.code = code
		self.address = address
		self.tax_type = tax_type
		self.doc_type = doc_type
		self.ib_type = ib_type

	def getPossibleBillTypes(self):
		#Todo ask jorge for the exact values
		#Always return a list even if there's not value, or just one
		#TODO filter in case the seller is Responsable or not
		if self.tax_type == self.TAX_RESPONSABLE_INSCRIPTO :
			return (Bill.TYPE_A, Bill.TYPE_NOTA_CRED_A, Bill.TYPE_NOTA_DEB_A )
		elif self.tax_type in (self.TAX_MONOTRIBUTO, self.TAX_MONOTRIBUTISTA_SOCIAL):
			return (Bill.TYPE_B,  Bill.TYPE_NOTA_CRED_B, Bill.TYPE_NOTA_DEB_B )
		elif self.tax_type in (self.TAX_CONSUMIDOR_FINAL, self.TAX_NO_CATEGORIZADO, self.TAX_NO_RESPONSABLE):
			return (Bill.TYPE_B, Bill.TYPE_C, Bill.TYPE_NOTA_CRED_B, Bill.TYPE_NOTA_DEB_B )
		else:
			return (Bill.TYPE_A, Bill.TYPE_B, Bill.TYPE_C, Bill.TYPE_NOTA_CRED_A, Bill.TYPE_NOTA_CRED_B, Bill.TYPE_NOTA_DEB_A )

	def putInDB(self):
		"""Saves a client into the database and returns an id.
		selff.idn holds the key for the inserted client
		"""
		#This is needed for a weird requeriment, that needs the client to have different codes.
		#Also some clients wont be saved in the db, the key shoudlnt be generated for every client
		if self.idn >-1:
			return #the client is already saved
		import banta.db
		if len(banta.db.DB.clients):
			self.idn = banta.db.DB.clients.maxKey()+1
		else :
			self.idn = 0
		banta.db.DB.clients[self.idn] = self
		return self.idn

	def taxStr(self):
		return self.TAX_NAMES[self.tax_type]
	
	def docStr(self):
		return self.DOC_NAMES[self.doc_type]
	
	def IBStr(self):
		return self.IB_NAMES[self.ib_type]

	def __str__(self):
		return "\n".join((self.code, self.name, self.address, self.taxStr()))

class Bill(_per.Persistent):
	"""Bill. Factura. Ticket. 
	"""
	#Constants for the bill type
	TYPE_A = 0
	TYPE_B = 1
	TYPE_C = 2
	TYPE_NOTA_CRED_A = 3
	TYPE_NOTA_CRED_B = 4
	TYPE_NOTA_DEB_A = 5
	TYPE_NOTA_DEB_B = 6
	TYPE_NAMES = (
		'A', 'B', 'C', 'Nota de Crédito A', 'Nota de Crédito B', 'Nota de Débito A', 'Nota de Débito B'
	)
	
	number = 0
	date = 0
	markup = 0.0
	tax = 0.0
	total = 0.0
	subtotal = 0.0
	btype = 0
	#Payment Type
	ptype = None
	client = None
	#User (cashier) that creates a bill
	user = None
	printed = False
	closed = False
	#used as a key
	time = 0
	def __init__(self):
		super(Bill, self).__init__()
		self.date = datetime.datetime.now()
		self.items = _per.list.PersistentList()

	def setTypePay(self, tpay):
		self.ptype = tpay
		self.setMarkup(tpay.markup)

	def setTypeBill(self, tb):
		self.btype = tb

	def setClient(self, client):
		self.client = client

	def setMarkup(self, markup):
		"""Sets the markup for the bill, which affects all the item.
		Neither the bill nor the items are recalculated"""
		self.markup = markup
		for i in self.items:
			i.markup = markup

	def calculate(self):
		"""Recalculate the values for the bill, and sets the values in each variable.
		It can be slow so call it only if it has changed"""
		self.subtotal = 0.0
		self.tax = 0.0
		self.total = 0.0
		for i in self.items:
			i.calculate()
			self.total += i.price
			self.tax += i.tax_total
		self.subtotal = self.total - self.tax
	
	def copy(self):
		copy = Bill()

		#copy of the rest of bill class
		copy.btype = self.btype
		copy.client = self.client
		copy.markup = self.markup
		copy.ptype = self.ptype
		copy.user = self.user
		copy.ptype = self.ptype
		#is easier to just copy this attributes than recalculating stuff
		copy.subtotal = self.subtotal
		copy.tax = self.tax

		for i in self.items:
			item = Item()
			#copy ALL item properties! :D!
			#here is safer to copy attributes instead of recalculating, because a bill could have a modified price/description
			#that's the reason we have redundant attributes in the item after all
			item.base_price = i.base_price
			item.client_exempt = i.client_exempt
			item.description = i.description
			item.markup = i.markup
			item.net_price = i.net_price
			item.price = i.price
			#copy the product to the new instance
			#product is an object that is safe to copy (that way we can do reports)
			item.product = i.product
			item.quantity = i.quantity
			item.reducible = i.reducible
			item.tax = i.tax
			item.tax_total = i.tax_total
			item.unit_price = i.unit_price			
			copy.items.append(item)
		return copy
	
	def close(self):
		"""Closes the bill.
		ADDS THE BILL TO THE DATABASE
		Reduces the stock, sets the bill date
		and add it to the bill list
		if the bill is already closed, it does nothing.
		Notice this is pretty destructive and has side-effects, so be careful when using it
		"""
		#TODO disable all functions if the bill is closed
		if self.closed:
			return False

		import banta.db
		self.closed = True
		self.date = datetime.datetime.now()
		#we will be using time as a key
		self.time = banta.utils.dateTimeToInt(self.date)
		#calculate if we will be adding or substracting the stock
		#this is a little trick to impact lowly on the code
		if self.btype in (self.TYPE_NOTA_CRED_A, self.TYPE_NOTA_CRED_B):
			sign = 1
		else :
			sign = -1
		#let's reduce the stock :D
		for item in self.items:
			prod = item.product
			prod.stock += sign* item.quantity
			#TODO ask the client if adding a "Move" for each returned item would be a good feature
		#check that there's not another bill with the same key (should not happen unless using several clients at once)
		#though that's not possible YET, let's be prepared (also if some stupid person changes the system date)

		while (self.time in banta.db.DB.bills):
			self.time += 1

		banta.db.DB.bills[self.time] = self
		return True

	def addItem(self, item):
		"""Adds an item to the bill. 
		Returns True if ok. 
		If the item is already on the bill, or there's an error it returns False."""
		
		if self.printed:
			#this means the bill has been printed fiscally
			#by no means we should modify printed bills
			return False
		
		if item in self.items:
			return False
		
		self.items.append(item)
		return True
		#DB.commit() #DONT COMMIT UNTIL THE BILL IS PRINTED (important also if we ever make a network shared-db version)

	def delItem(self, i):
		del self.items[i]

	def strPrinted(self):
		#TODO translate
		return (self.printed and "Impresa") or "Presupuesto"

class Printer(_per.Persistent):
	#One of the printers available in the system
	BRAND_NAMES = ('Hasar', 'Epson')
	BRAND_HASAR = 0
	BRAND_EPSON = 1
	SPEEDS = (2400, 4800, 9600, 19200, 38400, 57600, 115200)
	
	name = "Hasar P/320F"
	brand = BRAND_HASAR
	device = "COM1"
	#this stores the index of the speed in self.SPEEDS, not the speed itself
	speed = 2
	model = 3 #hasarPrinter.MODEL_320

class Provider(_per.Persistent):
	name = ""
	address = ""
	code = ""
	phone = ""
	mail = ""
	def __init__(self, code, name="", address="", phone="", mail=""):
		_per.Persistent.__init__(self)
		self.code = code
		self.name = name
		self.address = address
		self.phone = phone
		self.mail = mail

class User(_per.Persistent):
	name = ""
	def __init__(self, name=""):
		_per.Persistent.__init__(self)
		self.name = name

class Category(_per.Persistent):
	name = ""
	def __init__(self, name=""):
		_per.Persistent.__init__(self)
		self.name = name

#TODO STUDY if Move and Buy should be merged
class Move(_per.Persistent):
	date = 0
	time = 0
	product = None
	diff = 0
	reason = ""
	def __init__(self, product, reason, diff):
		"""
		Represents a movement in stock
		stores the product changed, the reason, and the diff in quantity (relative number)
		Instantiating a move adds it on the db, that's important because when you add it, it depends on the time
		 so it could break several stuff if its saved 2 times
		 (still you have to commit)"""
		_per.Persistent.__init__(self)
		import banta.utils
		self.reason = reason
		self.product = product
		self.diff = diff
		self.date = datetime.datetime.now()

		#Saves the move, as the key is time based, we need to do some calculations before saving
		self.time = banta.utils.dateTimeToInt(self.date)
		#check that there's not another move with the same key (should not happen unless using several clients at once)
		#though that's not possible YET, let's be prepared (also if some stupid person changes the system date)
		while (self.time in banta.db.DB.moves):
			self.time += 1
		banta.db.DB.moves[self.time] = self

class Buy(_per.Persistent):
	date = 0
	time = 0
	product = None
	quantity = 0
	total = 0.0
	def __init__(self, product, quantity):
		"""
		Represents a movement in stock
		stores the product changed, the reason, and the diff in quantity (relative number)
		Instantiating a move adds it on the db, that's important because when you add it, it depends on the time
		 so it could break several stuff if its saved 2 times
		 (still you have to commit)"""
		_per.Persistent.__init__(self)
		import banta.db
		self.product = product
		self.quantity = quantity
		self.total = self.product.buy_price * quantity
		self.date = datetime.datetime.now()

		#Saves the move, as the key is time based, we need to do some calculations before saving
		self.time = banta.utils.dateTimeToInt(self.date)
		#check that there's not another move with the same key (should not happen unless using several clients at once)
		#though that's not possible YET, let's be prepared (also if some stupid person changes the system date)
		while (self.time in banta.db.DB.buys):
			self.time += 1
		banta.db.DB.buys[self.time] = self
		m = Move(product, "Compra", quantity)

class Limit(_per.Persistent):
	"""Holds a limit-rule to be used for the current month"""
	#which product is affected (if any)
	product = None
	quantity = 0
	amount = 0

