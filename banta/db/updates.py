# -*- coding: utf-8 -*-
"""This module allows the update of old databases to new formats
To avoid cyclic references dont import db stuff on base level
"""
from __future__ import absolute_import, unicode_literals, print_function
import logging
logger = logging.getLogger(__name__)
import datetime
import BTrees.OOBTree as _oo
import BTrees.IOBTree as _io
import persistent.list as _pl
#when we can run into cyclic imports (or unloaded parent module problem) is always better to use "from" and only then
from banta.db import models as _mods


def v9(root):
	old_clients = root['clients']
	new_clients = _io.IOBTree()
	for i, c in enumerate(old_clients.values()):
		c.idn = i
		new_clients[i]  = c
	root['clients'] = new_clients

	for prod in root['products'].values():
		#reseting the name will ensure that the names doesnt have non-printable characters
		prod.setName(prod.name)

	for cli in root['clients'].values():
		cli.setName(cli.name)
		cli.setAddress(cli.address)

def v10(root):
	for u in root['users']:
		u.password = ""

#Convert all the objects to the new namespace
def blankInit(root):
	"""Initializes the database from zero.
	"""
	#initializes the database

	typePays = 'typePays'
	root[typePays] = _pl.PersistentList()
	root[typePays].append(_mods.TypePay("Efectivo"))
	root[typePays].append(_mods.TypePay("Tarjeta de Crédito (con recargo)", 0.1))
	root[typePays].append(_mods.TypePay("Cheque (con recargo)", 0.2))

	root['providers'] = _oo.OOBTree()

	root['products'] = _oo.OOBTree()

	root['clients'] = _io.IOBTree()
	cli_code = '00000000'
	#Type DNI is important
	cli = _mods.Client(cli_code, "Consumidor Final", doc_type=_mods.Client.DOC_DNI)
	cli.idn = 0
	root['clients'][cli.idn] = cli

	root['bills'] = _io.IOBTree()
	#for security we set the expire date 5 days in past, so if something happens to the database the license is invalidated
	#TODO remove this
	root['expire_date'] = datetime.date.today() - datetime.timedelta(days=5)
	root['license'] = _mods.LICENSE_FREE
	root['current_date'] = datetime.date.today()

	#stores the config of the printer
	root['printer'] = _mods.Printer()
	#users
	root['users'] = _pl.PersistentList()
	root['users'].append(_mods.User("User"))
	#Create stock movements
	root['moves'] = _io.IOBTree()
	#and buys
	root['buys'] = _io.IOBTree()
	#Categories
	root['limits'] = _pl.PersistentList()
	root['categories'] = _pl.PersistentList()
	root['categories'].append(_mods.Category("Rubro principal"))
	root['version'] = 10

#List of updates functions
#The key is the _base_ version from which it will be upgrading
#it uses a dictionary because in the future, old updates will be deleted
UPDATES = {
	8: v9,
	9: v10,
}

def init(zodb):
	"""Initializes the db, and leave it in its most updated form"""
	update(zodb, 'version', blankInit, UPDATES)

def update(zodb, version_key, init_callback, update_callbacks):
	keys = update_callbacks.keys()
	keys.sort()
	latest = keys[-1] +1
	version = zodb.root.get(version_key)
	if version is None:
		init_callback(zodb.root)
		msg = "Database initialized on '%s'."% (version_key, )
		zodb.commit("system", msg)
		logger.info(msg)
	else:
		logger.info('Checking database version.... Aplying updates if necesary. Might take a while')
		#TODO make a backup if a update is needed
		#check the version
		#make a list of possible versions
		#Range will return a list from V (*) to latest_version, if V>=LATEST_VERSION , range will return an empty tuple
		#*: v is included, that's why the update key in UPDATES relates a prior version to the update function for that version
		#That means that the _key_ in UPDATES is the version FROM WHICH update.
		#Versions should be consecutives.

		for v_from in range(version, latest):
			update_callbacks[v_from](zodb.root)
			zodb.root[version_key] = v_from+1
			#this is nande's way to call a function for each index, kinda crappy i know, but it works pretty fast.
			#without long chained "if"s
			msg = "Database upgraded to version '%s':%s "% (version_key, v_from+1)
			zodb.commit("system", msg)
			logger.info(msg)
	zodb.commit()