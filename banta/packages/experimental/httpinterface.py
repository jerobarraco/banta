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

	def get(self, *args, **kwargs):
		self.set_header('Content-Type', 'application/json; charset=utf-8')
		print (threading.currentThread(), threading.activeCount(), )
		cnx = _db.DB.getConnection()
		print(cnx)
		try:
			start = int(self.get_argument('start', 0))
			limit = int(self.get_argument('limit', 25))
			root = cnx.root()
			products = root['products']
			prod_cant = len(products)
			#prods = [
			#	self._prodDict(p)
			#	for p in list(products.values())[start:limit] #this could be slow, because list() could be converting everyobject in products
			#]

			if start >= prod_cant:
				start = 0
			end = start+limit
			if end >=prod_cant:
				end= prod_cant

			prods = [
				self._prodDict(products.values()[i])
				for i in range(start, end) #this could be slow, because list() could be converting everyobject in products
			]
			dict_res = {'count':len(prods), 'total':prod_cant, 'success':True, 'data':prods}
			json = tornado.escape.json_encode(dict_res)
			self.write(json)

		except Exception, e:
			logger.exception(str(e))
			self.write('{success:"false"}')

		cnx.close()




		"""$start = $request->query->get('start',0);
	$limit = $request->query->get('limit',20);

try {
$sql = "SELECT SQL_CALC_FOUND_ROWS * FROM usuarios LIMIT :atts,:attl";
$sth = $app['db']->prepare($sql);
$sth->bindValue(':atts',intval($start), PDO::PARAM_INT);
$sth->bindValue(':attl',intval($limit), PDO::PARAM_INT);
$sth->execute();

$results = $sth->fetchAll();

$sql = "SELECT FOUND_ROWS() cant";
$sth = $app['db']->prepare($sql);
$sth->execute();
$result = $sth->fetch(PDO::FETCH_ASSOC);

if(count($results) == 0) $response = new Response('',404);
else {
$response = new Response($app['twig']->render('list.json.twig',
	array(
		'usuarios' => $results,
									 'total' => $result['cant']
)),
200
);
}
}
catch(PDOException $e) {
$response = new Response('',404);
}

return $response;

});"""
		pass

	def post(self, *args, **kwargs):
		"""$info = json_decode($request->getContent(),true);

try {
$sql = "INSERT INTO usuarios(nombre,email,fecha_alta) VALUES
	(:nombre,:email,:falta)";
$sth = $app['db']->prepare($sql);
$sth->bindValue(':nombre',$info['nombre']);
$sth->bindValue(':email',$info['email']);
$sth->bindValue(':falta',DateTime::createFromFormat('d/m/Y',$info['fecha_alta'])->format('Y-m-d'));
$sth->execute();

$sql = "SELECT * FROM usuarios WHERE
id = :id";
$sth = $app['db']->prepare($sql);
$sth->bindValue(':id',intval($app['db']->lastInsertId('id')),PDO::PARAM_INT);
$sth->execute();

$results = $sth->fetchAll();
if(count($results) == 0) $response = new Response('',404);
else {
$response = new Response($app['twig']->render('usuarios.json.twig',
	array(
		'usuarios' => $results
)),
201
);
}
}
catch(PDOException $e) {
$response = new Response('', 404);
}

return $response;"""
		pass
	def put (self, user_id):
		#updates
		""" $sql = "UPDATE usuarios SET
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
		pass

	def delete(self, user_id):
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
				(r"/products/list", ProductsList),
				(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": pth }),
			],
			debug = True
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