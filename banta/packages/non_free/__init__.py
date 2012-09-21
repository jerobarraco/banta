# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from banta.packages.non_free import bill_list, printer, buys, categories, reports, users, limits
#todo rename to "optional"
NAME = "nonfree"
MODULES = (
	bill_list.BillList, printer.Printer, buys.Buys, categories.Categories, reports.Reports,
	users.Users, limits.Limits
)
