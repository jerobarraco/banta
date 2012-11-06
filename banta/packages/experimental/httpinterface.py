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

import tornado
import tornado.web
import tornado.escape
import threading
import os

import banta.db as _db
import banta.packages as _pack

#TODO use the (qt)model in product module, and be sure to be calling the slot in queued connection
#This module can be completely wrong, we might be calling the other thread directly

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

	def _write_json(self, obj):
		self.set_header('Content-Type', 'application/json; charset=utf-8')
		json = tornado.escape.json_encode(obj)
		self.write(json)

	def get(self, *args, **kwargs):
		"""Lists one or many products
		depending on the parameters
		"""
		print (threading.currentThread(), threading.activeCount(), )
		code = self.get_argument('code', None)
		if code is not None:
			self.getProduct(code)
		else:
			self.getProductList()

	def getProduct(self, code):
		cnx = _db.DB.getConnection()
		print ('getproduct ', cnx)
		res = {'success':False}
		try:
			r = cnx.root()
			code = self.get_argument('code')
			print('code', code)
			prod = r['products'][code]
			res['data'] = self._prodFullDict(prod)
			res['success']  = True
		except Exception, e:
			error = str(e)
			logger.exception(error)
			res['success']=False
			res['exception'] = error
		finally:
			self._write_json(res)

	def getProductList(self):
		cnx = _db.DB.getConnection()
		print ('getproductlist', cnx)
		res = {'success':False}
		try:
			start = int(self.get_argument('start', 0))
			limit = int(self.get_argument('limit', 25))
			root = cnx.root()
			products = root['products']
			prod_cant = len(products)

			if start >= prod_cant:
				start = 0

			end = start+limit

			if end >=prod_cant:
				end= prod_cant

			prods = [
				self._prodDict(products.values()[i])
				for i in range(start, end)
			]
			res = {'count':len(prods), 'total':prod_cant, 'success':True, 'data':prods}
		except Exception, e:
			error = str(e)
			logger.exception(error)
			res['exception'] = error
			res['success'] = False
		finally:
			self._write_json(res)
			cnx.close()

	def post(self, *args, **kwargs):
		"""inserts or modify element"""
		res = {'success':False}
		try:
			cnx = _db.DB.getConnection()
			print ("post", threading.currentThread(), threading.activeCount(), cnx)
			r = cnx.root()

			code = self.get_argument('code', "")
			old_code = self.get_argument ('old_code', "")

			print ('code:',code)
			print ('oldcode', old_code)

			if code.strip() == "":
				raise Exception ("Code can't be empty")

			if (old_code.strip() == "") or (old_code not in r['products']):
				#inserting
				prod = _db.models.Product(code)
			else:
				#modifying
				#notice "old_code"
				prod = r['products'][old_code]

			prod.name = self.get_argument ('name', "")
			prod.price = float(self.get_argument('price', 0.0))
			prod.stock = float(self.get_argument('stock', 0.0))


			#trying to re-code or insert
			if (code != old_code):
				if (code in r['products']):
					#If someone tries to change the code, but the new code is already on the db
					#fail gloriously
					raise Exception("The new code already exists")
				if (old_code in r['products']):
					#is a recode
					#todo emit delete
					del r['products'][old_code]
				#finally inserts the new one (notice is code)
				prod.code = code
				r['products'][code] = prod

			_db.DB.commit()
			row = list(r['products'].keys()).index(code)
			self.changed.emit(row)

			res['product'] = self._prodFullDict(prod)
			res['success'] = True

		except Exception, e:
			error = str(e).encode('ascii', 'replace')
			logger.exception(error)
			res['success'] = False
			res['exception'] = error
			_db.DB.abort()
		finally:
			self._write_json(res)
			cnx.close()

	def delete(self, *args, **kwargs):
		res = {'success':False}
		try:
			cnx = _db.DB.getConnection()
			print ("delete",  args, kwargs, threading.currentThread(), threading.activeCount(), cnx)
			r = cnx.root()

			code = self.get_argument('code')#code can't be None
			print ('code', code)
			if code not in r['products']:
				raise Exception("Product does not exists")

			row = list(r['products'].keys()).index(code)
			ret = self.deleteProduct.emit(row)
			res['success'] = True
			res['return'] = ret
		except Exception , e:
			res['success'] = False
			res['exception'] = str(e)
		finally:
			self.write (tornado.escape.json_encode(res))

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
				(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": pth }),
			],
			#debug = True
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
