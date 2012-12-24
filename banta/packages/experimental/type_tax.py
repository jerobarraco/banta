# -*- coding: utf-8 -*-
from  __future__ import  absolute_import, print_function, unicode_literals
import logging

logger = logging.getLogger(__name__)

import PySide.QtCore as _qc
from PySide import QtCore

from banta.packages import GenericModule
import banta.utils

class TypeTax(GenericModule):
	def load(self):
		self.app.uiLoader.load(":/data/ui/ttax.ui", self.app.settings.tabWidget)
		self.dialog.tr = banta.utils.unitr(self.dialog.trUtf8)
		self.app.settings.tabWidget.addTab(self.dialog, self.dialog.tr("Alícuotas"))