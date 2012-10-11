#!/usr/bin/env python
 
# If QML_FILE_NAME is None, the QML file must
# have the same name as this Python script, just with
# .qml as extension instead of .py. You can override
# this by setting an explicit filename here.
import PySide.QtCore as _qc
import PySide.QtDeclarative
import banta.packages as _pack
#todo add in the pyinstaller the dll for particle system
class QMLSame(_pack.GenericModule):
	REQUIRES = []
	NAME = "samegame"
	products = _qc.Signal(int)
	def __init__(self, app):
		super(QMLSame, self).__init__(app)

	def load(self):
		#the reader will fetch the news from internet, or fail-to if there's no internet
		self.f = PySide.QtDeclarative.QDeclarativeView()
		self.f.setSource("qrc:same/samegame.qml")
		self.f.setWindowTitle("Iguales")
		self.f.setWindowIcon(self.app.window.windowIcon())
		#none of this works
		#self.key_sequence = _qg.QKeySequence(_qc.Qt.Key_Up,_qc.Qt.Key_Up, _qc.Qt.Key_Up  )
		#self.app.window.acSameGame.setShortcut(self.key_sequence)
		#self.app.window.acSameGame.setShortcutContext(_qc.Qt.ApplicationShortcut)
		self.app.window.acSameGame.triggered.connect(self.show)
		self.f.engine().quit.connect(self.f.close)


	@_qc.Slot()
	def show(self):
		self.f.show()