#! python
from __future__ import absolute_import, print_function, unicode_literals
import sys,os,zipfile
import datetime
import platform
import csv
import banta.db
from banta.db.models import *
from banta.db.models import LICENSE_POWER, LICENSE_FREE, LICENSE_BASIC,LICENSE_ADVANCED

LICENSES = (LICENSE_FREE, LICENSE_BASIC, LICENSE_POWER, LICENSE_ADVANCED)
CLEARSTRING = "cls" if platform.system() == "Windows" else "clear"
DBPATH = "d"  #uses this name if  no path is assigned to find Data.sf file

def Pack():
	"""print "How much days"
	num = int(raw_input(">> "))"""
	db.zodb.db.pack(days=30)

def clear():
	os.system(CLEARSTRING)

def Backup():
	db.zodb.close()
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
	print "File Save with sucess: ", os.path.join(path, name)
	#reopens database for reuse
	db.zodb = db.cnx.MiZODB(DBPATH)

def ChangeExpirationDate():
	print "Actual Expiration Time is in ", db.zodb.root['expire_date']
	num = int(raw_input("Add how much days FROM TODAY (ex.  30 =  Today + 30 days) >> "))
	#data is a date
	data = datetime.date.today() + datetime.timedelta(days=num)

	db.zodb.root['expire_date'] = data
	if db.zodb.root['license'] == LICENSE_FREE:
		db.zodb.root['license'] = LICENSE_BASIC
	db.zodb.commit()
	print ("New Expiration Time is {0}".format(db.zodb.root['expire_date']))
	print ("New license type is {0}".format(db.zodb.root['license']))
	remaining = db.zodb.root['expire_date'] - datetime.date.today()
	#remaining is a timedelta
	print "Remaining days until expiration: {0} day(s) ".format(remaining.days)

def ChangeLicense():
	print "Choose License Type"
	print "1 - License Free"
	print "2 - License Basic"
	print "3 - License Power"
	print "4 - License Advanced"

	l = int(raw_input("Choose License: "))
	db.zodb.root['license'] = LICENSES[l-1]
	db.zodb.commit()

	print "Your New License type is:", db.zodb.root['license']
	print "Press any key to continue.."

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
	print "\nColumns are: Code, Name, Price, Stock, Tipe of iva [0|1|2], Provider Code"
	file = open(raw_input("Filename "), 'rb')

	reader = csv.reader(file, delimiter=';', quotechar='"' )
	total = 0
	for art  in reader:
		code, name, price, stock, tax_type, prov = art

		name = name.decode('utf-8', 'replace')
		if not code:
			print "\nInvalid code (%s) for (%s)"%(code, name)
			continue

		try:		price = float(price)
		except: price = 0.0

		try: 		stock = float(stock)
		except: stock = 0.0

		try:		tax_type = int(tax_type)
		except: tax_type = 1

		if code in db.zodb.products:
			prod = db.zodb.products[code]
		else:
			prod = Product(code)
			db.zodb.products[code] = prod
			total +=1
		prod.name = name
		prod.price = price
		prod.stock = stock
		prod.tax_type = tax_type
		if prov in db.zodb.providers:
			prod.provider = db.zodb.providers[prov]

	print "Imported %s records"%(total)
	db.zodb.commit('admin', 'product import')

def ImportClients():
	print "\nColumns are: Code, Name, Address, Tax Type"
	print "\tTax types:"
	for t in enumerate(Client.TAX_NAMES):
		print "\t%s\t%s"%t
	file = open(raw_input("Filename "), 'rb')
	reader = csv.reader(file, delimiter=';', quotechar='"' )
	total = 0
	for cli in reader:
		code, name, address, tax_type = cli

		if not code:
			print "\nInvalid code (%s) for (%s)"%(code, name)
			continue

		name = name.decode('utf-8', 'replace')
		address = address.decode('utf-8', 'replace')

		try:		tax_type = int(tax_type)
		except: tax_type = 0

		if code in db.zodb.clients:
			cli = db.zodb.clients[code]
		else:
			cli = Client(code)
			db.zodb.clients[code] = cli
			total +=1
		cli.name= name
		cli.address= address
		cli.tax_type = tax_type

	print "Imported %s records"%(total)
	db.zodb.commit('admin', 'client import')

def ImportProviders():
	print "\nColumns are: Code (CUIT), Name, Adress, Phone, Mail"
	file = open(raw_input("Filename "), 'rb')

	reader = csv.reader(file, delimiter=';', quotechar='"' )
	total = 0
	for prov in reader:
		code, name, address, phone, mail = prov

		name = name.decode('utf-8', 'replace')

		if not code:
			print "\nInvalid code (%s) for (%s)"%(code, name)
			continue

		if code in db.zodb.providers:
			sys.stdout.write('-')
		else:
			new = Provider(code, name, address, phone, mail)
			db.zodb.providers[code] = new
			total +=1
	print "Imported %s records"%(total)
	db.zodb.commit('admin', 'provider import')

def ImportCsv():
	while True:
		print "\nUse ';' for separator,  '\"' as string gruper (quotation), '.' as decimal separator and 'utf-8' as encoding"
		print '1 - Products'
		print '2 - Clients'
		print '3 - Providers'
		print '0 - Back'
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
	if not db.zodb.storage.supportsUndo():
		print "uops db doesnt support undo"
		return

	print "Choose transaction to undo. Available trans (showing 50)"
	#if it doesnt work, try db.zodb.storage.undoLog
	#convert to a list so it stays sorted
	trans = list(db.zodb.db.undoLog(0, 50))
	s = "\t%s\t%s %s '%s'"

	#Notice that we "insert" a fake item, for cancelling
	print s%(0, "Cancel", "", "")

	for i, t  in enumerate(trans):
		time = datetime.datetime.fromtimestamp(t['time'])
		print s%(i+1, time, t['user_name'], t['description'])

	#notice the -1, for cancel, is needed so then i will map to the list index
	i = int(raw_input(">>> ")) -1

	if i == -1:
		print "Canceled"
		return
	try:
		db.zodb.db.undo(trans[i]['id'])
		#performs a commit, as recommended by the documentation
		db.zodb.commit("fixit", "transaction rollback")
		#syncs the db, as recommended by the documentation
		db.zodb.cnx.sync()
		print "Transaction restored"
	except Exception as e:
		print "ERROR"
		print e
		db.zodb.abort()

def ForceVersion():
	print "Current database main version is %s" % db.zodb.root['version']
	print "Enter new version number or 0 to cancel"

	option = int(raw_input(">>> "))
	if option == 0:
		print "Cancelled"
		return
	else:
		db.zodb.root['version'] = option
		db.zodb.commit('fixit', 'version forced')
		print "Done"
		return

def MenuText():
	print "\n===BANTA TOOL 0.1==="
	print "Choose Option:"
	print "1 - Backup Database"
	print "2 - Change License Type:"
	print "3 - Change Expiration date:"
	print "4 - Packing"
	print "5 - Import Csv"
	print "6 - RollBack db"
	print "7 - Force database version"
	print "0 - Exit"

def run():
	while True:
		MenuText()
		option = int(raw_input(">>> "))
		if(option == 1):
			Backup()
		elif (option == 2):
			ChangeLicense()
		elif (option == 3):
			ChangeExpirationDate()
		elif (option == 4):
			Pack()
		elif (option == 5):
			ImportCsv()
		elif (option == 6):
			RollBack()
		elif option == 7:
			ForceVersion()
		else:
			break

def loadDB():
	print (sys.argv)
	if len(sys.argv)<2:
		return

	DBPATH = sys.argv[1]
	if not os.path.isfile(DBPATH):
		print ("Path to database file is incorrect")
		sys.exit(0)

	db.zodb.close() #prevent others use
	db.zodb = db.cnx.MiZODB(file_name=DBPATH)
