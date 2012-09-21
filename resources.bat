@ echo Building resources
@ C:\Python27\Lib\site-packages\PySide\pyside-rcc.exe -o banta/rc.py banta/res/rc.qrc
@ echo Done
@rem -compress 9 as argument on pyside-rcc would compress the rc.py file, we shouldnt do this, because all it will do is increase the load time. and we dont want that. the rc file will never be 200MB.. any pendrive has 2Gb now so.. is better a faster soft for now