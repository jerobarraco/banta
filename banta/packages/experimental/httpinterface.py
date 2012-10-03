# -*- coding: utf-8 -*-
########################
####################### 		E X P E R I M E N T A L
#######################
from __future__ import absolute_import, print_function, unicode_literals
import logging

from PySide import QtCore

import web
import json
import gzip
import banta.db
from banta.packages import GenericModule

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

logger = logging.getLogger(__name__)

#TODO use the (qt)model in product module, and be sure to be calling the slot in queued connection
class Reader( QtCore.QThread ):
	def __init__(self, parent):
		QtCore.QThread.__init__(self)
		self.parent = parent

	def run(self, *args, **kwargs):
		class main:
			def GET(self):
				o = StringIO()
				#si el usuario esta logueado, muestra la pagina principal
				#si no lo esta, le muestra el formulario de login
				o.write("<html><body>hi, I'm Nande and this is BANTA!\n and you have %s products"%self.prods())
				o.write("<br /><table>")
				for i in range(20):
					p = self.getProd(i)
					item = "<tr><td>%s</td><td>%s</td><td>%s</td>"%(p.code, p.name, p.price)
					o.write (item.encode('utf-8', 'replace'))
					o.write("</tr>")
				o.write("</table></body></html>")
				return o.getvalue()
		class prodlist:
			def prod_as_dict(self, p):
				return {'code':p.code, 'name':p.name, 'price':p.price, 'stock':p.stock}

			def GET(self):
				prod_mod = banta.packages.base.products.MODEL

				o = StringIO()
				prod_cant = prod_mod.rowCount()#self.prods()
				prods = [
					self.prod_as_dict(
						self.getProd(i)
					) for i in range(prod_cant)
				]
				dict_res = {'prods':prods, 'count':len(prods), 'total':prod_cant}
				#zipper = gzip.GzipFile(fileobj=o, mode="w")
				#json.dump(dict_res, zipper)
				#web.header('Content-Encoding','gzip', unique=True)
				json.dump(dict_res, o)
				web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
				return o.getvalue()
		main.prods =  self.parent.productCount
		main.getProd = self.parent.getProduct
		prodlist.prods = self.parent.productCount
		prodlist.getProd =  self.parent.getProduct
		d = locals()
		d['prods'] = self.parent.productCount

		urls = ('/', 'main',
		'/products/list', 'prodlist')
		app = web.application(urls, locals())
		app.run()


class HTTPInterface(GenericModule):
	REQUIRES = []
	NAME = "HTTPI"
	products = QtCore.Signal(int)
	def __init__(self, app):
		super(HTTPInterface, self).__init__(app)

	def load(self):
		#the reader will fetch the news from internet, or fail-to if there's no internet
		self.reader = Reader(self)
		self.reader.start()

	@QtCore.Slot()
	def productCount(self):
		return len(banta.db.DB.products)

	@QtCore.Slot(int)
	def getProduct(self, i):
		return banta.db.DB.products.values()[i]