# -*- coding: utf-8 -*-
########################
####################### 		E X P E R I M E N T A L
#######################
from __future__ import absolute_import, print_function, unicode_literals
from packages.generic import GenericModule
from PySide import QtCore
import logging
import web
import db

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

logger = logging.getLogger(__name__)

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
					o.write ("<tr><td>%s</td><td>%s</td><td>%s</td>"%(p.code.encode('utf-8'), p.name.encode('utf-8'), p.price))
					o.write("</tr>")
				o.write("</table></body></html>")
				return o.getvalue()
		main.prods =  self.parent.productCount
		main.getProd = self.parent.getProduct
		d = locals()
		d['prods'] = self.parent.productCount

		urls = ('/', 'main')
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
		return len(db.zodb.products)

	@QtCore.Slot(int)
	def getProduct(self, i):
		return db.zodb.products.values()[i]