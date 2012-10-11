# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

import banta.utils
import banta.db as _db
import banta.packages as _pkg

class ClientDetails(_pkg.GenericModule):
	REQUIRES = (_pkg.GenericModule.P_ADMIN, )
	NAME = 'client_details'
	def __init__(self, app):
		super(ClientDetails, self).__init__(app)
		self.dialog = self.app.uiLoader.load(":/data/ui/client_details.ui")
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("detalles"))
