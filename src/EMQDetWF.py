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

        self.guview = None        
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
        self.par_tmin  = det_list_of_pars[5][tabind]
        self.par_tmax  = det_list_of_pars[6][tabind]
        self.par_bmin  = det_list_of_pars[7][tabind]
        self.par_bmax  = det_list_of_pars[8][tabind]

        self.set_roi_sig()

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
        log.debug('init_det for src: %s' % self.src, self._name)


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
        if self.guview is not None :
            try : self.guview.close()
            except : pass
        QtGui.QWidget.closeEvent(self, e)
        #Frame.closeEvent(self, e)

#------------------------------

    def is_set(self):
        return True


    def roi_limit_bins(self):
        """Uses wt, tmin and tmax to find and return bin indexes bmin, bmax
        """
        #self.wf, self.wt
        tmin, tmax = self.par_tmin.value(),\
                     self.par_tmax.value()
        indwf = self.par_indwf.value()
        indwf = int(indwf) if indwf is not None else 0
        if indwf<0 : indwf=0

        bmin = None
        for b,t in enumerate(self.wt[indwf]) :
            if t<tmin : continue
            bmin = b-1
            break
        if bmin<0 : bmin = 0

        bmax = None
        for b,t in enumerate(self.wt[indwf]) :
            if t<tmax : continue
            bmax = b
            break
        if bmax is None : bmax = self.wt[indwf].size - 1
        
        return bmin, bmax


    def on_but_set(self):
        #print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('on_but_set', self._name)
        if self.guview is None :
            log.warning('"View" waveform then use "Set" button', self._name)
            return
        tmin, tmax, vmin, vmax = self.guview.axes_limits()
        #print 'tmin=%.6f  tmax=%.6f  vmin=%.1f  vmax=%.1f' % (tmin, tmax, vmin, vmax)
        self.par_tmin.setValue(tmin)
        self.par_tmax.setValue(tmax)
        bmin, bmax = self.roi_limit_bins()
        log.info('set WF ROI bins min=%d max=%d' % (bmin, bmax), self._name)
        self.par_bmin.setValue(bmin)
        self.par_bmax.setValue(bmax)
        self.set_roi_sig()
        self.set_info()


    def set_info(self):
        if None in (self.sig_tmin, self.sig_tmax) : return
        if None in (self.sig_bmin, self.sig_bmax) : return
        msg = 'ROI t:[%.3g, %.3g] b:[%d, %d]' % (self.sig_tmin, self.sig_tmax, self.sig_bmin, self.sig_bmax)
        self.lab_info.setText('%s' % msg)

#------------------------------

    def set_roi_sig(self):
        self.sig_tmin = self.par_tmin.value()
        self.sig_tmax = self.par_tmax.value()
        self.sig_bmin = self.par_bmin.value()
        self.sig_bmax = self.par_bmax.value()

        if self.sig_bmin is not None : self.sig_bmin = int(self.sig_bmin)
        if self.sig_bmax is not None : self.sig_bmax = int(self.sig_bmax)

#------------------------------

    def on_but_indwf(self):
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        #log.debug('on_but_indwf', self._name)
        ngrp = self.wf.shape[0] if self.wf is not None else 4
        lst_inds = ['-1'] + ['%d'%i for i in range(ngrp)]
        sel = qwu.selectFromListInPopupMenu(lst_inds)
        if sel is None : return
        self.par_indwf.setValue(None if sel is 'None' else int(sel))
        self.but_indwf.setText(sel)
        log.info('select WF index=%s' % sel, self._name)

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

        self.guview.remove_all_graphs()

        indwf = self.par_indwf.value()
        
        if wf is None : return

        ngrp = wf.shape[0]
        colors = (Qt.blue, Qt.green, Qt.yellow, Qt.red, Qt.black)
        for gr in range(ngrp) :
            if gr == indwf or indwf<0 :
                color = colors[gr%5]
                self.guview.add_graph(wt[gr], wf[gr], QtGui.QPen(color), brush=QtGui.QBrush())

#------------------------------

    #def on_but_view(self): self.message_def(sys._getframe().f_code.co_name)
    def on_but_view(self):
        msg = '%s' % (sys._getframe().f_code.co_name)
        log.debug(msg, self._name)
        if self.guview is None :
            wf, wt, tmin, tmax, fmin, fmax = self.get_wf_next_event()

            rectax=QtCore.QRectF(tmin, fmin, tmax-tmin, fmax-fmin) if wf is not None else\
                   QtCore.QRectF(0,0,1,1)

            self.guview = GUViewGraph(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                    margl=0.12, margr=0.01, margt=0.01, margb=0.06)

            self.guview.connect_view_is_closed_to(self.on_child_close)

            self.plot_wf_update(wf, wt)

            self.guview.move(self.pos() + QtCore.QPoint(self.width()+80, 0))
            self.set_window_geometry()
            self.guview.show()

        else :
            wf, wt, tmin, tmax, fmin, fmax = self.get_wf_next_event()
            self.plot_wf_update(wf, wt)
            self.guview.raise_()
            #self.guview.close()
            #self.guview = None

        tit = '%s  %s' % (cp.tab_names[self.tabind], self.src)
        self.guview.setWindowTitle(tit)


    def signal(self, evt):  

        if self.tabind < 0 :
            msg = 'WARNING: %s%s waveform index in not selected: %d'%\
                   (self._name, sys._getframe().f_code.co_name, self.tabind)
            print msg
            return None

        wf, wt, tmin, tmax, fmin, fmax = self.get_wf_next_event()
        wf1 = wf[self.tabind]
        bmin, bmax = self.sig_bmin, self.sig_bmax
        return wf1.sum() if bmin is None else wf1[bmin:bmax].sum()

#------------------------------

    def set_window_geometry(self) :
        win=self.guview
        if self.par_winx.value() is None : return
        win.setGeometry(self.par_winx.value(),\
                        self.par_winy.value(),\
                        self.par_winw.value(),\
                        self.par_winh.value())

#------------------------------

    def save_window_geometry(self) : 
        win=self.guview
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
        msg = 'In %s' % (sys._getframe().f_code.co_name)
        log.debug('init_det for src: %s' % self.src, self._name)
        self.save_window_geometry()
        self.guview.disconnect_view_is_closed_from(self.on_child_close)
        self.guview = None

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
