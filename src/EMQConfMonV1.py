#------------------------------
"""GUI for configuration of MonV1

@version $Id: EMQConfMonV1.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------
import sys
import os

from PyQt4 import QtGui, QtCore

from expmon.EMConfigParameters import cp
from expmon.Logger             import log
from graphqt.Styles            import style
from expmon.EMQConfDetV1       import EMQConfDetV1
import expmon.EMUtils          as emu
#from graphqt.Frame             import Frame
#from graphqt.QIcons            import icon

#------------------------------

#class EMQConfMonV1(Frame) :
class EMQConfMonV1(QtGui.QWidget) :
    """Configuration GUI
    """

    def __init__(self, parent=None, tabind=0) :

        #Frame.__init__(self, parent, mlw=1)
        QtGui.QWidget.__init__(self, parent)
        self._name = self.__class__.__name__

        self.tabind = tabind
 
        self.setGeometry(10, 25, 400, 600)
        self.setWindowTitle(self._name)

        self.wdet1 = EMQConfDetV1(parent, tabind, detind=1)
        self.wdet2 = EMQConfDetV1(parent, tabind, detind=2)
        #self.w     = QtGui.QTextEdit(self._name)

        self.box = QtGui.QVBoxLayout(self)
        self.box.addWidget(self.wdet1)
        self.box.addWidget(self.wdet2)
        self.box.addStretch(1)
        self.setLayout(self.box)

        #self.set_tool_tips()
        self.set_style()
        #gu.printStyleInfo(self)
        #cp.guitabs = self


    def set_style(self):
        self.setMinimumSize(300,100)
        #self.setMaximumSize(600,100)
        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        #self.vsplit.setMinimumHeight(700)        
        #self.setStyleSheet(style.styleBkgd)


    def closeEvent(self, e):
        #log.debug('EMQConfMonV1.closeEvent') # % self._name)
        log.debug('closeEvent', self._name)

        try : self.wdet1.close()
        except : pass

        try : self.wdet2.close()
        except : pass

        QtGui.QWidget.closeEvent(self, e)

#------------------------------

if __name__ == "__main__" :
    app = QtGui.QApplication(sys.argv)
    w = EMQConfMonV1()
    w.move(QtCore.QPoint(50,50))
    w.show()
    app.exec_()

#------------------------------
