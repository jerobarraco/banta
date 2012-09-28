#! python
from __future__ import absolute_import, print_function, unicode_literals
import sys,os,zipfile
import datetime
import platform
import csv

import banta.db as _db
#import banta.db as _db
from banta.db.models import *
from banta.db.models import LICENSE_POWER, LICENSE_FREE, LICENSE_BASIC,LICENSE_ADVANCED

LICENSES = (LICENSE_FREE, LICENSE_BASIC, LICENSE_POWER, LICENSE_ADVANCED)
CLEARSTRING = "cls" if platform.system() == "Windows" else "clear"
DBPATH = "d"  #uses this name if  no path is assigned to find Data.sf file

def Pack():
	"""print "How much days"
	num = int(raw_input(">> "))"""
	_db.DB.db.pack(days=30)

def clear():
	os.system(CLEARSTRING)

def Backup():
	_db.DB.close()
	path =   os.path.dirname( os.path.abspath(DBPATH))
	badchars = [" ", ":"]
	files = ("d", 'd.index', 'd.lock', 'd.temp', 'logfile.log')
	filelist = [ os.path.join(path, f) for f in files ]
	time = datetime.datetime.now()
	
	name = "backup_" + str(time).replace(":", "") +  ".zip"
	
	for chars in badchars:
		name = name.replace(chars, "")
	#TODO dont use With
	with(zipfile.ZipFile(name, 'w')) as zip:
		for file in filelist:
			if( os.path.isfile(file)):
				zip.write( os.path.basename(file) )
	zip.close()
	print ("File Save with sucess: ", os.path.join(path, name))
	#reopens database for reuse
	_db.DB = _db.cnx.MiZODB(DBPATH)

def ChangeLicense():
	print( "Choose License Type")
	print ("1 - License Free")
	print ("2 - License Basic")
	print ("3 - License Power")
	print ("4 - License Advanced")

	l = int(raw_input("Choose License: "))
	_db.DB.root['license'] = LICENSES[l-1]
	_db.DB.commit()

	print ("Your New License type is:", _db.DB.root['license'])
	print ("Press any key to continue..")

def ListToCsv(list):
	data = ""
	last = 0  #to check last element
	for d in list:
		last += 1
		if( last != len(list)): # check if is last element  to do not put ; in the end
			data += str(d) + ";"
		else:
			data += str(d)
		
	return data
#Todo move this to a csv stuff file
#TODO put the import stuff on the client gui
def ImportArticles():
	print ("\nColumns are: Code, Name, Price, Stock, Tipe of iva [0|1|2], Provider Code")
	file = open(raw_input("Filename "), 'rb')

	reader = csv.reader(file, delimiter=';', quotechar='"' )
	total = 0
	for art  in reader:
		code, name, price, stock, tax_type, prov = art

		name = name.decode('utf-8', 'replace')
		if not code:
			print ("\nInvalid code (%s) for (%s)"%(code, name))
			continue

		try:		price = float(price)
		except: price = 0.0

		try: 		stock = float(stock)
		except: stock = 0.0

		try:		tax_type = int(tax_type)
		except: tax_type = 1

		if code in _db.DB.products:
			prod = _db.DB.products[code]
		else:
			prod = Product(code)
			_db.DB.products[code] = prod
			total +=1
		prod.name = name
		prod.price = price
		prod.stock = stock
		prod.tax_type = tax_type
		if prov in _db.DB.providers:
			prod.provider = _db.DB.providers[prov]

	print ("Imported %s records"%(total))
	_db.DB.commit('admin', 'product import')

def ImportClients():
	print ("\nColumns are: Code, Name, Address, Tax Type")
	print ("\tTax types:")
	for t in enumerate(Client.TAX_NAMES):
		print ("\t%s\t%s"%t)
	file = open(raw_input("Filename "), 'rb')
	reader = csv.reader(file, delimiter=';', quotechar='"' )
	total = 0
	for cli in reader:
		code, name, address, tax_type = cli

		if not code:
			print ("\nInvalid code (%s) for (%s)"%(code, name))
			continue

		name = name.decode('utf-8', 'replace')
		address = address.decode('utf-8', 'replace')

		try:		tax_type = int(tax_type)
		except: tax_type = 0

		if code in _db.DB.clients:
			cli = _db.DB.clients[code]
		else:
			cli = Client(code)
			_db.DB.clients[code] = cli
			total +=1
		cli.name= name
		cli.address= address
		cli.tax_type = tax_type

	print ("Imported %s records"%(total))
	_db.DB.commit('admin', 'client import')

def ImportProviders():
	print ("\nColumns are: Code (CUIT), Name, Adress, Phone, Mail")
	file = open(raw_input("Filename "), 'rb')

	reader = csv.reader(file, delimiter=';', quotechar='"' )
	total = 0
	for prov in reader:
		code, name, address, phone, mail = prov

		name = name.decode('utf-8', 'replace')

		if not code:
			print( "\nInvalid code (%s) for (%s)"%(code, name))
			continue

		if code in _db.DB.providers:
			sys.stdout.write('-')
		else:
			new = Provider(code, name, address, phone, mail)
			_db.DB.providers[code] = new
			total +=1
	print ("Imported %s records"%(total))
	_db.DB.commit('admin', 'provider import')

def ImportCsv():
	while True:
		print ("\nUse ';' for separator,  '\"' as string gruper (quotation), '.' as decimal separator and 'utf-8' as encoding")
		print ('1 - Products')
		print ('2 - Clients')
		print ('3 - Providers')
		print ('0 - Back')
		option = int(raw_input(">>> "))
		if option == 1:
			ImportArticles()
		elif option==2:
			ImportClients()
		elif option== 3:
			ImportProviders()
		else:
			break

def RollBack():
	"""Shows a list of possible rollbacks (undo), shows a max of 10,
	 you can rollback directly to any of those. ie, you can rollback to the 3rd transaction, which will undo the changes
	 ALSO in the first 2 transactions (and the 3rd). You cant recover any of that data."""
	if not _db.DB.storage.supportsUndo():
		print ("uops db doesnt support undo")
		return

	print ("Choose transaction to undo. Available trans (showing 50)")
	#if it doesnt work, try _db.DB.storage.undoLog
	#convert to a list so it stays sorted
	trans = list(_db.DB.db.undoLog(0, 50))
	s = "\t%s\t%s %s '%s'"

	#Notice that we "insert" a fake item, for cancelling
	print (s%(0, "Cancel", "", ""))

	for i, t  in enumerate(trans):
		time = datetime.datetime.fromtimestamp(t['time'])
		print (s%(i+1, time, t['user_name'], t['description']))

	#notice the -1, for cancel, is needed so then i will map to the list index
	i = int(raw_input(">>> ")) -1

	if i == -1:
		print ("Canceled")
		return
	try:
		_db.DB.db.undo(trans[i]['id'])
		#performs a commit, as recommended by the documentation
		_db.DB.commit("fixit", "transaction rollback")
		#syncs the db, as recommended by the documentation
		_db.DB.cnx.sync()
		print ("Transaction restored")
	except Exception as e:
		print ("ERROR")
		print (e)
		_db.DB.abort()

def ForceVersion():
	print ("Current database main version is %s" % _db.DB.root['version'])
	print ("Enter new version number or 0 to cancel")

	option = int(raw_input(">>> "))
	if option == 0:
		print ("Cancelled")
		return
	else:
		_db.DB.root['version'] = option
		_db.DB.commit('fixit', 'version forced')
		print ("Done")
		return


funcs =[
	#(name, function object)
	('Exit', None),
	('Backup Database', Backup),
	('Change License Type', ChangeLicense),
	("Pack database", Pack),
	("Import Csv", ImportCsv),
	("RollBack db", RollBack),
	("Force database version", ForceVersion),
	]

def MenuText():
	for i, (fn, f) in enumerate(funcs):
		print ("%s\t-\t%s"%(i, fn))


def run():
	while True:
		MenuText()
		option = int(raw_input(">>> "))
		if option == 0:
			return 0
		elif option >= len(funcs):
			print ("Invalid option")
			continue
		else:
			#call the function
			func = funcs[option]
			#use a variable to make it more obvious
			func[1]()
