# -*- coding: utf-8 -*-
__author__="MoonGate"
__date__ ="$27-abr-2012 1:51:31$"
#python setup_banta.py bdist_egg --exclude-source-files
try:
	import distribute_setup
	distribute_setup.use_setuptools()
	from setuptools import setup , find_packages
except ImportError, e:
	print e
	print """
	You don't have distribute installed, run:
  $ curl -O http://python-distribute.org/distribute_setup.py
	$ python distribute_setup.py"""
	exit(1)

distribute_setup.use_setuptools()
from setuptools import setup, find_packages
#import py2exe
#Class for using py.test as testing 
from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
	def finalize_options(self):
		TestCommand.finalize_options(self)
		self.test_args = []
		self.test_suite = True
	def run_tests(self):
		#import here, cause outside the eggs aren’t loaded
		import pytest
		pytest.main(self.test_args)

import banta

setup (
	#console = [ "banta_run.py"],
  name = 'banta',
  version = banta.__version__,
	#packages = find_packages(exclude=['*fixit*']),
	packages = find_packages(),
  #exclude_package_data={'': ['*fixit*']},
  #scripts = ['bin/banta.py'],
  # Declare your packages' dependencies here, for eg:
  #transaction is needed in 1.2 for mac
  install_requires=['transaction==1.2.0', 'ZODB3', 'pyserial', 'feedparser', 'pyside', 'tornado'],
  provides = ['banta'],
  package_data={'':
		['gpl-3.0.txt', 'changelog.txt', 'user.qss']
	},
  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'MoonGate',
  author_email = 'mail@moongate.com.ar',
  keywords = "point-of-sale inventory accounting inventario stock control ventas billing facturacion",
  description = 'Accounting, point of sale, inventory',
  license = "GNU LGPL",
  long_description= 'Banta helps you with: Account, point of sale, List of articles, Manage product, prices, taxes, stock, List of providers, Different pay methods, allowing to adjust your prices where is needed.',
  url = "http://moongate.com.ar",
  #download_url="http://moongate.com.ar",
  platforms = "Platform Independent",
  classifiers = [
		"Operating System :: OS Independent",
		"License :: OSI Approved",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Natural Language :: Spanish",
		"Natural Language :: English",
		#"License :: GNU Library or Lesser General Public License (LGPL)",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Financial and Insurance Industry",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"Topic :: Office/Business",
		"Environment :: Win32 (MS Windows)",
		"Environment :: X11 Applications",
		"Environment :: MacOS X",
 	],
	entry_points = {
		#make it eggsecutable
		'setuptools.installation': [
			'eggsecutable = banta:run',
		],
		'gui_scripts': [
			'banta = banta:run',
		],
		'console_scripts': [
			'banta_fix = banta.fix:run',
		]
	},
	tests_require=['pytest'],
	cmdclass = {'test': PyTest},
)