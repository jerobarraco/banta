# -*- coding: utf-8 -*-
########################
####################### 		E X P E R I M E N T A L
#######################
from __future__ import absolute_import, print_function, unicode_literals
# system
import logging
logger = logging.getLogger(__name__)

import base64
import os
import contextlib
import sha

from operator import itemgetter, attrgetter
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

# 3rd party
import PySide.QtCore as _qc
import PySide.QtGui as _qg
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

	def __enter__(self):
		self.res = res = {'success':False}
		return self.res

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None:
			self.res['success'] = True
			act = 0
		else:
			error = unicode(exc_val)
			logger.exception(error)
			self.res['error'] = error
			self.res['success'] = False
			act = 1
		self.ins.set_header('Content-Type', 'application/json; charset=utf-8')
		json = tornado.escape.json_encode(self.res)
		self.ins.write(json)
		self.ins.onAct.emit(act)
		return True

class BasicAuthHandler(tornado.web.RequestHandler, _qc.QObject):
	#Avoid creating the signal per class, as this class will be inherited, it could lead
	#to duplicated connections and problems,
	#even though it seems to be fixed but, better to be explicit
	#http://stackoverflow.com/questions/7577290/pyside-signal-duplicating-behavior
	onAct = _qc.Signal(int)
	#looks like there  is no other way to create signals
	SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT", "OPTIONS")

	def initialize(self, server_thread, *args, **kwargs):
		self.server_thread = server_thread
		#we cant create the signal here, because error
		self.onAct.connect(self.server_thread.bling, _qc.Qt.QueuedConnection)

	def get_current_user(self, root):
		scheme, sep, token= self.request.headers.get('Authorization', '').partition(' ')
		#print ('aut', scheme, sep, token)
		#if the scheme is wrong (or have nothing
		if scheme.lower() != 'basic':
			self.set_status(500)
			self.set_header('WWW-Authenticate', 'basic realm="Banta"')
			raise Exception("Schema not supported, only Basic.")

		username, a, pwd = token.decode('base64').partition(':')
		# if pwd matches user:
		logger.debug("Login attempt [%s] [%s]" %( username, pwd))
		for user in root['users']:
			if user.name == username:
				#and user.password == pwd
				if user.password == pwd:
					logger.debug("login correcto")
					return user
		#if there is no user, or the user or passwrd is incorrect, it'll fail
		self.set_status(401)
		self.set_header('WWW-Authenticate:','basic realm="Banta"')
		raise Exception("Usuario y/o contraseña incorrecta!")


class HProducts(BasicAuthHandler):
	changed = _qc.Signal(int)
	deleteProduct = _qc.Signal(int)

	def initialize(self, server_thread):
		BasicAuthHandler.initialize(self, server_thread)
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
		if code:
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
				else:
					raise Exception("Producto no encontrado")
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
				prod_list = products.values()

				if order_by in ('stock', 'name', 'price', 'code'):
					prod_list = sorted(prod_list, key=attrgetter(order_by), reverse=reversed)


				def filter_name(p):
					return search_name in p.name.lower()

				if search_name:
					prod_list = filter(filter_name, prod_list)

				prod_cant = len(prod_list)
				end = start+limit
				if end >= prod_cant:
					end = prod_cant

				if start >=prod_cant:
					prods = []
				else:
					prods = map(self._prodDict, prod_list[start:end])
				res['count'] = len(prods)
				res['total'] = prod_cant
				res['data'] = prods

	def post(self, *args, **kwargs):
		"""inserts or modify element"""
		row = -1
		with JsonWriter(self) as res:#, _utils.Timer("post"):
			with _db.DB.threaded() as root:
				user = self.get_current_user(root)
				logger.debug('got user: '+ str(user))

				code = self.get_argument('code', "").strip()
				old_code = self.get_argument ('old_code', "").strip()

				#print ('code: ',code, 'oldcode', old_code)

				if code == "":
					raise Exception ("El código no puede estar vacio")

				if (old_code == "") or (old_code not in root['products']):
					#inserting
					prod = _db.models.Product(code)
				else:
					#modifying
					#notice "old_code"
					prod = root['products'][old_code]

				prod.setName(self.get_argument ('name', ""))
				prod.price = float(self.get_argument('price', 0.0))
				#if stock differs add a Move
				nstock = float(self.get_argument('stock', 0.0))
				if nstock != prod.stock:
					move = _db.models.Move(prod, "Modificado con Banta Touch Control", nstock-prod.stock, root=root)
				prod.stock = nstock

				#trying to re-code or insert
				if (code != old_code):
					if (code in root['products']):
						#If someone tries to change the code, but the new code is already on the db
						#fail gloriously
						raise Exception("El código ya existe")
					if (old_code in root['products']):
						#is a recode
						#todo emit delete ??
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
				user = self.get_current_user(root)
				logger.debug('got user: '+ str(user))
				if code not in root['products']:
					raise Exception("No existe el producto.")
				#no need to care of special cases, this will raise an exception if not in list
				row = list(root['products'].keys()).index(code)

			res['return'] = self.deleteProduct.emit(row)
			res['row'] = row
			res['code'] = code

class Reports(BasicAuthHandler):
	def get(self, *args, **kwargs):
		with JsonWriter(self) as res:#, _utils.Timer('reports'):
			#try to get the start and end parameter
			self.get_argument('start', 0)
			report_type = self.get_argument('type', 'product')
			#gets the start and end from the current date
			rep_mod = _pack.optional.reports
			reports = {
				'product': rep_mod.reportProduct,
				'category': rep_mod.reportCategory,
				'user': rep_mod.reportUser,
				'client': rep_mod.reportClient,
				'move': rep_mod.reportMove,
				'buy': rep_mod.reportBuy
			}
			start, today, end = map(_utils.dateTimeToInt, _utils.currentMonthDates())
			gen_report = reports[report_type]
			with _db.DB.threaded() as root:
				results = gen_report((start, end), root)

				#ponemos los headers en su propia clave
				heads = results.pop('_headers')
				res['headers'] = heads
				res['idx_tag'] = results.pop('_idx_tag')
				res['idx_val'] = results.pop('_idx_val')
				#converts the list of Results* to lists of strings, now l_results is a matrix (table)
				#sorted is used here to not speed down the reports in the main window...
				#is possible only because we defined __lt__ in the result* classes
				l_results = (i.toStringList() for i in sorted(results.values(), reverse=True))
				#we sort them by the column for the graphic
				#s_res = sorted(l_results, key=itemgetter(res['idx_val']))
				res['data'] = list(l_results)
				print ( res['data'] )


class Server( _qc.QThread ):
	gotIP = _qc.Signal(str)
	def __init__(self, parent):
		_qc.QThread.__init__(self)
		self.parent = parent
		#notice this is in the main thread
		self.lbs = self.parent.app.window.lb_server
		self.blue = _qg.QPixmap(":/same/SamegameCore/pics/blueStone.png")
		self.blue = self.blue.scaled(self.blue.size()/2.0)

		self.red = _qg.QPixmap(":/same/SamegameCore/pics/redStone.png")
		self.red = self.red.scaled(self.red.size()/2.0)

		self.green = _qg.QPixmap(":/same/SamegameCore/pics/greenStone.png")
		self.green = self.green.scaled(self.green.size()/2.0)

		self.yellow = _qg.QPixmap(":/same/SamegameCore/pics/yellowStone.png")
		self.yellow = self.yellow.scaled(self.yellow.size()/2.0)
		self.pixs = [self.green, self.red, self.yellow, self.blue]
		self.timer = _qc.QTimer()
		self.timer.setInterval(500)
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.blingOut)
		self.blingOut()
		self.gotIP.connect(self.showIP)

	@_qc.Slot(int)
	def syncDB(self, row):
		#call from main loop only (use queued connection)
		#print ("sync", threading.currentThread(), threading.activeCount())
		_db.DB.abort()
		_db.DB.cnx.sync()
		m = _pack.base.products.MODEL
		old = m.rowCount()
		m._setMaxRows()
		new = m.rowCount()
		start = m.index(row, 0)
		end = m.index(row+1, m.columnCount())
		if old<new:
			#cuold be (.., old, new-1), but it could crash the whole banta if there's an error
			#either way you can only add one item at a time
			#and SHOULD..
			m.beginInsertRows(_qc.QModelIndex(), old, old)
			m.endInsertRows()
		else:
			m.dataChanged.emit(start, end)


	@_qc.Slot(int)
	def deleteProduct(self, row):
		model = _pack.base.products.MODEL
		model.removeRows(row, 1)

	@_qc.Slot(int)
	def bling(self, activity=0):
		self.timer.stop()
		self.lbs.setPixmap(self.pixs[activity])
		self.timer.start()

	@_qc.Slot()
	def blingOut(self):
		#is single shot so we dont need to stop the timer
		self.lbs.setPixmap(self.blue)

	@_qc.Slot(str)
	def showIP(self, ip):
		#Main thread
		self.lbs.setToolTip("IP: "+ip)

	def _getIP(self):
		#Tries to get the ip on the local machine
		import socket
		n = "No se pudo detectar"
		s = None

		try:
			#first it tries to get it through the internet connection
			#this is good because it will show the ip associated to an interface connected to internet
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(("gmail.com", 80))
			n = s.getsockname()[0]
		except Exception, e:
			logger.exception("Error when trying to get the local ip: "+ unicode(e))
		finally:
			if s: s.close()

		try:
			#and then tries using gethostbyname
			#this could fail and get nothing
			if not n:
				ips = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
				ips = ips[:1]
				if ips:
					n = ips[0]
		except Exception , e:
			logger.exception("Error when trying to get the local ip 2: "+ unicode(e))
		return n

	def run(self, *args, **kwargs):
		#print (threading.currentThread(), threading.activeCount(), )
		#pth = os.path.split(__file__)[0]
		ip  = self._getIP()
		self.gotIP.emit(ip)
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
		application.listen(8080, '0.0.0.0')
		tornado.ioloop.IOLoop.instance().start()

class WebService(_pack.GenericModule):
	REQUIRES = []
	NAME = "webservice"

	def load(self):
		self.server = Server(self)
		self.server.start()

