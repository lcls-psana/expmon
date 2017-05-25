#------------------------------
"""GUI for configuration of detector object.
   Created: 2017-05-15
   Author : Mikhail Dubrovin
"""
#------------------------------
from expmon.EMQDetI import *
from expmon.PSDataSupplier import PSDataSupplier
from math import floor, ceil
#------------------------------

class EMQDetArea(EMQDetI) :
    """Interface for EMQDetArea objects.
    """
    def __init__ (self, parent, src=None) :
        EMQDetI.__init__(self, parent, src)
        self._name = self.__class__.__name__

        self.guview = None        
        self.arrimg = None

        #self.parent = parent
        tabind = parent.tabind
        detind = parent.detind

        det_list_of_pars = cp.det1_list_of_pars if detind == 1 else\
                           cp.det2_list_of_pars

        self.par_winx  = det_list_of_pars[0][tabind]
        self.par_winy  = det_list_of_pars[1][tabind]
        self.par_winh  = det_list_of_pars[2][tabind]
        self.par_winw  = det_list_of_pars[3][tabind]

        self.par_xmin  = det_list_of_pars[4][tabind]
        self.par_xmax  = det_list_of_pars[5][tabind]
        self.par_ymin  = det_list_of_pars[6][tabind]
        self.par_ymax  = det_list_of_pars[7][tabind]

        self.set_roi_sig()

        #self.w = QtGui.QTextEdit(self._name)
        #self.lab_info = QtGui.QLabel('Use EMQDetArea for "%s"' % src)

        self.lab_info.setText('Use EMQDetArea for "%s"' % src)
        self.set_info()

        self.but_set = QtGui.QPushButton('Set ROI')
        #self.box.addStretch(1)
        self.box.addWidget(self.but_set)

        #self.but_src = QtGui.QPushButton(self.par_src.value())
        #self.but_view = QtGui.QPushButton('View')
        #self.lab_info = QtGui.QLineEdit('NOT IMPLEMENTED "%s"' % src)

        #self.box = QtGui.QHBoxLayout(self)
        #self.box.addWidget(self.lab_info)
        #self.box.addStretch(1)
        #self.setLayout(self.box)

        #self.set_style()
        #self.set_tool_tips()
        #gu.printStyleInfo(self)
        #cp.guitabs = self

        #self.connect(self.but_src,  QtCore.SIGNAL('clicked()'), self.on_but_src)
        #self.connect(self.but_view, QtCore.SIGNAL('clicked()'), self.on_but_view)

        self.connect(self.but_set,   QtCore.SIGNAL('clicked()'), self.on_but_set)

        self.init_det()


    def init_det(self):
        self.dso = PSDataSupplier(cp, log, dsname=None, detname=self.src)
        log.info('init_det for src: %s' % self.src, self._name)
        self.arrimg = arr = self.dso.image(cp.event_number.value())


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

    def set_roi_sig(self):
        self.sig_cmin = self.par_xmin.value()
        self.sig_cmax = self.par_xmax.value()
        self.sig_rmin = self.par_ymin.value()
        self.sig_rmax = self.par_ymax.value()

        if self.sig_cmin is not None : self.sig_cmin = int(self.sig_cmin)
        if self.sig_cmax is not None : self.sig_cmax = int(self.sig_cmax)
        if self.sig_rmin is not None : self.sig_rmin = int(self.sig_rmin)
        if self.sig_rmax is not None : self.sig_rmax = int(self.sig_rmax)


    def on_but_set(self):
        #print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('on_but_set', self._name)
        if self.guview is None :
            log.warning('"View" image then use "Set" button', self._name)
            return
        xmin, xmax, ymin, ymax = self.guview.axes_limits()
        #print 'xmin=%.6f  xmax=%.6f  ymin=%.1f  ymax=%.1f' % (xmin, xmax, ymin, ymax)
        self.par_xmin.setValue(floor(xmin))
        self.par_xmax.setValue(ceil(xmax))
        self.par_ymin.setValue(floor(ymin))
        self.par_ymax.setValue(ceil(ymax))
        self.set_roi_sig()
        self.set_info()


    def set_info(self):
        if None in (self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax) : return
        msg = 'cols:[%d, %d] rows:[%d, %d]' % (self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax)
        self.lab_info.setText('ROI: %s' % msg)

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

        if self.guview is None :
            #self.guview = IVMain(parser=None)
            #arr = ag.random_standard((500,500), mu=0, sigma=10)
            self.arrimg = arr = self.dso.image(cp.event_number.value())
            self.guview = GUViewImage(None, arr)
            #self.move(self.pos())
            self.guview.move(self.pos() + QtCore.QPoint(self.width()+80, 100))
            #self.guview.move(QtGui.QCursor.pos()+QtCore.QPoint(200,-200))
            self.set_window_geometry()
            self.guview.show()
            self.guview.connect_view_is_closed_to(self.on_child_close)

        else :
            self.arrimg = arr = self.dso.image(self.dso.event_next()) # cp.event_number.value())
            self.guview.set_pixmap_from_arr(arr)
            self.guview.raise_()

        tit = '%s  %s' % (cp.tab_names[self.tabind], self.src)
        self.guview.setWindowTitle(tit)


    def raw(self, evt):
        cmin, cmax, rmin, rmax = self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax        
        img = self.dso.raw(evt)
        return img.sum() if cmin is None else img[rmin:rmax, cmin:cmax].sum()


    def signal(self, evt):  
        cmin, cmax, rmin, rmax = self.sig_cmin, self.sig_cmax, self.sig_rmin, self.sig_rmax        
        #print 'XXX %s.signal before image' % self._name
        img = self.dso.image(evt)
        #print 'XXX %s.signal after image' % self._name
        return img.sum() if cmin is None else img[rmin:rmax, cmin:cmax].sum()

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
        msg = 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug(msg, self._name)
        self.save_window_geometry()
        self.guview.disconnect_view_is_closed_from(self.on_child_close)
        self.guview = None

#------------------------------

if __name__ == "__main__" :
    app = QtGui.QApplication(sys.argv)
    w = EMQDetArea(None, 'SxrBeamline.0:Opal1000.1')
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.on_but_view()
    w.get_signal()
    w.show()
    app.exec_()

#------------------------------
