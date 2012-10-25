# -*- coding: utf-8 -*-
"""
Some utility stuff
"""
import datetime
import time
import csv
import codecs
import cStringIO

"""import PySide.QtGui
def utr(u):
	return PySide.QtGui.qApp.tr(u.encode('utf-8'))"""

FORBIDDEN_CHARACTERS = ('\n', '\t', '\r')
def printable(string):
	#not the fastet way but..
	for c in FORBIDDEN_CHARACTERS:
		string.replace(c, ' ')
	return string


def unitr(oldtr):#i dont like to return a function with an enclosed global.. but , is faster than the other option and i dont have to import PySide here
	def utr(u, *args):
		if isinstance(u, unicode):
			u = u.encode('utf-8')
		else:
			print "not unicode:", u
		return oldtr(u, *args)
	return utr

def currentMonthDates():
	"""Returns the dates for the current month as a tuple of datetime
	Return ( Start of month, Today, End of Month)"""
	today = datetime.date.today()
	#calculate the start of the month by simply substracting the days that have passed
	month_start = today - datetime.timedelta(days=(today.day-1))
	month_end = datetime.date(today.year, today.month+1, 1)
	return (month_start, today, month_end)

def dateTimeToInt(d):
	"""Covenverts a datetime object to a integer.
			Used in models.Bill as key and everywhere where is needed some comparison of those keys
	"""
	return int(time.mktime(d.timetuple()))

def getTimesFromFilters(date_min, date_max):
	"""Returns a touple of times from the date widgets.
		The data format is the same as the key in bill_list
		date_min and date_max are two QDateEdit with min and max dates respectively
 	"""
	dmin = date_min.date().toPython()
	#We add 1 day, so it also takes the current day
	#The timestamp for this days will always have time 0. and every bill for that day will obviously have bigger time
	#And time counts
	dmax = date_max.date().toPython() + datetime.timedelta(days=1)
	tmin = dateTimeToInt(dmin)
	tmax = dateTimeToInt(dmax)
	return (tmin, tmax)



class UTF8Recoder:
	"""
Iterator that reads an encoded stream and reencodes the input to UTF-8
"""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)

	def __iter__(self):
		return self

	def next(self):
		return self.reader.next().encode("utf-8")

class UnicodeCSVReader:
	"""
A CSV reader which will iterate over lines in the CSV file "f",
which is encoded in the given encoding.
"""
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)

	def next(self):
		row = self.reader.next()
		return [unicode(s, "utf-8") for s in row]

	def __iter__(self):
		return self

class UnicodeCSVWriter:
	"""
A CSV writer which will write rows to CSV file "f",
which is encoded in the given encoding.
"""
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)


def resourcePath(relative): #TODO with new pyinstaller this should be on the environ
	"""This functions convert a relative virtual path to a system path for a resource built in into an exe by pyinstaller
	"""
	import os
	return os.path.join(
		os.environ.get(
			"_MEIPASS2",
			os.path.abspath(".")
		),
		relative
	)