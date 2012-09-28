# -*- mode: python -*-
a = Analysis(
	['C:\\Svn\\moongate\\bantapkg\\banta_fix.py'],
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
	a.scripts,
	exclude_binaries=1,
	name=os.path.join('build\\pyi.win32\\fixit', 'fixit.exe'),
	debug=False,
	strip=None,
	upx=False,
	console=True
	)
coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=None,
	upx=False,
	name=os.path.join('dist', 'fixit')
)
