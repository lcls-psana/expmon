
#------------------------------
"""EMQPresenter shows/updates resulting plots.
   Created: 2017-05-23
   Author : Mikhail Dubrovin
"""
#------------------------------
import sys
#import os

from PyQt4 import QtCore, QtGui

from expmon.EMConfigParameters import cp
from expmon.Logger             import log

class EMQPresenter(QtCore.QObject) :
    """
    """
    def __init__(self, parent=None) :

        QtCore.QObject.__init__(self, parent)
        self._name = self.__class__.__name__
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('in %s'%sys._getframe().f_code.co_name, self._name)

        self.dt_msec = 1000
        self.timer = QtCore.QTimer()
        self.count_time_checks = 0
        self.count_updates = 0
        self.edi_fld = None

        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timeout)
        self.start_timer()


    def start_timer(self) :    
        self.timer.start(self.dt_msec)


    def stop_timer(self) :
        self.timer.stop()

 
    def on_timeout(self) :
        self.count_time_checks += 1
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)

        if  cp.flag_nevents_collected : 
            cp.flag_nevents_collected = False
            self.count_updates += 1
            self.proc_presenter()

        #if self.counter > 4 : 
        #    self.stop_timer()
        #    sys.exit('End of %s' % self._name)

        self.start_timer()


#    def event(self, e) :
#        print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
#        print 'XXX event', str(e)

 
    def __del__(self) :
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('in %s'%sys._getframe().f_code.co_name, self._name)
        self.stop_timer()
        self.disconnect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timeout)
        if self.edi_fld is not None : self.edi_fld.close()
        #self.deleteLater()

#------------------------------
#------------------------------
#------------------------------

    def proc_presenter(self) :

        nrecs = cp.nevents_update.value()
        #recs = cp.dataringbuffer.records_latest(nrecs)
        recs = cp.dataringbuffer.records_new()

        #print 'XXX %s.%s events are collected' % (self._name, sys._getframe().f_code.co_name)
        #log.info('in %s'%sys._getframe().f_code.co_name, self._name)

        print 50*'='
        for rec in recs :
            print rec
        print 'XXX %s : number of new records = %d' % (sys._getframe().f_code.co_name, len(recs))
        print 50*'='

        #self.update_info_window()

#------------------------------

    def update_info_window(self) :

        if self.edi_fld is None :
            self.counter = 0
            e = self.edi_fld = QtGui.QTextEdit(self._name)
            e.show()
            e.setReadOnly(True)
            e.setStyleSheet(style.styleWhiteFixed)
            e.edi_fld.show()

        self.counter += 1
        e = self.edi_fld
        e.setText('Here we are, # of checks:%3d updates:%3d' % (self.count_time_checks, self.count_updates))
        #e.moveCursor(QtGui.QTextCursor.End)
        e.repaint()
        #e.raise_()
        e.update()

#------------------------------
#------------------------------

if __name__ == "__main__" :
    #from PyQt4 import QtGui#, QtCore
    app = QtGui.QApplication(sys.argv)
    o = EMQPresenter(parent=None)
    #w.show()
    app.exec_()

#------------------------------
#------------------------------

