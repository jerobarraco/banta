# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

import PySide.QtCore as _qc
import PySide.QtGui as _qg

import banta.utils
import banta.db as _db
import banta.packages as _pkg

class ClientDetails(_pkg.GenericModule):
	REQUIRES = (_pkg.GenericModule.P_ADMIN, )
	NAME = 'client_details'
	def __init__(self, app):
		super(ClientDetails, self).__init__(app)
		self.app.window.bClientAccount.setVisible(False)

	def load(self):
		w = self.app.window
		self.dialog = self.app.uiLoader.load(":/data/ui/client_details.ui")
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		#TOdo check if other dynamically loaded dialogs also sets their translator and if it affects or not
		self.dialog.setWindowIcon(w.windowIcon())
		self.dialog.setWindowTitle(self.dialog.tr('Detalles de cliente'))
		w.bClientAccount.setDefaultAction(w.acShowClientDetails)
		#Not ready for release yet
		w.acShowClientDetails.triggered.connect(self.showDetails)
		w.bClientAccount.setVisible(True)


	@_qc.Slot()
	def showDetails(self):
		"""
			Displays the details for a client
		"""
		d = self.dialog
		w = self.app.window
		model = w.v_clients.model()
		selected = w.v_clients.selectedIndexes()
		if not selected:
			_qg.QMessageBox.critical(self.app.window, "Banta", self.dialog.tr("Primero seleccione el cliente."))
			return

		r = selected[0]
		#TODO use the model to work with the db instead of using it directly????
		cli_code = r.data(_qc.Qt.UserRole)
		cli = _db.DB.clients[cli_code]
		d.balance.setText(str(cli.balance))
		"""r.data()
		d.balance.setText(str())
		d.eName.setText("")
		d.eCode.setText("")
		d.eAddress.setText("")
		#When we have a one-shot buyer, the probabilities says he'll be using his DNI (National ID)
		d.cbCodeType.setCurrentIndex(_db.models.Client.DOC_DNI)
		#And most probably a Final Consumer
		d.cbTaxType.setCurrentIndex(_db.models.Client.TAX_CONSUMIDOR_FINAL)
		#most probably
		d.cbIBType.setCurrentIndex(_db.models.Client.IB_UNREGISTERED)"""
		if d.exec_() != _qg.QDialog.Accepted:
			return
		#gets the data
		"""name = d.eName.text()
		code = d.eCode.text()
		address = d.eAddress.text()
		t_code = d.cbCodeType.currentIndex()
		t_tax = d.cbTaxType.currentIndex()
		t_ib = d.cbIBType.currentIndex()
		#Instantiate a new client with the correct data
		c = _db.models.Client(code, name, address, t_code, t_tax, t_ib)
		#sets the client to the current bill (Performs sone validation and secondary effects)
		self.setClient(c)"""