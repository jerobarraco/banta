# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)
import csv
import datetime
import PySide.QtCore as _qc
import PySide.QtGui as _qg

import banta.packages as _packs
import banta.utils as _utils
import banta.db as _db

class ResultProduct:
	#These objects are necesary so we can acumulate values in an ordered way
	code = ""
	name = ""
	#like acumulating here
	count = 0
	#and here
	total_sold = 0.0
	def toDict(self):
		return dict(
			zip(
				('code', 'name', 'count', 'total'),
				self.toStringList()
			)
		)
	def toStringList(self):
		return (self.code, self.name, str(self.count), str(self.total_sold))

class ResultCategory:
	prod_count = 0
	total_sold = 0.0
	total_tax = 0.0
	name = ""
	def toStringList(self):
		return (self.name, str(self.prod_count), str(self.total_sold), str(self.total_tax))

class ResultUser:
	#Inner classes sucks but is better than other approach. also this wont (and must not) be used any place else
	name = ""
	count = 0
	prod_count = 0
	total_sold = 0.0
	def toStringList(self):
		return (self.name, str(self.count), str(self.prod_count), str(self.total_sold))

def reportUser(times, root):
	results = {'_headers':  ('Usuario', 'Facturas', 'Productos', 'Total Vendido')}
	tmin, tmax = times
	bills = root['bills']
	try:
		for b in bills.values(min = tmin, max = tmax):
			user = b.user
			if not user:
				uname = "No especificado"
			else:
				uname = user.name
			if uname not in results:
				res = ResultUser()
				res.name = uname
				results[uname] = res

			r = results[uname]
			r.count += 1
			r.prod_count += sum([i.quantity for i in b.items])
			r.total_sold += b.total

	except Exception, e:
		logger.exception('Error when generating the report\n'+str(e))
	return results

def reportCategory(times, root):
	results = {'_headers': ('Rubro', 'Productos', 'Total Vendido', 'Impuesto')}
	tmin, tmax = times
	bills = root['bills']
	try:
		for b in bills.values(min = tmin, max = tmax):
			for i in b.items:
				cat = i.product.category
				if not cat:
					cname = "Sin rubro"
				else:
					cname = cat.name
				if cname not in results:
					res = ResultCategory()
					res.name = cname
					results[cname] = res

				r = results[cname]
				r.prod_count += i.quantity
				r.total_sold += i.price
				r.total_tax += i.tax_total
	except Exception, e:
		logger.exception('Error when generating the report\n'+str(e))
	return results

def reportProduct(times=list((0, 0)), root=None):
	"""Calculates a report of products and returns a list of results
	times is a tuple with the min and max time (as int objects) (utils.dateTimeToInt)
	root is the root of the database, this is needed so this report can be generated from several threads
	"""
	tmin, tmax = times
	#Define the collection
	#define the header
	results = {'_headers': ('Código', 'Nombre', 'Cantidad', 'Total Vendido') }
	#cache the bills list
	bills = root['bills']
	try:
		for b in bills.values(min = tmin, max = tmax):
			for i in b.items:
				prod = i.product
				if not prod:
					#shouldnt happen
					continue
				pcode = prod.code
				if pcode not in results:
					#if the code is not already in the results we create a new result for the product
					res = ResultProduct()
					res.name = prod.name#i use prod here, carefull, either way a null product is nonsense
					res.code = pcode#for the toStringList
					results[pcode] = res

				r = results[pcode]
				r.count += i.quantity
				r.total_sold += i.price
	except Exception, e:
		logger.exception('Error when generating the report\n'+str(e))
	return results

class Reports(_packs.GenericModule):
	REQUIRES = (_packs.GenericModule.P_ADMIN, )
	NAME = "reports"
	REPORT_NAMES = (
		_qc.QT_TRANSLATE_NOOP('reports', 'Por Rubro'),
		_qc.QT_TRANSLATE_NOOP('reports', 'Por Producto'),
		_qc.QT_TRANSLATE_NOOP('reports', 'Por Usuario'),
		_qc.QT_TRANSLATE_NOOP('reports', 'Por Cliente'),
		_qc.QT_TRANSLATE_NOOP('reports', 'Movimientos'),
		_qc.QT_TRANSLATE_NOOP('reports', 'Compras'),
	)

	def load(self):
		#define here, so we use "self." notation, which means a bounded method, also avoid problems
		self.REPORT_FUNCS = (
			reportCategory,
			reportProduct,
			reportUser,
			self._showClients,
			self._showMovements,
			self._showBuys,
		)
		self.widget = self.app.uiLoader.load(":/data/ui/reports.ui")
		self.widget.tr = _utils.unitr(self.widget.trUtf8)
		self.app.window.tabWidget.addTab(self.widget, self.widget.tr("Reportes"))

		month_start, today, month_end = _utils.currentMonthDates()
		self.widget.dMin.setDate(month_start)
		self.widget.dMax.setDate(month_end)
		self.widget.cb_type.addItems(self.REPORT_NAMES)
		self.widget.bShow.clicked.connect(self.show)
		self.widget.bExport.clicked.connect(self.export)

	@_qc.Slot()
	def show(self):
		rep_type = self.widget.cb_type.currentIndex()
		if rep_type < 0 : return
		self.widget.v_list.clear()
		times = self.getTimesFromFilters()
		#we pass the times and the root of the db to allow to call the reports from another thread
		#todo , we can use a worker thread
		results = self.REPORT_FUNCS[rep_type](times, _db.DB.root)
		self._showResults(results)

	def getTimesFromFilters(self):
		"""Returns a touple of times from the date widgets.
			 The data format is the same as the key in move_list
 		"""
		return _utils.getTimesFromFilters(self.widget.dMin, self.widget.dMax)

	@_qc.Slot()
	def export(self):
		report_name = self.REPORT_NAMES[self.widget.cb_type.currentIndex()]
		name =  "banta_report_"+ report_name+ '-'+  str( datetime.datetime.now()).replace(":", "_") + ".csv"
		fname = _qg.QFileDialog.getSaveFileName(self.app.window,
			self.widget.tr('Guardar Reporte'), name,
			self.widget.tr("Archivos CSV (*.csv);;Todos los archivos (*.*)"),
		)
		#gets the name from the return value
		fname = fname[0]
		if not fname:
			return False
		writer = csv.writer(open(name, 'wb'),
			delimiter=b';', quotechar=b'"',  quoting=csv.QUOTE_MINIMAL)
		#Write headers
		row = []
		for c in range (self.widget.v_list.columnCount()):
			hi = self.widget.v_list.horizontalHeaderItem(c)
			row.append(hi.text().encode('utf-8'))
		try:
			writer.writerow(row)
		except:
			pass

		for r in range(self.widget.v_list.rowCount()):
			row = []
			for c in range(self.widget.v_list.columnCount()):
				i = self.widget.v_list.item(r, c)
				row.append(i.text().encode('utf-8'))
			try:
				writer.writerow(row)
			except :
				pass

	def _showResults(self, results):
		"""Shows the result in the view.
		results is a dictionary.
		the key "_headers" is a list of strings for the headers.
		the other keys represents other rows, must be of a type of Result* with a toStringList() method
	 	"""
		v = self.widget.v_list
		#we use pop to remove from the dictionary
		headers = results.pop('_headers')

		#v = self.widget.v_list
		v.setColumnCount(len(headers))
		v.setHorizontalHeaderLabels(headers)

		v.setRowCount( len(results) )

		for r, res in enumerate(results.values()):
			#res = results[k]
			#r = v.rowCount()
			#v.setRowCount(r+1)
			for c, t in enumerate(res.toStringList()):
				self.widget.v_list.setItem(r, c, _qg.QTableWidgetItem(t))

	def _showClients(self, times, root=None):
		class Result:
			#Inner classes sucks but is better than other approach. also this wont (and must not) be used any place else
			code = ""
			ctype = ""
			name = ""
			count = 0
			prod_count = 0
			total_bought = 0.0
			def toStringList(self):
				return (str(self.code), str(self.ctype), self.name, str(self.count), str(self.prod_count), str(self.total_bought))
		#TODO Translate
		headers  = ('Código', 'Tipo', 'Nombre', 'Compras', 'Items', 'Total Comprado')
		v = self.widget.v_list
		v.setColumnCount(len(headers))
		v.setHorizontalHeaderLabels(headers)

		v.setRowCount(0)
		tmin, tmax = self.getTimesFromFilters()
		#Define the collection
		results = {}
		#TODO use a worker thread
		for b in _db.DB.bills.values(min = tmin, max = tmax):
			cli = b.client
			if not cli:
				continue #ASDF WARNING!
			ccode = cli.code
			if ccode not in results:
				res = Result()
				res.code = ccode
				res.name = cli.name
				res.ctype = cli.DOC_NAMES[cli.doc_type]
				results[ccode] = res

			r = results[ccode]
			r.count += 1
			r.prod_count += sum([i.quantity for i in b.items])
			r.total_bought += b.total

		return results

	def _showMovements(self, times, root = None):
		class Result:
			#Inner classes sucks but is better than other approach. also this wont (and must not) be used any place else
			date = ""
			code = ""
			name = ""
			diff = 0
			reason = ""
			def toStringList(self):
				return (_qc.QDateTime(self.date).toString(), self.code, self.name, str(self.diff), self.reason)

		headers  = ('Fecha', 'Código', 'Producto', 'Diferencia', 'Razón')
		v = self.widget.v_list
		v.setColumnCount(len(headers))
		v.setHorizontalHeaderLabels(headers)

		v.setRowCount(0)
		tmin, tmax = self.getTimesFromFilters()
		results ={}
		for m in _db.DB.moves.values(min = tmin, max = tmax):
			r = Result()
			r.date = m.date
			r.code = m.product.code
			r.name = m.product.name
			r.diff =  m.diff
			r.reason = m.reason
			results[r.date] = r
		return results

	def _showBuys(self, times, root=None):
		class Result:
			#Inner classes sucks but is better than other approach. also this wont (and must not) be used any place else
			date = 0
			prod_code = u""
			prod_name = u""
			quantity = 0.0
			total = 0.0
			def toStringList(self):
				return (_qc.QDateTime(self.date).toString(), self.prod_code, self.prod_name, unicode(self.quantity), unicode(self.total))

		headers  = (u'Fecha', u'Código', u'Producto', u'Cantidad', u'Total')
		v = self.widget.v_list
		v.setColumnCount(len(headers))
		v.setHorizontalHeaderLabels(headers)

		v.setRowCount(0)
		tmin, tmax = self.getTimesFromFilters()
		results ={}
		for m in _db.DB.buys.values(min = tmin, max = tmax):
			r = Result()
			r.date = m.date
			r.prod_code = m.product.code
			r.prod_name = m.product.name
			r.quantity =  m.quantity
			r.total = m.total
			results[r.date] = r
		return results
