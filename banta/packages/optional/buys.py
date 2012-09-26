# -*- coding: utf-8 -*-
#TODO keep code compatible with 3.x
#CAREFUL! unicode literals!
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
#TODO refactor
from PySide import QtCore, QtGui
from banta.packages import GenericModule
from banta.db.models import LICENSES_NOT_FREE

import banta.db as _db

class Buys(GenericModule):
	REQUIRES = (GenericModule.P_ADMIN, )
	NAME = 'Buys'
	LICENSES = LICENSES_NOT_FREE
	def __init__(self, app):
		super(Buys, self).__init__(app)
		self.app.window.bNewStockBuy.setDefaultAction(self.app.window.acNewStockBuy)
		self.dialog = self.app.uiLoader.load(":/data/ui/buys.ui", self.app.window)
		self.dialog.setWindowIcon(self.app.window.windowIcon())

	def load(self):
		import banta.packages.base.products
		self.prod = None
		self.packs = 0
		self.pack_units = 0
		self.buy_price = 0
		self.app.window.acNewStockBuy.setEnabled(True)
		self.app.window.acNewStockBuy.triggered.connect(self.newBuy)
		self.dialog.cbProd.currentIndexChanged.connect(self.prodChanged)
		self.dialog.dPacks.valueChanged.connect(self.packChanged)
		prod_mod_name = banta.packages.base.products.Products.NAME
		model = self.app.modules[prod_mod_name].model
		cbp = self.dialog.cbProd
		cbp.setModel(model)

		#v = QtGui.QTableView()
		#v.setSelectionMode(QtGui.QTableView.SingleSelection)
		#v.setSelectionBehavior(QtGui.QTableView.SelectRows)#i should be hidding all the columns
		#cbp.setView(v)
		#cbp.setModelColumn(0)
		#i was decided whether to set do this in "product" model or here. i've concluded that:
		#as this module (buys) is not part of the FREE (hence always loaded) modules, is best to load this here.
		#todo button to change to external_code

	@QtCore.Slot()
	def newBuy(self):
		if self.dialog.exec_() != QtGui.QDialog.Accepted:
			#flat is better than nested
			return
		if (not self.prod) or (self.units == 0):
			return
		self.prod.stock += self.units
		#Beware, a new buy triggers a new movement
		b = _db.models.Buy(self.prod, self.units)
		_db.DB.commit()

	@QtCore.Slot(int)
	def prodChanged(self, i):
		if i<0: return
		code = self.app.window.cb_billProds.itemData(i, QtCore.Qt.UserRole)
		self.prod = _db.DB.products[code]
		self.pack_units = self.prod.pack_units
		self.buy_price = self.prod.buy_price
		self.showInfo()

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