#------------------------------
"""GUI for configuration of MonV1
Created: 2017-05-19
Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQConfMonV1 import EMQConfMonV1
"""
#------------------------------

from expmon.EMQConfMonI        import *
from expmon.EMQConfDetV1       import EMQConfDetV1

#------------------------------

class EMQConfMonV1(EMQConfMonI) :
    """Configuration GUI for MonV1
    """

    def __init__(self, parent=None, tabind=0) :

        #Frame.__init__(self, parent, mlw=1)
        #QtGui.QWidget.__init__(self, parent)
        EMQConfMonI.__init__(self, parent, tabind)
        self._name = self.__class__.__name__

        log.debug('in __init__', self._name)

        #self.tabind = tabind # is set in EMQConfMonI 
 
        self.wdet1 = EMQConfDetV1(parent, tabind, detind=1)
        self.wdet2 = EMQConfDetV1(parent, tabind, detind=2)

        self.box = QtWidgets.QVBoxLayout(self)
        self.box.addWidget(self.wdet1)
        self.box.addWidget(self.wdet2)
        self.box.addStretch(1)
        self.setLayout(self.box)

        self.set_style()
        self.set_tool_tips()

    def set_style(self):
        EMQConfMonI.set_style(self)
#        self.setMinimumSize(300,100)
#        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
#        self.setMaximumSize(600,100)
#        self.vsplit.setMinimumHeight(700)        
#        self.setStyleSheet(style.styleBkgd)


    def reset_monitor(self):
        self.wdet1.set_src()      
        self.wdet2.set_src()      


#    def closeEvent(self, e):
#        log.debug('EMQConfMonV1.closeEvent') # % self._name)
#        log.debug('closeEvent', self._name)
#        try : self.wdet1.close()
#        except : pass
#        EMQConfMonI.closeEvent(self, e)
#        QtGui.QWidget.closeEvent(self, e)

#------------------------------

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    w = EMQConfMonV1()
    w.setGeometry(10, 25, 700, 600)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.show()
    app.exec_()

#------------------------------
