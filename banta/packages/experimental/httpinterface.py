# -*- coding: utf-8 -*-
########################
####################### 		E X P E R I M E N T A L
#######################
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

import PySide.QtCore as _qc

import os
import contextlib

import tornado
import tornado.web
import tornado.escape
import threading


import banta.db as _db
import banta.packages as _pack

#This module can be completely wrong, we might be calling the other thread directly,
#so be sure to check the threads!

import time
@contextlib.contextmanager
def timer():
	s = None
	try:
		s = time.time()
		yield
		r = time.time() -s
		print ('time:', r)
	except:
		print ("error")
		pass

def jsonwriter(func):
	"""Decorator,
	the decorated function must be a method of a class inherinting RequestHandler
	(or implementing write)
	it must have at least 1 parameter (self),
	and it will create a dictionary self.res in where the data should be stored
	When it finishes it writes everything back as a json, and sets the headers.
	if there where any exception, it sets the success flag to False, and logs the exception
 	"""
	def jsonify(*args, **kwargs ):
		self = args[0]
		self.res = {'success':False}
		try:
			func(*args, **kwargs)
			self.res['success'] = True
		except Exception, e:
			error = str(e)
			logger.exception(error)
			self.res['exception'] = error
			self.res['success'] = False

		self.set_header('Content-Type', 'application/json; charset=utf-8')
		json = tornado.escape.json_encode(self.res)
		self.write(json)
	#outside jsonify
	return jsonify

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

	@jsonwriter
	def get(self, *args, **kwargs):
		"""Lists one or many products
		depending on the parameters
		"""
		print ('get', threading.currentThread(), threading.activeCount(), )
		code = self.get_argument('code', None)
		if code is not None:
			self._getProduct(code)
		else:
			self._getProductList()

	def _getProduct(self, code):
		with _db.DB.threaded() as root:
			code = self.get_argument('code')
			print('code', code)
			prod = root['products'][code]
			self.res['data'] = self._prodFullDict(prod)

	def _getProductList(self):
		with _db.DB.threaded() as root:
			start = int(self.get_argument('start', 0))
			limit = int(self.get_argument('limit', 25))
			products = root['products']
			prod_cant = len(products)
			if start >= prod_cant:
				start = 0

			end = start+limit

			if end >=prod_cant:
				end= prod_cant

			prods = [
				self._prodDict( products.values()[i] )
				for i in range(start, end)
			]
			self.res = {'count':len(prods), 'total':prod_cant, 'success':True, 'data':prods}

	@jsonwriter
	def post(self, *args, **kwargs):
		"""inserts or modify element"""
		row = -1
		with _db.DB.threaded() as root:
			print ("post", threading.currentThread(), threading.activeCount())

			code = self.get_argument('code', "")
			old_code = self.get_argument ('old_code', "")

			print ('code: ',code, 'oldcode', old_code)

			if code.strip() == "":
				raise Exception ("Code can't be empty")

			if (old_code.strip() == "") or (old_code not in root['products']):
				#inserting
				prod = _db.models.Product(code)
			else:
				#modifying
				#notice "old_code"
				prod = root['products'][old_code]

			prod.name = self.get_argument ('name', "")
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

			self.res['product'] = self._prodFullDict(prod)
			#Outside with
			#we emit the signal now, because the changes must be commited
			#Is a queued connection, it shouln't care,
			# BUT in the rare case its trapped before the thread is commited, it will be no good
			self.changed.emit(row)
		#end

	@jsonwriter
	def delete(self, *args, **kwargs):
		row = -1
		code = self.get_argument('code')#code can't be None
		print ("delete", threading.currentThread(), threading.activeCount())
		print ('code', code)
		with _db.DB.threaded() as root:
			if code not in root['products']:
				raise Exception("Product does not exists")
			#no need to care of special cases, this will raise an exception if not in list
			row = list(root['products'].keys()).index(code)

		ret = self.deleteProduct.emit(row)
		self.res['row']= row
		self.res['code'] = code
		self.res['return'] = ret


class Server( _qc.QThread ):
	def __init__(self, parent):
		_qc.QThread.__init__(self)
		self.parent = parent

	#called from main loop
	@_qc.Slot(int)
	def syncDB(self, row):
		print ("sync", threading.currentThread(), threading.activeCount())
		_db.DB.abort()
		_db.DB.cnx.sync()
		print(row)
		m = _pack.base.products.MODEL
		start = m.index(row, 0)
		end = m.index(row, m.columnCount())
		m.dataChanged.emit(start, end)

	@_qc.Slot(int)
	def deleteProduct(self, row):
		model = _pack.base.products.MODEL
		model.removeRows(row, 1)

	def run(self, *args, **kwargs):
		print (threading.currentThread(), threading.activeCount(), )
		pth = os.path.split(__file__)[0]
		pth = os.path.join(pth, 'static')
		application = tornado.web.Application(
			[
				(r'/prods(.*)', HProducts, {'server_thread':self}),
				#(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": pth }),
			],
			#debug = True
			gzip = True,
			static_path= pth,

		)
		application.listen(8080)
		tornado.ioloop.IOLoop.instance().start()

#TODO use qt signnls on the model to delete and insert
class HTTPInterface(_pack.GenericModule):
	REQUIRES = []
	NAME = "HTTPI"
	products = _qc.Signal(int)

	def load(self):
		self.server = Server(self)
		self.server.start()
