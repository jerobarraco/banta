@ echo Building translation

@ echo Updating 
@rem if we update the qt_es everything gets screwed so .. DONT!
@ C:\Python27\Lib\site-packages\PySide\pyside-lupdate -verbose banta/res/trans/gf.pro

@ echo Translating 
@ C:\Python27\Lib\site-packages\PySide\linguist.exe banta/res/trans/es.ts banta/res/trans/en.ts banta/res/trans/pt.ts banta/res/trans/ja.ts banta/res/trans/de.ts 

@ echo Releasing 
@ C:\Python27\Lib\site-packages\PySide\lrelease.exe banta/res/trans/gf.pro
@ C:\Python27\Lib\site-packages\PySide\lrelease.exe banta/res/trans/qt_es.ts

@ echo Done
pause