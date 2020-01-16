#------------------------------
"""GUI for configuration of DetV1
   Created: 2017-02-18
   Author : Mikhail Dubrovin
"""
#------------------------------
import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets

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

        self.p_src = cp.det1_src_list[tabind] if detind == 1 else\
                     cp.det2_src_list[tabind]

        self.tabind = tabind
        self.detind = detind
        src = self.p_src.value()
        #self.w = QtGui.QTextEdit(self._name)
        self.lab_src = QtWidgets.QLabel('Det %d:'%self.detind)
        self.but_src = QtWidgets.QPushButton(src)
        self.but_view = QtWidgets.QPushButton('View')
        self.wdet = get_detector_widget(self, src) # default

        self.box = QtWidgets.QHBoxLayout(self)
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

        self._src_is_set = self.src() != 'None'

        self.but_src.clicked.connect(self.on_but_src)
        self.but_view.clicked.connect(self.on_but_view)


    def par_src(self):
        return self.p_src


    def src(self):
        return self.par_src().value()


    def src_is_set(self):
        return self._src_is_set


    def det_is_set(self):
        if self.wdet is None : return False
        return self.wdet.is_set()


    def on_but_src(self):
        #t0_sec = time()

        srcs = cp.list_of_sources if cp.list_of_sources is not None\
               else psu.list_of_sources()
        
        cp.list_of_sources = srcs

        #print '\nconsumed time (sec) =', time()-t0_sec
        #for s in srcs : print 'XXX EMQConfDetV1:', s
        
        lst_srcs = list(srcs) if srcs is not None else []

        sel = qwu.selectFromListInPopupMenu(['None',] + lst_srcs)
        if sel is None : return
        self.set_src(src=sel)


    def set_src(self, src='None'):
        #if sel != self.instr_name.value() :
        #    self.set_exp()
        #    self.set_run()
        #    self.set_calib()
        
        self.p_src.setValue(src)
        self.but_src.setText(src)
        self._src_is_set = self.src() != 'None'

        #---- update self.wdet
        try :
          self.box.removeWidget(self.wdet)
          self.wdet.close()
          del self.wdet
        except : 
          pass
        self.wdet = get_detector_widget(self, src)
        self.wdet.reset_pars()
        self.wdet.setMinimumWidth(300)
        self.box.insertWidget(3,self.wdet)
        #self.box.addWidget(self.wdet)
        #---- 

        log.info('%s  Det:%s  selected: %s' %\
                 (cp.tab_names[self.tabind], self.detind, src), self._name)


    def on_but_view(self):
        log.info('"View" src: %s'%self.src(), self._name)
        #print '%s.on_but_view' % self._name
        self.wdet.on_but_view()


    def signal(self, evt):
        return self.wdet.signal(evt)


    def set_style(self):
        #self.setGeometry(10, 25, 400, 600)
        self.setMinimumSize(350,50)

        #self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        #self.vsplit.setMinimumHeight(700)        
        #self.setStyleSheet(style.styleBkgd)

        self.lab_src.setStyleSheet(style.styleLabel)
        self.but_src.setMinimumWidth(200)
        self.wdet.setMinimumWidth(350)

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
    app = QtWidgets.QApplication(sys.argv)
    w = EMQConfDetV1(None)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.show()
    app.exec_()

#------------------------------
