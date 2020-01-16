#------------------------------
"""GUI for configuration of detector object.
Created: 2017-05-15
Author : Mikhail Dubrovin
"""
from __future__ import print_function
from __future__ import division
#------------------------------
import numpy as np

from expmon.EMQDetI import *
from expmon.PSDataSupplier import PSDataSupplier
from pyimgalgos.GlobalUtils import print_ndarr
import graphqt.QWUtils as qwu
from expmon.EMQUtils import point_relative_window

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from graphqt.GUViewGraph import GUViewGraph
#import pyimgalgos.NDArrGenerators as ag

#------------------------------

class EMQDetWF(EMQDetI) :
    """Interface for EMQDetWF objects.
    """
    def __init__ (self, parent, src=None) :
        EMQDetI.__init__(self, parent, src)
        self._name = 'EMQDetWF'

        self.guview = None        
        self.wf = None        
        self.wt = None        

        #self.parent = parent
        tabind = parent.tabind if parent is not None else 0
        detind = parent.detind if parent is not None else 0

        det_list_of_pars = cp.det1_list_of_pars if detind == 1 else\
                           cp.det2_list_of_pars

        self.par_winx  = det_list_of_pars[0][tabind]
        self.par_winy  = det_list_of_pars[1][tabind]
        self.par_winh  = det_list_of_pars[2][tabind]
        self.par_winw  = det_list_of_pars[3][tabind]

        self.par_indwf    = det_list_of_pars[4][tabind]
        self.par_sig_tmin = det_list_of_pars[5][tabind]
        self.par_sig_tmax = det_list_of_pars[6][tabind]
        self.par_sig_bmin = det_list_of_pars[7][tabind]
        self.par_sig_bmax = det_list_of_pars[8][tabind]

        self.par_bkg_tmin = det_list_of_pars[9][tabind]
        self.par_bkg_tmax = det_list_of_pars[10][tabind]
        self.par_bkg_bmin = det_list_of_pars[11][tabind]
        self.par_bkg_bmax = det_list_of_pars[12][tabind]

        self.item_roi_sig = None
        self.item_roi_bkg = None
        self.set_pen_brush()
        self.set_roi_sig()
        self.set_roi_bkg()


        #self.w = QtGui.QTextEdit(self._name)
        #self.lab_info = QtGui.QLabel('Use EMQDetWF for "%s"' % src)

        self.lab_indwf = QtWidgets.QLabel('WF#')
        self.lab_indwf.setStyleSheet(style.styleLabel)
        self.lab_info.setText('Use EMQDetWF for "%s"' % src)
        self.set_info()
        self.lab_roi = QtWidgets.QLabel('Set ROI')
        self.but_set_sig = QtWidgets.QPushButton('Signal')
        self.but_set_bkg = QtWidgets.QPushButton('Bkgd')
        indwf = self.par_indwf.value()
        self.but_indwf = QtWidgets.QPushButton('%d' % (indwf if indwf is not None else -1))
        self.but_indwf.setFixedWidth(30)
        #self.box.addStretch(1)
        self.box.insertWidget(0, self.lab_indwf)
        self.box.insertWidget(1, self.but_indwf)
        self.box.addWidget(self.lab_roi)
        self.box.addWidget(self.but_set_sig)
        self.box.addWidget(self.but_set_bkg)

        #self.but_src = QtGui.QPushButton(self.par_src.value())
        #self.but_view = QtGui.QPushButton('View')
        #self.lab_info = QtGui.QLineEdit('NOT IMPLEMENTED "%s"' % src)

        #self.box = QtGui.QHBoxLayout(self)
        #self.box.addWidget(self.lab_info)
        #self.box.addStretch(1)
        #self.setLayout(self.box)

        #gu.printStyleInfo(self)
        #cp.guitabs = self

        self.but_set_sig.clicked.connect(self.on_but_set)
        self.but_set_bkg.clicked.connect(self.on_but_set)
        self.but_indwf.clicked.connect(self.on_but_indwf)

        self.set_style()
        self.set_tool_tips()

        self.init_det()


    def init_det(self):
        self.dso = PSDataSupplier(cp, log, dsname=None, detname=self.src)
        log.debug('init_det for src: %s' % self.src, self._name)


    def set_tool_tips(self):
        self.but_indwf.setToolTip('Select WF index\n-1 - show all')
        self.but_set_sig.setToolTip('Select visible window for signal\nand click on "Signal"')
        self.but_set_bkg.setToolTip('Select visible window for background\nand click on "Bkgd"')



    def set_pen_brush(self):
        alpha = 50
        col_sig = QtGui.QColor(QtCore.Qt.red)
        col_bkg = QtGui.QColor(QtCore.Qt.white)

        self.pen_sig = QtGui.QPen(col_sig,0)
        self.pen_bkg = QtGui.QPen(col_bkg,0)
        col_sig.setAlpha(alpha)
        col_bkg.setAlpha(alpha)
        self.brush_sig = QtGui.QBrush(col_sig)
        self.brush_bkg = QtGui.QBrush(col_bkg)



    def set_style(self):
        EMQDetI.set_style(self)
        self.lab_roi.setStyleSheet(style.styleLabel)

        self.lab_info.setMinimumWidth(350)
        #self.lab_info.setStyleSheet(style.styleLabel)
        #self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
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
        QtWidgets.QWidget.closeEvent(self, e)
        #Frame.closeEvent(self, e)

#------------------------------

    def roi_sig_xywh(self):
        gv = self.guview
        if gv is None : return None, None, None, None
        rs = gv.scene().sceneRect()

        x, y = self.par_sig_bmin.value(), rs.y()
        w = self.par_sig_bmax.value()-x if x is not None else None
        h = rs.height() if y is not None else None
        return x, y, w, h


    def roi_bkg_xywh(self):
        gv = self.guview
        if gv is None : return None, None, None, None
        rs = gv.scene().sceneRect()

        x, y = self.par_bkg_bmin.value(), rs.y()
        w = self.par_bkg_bmax.value()-x if x is not None else None
        h = rs.height() if y is not None else None
        return x, y, w, h


    def draw_roi(self):
        gv = self.guview
        if gv is not None :
            sc = gv.scene()
            #print 'XXX: draw ROI on scene', sc
            if self.item_roi_sig is not None : 
                sc.removeItem(self.item_roi_sig)
                self.item_roi_sig = None
            x, y, w, h = self.roi_sig_xywh()
            if x is not None :
                self.item_roi_sig = sc.addRect(x, y, w, h, self.pen_sig, self.brush_sig)
                self.item_roi_sig.setZValue(0.5)

            if self.item_roi_bkg is not None : 
                sc.removeItem(self.item_roi_bkg)
                self.item_roi_bkg = None
            x, y, w, h = self.roi_bkg_xywh()
            if x is not None :
                self.item_roi_bkg = sc.addRect(x, y, w, h, self.pen_bkg, self.brush_bkg)
                self.item_roi_bkg.setZValue(0.5)

#------------------------------

    def is_set(self):
        return True


    def reset_pars(self): 

        self.par_sig_tmin.setDefault()
        self.par_sig_tmax.setDefault()
        self.par_sig_bmin.setDefault()
        self.par_sig_bmax.setDefault()

        self.par_bkg_tmin.setDefault()
        self.par_bkg_tmax.setDefault()
        self.par_bkg_bmin.setDefault()
        self.par_bkg_bmax.setDefault()

        self.set_roi_sig()
        self.set_roi_bkg()
        self.set_info()

        self.par_indwf.setDefault()
        indwf = self.par_indwf.value()
        self.but_indwf.setText('%d' % (indwf if indwf is not None else -1))


    def roi_limit_bins(self, tmin, tmax):
        """Uses wt, tmin and tmax to find and return bin indexes bmin, bmax using self.wf, self.wt
        """
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
        bmin, bmax = self.roi_limit_bins(tmin, tmax)

        set_mode = 'signal'     if self.but_set_sig.hasFocus() else\
                   'background' if self.but_set_bkg.hasFocus() else\
                   'UNKNOWN'

        if self.but_set_sig.hasFocus() : 
            self.par_sig_tmin.setValue(tmin)
            self.par_sig_tmax.setValue(tmax)
            self.par_sig_bmin.setValue(bmin)
            self.par_sig_bmax.setValue(bmax)
            self.set_roi_sig()

        if self.but_set_bkg.hasFocus() : 
            self.par_bkg_tmin.setValue(tmin)
            self.par_bkg_tmax.setValue(tmax)
            self.par_bkg_bmin.setValue(bmin)
            self.par_bkg_bmax.setValue(bmax)
            self.set_roi_bkg()

        log.info('set WF %s ROI bins min=%d max=%d' % (set_mode, bmin, bmax), self._name)
        self.set_info()


    def set_info(self):
        msg = ''
        if not(self.sig_bmin is None or self.sig_bmax is None) :
            msg = 'S:[%d,%d]' % (self.sig_bmin, self.sig_bmax)
        if not(self.bkg_bmin is None or self.bkg_bmax is None) :
            msg += ' B:[%d,%d]' % (self.bkg_bmin, self.bkg_bmax)
        self.lab_info.setText('%s' % msg)

#------------------------------

    def set_roi_sig(self):
        self.sig_tmin = self.par_sig_tmin.value()
        self.sig_tmax = self.par_sig_tmax.value()
        self.sig_bmin = self.par_sig_bmin.value()
        self.sig_bmax = self.par_sig_bmax.value()

        if self.sig_bmin is not None : self.sig_bmin = int(self.sig_bmin)
        if self.sig_bmax is not None : self.sig_bmax = int(self.sig_bmax)

        self.sig_nbins = None if self.sig_bmin is None or self.sig_bmax is None else\
                         (self.sig_bmax - self.sig_bmin)
        self.draw_roi()

#------------------------------

    def set_roi_bkg(self):
        self.bkg_tmin = self.par_bkg_tmin.value()
        self.bkg_tmax = self.par_bkg_tmax.value()
        self.bkg_bmin = self.par_bkg_bmin.value()
        self.bkg_bmax = self.par_bkg_bmax.value()

        if self.bkg_bmin is not None : self.bkg_bmin = int(self.bkg_bmin)
        if self.bkg_bmax is not None : self.bkg_bmax = int(self.bkg_bmax)

        self.bkg_nbins = None if self.bkg_bmin is None or self.bkg_bmax is None else\
                         (self.bkg_bmax - self.bkg_bmin)
        self.draw_roi()

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

    def get_wf_event(self, evt=None):

        det = self.dso.detector()
        if det is None : 
            self.wf, self.wt = None, None
            return None, None, None, None, None, None
        e = evt if evt is not None else self.dso.event_next()
        resp = self.dso.detector().raw(e) # cp.event_number.value()
        if resp is None : 
            self.wf, self.wt = None, None
            return None, None, None, None, None, None
        self.wf, self.wt = wf, wt = resp
        #print_ndarr(wf, name='wf', first=0, last=10)
        #print_ndarr(wt, name='wt', first=0, last=10)

        # use wt as a bin number in stead of time
        nch, npt = shape = wt.shape
        wt = np.array(tuple(list(range(npt))*nch))
        wt.shape = shape
        self.wt = wt
        #print 'wt.shape', wt.shape

        tmin, tmax = wt.min(), wt.max()
        fmean, fstd = wf.mean(), wf.std()
        fmin, fmax = fmean-10*fstd, fmean+10*fstd

        return wf, wt, tmin, tmax, fmin, fmax

#------------------------------

    def plot_wf_update(self, wf, wt):

        self.guview.remove_all_graphs()

        indwf = self.par_indwf.value()
        indwf = int(indwf) if indwf is not None else -1
        #if indwf<0 : indwf=0

        if wf is None : return
        ngrp = wf.shape[0]
        #print 'XXX: EMQDetWF.plot_wf_update indwf, ngrp:', indwf, ngrp

        colors = (Qt.blue, Qt.green, Qt.yellow, Qt.red, Qt.black)
        for gr in range(ngrp) :
            if gr == indwf or indwf<0 :
                color = colors[gr%5]
                self.guview.add_graph(wt[gr,:-2], wf[gr,:-2], QtGui.QPen(color), brush=QtGui.QBrush())

#------------------------------

    #def on_but_view(self): self.message_def(sys._getframe().f_code.co_name)
    def on_but_view(self):
        msg = '%s' % (sys._getframe().f_code.co_name)
        log.debug(msg, self._name)
        if self.guview is None :
            wf, wt, tmin, tmax, fmin, fmax = self.get_wf_event()

            rectax=QtCore.QRectF(tmin, fmin, tmax-tmin, fmax-fmin) if wf is not None else\
                   QtCore.QRectF(0,0,1,1)

            self.guview = GUViewGraph(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                    margl=0.12, margr=0.01, margt=0.01, margb=0.06)

            self.guview.connect_view_is_closed_to(self.on_child_close)

            self.plot_wf_update(wf, wt)

            #win = cp.guimain
            #point, size = win.mapToGlobal(QtCore.QPoint(0,0)), win.size() # Offset (-5,-22) for frame size.
            #x,y,w,h = point.x(), point.y(), size.width(), size.height()
            #self.guview.move(QtCore.QPoint(x,y) + QtCore.QPoint(w+10, 10))
            ##self.guview.move(self.pos() + QtCore.QPoint(self.width()+80, 10))

            dx, dy = self.tabind*50, self.detind*100
            if cp.guimain is not None :
                point = point_relative_window(cp.guimain, QtCore.QPoint(dx, dy))
                self.guview.move(point)

            self.set_window_geometry()
            self.guview.show()

        else :
            wf, wt, tmin, tmax, fmin, fmax = self.get_wf_event()
            self.plot_wf_update(wf, wt)
            self.guview.raise_()
            #self.guview.close()
            #self.guview = None

        tit = '%s  %s' % (cp.tab_names[self.tabind], self.src)
        self.guview.setWindowTitle(tit)

        self.draw_roi()


    def signal(self, evt):  
        if self.tabind < 0 :
            msg = 'WARNING: %s%s waveform index in not selected: %d'%\
                   (self._name, sys._getframe().f_code.co_name, self.tabind)
            print(msg)
            return None

        wf, wt, tmin, tmax, fmin, fmax = self.get_wf_event(evt)

        indwf = self.par_indwf.value()
        indwf = int(indwf) if indwf is not None else 0
        #print 'XXX: EMQDetWF tabind = ', str(indwf)
        wf1 = wf[indwf]
        sbmin, sbmax, snbins = self.sig_bmin, self.sig_bmax, self.sig_nbins
        bbmin, bbmax, bnbins = self.bkg_bmin, self.bkg_bmax, self.bkg_nbins

        bb = 0 if bnbins is None else wf1[bbmin:bbmax].sum()/bnbins
        return wf1.sum()-bb*wf1.size if sbmin is None else wf1[sbmin:sbmax].sum()-bb*snbins

#------------------------------

    def set_window_geometry(self) :
        win=self.guview
        if self.par_winx.value() is None : return
        if self.par_winx.is_default() : return

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
    app = QtWidgets.QApplication(sys.argv)
    w = EMQDetWF(None, 'SxrEndstation.0:Acqiris.1')
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.on_but_view()
    w.get_signal()
    w.show()
    app.exec_()

#------------------------------
