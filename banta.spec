# -*- mode: python -*-
a = Analysis(
		['C:\\Svn\\moongate\\bantapkg\\banta_run.py'],
        pathex=[
			'C:\\Svn\\moongate\\bantapkg',
			#'C:\\Python27\\lib\\site-packages\\zope.interface-4.0.1-py2.7-win32.egg',
			#'C:\\Python27\\lib\\site-packages\\zope.event-4.0.0-py2.7.egg'
		],
        hiddenimports=[
			'PySide.QtXml', 'PySide.QtNetwork', 'PySide.QtGui',
			'zope.event', 'zope.interface', 'ZEO', 'tornado', 'zope',
			'zc.lockfile',
		],
        #hookspath='C:\\Svn\\moongate\\bantapkg\\hooks'
	)
pyz = PYZ(a.pure)
exe = EXE(
		pyz,
        a.scripts + [('O', '', 'OPTION')],
        exclude_binaries=1,
        name=os.path.join('build\\pyi.win32\\banta', 'banta.exe'), 
        debug=False,
        console=False,
        strip=None,
        upx=False,
		icon='banta\\ico.ico'
	)
dats = [
	('changelog.txt', 'banta\\changelog.txt', 'DATA'),
	('gpl-3.0.txt', 'banta\\gpl-3.0.txt', 'DATA'),
	('user.qss', 'banta\\user.qss', 'DATA'),
	('static/API WebService.odt', 'docs/dev/API WebService.odt', 'DATA'),	
	#particles for samegame
	('Qt/labs/particles/qmldir',  'C:\\Python27\\Lib\\site-packages\\PySide\\imports\\Qt\\labs\\particles\\qmldir', 'DATA'),
	('Qt/labs/particles/qmlparticlesplugin.dll', 'C:\\Python27\\Lib\\site-packages\\PySide\\imports\\Qt\\labs\\particles\\qmlparticlesplugin.dll', 'DATA'),
	('imageformats/qgif4.dll',
		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qgif4.dll', 'DATA'),
 	('imageformats/qico4.dll',
 		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qico4.dll', 'DATA'),
 	('imageformats/qjpeg4.dll',
		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qjpeg4.dll', 'DATA'),
    ('imageformats/qmng4.dll',
		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qmng4.dll', 'DATA'),
    ('imageformats/qsvg4.dll',
		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qsvg4.dll', 'DATA'),
    ('imageformats/qtiff4.dll',
		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qtiff4.dll', 'DATA'),
    ('imageformats/qtga4.dll',
		'C:\\Python27\\Lib\\site-packages\\PySide\\plugins\\imageformats\\qtga4.dll', 'DATA'),
	#Static stuff
		('static/index.html', 'static/index.html', 'DATA'),
		('static/array-grid.js', 'static/array-grid.js', 'DATA'),
		('static/bootstrap.js', 'static/bootstrap.js', 'DATA'),
		('static/example.css', 'static/example.css', 'DATA'),
		('static/ext-all.css', 'static/ext-all.css', 'DATA'),
		('static/ext-all-debug.js', 'static/ext-all-debug.js', 'DATA'),	
		
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