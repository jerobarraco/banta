# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from banta.packages.optional import bill_list, printer, buys, categories, type_tax, reports
from banta.packages.optional import limits, client_details, webservice

NAME = "optional"
MODULES = (
	bill_list.BillList, printer.Printer, buys.Buys, categories.Categories, type_tax.TypeTax,
	reports.Reports, limits.Limits, client_details.ClientDetails, webservice.WebService
)
