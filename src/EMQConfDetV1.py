#------------------------------
"""GUI for configuration of DetV1
   Created: 2017-02-18
   Author : Mikhail Dubrovin
"""
#------------------------------
import sys
import os

from PyQt4 import QtGui, QtCore

from expmon.EMConfigParameters import cp
from expmon.Logger             import log
import expmon.PSUtils          as psu
import graphqt.QWUtils         as qwu
from graphqt.Frame             import Frame
from graphqt.Styles            import style
#from graphqt.QIcons            import icon


#from expmon.EMQDetI       import EMQDetI
from expmon.EMQDetF import get_detector_widget
#    w = get_detector_widget(src)

from time import time

#------------------------------

#class EMQConfDetV1(QtGui.QWidget) :
class EMQConfDetV1(Frame) :
    """Detector configuration GUI
    """
    def __init__ (self, parent, tabind=0, detind=0) :
        Frame.__init__(self, parent, mlw=1, vis=False)
        #QtGui.QWidget.__init__(self, parent)
        self._name = self.__class__.__name__

        self.par_src = cp.det1_src_list[tabind] if detind == 1 else\
                       cp.det2_src_list[tabind]

        self.tabind = tabind
        self.detind = detind
        src = self.par_src.value()
        #self.w = QtGui.QTextEdit(self._name)
        self.lab_src = QtGui.QLabel('Det %d:'%self.detind)
        self.but_src = QtGui.QPushButton(src)
        self.but_view = QtGui.QPushButton('View')
        self.wdet = get_detector_widget(self, src) # default

        self.box = QtGui.QHBoxLayout(self)
        self.box.addWidget(self.lab_src)
        self.box.addWidget(self.but_src)
        self.box.addWidget(self.but_view)
        self.box.addWidget(self.wdet)
        self.box.addStretch(1)
        self.setLayout(self.box)

        self.set_style()
        #self.set_tool_tips()
        #gu.printStyleInfo(self)
        #cp.guitabs = self

        self.connect(self.but_src,  QtCore.SIGNAL('clicked()'), self.on_but_src)
        self.connect(self.but_view, QtCore.SIGNAL('clicked()'), self.on_but_view)


    def on_but_src(self):
        #t0_sec = time()

        srcs = cp.list_of_sources if cp.list_of_sources is not None\
               else psu.list_of_sources()
        
        cp.list_of_sources = srcs

        #print '\nconsumed time (sec) =', time()-t0_sec
        #for s in srcs : print 'XXX EMQConfDetV1:', s
        
        sel = qwu.selectFromListInPopupMenu(srcs)
        if sel is None : return

        #if sel != self.instr_name.value() :
        #    self.set_exp()
        #    self.set_run()
        #    self.set_calib()
        self.par_src.setValue(sel)
        self.but_src.setText(sel)

        #---- update self.wdet
        self.box.removeWidget(self.wdet)
        self.wdet.close()
        del self.wdet
        self.wdet = get_detector_widget(self, sel)
        self.wdet.setMinimumWidth(300)
        self.box.insertWidget(3,self.wdet)
        #self.box.addWidget(self.wdet)
        #---- 

        log.info('Mon: %d  Det: %s  selected: %s' %\
                 (self.tabind, self.detind, sel), __name__)


    def on_but_view(self):
        log.debug('on_but_view', self._name)
        #print '%s.on_but_view' % self._name
        self.wdet.on_but_view()


    def get_signal(self):
        return self.wdet.get_signal()


    def set_style(self):
        #self.setGeometry(10, 25, 400, 600)
        self.setMinimumSize(300,50)

        #self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        #self.vsplit.setMinimumHeight(700)        
        #self.setStyleSheet(style.styleBkgd)

        self.lab_src.setStyleSheet(style.styleLabel)
        self.but_src.setMinimumWidth(200)
        self.wdet.setMinimumWidth(300)

    #def moveEvent(self, e):
        #log.debug('%s.moveEvent' % self._name) 
        #pass


    def closeEvent(self, e):
        log.debug('closeEvent', self._name)

        try : self.wdet.close()
        except : pass

        #QtGui.QWidget.closeEvent(self, e)
        Frame.closeEvent(self, e)

#------------------------------

if __name__ == "__main__" :
    app = QtGui.QApplication(sys.argv)
    w = EMQConfDetV1()
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.show()
    app.exec_()

#------------------------------
