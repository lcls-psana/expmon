#------------------------------
"""GUI for configuration of detector object.
Created: 2017-05-15
Author : Mikhail Dubrovin
"""
#------------------------------
from expmon.EMQDetI import *
from expmon.PSDataSupplier import PSDataSupplier
from pyimgalgos.GlobalUtils import print_ndarr
import graphqt.QWUtils as qwu

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from graphqt.GUViewGraph import GUViewGraph
#import pyimgalgos.NDArrGenerators as ag

#------------------------------

class EMQDetWF(EMQDetI) :
    """Interface for EMQDetWF objects.
    """
    def __init__ (self, parent, src=None) :
        EMQDetI.__init__(self, parent, src)
        self._name = self.__class__.__name__

        self.wgrp = None        
        self.wf = None        
        self.wt = None        

        #self.parent = parent
        tabind = parent.tabind
        detind = parent.detind

        det_list_of_pars = cp.det1_list_of_pars if detind == 1 else\
                           cp.det2_list_of_pars

        self.par_winx  = det_list_of_pars[0][tabind]
        self.par_winy  = det_list_of_pars[1][tabind]
        self.par_winh  = det_list_of_pars[2][tabind]
        self.par_winw  = det_list_of_pars[3][tabind]

        self.par_indwf = det_list_of_pars[4][tabind]
        self.par_xmin  = det_list_of_pars[5][tabind]
        self.par_xmax  = det_list_of_pars[6][tabind]

        #self.w = QtGui.QTextEdit(self._name)
        #self.lab_info = QtGui.QLabel('Use EMQDetWF for "%s"' % src)

        self.lab_indwf = QtGui.QLabel('WF#')
        self.lab_indwf.setStyleSheet(style.styleLabel)

        self.lab_info.setText('Use EMQDetWF for "%s"' % src)
        self.set_info()

        self.but_set = QtGui.QPushButton('Set ROI')
        indwf = self.par_indwf.value()
        self.but_indwf = QtGui.QPushButton('%d' % (indwf if indwf is not None else -1))
        self.but_indwf.setFixedWidth(30)
        #self.box.addStretch(1)
        self.box.insertWidget(0, self.lab_indwf)
        self.box.insertWidget(1, self.but_indwf)
        self.box.addWidget(self.but_set)

        #self.but_src = QtGui.QPushButton(self.par_src.value())
        #self.but_view = QtGui.QPushButton('View')
        #self.lab_info = QtGui.QLineEdit('NOT IMPLEMENTED "%s"' % src)

        #self.box = QtGui.QHBoxLayout(self)
        #self.box.addWidget(self.lab_info)
        #self.box.addStretch(1)
        #self.setLayout(self.box)

        #gu.printStyleInfo(self)
        #cp.guitabs = self

        self.connect(self.but_set,   QtCore.SIGNAL('clicked()'), self.on_but_set)
        self.connect(self.but_indwf, QtCore.SIGNAL('clicked()'), self.on_but_indwf)

        self.set_style()
        self.set_tool_tips()

        self.init_det()


    def init_det(self):
        self.dso = PSDataSupplier(cp, log, dsname=None, detname=self.src)
        print 'init_det for src: %s' % self.src


    def set_tool_tips(self):
        self.but_indwf.setToolTip('Select WF index\n-1 - show all')


    def set_style(self):
        self.lab_info.setMinimumWidth(300)
        self.lab_info.setStyleSheet(style.styleLabel)
        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))

        #self.setGeometry(10, 25, 400, 600)
        #self.setMinimumSize(400,50)
        #self.vsplit.setMinimumHeight(700)        
        #self.setStyleSheet(style.styleBkgd)
        #self.but_src.setMinimumWidth(200)


    #def moveEvent(self, e):
    #    #log.debug('%s.moveEvent' % self._name) 
    #    pass


    def closeEvent(self, e):
        log.debug('closeEvent', self._name)
        if self.wgrp is not None :
            try : self.wgrp.close()
            except : pass
        QtGui.QWidget.closeEvent(self, e)
        #Frame.closeEvent(self, e)

#------------------------------

    def on_but_set(self):
        #print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('on_but_set', self._name)
        if self.wgrp is None :
            log.warning('"View" waveform then use "Set" button', self._name)
            return
        xmin, xmax, ymin, ymax = self.wgrp.axes_limits()
        #print 'xmin=%.6f  xmax=%.6f  ymin=%.1f  ymax=%.1f' % (xmin, xmax, ymin, ymax)
        self.par_xmin.setValue(xmin)
        self.par_xmax.setValue(xmax)
        self.set_info()


    def set_info(self):
        xmin = self.par_xmin.value()
        xmax = self.par_xmax.value()
        if None in (xmin, xmax) : return
        msg = '[%.3g, %.3g]' % (xmin, xmax)
        self.lab_info.setText('ROI time: %s' % msg)

#------------------------------

    def on_but_indwf(self):
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('on_but_indwf', self._name)
        ngrp = self.wf.shape[0] if self.wf is not None else 4
        lst_inds = ['-1'] + ['%d'%i for i in range(ngrp)]
        sel = qwu.selectFromListInPopupMenu(lst_inds)
        if sel is None : return
        self.par_indwf.setValue(None if sel is 'None' else int(sel))
        self.but_indwf.setText(sel)
        log.info('Set wave index: %s' % sel, __name__)

#------------------------------
# Abstract methods IMPLEMENTATION:
#------------------------------

    def get_wf_next_event(self):

        det = self.dso.detector()
        if det is None : 
            self.wf, self.wt = None, None
            return None, None, None, None, None, None
        self.wf, self.wt = wf, wt = self.dso.detector().raw(self.dso.event_next()) # cp.event_number.value()
        #print_ndarr(wf, name='wf', first=0, last=10)
        #print_ndarr(wt, name='wt', first=0, last=10)

        tmin, tmax = wt.min(), wt.max()
        fmean, fstd = wf.mean(), wf.std()
        fmin, fmax = fmean-10*fstd, fmean+10*fstd

        return wf, wt, tmin, tmax, fmin, fmax

#------------------------------

    def plot_wf_update(self, wf, wt):

        self.wgrp.remove_all_graphs()

        indwf = self.par_indwf.value()
        
        if wf is None : return

        ngrp = wf.shape[0]
        colors = (Qt.blue, Qt.green, Qt.yellow, Qt.red, Qt.black)
        for gr in range(ngrp) :
            if gr == indwf or indwf<0 :
                color = colors[gr%5]
                self.wgrp.add_graph(wt[gr], wf[gr], QtGui.QPen(color), brush=QtGui.QBrush())

#------------------------------

    #def on_but_view(self): self.message_def(sys._getframe().f_code.co_name)
    def on_but_view(self):
        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)

        if self.wgrp is None :
            wf, wt, tmin, tmax, fmin, fmax = self.get_wf_next_event()

            rectax=QtCore.QRectF(tmin, fmin, tmax-tmin, fmax-fmin) if wf is not None else\
                   QtCore.QRectF(0,0,1,1)

            self.wgrp = GUViewGraph(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                    margl=0.12, margr=0.01, margt=0.01, margb=0.06)

            self.wgrp.connect_view_is_closed_to(self.on_child_close)

            self.plot_wf_update(wf, wt)

            self.wgrp.move(self.pos() + QtCore.QPoint(self.width()+80, 0))
            self.set_window_geometry()
            self.wgrp.show()

        else :
            wf, wt, tmin, tmax, fmin, fmax = self.get_wf_next_event()
            self.plot_wf_update(wf, wt)
            self.wgrp.raise_()
            #self.wgrp.close()
            #self.wgrp = None

    #def get_signal(self):  self.message_def(sys._getframe().f_code.co_name)

#------------------------------

    def set_window_geometry(self) :
        win=self.wgrp
        if self.par_winx.value() is None : return
        win.setGeometry(self.par_winx.value(),\
                        self.par_winy.value(),\
                        self.par_winw.value(),\
                        self.par_winh.value())

#------------------------------

    def save_window_geometry(self) : 
        win=self.wgrp
        point, size = win.mapToGlobal(QtCore.QPoint(0,0)), win.size() # Offset (-5,-22) for frame size.
        x,y,w,h = point.x(), point.y(), size.width(), size.height()
        msg = 'Save window x,y,w,h : %d, %d, %d, %d' % (x,y,w,h)
        log.info(msg, self._name)
        self.par_winx.setValue(x)
        self.par_winy.setValue(y)
        self.par_winw.setValue(w)
        self.par_winh.setValue(h)

#------------------------------

    def on_child_close(self): 
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        self.save_window_geometry()
        self.wgrp.disconnect_view_is_closed_from(self.on_child_close)
        self.wgrp = None

#------------------------------

if __name__ == "__main__" :
    app = QtGui.QApplication(sys.argv)
    w = EMQDetWF(None, 'SxrEndstation.0:Acqiris.1')
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.on_but_view()
    w.get_signal()
    w.show()
    app.exec_()

#------------------------------
