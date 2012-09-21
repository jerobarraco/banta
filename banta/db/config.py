# -*- coding: utf-8 -*-
"""Module for configuration on a .ini file.
#This is important for stuff that could break the app"""
from __future__ import absolute_import, print_function, unicode_literals
import ConfigParser, os

class Config:
	def __init__(self, cfg = 'banta.cfg'):
		self.filename = os.path.join(os.path.abspath('.'), cfg)
		self.defaults = {
			'profiling':str(False),
			'persistent_printer':str(False),
			'debug':str(False),
			'server':'',
		}

		self.config = ConfigParser.SafeConfigParser(self.defaults)
		self.config.readfp(open(self.filename, 'a+'))
		self.load()

	def load(self):
		sect = 'DEFAULT'
		self.PROFILING = self.config.getboolean(sect, 'profiling')
		self.DEBUG = self.config.getboolean(sect, 'debug')
		self.PERSISTENT_PRINTER = self.config.getboolean(sect, 'persistent_printer')
		self.SERVER = self.config.get(sect, 'server')

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
		self.set('profiling', self.PROFILING)
		self.set('debug', self.DEBUG)
		self.set('persistent_printer', self.PERSISTENT_PRINTER)
		self.set('server', self.SERVER)
		if self.config:
			self.config.write(open(self.filename, 'w'))
