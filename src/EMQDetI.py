#------------------------------
"""GUI for configuration of detector object.
   Created: 2017-02-18
   Author : Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------
import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from expmon.EMConfigParameters import cp
from expmon.Logger             import log
import expmon.PSUtils          as psu
import graphqt.QWUtils         as qwu
from graphqt.Styles            import style
#from psana import Detector, Source    
#from graphqt.Frame             import Frame
#from graphqt.QIcons            import icon
#from time import time
#------------------------------

class EMQDetI(QtWidgets.QWidget) :
    """Interface for EMQDet* objects
    """
    def __init__ (self, parent, src=None) :
        #Frame.__init__(self, parent, mlw=1, vis=False)
        QtWidgets.QWidget.__init__(self, parent=None)
        self._name = 'EMQDetI'

        self.parent = parent
        self.tabind = parent.tabind if parent is not None else 0
        self.detind = parent.detind if parent is not None else 0

        self.set_source(src)

        #self.w = QtGui.QTextEdit(self._name)
        self.lab_info = QtWidgets.QLabel('NOT IMPLEMENTED "%s"' % src)
        self.lab_info.setStyleSheet(style.styleRed)
        #self.but_src = QtGui.QPushButton(self.par_src.value())
        #self.but_view = QtGui.QPushButton('View')

        self.box = QtWidgets.QHBoxLayout(self)
        self.box.addWidget(self.lab_info)
        #self.box.addStretch(1)
        self.setLayout(self.box)

        #self.set_style()
        #self.set_tool_tips()
        #gu.printStyleInfo(self)
        #cp.guitabs = self

        #self.connect(self.but_src,  QtCore.SIGNAL('clicked()'), self.on_but_src)
        #self.connect(self.but_view, QtCore.SIGNAL('clicked()'), self.on_but_view)


    def set_source(self, src):
        self.src = str(src)
        #self.source = Source(src)
        #print '%s.set_source: source: %s  %s' % (self._name, self.src, str(self.source))


    def set_style(self):
        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        self.lab_info.setMinimumWidth(300)
        self.lab_info.setStyleSheet(style.styleLabel)

        #self.setGeometry(10, 25, 400, 600)
        #self.setMinimumSize(400,50)
        #self.vsplit.setMinimumHeight(700)        
        #self.setStyleSheet(style.styleBkgd)
        #self.but_src.setMinimumWidth(200)


    #def moveEvent(self, e):
        #log.debug('%s.moveEvent' % self._name) 
        #pass


    def closeEvent(self, e):
        log.debug('closeEvent', self._name)
        #if self.wimg is not None :
        #    try : self.wimg.close()
        #    except : pass

        QtWidgets.QWidget.closeEvent(self, e)
        #Frame.closeEvent(self, e)

#------------------------------

    def message_def(self, met, cmt=''):
        msg = 'Default %s must be re-implemented in derived class. %s' % (met, cmt)
        #self.lab_info.setText(msg)
        #log.info(msg, self._name)
        print(msg)

#------------------------------
# Abstract methods MUST BE RE-IMPLEMENTED:
#------------------------------

    def is_set(self):
        return False

    def reset_pars(self): 
        #self.message_def(sys._getframe().f_code.co_name)
        pass

    def on_but_view(self, evt=None): self.message_def(sys._getframe().f_code.co_name)

    def signal(self, evt=None):  
        self.message_def(sys._getframe().f_code.co_name)
        return None

#------------------------------

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    w = EMQDetI()
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.on_but_view()
    w.get_signal()
    w.show()
    app.exec_()

#------------------------------
