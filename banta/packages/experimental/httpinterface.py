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


class ProductsList(tornado.web.RequestHandler):
	def initialize2(self, server):
		pass
	def get(self, *args, **kwargs):
		self.set_header('Content-Type', 'application/json; charset=utf-8')
		print (threading.currentThread(), threading.activeCount(), )
		cnx = _db.DB.getConnection()
		print(cnx)
		try:
			root = cnx.root()
			products = root['products']
			prod_cant = len(products)
			prods = [
			self.prod_as_dict(p)
			for p in products.values()
			]
			dict_res = {'prods':prods, 'count':len(prods), 'total':prod_cant}
			json = tornado.escape.json_encode(dict_res)
			self.write(json)

		except Exception, e:
			logger.exception(str(e))

		cnx.close()

	def prod_as_dict(self, p):
		return {'code':p.code, 'name':p.name, 'price':p.price, 'stock':p.stock}

class HProducts(tornado.web.RequestHandler):
	SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT",
											 "OPTIONS")
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

			code = self.get_argument('code')#code can't be None
			print ('code:',code)
			if code in r['products']:
				prod = r['products'][code]
			else:
				prod = _db.models.Product(code)
				r['products'][code] = prod
			prod.name = self.get_argument ('name', "")
			prod.price = float(self.get_argument('price', 0.0))
			prod.stock = float(self.get_argument('stock', 0.0))
			_db.DB.commit()
			res['product'] = self._prodFullDict(prod)
			res['success'] = True
		except Exception, e:
			error = str(e).encode('ascii', 'replace')
			logger.exception(error)
			res['success']=False
			res['exception'] = error
		finally:
			self._write_json(res)

	"""def put (self, user_id):
		#updates
		 $sql = "UPDATE usuarios SET
                    nombre = :nombre,
                    email= :email,
                    fecha_alta = :fecha_alta
                WHERE id = :id";
        $sth = $app['db']->prepare($sql);
        $sth->bindValue(':nombre',$info['nombre']);
        $sth->bindValue(':email',$info['email']);
        $sth->bindValue(':fecha_alta',$info['fecha_alta']);
        $sth->bindValue(':id',intval($info['id']),PDO::PARAM_INT);
        $sth->execute();
        """

	def delete(self, *args, **kwargs):
		print ("delete", args, kwargs)
		res = {'success':False}
		try:
			idn = int(self.get_argument('id', None ))
			print(idn)
			res['success'] = True
			res['id'] = idn
		except Exception , e:
			res['success'] = False
			res['exception'] = str(e)
		finally:
			self.write (tornado.escape.json_encode(res))
		"""try {
		$sql = "DELETE FROM usuarios
		WHERE id = :id";
		$sth = $app['db']->prepare($sql);
		$sth->bindValue(':id',intval($id),PDO::PARAM_INT);
		$sth->execute();
		$response = new Response('',204);
		}
	catch(PDOException $e) {
	$response = new Response('', 404);
	}

	return $response;"""

class Server( _qc.QThread ):
	def __init__(self, parent):
		_qc.QThread.__init__(self)
		self.parent = parent

	def run(self, *args, **kwargs):
		print (threading.currentThread(), threading.activeCount(), )
		pth = os.path.split(__file__)[0]
		pth = os.path.join(pth, 'static')
		application = tornado.web.Application(
			[
				(r'/prods/(.*)', HProducts),
				(r'/prods(.*)', HProducts),
				(r"/products/list", ProductsList),
				(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": pth }),
				],
			#debug = True
		)
		application.listen(8080)
		tornado.ioloop.IOLoop.instance().start()

class HTTPInterface(_pack.GenericModule):
	REQUIRES = []
	NAME = "HTTPI"
	products = _qc.Signal(int)
	def __init__(self, app):
		super(HTTPInterface, self).__init__(app)

	def load(self):
		self.server = Server(self)
		self.server.start()

	@_qc.Slot()
	def productCount(self):
		print('2', threading.currentThread())
		return len(_db.DB.products)

	@_qc.Slot(int)
	def getProduct(self, i):
		return _db.DB.products.values()[i]