#------------------------------
"""Interface class for configuration of monitor object
Created: 2017-05-19
Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQConfMonI import *

    w = EMQConfMonI(parent=None, tabind=2)
    w1 = w.det1()
    w2 = w.det2()
    status = w.is_active()
    lst_wdets = w.detectors()
"""
from __future__ import print_function
#------------------------------
import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from expmon.EMConfigParameters import cp
from expmon.Logger             import log
from graphqt.Styles            import style
import expmon.EMUtils          as emu
#from graphqt.QIcons            import icon
#from expmon.EMQConfDetV1       import EMQConfDetV1

#------------------------------

class EMQConfMonI(QtWidgets.QWidget) :
    """Interface class for configuration of monitor object
    """
    def __init__(self, parent=None, tabind=0) :
        QtWidgets.QWidget.__init__(self, parent)
        self._name = self.__class__.__name__

        log.debug('in __init__', self._name)

        self.tabind = tabind
 
        self.wdet1 = None # EMQConfDetV1(parent, tabind, detind=1)
        self.wdet2 = None # EMQConfDetV1(parent, tabind, detind=2)

        #self.lab = QtGui.QLabel('Other type of monitors can be implemented')
        #self.box = QtGui.QVBoxLayout(self)
        #self.box.addWidget(self.lab)
        #self.box.addWidget(self.wdet1)
        #self.box.addWidget(self.wdet2)
        #self.box.addStretch(1)
        #self.setLayout(self.box)

        #self.set_tool_tips()
        self.set_style()


    def set_tool_tips(self):
        self.setToolTip('Monitor Control GUI')


    def set_style(self):
        self.setMinimumSize(300,100)
        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))


    def det1(self):
        return self.wdet1


    def det2(self):
        return self.wdet2


    def detectors(self):
        return (self.wdet1, self.wdet2)


    def reset_monitor(self):
        pass


    def is_active(self):
        return not(None in self.detectors()) and self.wdet1.det_is_set() and self.wdet2.det_is_set()


    def closeEvent(self, e):
        #log.debug('EMQConfMonV1.closeEvent') # % self._name)
        log.debug('closeEvent', self._name)

        if self.wdet1 is not None : self.wdet1.close()
        if self.wdet2 is not None : self.wdet2.close()

        #try : self.wdet1.close()
        #except : pass

        #try : self.wdet2.close()
        #except : pass

        QtWidgets.QWidget.closeEvent(self, e)

#------------------------------

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    w = EMQConfMonI()
    w.setGeometry(10, 25, 400, 600)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    print('det1():%s  det2():%s  w.detectors():%s  is_active()::%s'%\
          (w.det1(), w.det2(), str(w.detectors()), w.is_active()))
    w.show()
    app.exec_()

#------------------------------
