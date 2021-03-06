# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from banta.packages.base import feeds, tpay, tbill, bills, clients, products, providers
from banta.packages.base import csv_imports, users

NAME = 'base'
MODULES = (
		feeds.Feeds, tpay.TPay, tbill.TBill, bills.Bills, clients.Clients,
		products.Products, providers.Providers, csv_imports.CSVImports, users.Users
	)
