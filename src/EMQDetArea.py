#------------------------------
"""GUI for configuration of detector object.
   Created: 2017-05-15
   Author : Mikhail Dubrovin
"""
from __future__ import division
#------------------------------
from expmon.EMQDetI import *
from PyQt5 import QtCore, QtGui, QtWidgets
from expmon.PSDataSupplier import PSDataSupplier
from math import floor, ceil
from pyimgalgos.GlobalUtils import reshape_to_2d, print_ndarr
from expmon.EMQUtils import point_relative_window
#------------------------------

class EMQDetArea(EMQDetI) :
    """Interface for EMQDetArea objects.
    """
    def __init__ (self, parent, src=None) :
        EMQDetI.__init__(self, parent, src)
        self._name = 'EMQDetArea'

        self.guview = None        
        self.arrimg = None
        self.ncall = 0

        tabind = parent.tabind
        detind = parent.detind

        det_list_of_pars = cp.det1_list_of_pars if detind == 1 else\
                           cp.det2_list_of_pars

        self.par_winx  = det_list_of_pars[0][tabind]
        self.par_winy  = det_list_of_pars[1][tabind]
        self.par_winh  = det_list_of_pars[2][tabind]
        self.par_winw  = det_list_of_pars[3][tabind]

        self.par_sig_xmin  = det_list_of_pars[4][tabind]
        self.par_sig_xmax  = det_list_of_pars[5][tabind]
        self.par_sig_ymin  = det_list_of_pars[6][tabind]
        self.par_sig_ymax  = det_list_of_pars[7][tabind]

        self.par_bkg_xmin  = det_list_of_pars[8][tabind]
        self.par_bkg_xmax  = det_list_of_pars[9][tabind]
        self.par_bkg_ymin  = det_list_of_pars[10][tabind]
        self.par_bkg_ymax  = det_list_of_pars[11][tabind]
            
        self.item_roi_sig = None
        self.item_roi_bkg = None
        self.set_pen_brush()
        self.set_roi_sig()
        self.set_roi_bkg()

        self.lab_info.setText('Use EMQDetArea') # for "%s"' % src)

        self.lab_roi = QtWidgets.QLabel('Set ROI')
        self.but_set_sig = QtWidgets.QPushButton('Signal')
        self.but_set_bkg = QtWidgets.QPushButton('Bkgd')
        #self.box.addStretch(1)
        self.box.addWidget(self.lab_roi)
        self.box.addWidget(self.but_set_sig)
        self.box.addWidget(self.but_set_bkg)

        self.but_set_sig.clicked.connect(self.on_but_set)
        self.but_set_bkg.clicked.connect(self.on_but_set)

        self.init_det()
        self.set_style()
        #self.set_tool_tips()


    def init_det(self):
        self.dso = PSDataSupplier(cp, log, dsname=None, detname=self.src)
        log.info('init_det for src: %s' % self.src, self._name)
        self.arrimg = self.image(self.dso.event_next()) # cp.event_number.value())



    def set_pen_brush(self):
        alpha = 100
        col_sig = QtGui.QColor(QtCore.Qt.red)
        col_bkg = QtGui.QColor(QtCore.Qt.white)

        self.pen_sig = QtGui.QPen(col_sig,4)
        self.pen_bkg = QtGui.QPen(col_bkg,4)
        col_sig.setAlpha(alpha)
        col_bkg.setAlpha(alpha)
        self.brush_sig = QtGui.QBrush(col_sig)
        self.brush_bkg = QtGui.QBrush(col_bkg)


 
    def set_style(self):
        EMQDetI.set_style(self)
        self.lab_roi.setStyleSheet(style.styleLabel)
        #self.lab_info.setMinimumWidth(300)
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
        x, y = self.par_sig_xmin.value(), self.par_sig_ymin.value()
        w = self.par_sig_xmax.value()-x if x is not None else None
        h = self.par_sig_ymax.value()-y if y is not None else None
        return x, y, w, h


    def roi_bkg_xywh(self):
        x, y = self.par_bkg_xmin.value(), self.par_bkg_ymin.value()
        w = self.par_bkg_xmax.value()-x if x is not None else None
        h = self.par_bkg_ymax.value()-y if y is not None else None
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


    def set_roi_sig(self):
        self.sig_cmin = self.par_sig_xmin.value()
        self.sig_cmax = self.par_sig_xmax.value()
        self.sig_rmin = self.par_sig_ymin.value()
        self.sig_rmax = self.par_sig_ymax.value()

        if self.sig_cmin is not None : self.sig_cmin = int(self.sig_cmin)
        if self.sig_cmax is not None : self.sig_cmax = int(self.sig_cmax)
        if self.sig_rmin is not None : self.sig_rmin = int(self.sig_rmin)
        if self.sig_rmax is not None : self.sig_rmax = int(self.sig_rmax)

        self.sig_npix = None if None in (self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax) else\
                        (self.sig_cmax - self.sig_cmin)\
                      * (self.sig_rmax - self.sig_rmin)
        self.draw_roi()


    def set_roi_bkg(self):
        self.bkg_cmin = self.par_bkg_xmin.value()
        self.bkg_cmax = self.par_bkg_xmax.value()
        self.bkg_rmin = self.par_bkg_ymin.value()
        self.bkg_rmax = self.par_bkg_ymax.value()

        if self.bkg_cmin is not None : self.bkg_cmin = int(self.bkg_cmin)
        if self.bkg_cmax is not None : self.bkg_cmax = int(self.bkg_cmax)
        if self.bkg_rmin is not None : self.bkg_rmin = int(self.bkg_rmin)
        if self.bkg_rmax is not None : self.bkg_rmax = int(self.bkg_rmax)

        self.bkg_npix = None if self.bkg_cmin is None else\
                        (self.bkg_cmax - self.bkg_cmin)\
                      * (self.bkg_rmax - self.bkg_rmin)
        self.draw_roi()

#------------------------------

    def on_but_set(self):
        #print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('on_but_set', self._name)
        if self.guview is None :
            log.warning('"View" image then use "Set" button', self._name)
            return
        xmin, xmax, ymin, ymax = self.guview.axes_limits()
        #print 'xmin=%.6f  xmax=%.6f  ymin=%.1f  ymax=%.1f' % (xmin, xmax, ymin, ymax)

        set_mode = 'signal'     if self.but_set_sig.hasFocus() else\
                   'background' if self.but_set_bkg.hasFocus() else\
                   'UNKNOWN'

        #print 'arrimg.shape:', self.arrimg.shape
        h,w = self.arrimg.shape

        if xmin<0      : xmin=0
        if ymin<0      : ymin=0
        if not(xmax<w) : xmax=w-1
        if not(ymax<h) : ymax=h-1

        if xmax<0      : xmax=1
        if ymax<0      : ymax=1
        if not(xmin<w) : xmin=w-2
        if not(ymin<h) : ymin=h-2

        msg = None
        if self.but_set_sig.hasFocus() :
            self.par_sig_xmin.setValue(floor(xmin))
            self.par_sig_xmax.setValue(ceil(xmax))
            self.par_sig_ymin.setValue(floor(ymin))
            self.par_sig_ymax.setValue(ceil(ymax))
            self.set_roi_sig()
            msg = 'cols:[%d, %d] rows:[%d, %d]' % (self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax)

        if self.but_set_bkg.hasFocus() :
            self.par_bkg_xmin.setValue(floor(xmin))
            self.par_bkg_xmax.setValue(ceil(xmax))
            self.par_bkg_ymin.setValue(floor(ymin))
            self.par_bkg_ymax.setValue(ceil(ymax))
            self.set_roi_bkg()
            msg = 'cols:[%d, %d] rows:[%d, %d]' % (self.bkg_cmin, self.bkg_cmax, self.bkg_rmin, self.bkg_rmax)

        log.info('set %s ROI %s' % (set_mode, msg), self._name)
        self.set_info(set_mode)


    def set_info(self, set_mode):
        #if None in (self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax) : return
        #msg = 'cols:[%d, %d] rows:[%d, %d]' % (self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax)
        self.lab_info.setText('%s ROI is changed'%set_mode)
        #log.info('set ROI %s' % msg, self._name)

#------------------------------
# Abstract methods IMPLEMENTATION:
#------------------------------

    def is_set(self):
        return True


    #def on_but_view(self): self.message_def(sys._getframe().f_code.co_name)
    def on_but_view(self):
        msg = '%s.on_but_view  plot for src: %s' % (self._name, self.src)
        log.debug(msg, self._name)

        from graphqt.GUViewImage import GUViewImage

        #import pyimgalgos.NDArrGenerators as ag
        #self.arrimg = ag.random_standard((500,500), mu=0, sigma=10)

        self.arrimg = self.image(self.dso.event_next(), do_cmod=True) # cp.event_number.value())
        #print_ndarr(self.arrimg, 'XXX self.arrimg') 

        if self.guview is None :
            self.guview = GUViewImage(None, self.arrimg)

            #win = cp.guimain
            #point, size = win.mapToGlobal(QtCore.QPoint(0,0)), win.size()
            #x,y,w,h = point.x(), point.y(), size.width(), size.height()
            #self.guview.move(QtCore.QPoint(x,y) + QtCore.QPoint(w+10, 100))
            #self.guview.move(self.pos() + QtCore.QPoint(self.width()+80, 100))

            dx, dy = self.tabind*50, self.detind*100
            point = point_relative_window(cp.guimain, QtCore.QPoint(dx, dy))
            self.guview.move(point)
            #print 'XXX: EMQDetArea point', point

            self.set_window_geometry()
            self.guview.show()
            self.guview.connect_view_is_closed_to(self.on_child_close)

        else :
            self.guview.set_pixmap_from_arr(self.arrimg)
            self.guview.raise_()

        tit = '%s  %s' % (cp.tab_names[self.tabind], self.src)
        self.guview.setWindowTitle(tit)

        self.draw_roi()


#    def raw(self, evt):
#        cmin, cmax, rmin, rmax = self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax        
#        #print 'XXX: EMQDetArea.raw'
#        img = self.dso.raw(evt)
#        return img.sum() if cmin is None else img[rmin:rmax, cmin:cmax].sum()

        
    def image(self, evt, do_cmod=False):  
        nda = self.dso.raw(evt)
        self.ncall += 1
        if self.ncall == 1 :
            self.peds = self.dso.pedestals(evt)
            print_ndarr(self.peds, 'XXX: EMQDetArea pedestals')
            self.cmpars = self.dso.common_mode(evt)
            print_ndarr(self.cmpars, 'XXX: EMQDetArea common_mode')
        #print 'XXX: EMQDetArea.image', nda         
        if nda is None : return None
        if self.peds is not None : nda = nda.astype(self.peds.dtype) - self.peds
        if do_cmod and (self.cmpars is not None) : self.dso.detector().common_mode_apply(evt, nda, self.cmpars)
        img = self.dso.image(evt, nda)
        if img is None : img = reshape_to_2d(nda)
        #print_ndarr(img, 'XXX: EMQDetArea.image img')
        return img


    def signal(self, evt, do_cmod=False):  
        scmin, scmax, srmin, srmax, snpix = self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax, self.sig_npix        
        bcmin, bcmax, brmin, brmax, bnpix = self.bkg_cmin, self.bkg_cmax, self.bkg_rmin, self.bkg_rmax, self.bkg_npix       
        #print 'XXX %s.signal before image' % self._name
        img = self.image(evt, do_cmod)
        if img is None : return None
        #print 'XXX %s.signal after image' % self._name
        bb = 0 if bnpix is None else img[brmin:brmax, bcmin:bcmax].sum()/bnpix
        return img.sum() if scmin is None else img[srmin:srmax, scmin:scmax].sum() - bb*snpix

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
        msg = 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug(msg, self._name)
        self.save_window_geometry()
        self.guview.disconnect_view_is_closed_from(self.on_child_close)
        self.guview = None

#------------------------------

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    w = EMQDetArea(None, 'SxrBeamline.0:Opal1000.1')
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.on_but_view()
    w.get_signal()
    w.show()
    app.exec_()

#------------------------------
