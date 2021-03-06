# -*- coding: utf-8 -*-
"""This module handles the conection to the database"""
from __future__ import absolute_import, unicode_literals, print_function
import contextlib
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
	def __init__(self, file_name= 'd', server=None, port=8090):
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
			try:
				self.storage =  ZEO.ClientStorage.ClientStorage((server, port), blob_dir="./blobs")
			except:
				self.storage =  ZEO.ClientStorage.ClientStorage((server, port))#mac's old transaction can't handle blobs
		else:
			try:
				self.storage = ZODB.FileStorage.FileStorage(file_name, blob_dir="./blobs")# we have to solve the problem on mac
			except:
				self.storage = ZODB.FileStorage.FileStorage(file_name)#, blob_dir="./blobcache")# we have to solve the problem on mac
		self.db = ZODB.DB(self.storage)
		self.cnx = self.db.open()
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
		self.type_tax = self.root.get('typeTax')

	def commit(self, user=None, note=None):
		"""Esta funcion permite realizar un commit 
		recibe como parametros el nombre de usuario y una nota
		las que se guardan con el commit y se informan en el log"""

		trans = transaction.get()
		#print('commit', trans)
		if user:
			trans.setUser(user)
		if note:
			trans.note(note)
		trans.commit()
		
	def abort(self):
		trans = transaction.get()
		#print ("abort!", trans)
		trans.abort()
		
	def close(self):
		self.cnx.close()
		self.db.close()
		self.storage.close()

	@contextlib.contextmanager
	def threaded(self):
		"""
		A context manager for connections outside the main thread
		This is meant to be used on functions that need to use the database from another thread
		ensures that the transaction will always be commited, or aborted in case of an exception.

		use like:

		with banta.db.DB.threaded() as root:
			if 'something' in root['products']:
				raise ....

		if an exception occurs inside the "with", the transaction will get aborted
		else, the transaction gets commited.
		a new connection has its own root object.
		in theory you can use another connection in another thread to allow a better threading usability

		the returning object is a new root object.
		"""
		#this is another way to implement a context manager, but i dont actually like it much...
		#i sense the Object way is kinda faster...
		#The speed difference is very small and it seems like this way is a little faster..
		# no way to test that really
		#but anyway this way leaves the code more organized...
		#also i can access self.* objects directly, like self.db.open and self.commit

		cnx = self.db.open()
		root = cnx.root()
		try:
			yield root
			self.commit()
		except Exception, e:
			self.abort()
			#Sorry but we are not hidding exceptions!
			cnx.close()
			raise e
		cnx.close()
		#This should not be needed. because the cnx will (in theory) close itself.
		#And also because ZODB is smart enough to pool/cache the connections per thread! (Damm i love ZODB!)
		#but we do no harm in doing the "correct" stuff...
		#in case ZODB doesnt cache connections, this COULD be a speeddown, but i rather lower speed than crashing software
