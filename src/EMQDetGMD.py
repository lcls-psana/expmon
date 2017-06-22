#------------------------------
"""GUI for configuration of the detector object.
   Created: 2017-05-15
   Author : Mikhail Dubrovin
"""
#------------------------------
from expmon.EMQDetI import *
from expmon.PSDataSupplier import PSDataSupplier
#------------------------------

class EMQDetGMD(EMQDetI) :
    """Interface for EMQDetGMD objects.
    """
    def __init__ (self, parent, src=None) :
        EMQDetI.__init__(self, parent, src)
        self._name = self.__class__.__name__

        #self.parent = parent
        #self.tabind = parent.tabind
        #self.detind = parent.detind
        #self.src=str(src)

        #self.w = QtGui.QTextEdit(self._name)
        #self.lab_info = QtGui.QLabel('Use EMQDetGMD for "%s"' % src)

        self.lab_info.setText('Use EMQDetGMD for "%s"' % src)
        #self.but_set = QtGui.QPushButton('Set')
        #self.box.addStretch(1)
        #self.box.addWidget(self.but_set)

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

        self.init_det()


    def init_det(self):
        self.dso = PSDataSupplier(cp, log, dsname=None, detname=self.src)


    def set_style(self):
        self.lab_info.setMinimumWidth(300)
        self.lab_info.setStyleSheet(style.styleLabel)
        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))

        #self.setGeometry(10, 25, 400, 600)
        #self.setMinimumSize(400,50)
        #self.vsplit.setMinimumHeight(700)        
        #self.setStyleSheet(style.styleBkgd)
        #self.but_src.setMinimumWidth(200)


    def closeEvent(self, e):
        log.debug('closeEvent', self._name)
        QtGui.QWidget.closeEvent(self, e)

#------------------------------
# Abstract methods IMPLEMENTATION:
#------------------------------

    def is_set(self):
        return True


    #def on_but_view(self): self.message_def(sys._getframe().f_code.co_name)
    def on_but_view(self):
        #log.debug('on_but_view', self._name)
        #print '%s.on_but_view' % self._name
        v = self.signal()
        self.lab_info.setText('GMD value: %.3f'%v if v is not None else 'GMD value: None')

 
    def signal(self, evt=None):
        evt_sig = self.dso.event_next() if evt is None else evt
        det = self.dso.detector()
        if det is None : return None
        gmd_data = det.get(evt_sig)
        if gmd_data is None : return None
        return gmd_data.relativeEnergyPerPulse()

#------------------------------

if __name__ == "__main__" :
    app = QtGui.QApplication(sys.argv)
    w = EMQDetGMD(None, 'SxrBeamline.0:Opal1000.1')
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.on_but_view()
    w.signal()
    w.show()
    app.exec_()

#------------------------------
