# -*- mode: python -*-
a = Analysis(
		['C:\\Svn\\moongate\\bantapkg\\banta_run.py'],
        pathex=['C:\\Svn\\moongate\\bantapkg',
		'C:\\Python27\\lib\\site-packages\\zope.interface-4.0.1-py2.7-win32.egg',
		'C:\\Python27\\lib\\site-packages\\zope.event-4.0.0-py2.7.egg'
		],
        hiddenimports=[
			'PySide.QtXml', 'PySide.QtNetwork', 'PySide.QtGui',
			'zope.event', 'zope.interface', 'ZEO'
		],
        hookspath='C:\\Svn\\moongate\\bantapkg\\hooks'
	)
pyz = PYZ(a.pure)
exe = EXE(
		pyz,
        a.scripts + [('O', '', 'OPTION')],
        exclude_binaries=1,
        name=os.path.join('build\\pyi.win32\\banta', 'banta.exe'), 
        debug=True,
        strip=None,
        upx=False,
        console=True,
		icon='banta\\ico.ico'
	)
dats = [
	('changelog.txt', 'banta\\changelog.txt', 'DATA'),
	('gpl-3.0.txt', 'banta\\gpl-3.0.txt', 'DATA'),
	('user.qss', 'banta\\user.qss', 'DATA'),
	]
coll = COLLECT(
		exe,
		a.binaries,
		a.zipfiles,
		a.datas+dats,
		#a.datas,
		strip=None,
		upx=False,
		name=os.path.join('dist', 'banta')
   )