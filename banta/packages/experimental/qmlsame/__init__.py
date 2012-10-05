#!/usr/bin/env python
 
# If QML_FILE_NAME is None, the QML file must
# have the same name as this Python script, just with
# .qml as extension instead of .py. You can override
# this by setting an explicit filename here.
QML_FILE_NAME = "samegame.qml"
WINDOW_TITLE = "Iguales"
 
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import *
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)
    f = QDeclarativeView()
    f.setSource(QML_FILE_NAME)
    f.setWindowTitle(WINDOW_TITLE)
    f.show()
    app.exec_()