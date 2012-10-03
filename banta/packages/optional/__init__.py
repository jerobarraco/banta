# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from banta.packages.optional import bill_list, printer, buys, categories, reports, users, limits

NAME = "optional"
MODULES = (
	bill_list.BillList, printer.Printer, buys.Buys, categories.Categories, reports.Reports,
	users.Users, limits.Limits
)
