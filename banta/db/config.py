# -*- coding: utf-8 -*-
"""Module for configuration on a .ini file.
The class in this module should be instantiated before loading the rest of the app.
Because it holds the criticial configuration for the app, the one that could be used as a safenet.
This is important for stuff that could break the app"""
from __future__ import absolute_import, print_function, unicode_literals
import ConfigParser, os

class Config:
	EXPERIMENTAL = False
	PERSISTENT_PRINTER = True
	DEBUG = False
	PROFILING = False
	SERVER = ''
	DISABLED_MODULES = [ ]
	WEBSERVICE_PORT = 8008

	K_EXPERIMENTAL = 'experimental'
	K_PERSISTENT_PRINTER = 'persistent_printer'
	K_DEBUG = 'debug'
	K_PROFILING = 'profiling'
	K_DISABLED_MODULES = 'disabled_modules'
	K_WEBSERVICE_PORT = 'webservice_port'
	K_SERVER = 'server'


	def __init__(self, cfg = 'banta.cfg'):
		self.filename = os.path.join(os.path.abspath('.'), cfg)
		self.defaults = {
			self.K_DEBUG : str(self.DEBUG),
			self.K_PROFILING : str(self.PROFILING),
			self.K_PERSISTENT_PRINTER : str(self.PERSISTENT_PRINTER),
			self.K_EXPERIMENTAL : str(self.EXPERIMENTAL),
			self.K_DISABLED_MODULES : ','.join(self.DISABLED_MODULES),
			self.K_WEBSERVICE_PORT : str(self.WEBSERVICE_PORT),
			self.K_SERVER : self.SERVER,

		}

		self.config = ConfigParser.SafeConfigParser(self.defaults)
		self.config.readfp(open(self.filename, 'a+'))
		self.load()

	def load(self):
		sect = 'DEFAULT'
		self.PROFILING = self.config.getboolean(sect, self.K_PROFILING)
		self.DEBUG = self.config.getboolean(sect, self.K_DEBUG)
		self.PERSISTENT_PRINTER = self.config.getboolean(sect, self.K_PERSISTENT_PRINTER)
		self.EXPERIMENTAL = self.config.getboolean(sect, self.K_EXPERIMENTAL)
		d_modules = self.config.get(sect, self.K_DISABLED_MODULES)
		self.DISABLED_MODULES = [
			m.strip()
			for m in d_modules.split(',')
		]
		self.WEBSERVICE_PORT = int(self.config.get(sect, self.K_WEBSERVICE_PORT))
		self.SERVER = self.config.get(sect, self.K_SERVER)

	def get(self, section, key):
		return self.config.get(section, key)

	def set(self, key, value, section=None):
		if self.config:
			if section:
				if not self.config.has_section(section):
					self.config.add_section(section)
			else:
				section = 'DEFAULT'
			self.config.set(section, key, str(value))
			return True
		else:
			return False

	def write(self):
		"""This method writes back the configuration.
		Is better to call this method explicitly instead of putting this code in __del__
		This file only holds critical configuration that might crash banta,
		so , if the software crashes is better not to write that configuration..

		"""
		self.set(self.K_PROFILING, self.PROFILING)
		self.set(self.K_DEBUG, self.DEBUG)
		self.set(self.K_EXPERIMENTAL, self.EXPERIMENTAL)
		self.set(self.K_PERSISTENT_PRINTER, self.PERSISTENT_PRINTER)
		self.set(self.K_DISABLED_MODULES, ','.join(self.DISABLED_MODULES))
		self.set(self.K_WEBSERVICE_PORT, str(self.WEBSERVICE_PORT))
		self.set(self.K_SERVER, self.SERVER)

		if self.config:
			self.config.write(open(self.filename, 'w'))
