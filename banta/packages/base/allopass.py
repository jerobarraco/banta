# -*- coding: utf-8 -*-
#TODO keep code compatible with 3.x
#CAREFUL! unicode literals!
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
from PySide import QtCore, QtGui
import db
import db.models
from packages.generic import GenericModule

class Buys(GenericModule):
	REQUIRES = (GenericModule.P_ADMIN, )
	NAME = 'Buys'
	countries = ('United states', 'Chile')
	messages = ('')
	def __init__(self, app):
		super(Buys, self).__init__(app)
		self.dialog = self.app.uiLoader.load(":/data/ui/allopass.ui", self.app.window)
		self.dialog.setWindowIcon(self.app.window.windowIcon())

	def load(self):
		self.app.window.acAllopass.triggered.connect(self.code)
		self.dialog.cbCountries.setItems(self.countries)
		self.dialog.cbCountries.currentIndexChanged.connect(self.countChanged)
		self.dialog.dPacks.valueChanged.connect(self.packChanged)
		import packages.base.products
		model = self.app.modules[packages.base.products.Products.NAME].model
		cbp = self.dialog.cbProd
		cbp.setModel(model)

	@QtCore.Slot()
	def code(self):
		if self.dialog.exec_() == QtGui.QDialog.Accepted:
			pass


	@QtCore.Slot(int)
	def countChanged(self, i):
		if i<0: return
		self.dialog.lb_msg.setText(self.messages[i])

	@QtCore.Slot(int)
	def packChanged(self, i):
		self.packs = i
		self.showInfo()

	def showInfo(self):
		self.units = self.pack_units*self.packs
		self.price = self.units*self.buy_price
		self.dialog.lb_packItems.setText(str(self.pack_units))
		self.dialog.lb_items.setText(str(self.units))
		self.dialog.lb_price.setText(str(self.buy_price))
		self.dialog.lb_total.setText(str(self.price))


#			{'formName':'form1', 'trxid':'', 'idd':'889565', 'ids':'225379','recall':'1',
#			 'lang':'es_ES','code-txt':'CÓDIGO%d', 'code[]':'lawlwtf',
#			 'referer':'https://payment.allopass.com/buy/checkout.apu?ids=284381&idd=1180652&lang=en}
#
#
#			 eng = {'formName':'form2', 'trxid':'', 'idd':'1180652', 'ids':'284381','recall':'1',
#							'lang':'en_GB','code-txt':'CÓDIGO%d', 'code[]':'lolwhat',
#							'referer':'https://payment.allopass.com/buy/checkout.apu?ids=284381&idd=1180652&lang=en'}
#		https://payment.allopass.com/acte/access.apu
#
#
#		import httplib, urllib
#		>>> params = {'spam': 1, 'eggs': 2, 'bacon': 0})
#		>>> headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
#		>>> conn = httplib.HTTPConnection("payment.allopass.com:80")
#		>>> conn.request("POST", "/acte/access.apu", params, headers)
#		>>> response = conn.getresponse()
#		>>> print response.status, response.reason
#		200 OK
#		>>> data = response.read()
#		>>> conn.close()