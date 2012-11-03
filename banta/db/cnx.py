# -*- coding: utf-8 -*-
"""This module handles the conection to the database"""
from __future__ import absolute_import, unicode_literals, print_function
import ZODB.DB, ZODB.FileStorage

import transaction
doc = """PersistentList are not lazy , so be carefull.
is better to use IOBTree s when possible (or OOBTrees)
Choosing the "key" carefully can be a big optimization
ie using a timestamp as a key for the bills will allow to search by date much more easily as only the keys are loaded, and can be
cropped by date with BTree.values(min=someminddata, max=somemaxdate)
(thansk kosh @ #zodb @irc.freenode.net)
"""
class MiZODB(object):
	def __init__(self, file_name= 'db', server=None, port=8090):
		"""Handles a ZODB connection"""
		#We cant use import banda.db.updates here, because is probably still loading banta.db..
		from banta.db import updates as _up
		#if the server is set, then is a server connection (and ignore the file_name)
		if server:
			#Recibe como parametro, el servidor al cual se conectara
			#por defecto se conectara a localhost en el puerto 8090
			#es importante asignar el blob_dir para poder contar con soporte de blobs
			#de manera correcta
			import ZEO.ClientStorage
			self.storage =  ZEO.ClientStorage.ClientStorage((server, port))#, blob_dir="./blobcache")#mac stuff?
		else:
			self.storage = ZODB.FileStorage.FileStorage(file_name)#, blob_dir="./blobcache")# we have to solve the problem on mac
		self.db = ZODB.DB(self.storage)
		self.cnx = self.db.open()
		print(self.cnx)
		self.root = self.cnx.root()
		#this method keps the database up to date, and initializes it in case of a new database
		_up.init(self)
		self.products = self.root.get('products')
		self.typePays = self.root.get('typePays')
		self.clients = self.root.get('clients')
		self.bills = self.root.get('bills')
		self.printer = self.root.get('printer')
		self.providers = self.root.get('providers')
		self.users = self.root.get('users')
		self.moves = self.root.get('moves')
		self.categories = self.root.get('categories')
		self.buys = self.root.get('buys')
		self.limits = self.root.get('limits')

	def commit(self, user=None, note=None):
		"""Esta funcion permite realizar un commit 
		recibe como parametros el nombre de usuario y una nota
		las que se guardan con el commit y se informan en el log"""

		trans = transaction.get()
		print('comm', trans)
		if user:
			trans.setUser(user)
		if note:
			trans.note(note)
		trans.commit()
		
	def abort(self):
		transaction.get().abort()
		
	def close(self):
		self.cnx.close()
		self.db.close()
		self.storage.close()

	def getConnection(self):
		"""EXPERIMENTAL!
		a new connection has its own root object.
		in theory you can use another connection in another thread to allow a better threading usability
		the returning object is a new connection, the consumer should close it and take care of it.
		Not sure, but probably there shouldnt be two connections on the same thread.
		And also i dont exactly knows how to get the transaction for the current connection
		"""
		return self.db.open()