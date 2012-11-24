# -*- coding: utf-8 -*-
########################
####################### 		E X P E R I M E N T A L
#######################
from __future__ import absolute_import, print_function, unicode_literals
# system
import logging
logger = logging.getLogger(__name__)

import os
import contextlib
from operator import itemgetter, attrgetter
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

# 3rd party
import PySide.QtCore as _qc
import tornado
import tornado.web
import tornado.escape
import threading

#internal

import banta.db as _db
import banta.packages as _pack
import banta.utils as _utils

#This module can be completely wrong, we might be calling the other thread directly,
#so be sure to check the threads!

#I dont really like decorators, i think they are a bad idea and can be supplied by other means...
# like passing results to a function.
#so i think i'll convert this to a context manager which does the same thing but less cumbersome
class JsonWriter(object):
	"""Context manager for a json writer.
	needs an argument, an instance that inherits from RequestHandler
	(which must implement the method write and set_header)
	it will create a dictionary in where the data should be stored
	When it finishes it writes everything back as a json, and sets the headers.
	if there where any exception, it sets the success flag to False, and logs the exception
	"""
	def __init__(self, instance=None):
		self.ins = instance

	def __enter__(self, instance=None):
		self.res = res = {'success':False}
		return self.res

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None:
			self.res['success']= True
		else:
			error = str(exc_val)
			logger.exception(error)
			self.res['exception'] = error
			self.res['success'] = False

		self.ins.set_header('Content-Type', 'application/json; charset=utf-8')
		json = tornado.escape.json_encode(self.res)
		self.ins.write(json)
		return True

class HProducts(tornado.web.RequestHandler, _qc.QObject):
	SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT",
											 "OPTIONS")
	changed = _qc.Signal(int)
	deleteProduct = _qc.Signal(int)

	def initialize(self, server_thread):
		self.server_thread = server_thread
		self.changed.connect(self.server_thread.syncDB, _qc.Qt.QueuedConnection)
		#i could delete from here.. but to be honest, is safer to do it in the main thread
		#beause of signals needed to be emited and models and modelproxies
		#notice the blocking queued
		self.deleteProduct.connect(self.server_thread.deleteProduct, _qc.Qt.QueuedConnection)

	def _prodDict(self, p):
		return {'code':p.code, 'name':p.name, 'price':p.price, 'stock':p.stock}

	def _prodFullDict(self, p):
		return {'code':p.code, 'name':p.name, 'price':p.price, 'stock':p.stock}

	def get(self, *args, **kwargs):
		"""Lists one or many products
		depending on the parameters
		"""
		code = self.get_argument('search_code', None)
		if code is not None:
			self._getProduct(code)
		else:
			self._getProductList()

	def _getProduct(self, code):
		with JsonWriter(self) as res:
			with _db.DB.threaded() as root:
				prods = []
				if code in root['products']:
					prod = root['products'][code]
					#to allow a "search" function later
					prods.append(self._prodFullDict(prod))

				res['count'] = len(prods)
				res['total'] = len(root['products'])
				res['data'] = prods

	def _getProductList(self):
		with JsonWriter(self) as res:
			with _db.DB.threaded() as root:
				start = int(self.get_argument('start', 0))
				limit = int(self.get_argument('limit', 100))
				search_name = self.get_argument('search_name', "").lower()
				order_by = self.get_argument("order_by", "").lower()
				reversed = self.get_argument('order_asc', "1").lower() != "1"

				products = root['products']
				prod_cant = len(products)

				if start >= prod_cant:
					start = 0

				end = start+limit

				if end >= prod_cant:
					end = prod_cant

				prod_list = products.values()

				if order_by == 'stock':
					prod_list = sorted(prod_list, key=attrgetter('stock'), reverse=reversed)

				def filter_name(p):
					return search_name in p.name.lower()

				if search_name:
					prod_list = filter(filter_name, prod_list)

				prods = map(self._prodDict, prod_list[start:end])
				res['count'] = len(prods)
				res['total'] = prod_cant
				res['data'] = prods

	def post(self, *args, **kwargs):
		"""inserts or modify element"""
		row = -1
		with JsonWriter(self) as res:
			with _db.DB.threaded() as root:
				#print ("post", threading.currentThread(), threading.activeCount())

				code = self.get_argument('code', "")
				old_code = self.get_argument ('old_code', "")

				#print ('code: ',code, 'oldcode', old_code)

				if code.strip() == "":
					raise Exception ("Code can't be empty")

				if (old_code.strip() == "") or (old_code not in root['products']):
					#inserting
					prod = _db.models.Product(code)

				else:
					#modifying
					#notice "old_code"
					prod = root['products'][old_code]

				prod.setName(self.get_argument ('name', ""))
				prod.price = float(self.get_argument('price', 0.0))
				prod.stock = float(self.get_argument('stock', 0.0))

				#trying to re-code or insert
				if (code != old_code):
					if (code in root['products']):
						#If someone tries to change the code, but the new code is already on the db
						#fail gloriously
						raise Exception("The new code already exists")
					if (old_code in root['products']):
						#is a recode
						#todo emit delete
						del root['products'][old_code]
				#finally inserts the new one (notice is code)
				prod.code = code
				root['products'][code] = prod

				row = list(root['products'].keys()).index(code)

				res['product'] = self._prodFullDict(prod)
			#end db
			#Outside with
			#we emit the signal now, because the changes must be commited
			#Is a queued connection, it shouln't care,
			# BUT in the rare case its trapped before the thread is commited, it will be no good
			self.changed.emit(row)
		#endjson
	#endfunc

	def delete(self, *args, **kwargs):
		row = -1
		with JsonWriter(self) as res:
			code = self.get_argument('code')#code can't be None
			#print ("delete", threading.currentThread(), threading.activeCount())
			#print ('code', code)
			with _db.DB.threaded() as root:
				if code not in root['products']:
					raise Exception("Product does not exists")
				#no need to care of special cases, this will raise an exception if not in list
				row = list(root['products'].keys()).index(code)

			res['return'] = self.deleteProduct.emit(row)
			res['row'] = row
			res['code'] = code

class Reports(tornado.web.RequestHandler, _qc.QObject):
	SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT", "OPTIONS")

	def initialize(self, server_thread):
		self.server_thread = server_thread

	def get(self, *args, **kwargs):
		with JsonWriter(self) as res:
			#try to get the start and end parameter
			self.get_argument('start', 0)
			report_type = self.get_argument('type', 'product')
			#gets the start and end from the current date
			rep_mod = _pack.optional.reports
			reports = {
				'product':rep_mod.reportProduct,
				'category': rep_mod.reportCategory,
				'user':rep_mod.reportUser,
				'client':rep_mod.reportClient,
				'move':rep_mod.reportMove,
				'buy':rep_mod.reportBuy
			}
			start, today, end = map(_utils.dateTimeToInt, _utils.currentMonthDates())
			gen_report = reports[report_type]
			with _db.DB.threaded() as root:
				results = gen_report((start, end), root)
				res['headers'] = results.pop('_headers')
				res['data'] = []
				for i in results.values():
					res['data'].append(i.toList())


class Server( _qc.QThread ):
	def __init__(self, parent):
		_qc.QThread.__init__(self)
		self.parent = parent

	@_qc.Slot(int)
	def syncDB(self, row):
		#call from main loop only (use queued connection)
		#print ("sync", threading.currentThread(), threading.activeCount())
		_db.DB.abort()
		_db.DB.cnx.sync()
		m = _pack.base.products.MODEL
		m._setMaxRows()
		start = m.index(row, 0)
		end = m.index(row, m.columnCount())
		m.dataChanged.emit(start, end)

	@_qc.Slot(int)
	def deleteProduct(self, row):
		model = _pack.base.products.MODEL
		model.removeRows(row, 1)

	def run(self, *args, **kwargs):
		#print (threading.currentThread(), threading.activeCount(), )
		#pth = os.path.split(__file__)[0]
		pth = os.getcwd()
		pth = os.path.join(pth, 'static')
		application = tornado.web.Application(
			[
				(r'/prods(.*)', HProducts, {'server_thread':self}),
				(r'/reports(.*)', Reports, {'server_thread':self}),
			],
			#debug = True
			gzip = True,
			static_path= pth,
		)
		application.listen(8080)
		tornado.ioloop.IOLoop.instance().start()

class WebService(_pack.GenericModule):
	REQUIRES = []
	NAME = "webservice"

	def load(self):
		self.server = Server(self)
		self.server.start()
