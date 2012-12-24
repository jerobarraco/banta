# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

import PySide.QtCore as _qc
from PySide.QtTest import QTest as _qtt

import banta.packages as _pack

class Reader( _qc.QThread ):
	onCode = _qc.Signal(str)
	def __init__(self, parent):
		_qc.QThread.__init__(self)
		self.parent = parent
		self.onCode.connect(self.parent.code)

		#self.p.set_data_handler(self.my_handler)

	def my_handler(self, proc, image, closure):
		# extract results
		for symbol in image.symbols:
			# do something useful with results
			print( 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data)
			self.onCode.emit(symbol.data)

	def run(self):
		import zbar
		self.zbar = zbar
		self.p = zbar.Processor()
		self.p.init()
		self.p.visible = True
		self.p.active = True
		self.p.process_one()
		self.p.visible = False
		for r in self.p.results:
			self.onCode.emit(r.data)
		"""try:
			# keep scanning until user provides key/mouse input
			print ("waiting")
			p.user_wait()
		except zbar.WindowClosed, e:
			pass"""


class ZBarCode(_pack.GenericModule):
	REQUIRES = []
	NAME = "zbarcode"
	products = _qc.Signal(int)
	def __init__(self, app):
		super(ZBarCode, self).__init__(app)
		self.app.window.acSameGame.setEnabled(False)

	def load(self):
		self.reader = Reader(self)
		self.app.window.acScan.triggered.connect(self.scan)

	def scan(self):
		self.reader.start()

	@_qc.Slot(str)
	def code(self, code):
		print (code)
		self.app.window.cb_billProds.lineEdit().setText(code + "\t")