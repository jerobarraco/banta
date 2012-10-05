# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from banta.packages.experimental import httpinterface, qmlsame

NAME = "experimental"
MODULES = (
	httpinterface.HTTPInterface, qmlsame.QMLSame
)
