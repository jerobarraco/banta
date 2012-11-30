# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from banta.packages.experimental import  qmlsame, zbarcode

NAME = "experimental"
MODULES = (
	qmlsame.QMLSame,
	zbarcode.ZBarCode#unusable, it request to run and block the main thread
)
