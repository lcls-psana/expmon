from __future__ import print_function
#------------------------------

import sys
from PyQt4 import QtGui, QtCore

#------------------------------

class MWidget(QtGui.QWidget) :
    def __init__(self, parent=None) :
        QtGui.QWidget.__init__(self, parent)
        self.timer = QtCore.QTimer()
        self.dt_msec = 500
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timeout)


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
    app = QtGui.QApplication(sys.argv)
    w = MWidget()
    w.show()
    w.test_qtimer()
    app.exec_()

#------------------------------


