#------------------------------
"""
@version $Id: QWDataSource.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------

import sys
import os
from expmon.EMQFrame import Frame
from PyQt5 import QtCore, QtGui, QtWidgets

import expmon.PSUtils  as psu
import graphqt.QWUtils as qwu
from graphqt.Styles    import style

#------------------------------

class QWDataSource(Frame) :
    """GUI to input data source, e.g. cspad
    """
    def __init__(self, cp, log, parent=None, show_mode=0) :
        Frame.__init__(self, parent, mlw=1, vis=show_mode&1)
        self._name = self.__class__.__name__

        self.cp  = cp
        self.log = log
        self.show_mode = show_mode

        self.char_expand = cp.char_expand
        self.data_source = cp.data_source
 
        self.lab_src = QtWidgets.QLabel('Src:')
        self.but_src = QtWidgets.QPushButton(self.data_source.value())

        self.set_layout()
        self.set_style()
        self.set_tool_tips()

        self.but_src.clicked.connect(self.on_but_src)


    def set_layout(self):
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.lab_src)
        self.hbox.addWidget(self.but_src)
        self.hbox.addStretch(1)
        self.setLayout(self.hbox)
 

    def set_tool_tips(self):
       self.setToolTip('Select data source (detector)')


    def set_style(self):
        self.lab_src.setStyleSheet(style.styleLabel)
        #self.setMinimumWidth(500)
        #self.setGeometry(10, 25, 400, 600)
        #self.setFixedHeight(100)
        #self.setContentsMargins(QtCore.QMargins(-5,-5,-5,-5))


    def on_but_src(self):
        #t0_sec = time()

        lst_srcs = self.cp.list_of_sources
        srcs = lst_srcs if lst_srcs is not None else psu.list_of_sources()        
        self.cp.list_of_sources = srcs

        #print '\nconsumed time (sec) =', time()-t0_sec
        #for s in srcs : print 'XXX EMQConfDetV1:', s

        sel = qwu.selectFromListInPopupMenu(srcs)
        if sel is None : return

        self.data_source.setValue(sel)
        self.but_src.setText(sel)
        self.log.info('Data source: %s' % sel, __name__)

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

    from expmon.Logger              import log
    from graphqt.IVConfigParameters import cp
    from expmon.PSNameManager       import nm
    from expmon.PSQThreadWorker     import PSQThreadWorker

    nm.set_config_pars(cp)

    app = QtWidgets.QApplication(sys.argv)

    t1 = PSQThreadWorker(cp, parent=None, dt_msec=5000, pbits=0) #0177777)
    t1.start()

    w = QWDataSource(cp, log, show_mode=1)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.show()
    
    t1.quit()
    app.exec_()

#------------------------------
