# -*- mode: python -*-
a = Analysis(
		['C:\\Svn\\moongate\\bantapkg\\banta_run.py'],
        pathex=['C:\\Svn\\moongate\\bantapkg'],
        hiddenimports=[
			'zc', 'PySide.QtXml', 'PySide.QtNetwork', 'PySide.QtGui',
			'encodings', 'zc.lockfile', 'zope', 'zope.event'
		],
        hookspath=None
	)
pyz = PYZ(a.pure)
exe = EXE(
		pyz,
        a.scripts + [('O', '', 'OPTION')],
        exclude_binaries=1,
        name=os.path.join('build\\pyi.win32\\banta', 'banta.exe'), 
        debug=False,
        strip=None,
        upx=False,
        console=False,
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