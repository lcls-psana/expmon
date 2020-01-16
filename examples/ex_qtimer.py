from __future__ import print_function
#------------------------------

import sys
from PyQt5 import QtCore, QtGui, QtWidgets

#------------------------------

class MWidget(QtWidgets.QWidget) :
    def __init__(self, parent=None) :
        QtWidgets.QWidget.__init__(self, parent)
        self.timer = QtCore.QTimer()
        self.dt_msec = 500
        self.timer.timeout.connect(self.on_timeout)


    def on_timeout(self) :
        print('%s.%s' % (__name__, sys._getframe().f_code.co_name))
        #self.timer.stop() # otherwise loop is not ending


    def test_qtimer(self) :
        print('%s.%s' % (__name__, sys._getframe().f_code.co_name))
        #for i in range(10) :
        #    print 'loop %d' % i

        self.timer.start(self.dt_msec)

#------------------------------

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    w = MWidget()
    w.show()
    w.test_qtimer()
    app.exec_()

#------------------------------


