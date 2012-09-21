# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
#we import this modules here to avoid cyclic import, which, in conjunctin with the fact that
#zodb has to be a singleton, added to the fact that we can only instantiate zodb AFTER we imported the config
#results in a fatal error while loading.
#we must use full module name (ie, banta.db instead of ".") also we use "from" only in __init__ 
#that way it doesnt mix the namespace

import sys
import logging
#from banta.db import cnx will import it correctly, then using banta.db.cnx wont be confusing for python
from banta.db import cnx, config

if 'CONF' not in globals():
	global CONF
	CONF = config.Config()
	#is important to set this here, because the db could want to log stuff
	level = CONF.DEBUG and logging.DEBUG or logging.INFO
	logging.basicConfig(filename='logfile.log', level=level)

#zodb singleton para la base de datos
#we try to avoid problems like this2
#check if the zodb signleton is defined
#TODO move this to the main module¿¿
if 'DB' not in globals():
	global DB
	#tries to get it from args.. this is needed for fixit,
	#as we are using singletons there aren't an easy way to do this.
	if len(sys.argv) > 1:
		f_name = sys.argv[1]
	else:
		f_name = "d"
	DB = cnx.MiZODB(file_name=f_name, server=CONF.SERVER)
