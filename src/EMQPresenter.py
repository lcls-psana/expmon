
#------------------------------
"""EMQPresenter shows/updates resulting plots.
   Created: 2017-05-23
   Author : Mikhail Dubrovin
"""
#------------------------------
import sys
#import os
from time import time
import numpy as np

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from graphqt.GUViewGraph import GUViewGraph

from graphqt.Styles    import style
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
        self.t0_sec = None

        self.nmonitors = cp.number_of_tabs
        self.wscatter = [None] * self.nmonitors
        self.whsig1   = [None] * self.nmonitors
        self.whsig2   = [None] * self.nmonitors

        #self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timeout)
        #self.start_timer()


    def on_events_collected(self) :
        #log.info('XXX in %s' % sys._getframe().f_code.co_name, self._name)
        self.update_presenter()


#    def start_timer(self) :    
#        self.timer.start(self.dt_msec)


#    def stop_timer(self) :
#        self.timer.stop()

 
#    def on_timeout(self) :
#        self.count_time_checks += 1
#        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
#        if  cp.flag_nevents_collected : 
#            cp.flag_nevents_collected = False
#            self.update_presenter()
#        self.start_timer()
        #if self.counter > 4 : 
        #    self.stop_timer()
        #    sys.exit('End of %s' % self._name)


#    def event(self, e) :
#        print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
#        print 'XXX event', str(e)

 
    def __del__(self) :
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('%s'%sys._getframe().f_code.co_name, self._name)
        if self.edi_fld is not None : self.edi_fld.close()

        for i in range(self.nmonitors) :
            if self.wscatter[i] is not None : self.wscatter[i].close()
            if self.whsig1[i]   is not None : self.whsig1[i].close()
            if self.whsig2[i]   is not None : self.whsig2[i].close()

        #self.deleteLater()

#------------------------------

    def records_parser(self, recs) :
        """Decomposes list of records like 
           ['sxro5916', 24, 1200, 
             0, 586742.0, 15.305053710937486, 
             1, 48072616331.357925, -3.9454345703125, 
             2, 1.6427001953125, 1.59228515625, 
             None, None, None]
        """
        rec0 = recs[0]
        nrecs = len(recs)
        exp, run = rec0[:2]
        evnums = [rec[2] for rec in recs]
        #print 'XXX %s.%s' % (self._name, sys._getframe().f_code.co_name)
        #print 'XXX - exp %s  run %d  nrecs %d' % (exp, run, nrecs)
        #print 'XXX - evnums:', evnums

        mon_sig1 = [None] * self.nmonitors
        mon_sig2 = [None] * self.nmonitors

        for i in range(self.nmonitors) :
            is1 = 3 + i*3 + 1
            is2 = is1 + 1
            if rec0[is1] is not None : mon_sig1[i] = [rec[is1] for rec in recs]
            if rec0[is2] is not None : mon_sig2[i] = [rec[is2] for rec in recs]

        return nrecs, exp, run, evnums, mon_sig1, mon_sig2

#------------------------------

    def update_presenter(self) :

        self.count_updates += 1

        nrecs = cp.nevents_update.value()
        #recs = cp.dataringbuffer.records_latest(nrecs)
        recs = cp.dataringbuffer.records_new()
        nrecs, exp, run, evnums, mon_sig1, mon_sig2 = self.records_parser(recs)

        msg = '%s %4d for %4d events, last event: %6d'%\
              (sys._getframe().f_code.co_name, self.count_updates, nrecs, recs[-1][2])
        if self.t0_sec is not None : msg += '  t(sec/event) = %.6f' % ((time()-self.t0_sec)/nrecs)
        log.info(msg, self._name)
        log.debug('recs[0]: %s' % str(recs[0]))

        self.t0_sec = time()

        # print 'raw records from ring buffer'
        # for rec in recs : print rec

        #self.print_signals(evnums, mon_sig1, mon_sig2)
        #self.update_info_window()

        for i, mon in enumerate(cp.monitors) :
            if not mon.is_active() : continue
            self.update_scatter(i, np.array(mon_sig1[i]), np.array(mon_sig2[i]))

#------------------------------

    def update_scatter(self, imon, sig1, sig2):
        #print 'XXX In %s.%s imon: %s' % (self._name, sys._getframe().f_code.co_name, cp.tab_names[imon])
        w = self.wscatter[imon]
        if w is None :
            if sig1 is None or sig2 is None : return
            xmin, xmax = sig1.min(), sig1.max()
            ymin, ymax = sig2.min(), sig2.max()
            if xmin is None or xmax is None or ymin is None or ymax is None : return
            rectax=QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)
            w = self.wscatter[imon] = GUViewGraph(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                                  margl=0.12, margr=0.01, margt=0.01, margb=0.06)
            w.connect_view_is_closed_to(self.on_scatter_close)
            self.draw_scatter(imon, sig1, sig2)
            #w.move(self.pos() + QtCore.QPoint(self.width()+80, 0))
            #self.set_window_geometry()
            w.show()
        else :
            self.draw_scatter(imon, sig1, sig2)
            w.raise_()

#------------------------------

    def on_scatter_close(self): 
        msg = 'TBD %s' % (sys._getframe().f_code.co_name)
        log.debug(msg, self._name)

#        for w in self.wscatter:
#            if w is None : continue
#            print 'w:%s  hasFocus:%s' % (str(w), w.hasFocus())

        #self.save_window_geometry()
        #self.w.disconnect_view_is_closed_from(self.on_child_close)
        #self.w = None

##------------------------------

    def draw_scatter(self, imon, sig1, sig2):
        w = self.wscatter[imon]
        if w is None : return
        w.remove_all_graphs()
        color = (Qt.blue, Qt.green, Qt.yellow, Qt.red, Qt.black)[imon%5]
        w.add_graph(sig1, sig2, QtGui.QPen(color), brush=QtGui.QBrush())
        w.setWindowTitle('Scatter plot for %s' % cp.tab_names[imon])

#------------------------------
#------------------------------
#------------------------------
#------------------------------

    def print_signals(self, evnums, mon_sig1, mon_sig2) :
        #=========
        if True :
            for i, mon in enumerate(cp.monitors) :
                print 'Records for mon %d  %s' % (i, cp.tab_names[i])
                if not mon.is_active() : 
                    print 'NON-ACTIVE'
                    continue

                for evnum, s1, s2 in zip(evnums, mon_sig1[i], mon_sig2[i]) :
                    print evnum, s1, s2

        #=========
        if False : # True :
            for i in range(self.nmonitors) :
                print 'Records for mon %d:' % i
                if mon_sig1[i] is None : 
                    print 'NON-ACTIVE'
                    continue

                for evnum, s1, s2 in zip(evnums, mon_sig1[i], mon_sig2[i]) :
                    print evnum, s1, s2

#------------------------------

    def update_info_window(self) :

        if self.edi_fld is None :
            self.counter = 0
            e = self.edi_fld = QtGui.QTextEdit(self._name)
            e.setGeometry(500, 25, 300, 200)
            e.show()
            e.setReadOnly(True)
            e.setStyleSheet(style.styleWhiteFixed)
            e.show()

        self.counter += 1
        e = self.edi_fld
        e.setText('Here we are, # of checks:%3d updates:%3d' % (self.count_time_checks, self.count_updates))
        #e.moveCursor(QtGui.QTextCursor.End)
        e.repaint()
        #e.raise_()
        e.update()

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :
    sys.exit('Test is N/A')
    #from PyQt4 import QtGui#, QtCore
    #app = QtGui.QApplication(sys.argv)
    #o = EMQPresenter(parent=None)
    #w.show()
    #app.exec_()

#------------------------------

