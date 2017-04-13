#------------------------------
"""
@version $Id: QWDataSetExtension.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------

import sys
import os
from expmon.EMQFrame import Frame
from PyQt4 import QtGui, QtCore

import expmon.PSUtils  as psu
import graphqt.QWUtils as qwu
from graphqt.Styles    import style

#------------------------------

class QWDataSetExtension(Frame) :
    """GUI to input data set extension, e.g. smd, edx, ffb
    """

    def __init__(self, cp, log, parent=None, show_mode=0) :

        Frame.__init__(self, parent, mlw=1, vis=show_mode&1)
        self._name = self.__class__.__name__

        self.cp  = cp
        self.log = log
        self.show_mode = show_mode

        self.char_expand = cp.char_expand
        self.dsextension = cp.dsextension

        self.lab_ext = QtGui.QLabel('Ext:')
        self.but_ext = QtGui.QPushButton(self.dsextension.value())

        self.set_layout()
        self.set_style()
        self.set_tool_tips()

        self.connect(self.but_ext, QtCore.SIGNAL('clicked()'), self.on_but_ext)


    def set_layout(self):
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.lab_ext)
        self.hbox.addWidget(self.but_ext)
        self.hbox.addStretch(1)
        self.setLayout(self.hbox)
 

    def set_tool_tips(self):
       self.setToolTip('Select data set extension')


    def set_style(self):
        #self.setMinimumWidth(500)
        #self.setGeometry(10, 25, 400, 600)
        #self.setFixedHeight(100)
        #self.setContentsMargins(QtCore.QMargins(-5,-5,-5,-5))

        self.lab_ext.setStyleSheet(style.styleLabel)
        self.but_ext.setFixedWidth(50)
        #self.lab_ext.setVisible(self.show_mode & 2)
        #self.but_ext.setVisible(self.show_mode & 2)


    def on_but_ext(self):
        sel = qwu.selectFromListInPopupMenu(self.cp.list_of_dsext)
        if sel is None : return

        self.dsextension.setValue(sel)
        self.but_ext.setText(sel)
        self.log.info('Data set extension: %s' % sel, __name__)

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

    from expmon.Logger              import log
    from graphqt.IVConfigParameters import cp

    app = QtGui.QApplication(sys.argv)
    w = QWDataSetExtension(cp, log, show_mode=0377)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.show()
    app.exec_()

#------------------------------
