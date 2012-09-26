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

def v1(root):
	import banta.utils
	#Converts the bill keys to timestamps as suggested by kosh @ #zope@irc.rizon.net
	#if you are not sure why i use time.time() as key (forced to int), check python documentation
	#copy bills
	bills = root['bills']
	#replace with a new Iobtree
	new_bills = _io.IOBTree()
	#we can have a problem if 2 or 3 people try to print a bill on the same second
	#we have to be careful with that
	for b in bills.values():
		if isinstance(b, _mods.Bill):
			#this will delete any weird object in bills tree (by discarding it)
			b.time = banta.utils.dateTimeToInt(b.date)
			new_bills[b.time] = b
	root['bills'] = new_bills

	#Add providers
	root['providers'] = _oo.OOBTree()

def v2(root):
	#create users
	#TODO change to IOBtree or something else when we have lots of users...
	root['users'] = _pl.PersistentList()
	default_user = _mods.User("User")
	root['users'].append(default_user)
	#set's up a default user for the
	for b in root['bills'].values():
		#check if the bill has a user attribute that is None
		# (not need to check if the bill instance has a "user" attribute (hasattr(b, 'user'))
		# because we declare attribute as class attributes on purpose)
		if (b.user is None):
			#you have to accept that zodb is damm easy
			b.user = default_user
	#Create stock movements
	root['moves'] = _io.IOBTree()

def v3(root):
	#we need the if because some clients already upgraded to v2
	if 'categories' not in root:
		root['categories'] = _pl.PersistentList()
		root['categories'].append(_mods.Category("Rubro Principal"))

def v4(root):
	#initialize extra parameters (there's no actual need for this.. but.. is not bad)
	for prod in root['products'].values():
		prod.description = u""
		prod.pack_units = 1
		prod.buy_price = 0.0
		prod.external_code = u""
	root['buys'] = _io.IOBTree()

def v5(root):
	root['limits'] = _pl.PersistentList()

def v6(root):
	for u in root['users']:
		u.balance = 0.0

def v7(root):
	clients = root['clients']
	for oldkey in clients.keys()[:]:
		newkey = oldkey.decode('utf-8', 'ignore')
		client = clients[oldkey]
		del clients[oldkey]
		client.code = newkey
		clients[newkey] = client

	products = root['products']
	for oldkey in products.keys()[:]:
		newkey = oldkey.decode('utf-8', 'ignore')
		prod = products[oldkey]
		del products[oldkey]
		prod.code = newkey
		products[newkey] = prod

"""
def v8b(root):
	"This method doesnt work, providers get in an inconsistent state... dunno why"

	#We start with simple data
	root['printer'].__class__ = _mods.Printer
	#iterate all the instances
	for tp in root['typePays']:
		#set the class to the correct one, this is non -destructive
		#obviously, asuming that the instance is of the expected type
		tp.__class__ = _mods.TypePay
	root['typePays']._p_changed = True

	for user in root['users']:
		user.__class__ = _mods.User
	root['users']._p_changed = True

	for lim in root['limits']:
		lim.__class__ = _mods.Limit
		#A limit holds a link to a product
		#That product MIGHT NOT be on the product list..
		#that's intentional and awesome from zodb part..
		#but we must be mature and handle it like mans
		if lim.product:
			lim.product.__class__ = _mods.Product
			lim._p_changed = True
	#for cli in root['clients'].values():
	#	cli.__class__ = _mods.Client
	#	#also we need to udpate the bucket... to do this we coudl do
	#	root['clients'][cli.code] = cli
	#	#but it uses more memory, cpu and the db gets bigger

	#gets the first bucket in the BTree
	buck = root['clients']._firstbucket
	#while the bucket has something
	while buck:
		#iterates the items in the bucket
		for c in buck.values():
			#sets the correct class
			c.__class__ = _mods.Client
		#marks the bucket as dirty
		buck._p_changed = True
		#gets the net bucket
		buck = buck._next

	for cat in root['categories']:
		cat.__class__ = _mods.Category
	root['categories']._p_changed = True

	buck = root['providers']._firstbucket
	#while the bucket has something
	while buck:
		for prov in buck.values():
			prov.__class__ = _mods.Provider
			prov._p_changed = True
		buck._p_changed = True
		buck = buck._next

	buck = root['moves']._firstbucket
	#while the bucket has something
	while buck:
		for move in buck.values():
			move.__class__ = _mods.Move
			if move.product:
				move.product.__class__ = _mods.Product
				move._p_changed = True
		buck._p_changed = True
		buck = buck._next

	buck = root['buys']._firstbucket
	while buck:
		for buy in buck.values():
			buy.__class__ = _mods.Buy
			if buy.product:
				buy.product.__class__ = _mods.Product
				buy._p_changed = True
		buck._p_changed = True
		buck = buck._next

	buck = root['products']._firstbucket
	while buck:
		for prod in buck.values():
			prod.__class__ = _mods.Product
			if prod.provider:
				prod.provider.__class__ = _mods.Provider
			if prod.category:
				prod.category.__class__ = _mods.Category
			prod._p_changed = True
		buck._p_changed = True
		buck = buck._next

	buck = root['bills']._firstbucket
	while buck:
		for bill in buck.values():
			bill.__class__ = _mods.Bill
			#this is pretty possible to happen with the new Casual Client
			if bill.client:
				bill.client.__class__ = _mods.Client

			if bill.ptype:
				bill.ptype.__class__ = _mods.TypePay

			if bill.user:
				bill.user.__class__ = _mods.User

			for i in bill.items:
				i.__class__ = _mods.Item
				i.product.__class__ = _mods.Product
				i._p_changed = True
			bill._p_changed = True
		buck._p_changed = True
		buck = buck._next

	root._p_changed = True
	#Convert all the objects to the new namespace
"""
def v8(root):
	"""'Move' the objects... the path has changed, so the class-link of the objects is broken
	now they link to a non-existent class because the class code is not stored in the same path
	as before"""
	#We start with simple data
	root['printer'].__class__ = _mods.Printer
	#iterate all the instances
	for tp in root['typePays']:
		#set the class to the correct one, this is non -destructive
		#obviously, asuming that the instance is of the expected type
		tp.__class__ = _mods.TypePay
	root['typePays']._p_changed = True

	for user in root['users']:
		user.__class__ = _mods.User
	root['users']._p_changed = True

	for cat in root['categories']:
		cat.__class__ = _mods.Category
	root['categories']._p_changed = True

	for lim in root['limits']:
		lim.__class__ = _mods.Limit
		#A limit holds a link to a product
		#That product MIGHT NOT be on the product list..
		#that's intentional and awesome from zodb part..
		#but we must be mature and handle it like mans
		if lim.product:
			lim.product.__class__ = _mods.Product
			lim._p_changed = True
	#for cli in root['clients'].values():
	#	cli.__class__ = _mods.Client
	#	#also we need to udpate the bucket... to do this we coudl do
	#	root['clients'][cli.code] = cli
	#	#but it uses more memory, cpu and the db gets bigger

	for c in root['clients'].values():
		#sets the correct class
		c.__class__ = _mods.Client
		root['clients'][c.code] = c

	for prov in root['providers'].values():
		prov.__class__ = _mods.Provider
		root['providers'][prov.code] = prov

	for move in root['moves'].values():
		move.__class__ = _mods.Move
		if move.product:
			move.product.__class__ = _mods.Product
			move._p_changed = True
		root['moves'][move.time]  = move

	for buy in root['buys'].values():
		buy.__class__ = _mods.Buy
		if buy.product:
			buy.product.__class__ = _mods.Product
			buy._p_changed = True
		root['buys'][buy.time] = buy

	for prod in root['products'].values():
		prod.__class__ = _mods.Product
		if prod.provider:
			prod.provider.__class__ = _mods.Provider
		if prod.category:
			prod.category.__class__ = _mods.Category
		prod._p_changed = True
		root['products'][prod.code] = prod

	for bill in root['bills'].values():
		bill.__class__ = _mods.Bill
		#this is pretty possible to happen with the new Casual Client
		if bill.client:
			bill.client.__class__ = _mods.Client

		if bill.ptype:
			bill.ptype.__class__ = _mods.TypePay

		if bill.user:
			bill.user.__class__ = _mods.User

		for i in bill.items:
			i.__class__ = _mods.Item
			if i.product:
				i.product.__class__ = _mods.Product
				i.product = i.product
				if i.product.category :
					i.product.category.__class__ = _mods.Category
					i.product.categry = i.product.category
					if i.product.provider:
						i.product.provider.__class__ = _mods.Provider
						i.product.provider = i.product.provider
						i.product._p_changed = True
			i._p_changed = True
		#important to tell the bill that the persistentlist changed
		bill.items._p_changed = True
		bill._p_changed = True #not really important, but...p
		root['bills'][bill.time] = bill
	root._p_changed = True

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

	root['clients'] = _oo.OOBTree()
	cli_code = '00000000'
	cli = _mods.Client(cli_code, "Consumidor Final", doc_type=_mods.Client.DOC_DNI)
	root['clients'][cli_code] = cli

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
	root['version'] = 8

#List of updates functions
#The key is the _base_ version from which it will be upgrading
#it uses a dictionary because in the future, old updates will be deleted
UPDATES = {
	0: v1,
	1: v2,
	2: v3,
	3: v4,
	4: v5,
	5: v6,
	6: v7,
	7: v8
}

def init(zodb):
	"""Initializes the db, and leave it in its most updated form"""
	update(zodb, 'version', blankInit, UPDATES)

def update(zodb, version_key, init_callback, update_callbacks):
	import sys
	sys.modules['db.models'] = _mods
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
	del sys.modules['db.models']
	zodb.commit()