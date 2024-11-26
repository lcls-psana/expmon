
#------------------------------
"""EMQPresenter shows/updates resulting plots.
   Created: 2017-05-23
   Author : Mikhail Dubrovin
"""
from __future__ import print_function
from __future__ import division
#------------------------------
import sys
#import os
from time import time, sleep
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
#from graphqt.GUViewGraph import GUViewGraph
#from expmon.EMQViewGraph import EMQViewGraph
from expmon.EMQGraphic import EMQGraphic
from expmon.EMQHistogram import EMQHistogram, image_to_hist_arr
from expmon.EMQUtils import point_relative_window

from graphqt.Styles    import style
from expmon.EMConfigParameters import cp
from expmon.Logger             import log

#------------------------------

from scipy.stats import pearsonr
from scipy.optimize import curve_fit
from scipy.stats import chi2
from pyimgalgos.GlobalUtils import print_ndarr

from expmon.least_squares_fit import *

#------------------------------

def funcy(x, p0, p1) :
    """Function for parameterization of y(x, p1, p2)
       ATTENTION!: curve_fit assumes that x and returned y are numpy arrays.
    """
    return p0 + p1*x

#------------------------------

def color_for_imon(imon):
    return (Qt.cyan, Qt.blue, Qt.green, Qt.yellow, Qt.red, Qt.black)[imon%5]

#------------------------------

class EMQPresenter(QtCore.QObject) :
    """
    """
    def __init__(self, parent=None, do_self_update=False) :

        QtCore.QObject.__init__(self, parent)
        self._name = self.__class__.__name__
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('in %s'%sys._getframe().f_code.co_name, self._name)

        self.dt_msec = 100
        self.count_time_checks = 0
        self.count_updates = 0
        self.edi_fld = None
        self.t0_sec = None
        self.do_self_update = do_self_update

        self.nmonitors = cp.number_of_tabs
        self.wscatter = [None] * self.nmonitors
        self.whsig1   = [None] * self.nmonitors
        self.whsig2   = [None] * self.nmonitors
        self.whistogr = [None] * self.nmonitors
        self.wpearson = [None] * self.nmonitors # [None, None, None, ...]

        self.timer = None


        # SELECT ONE OF TWO UPDATE MODES:
        if do_self_update : self.start_check_on_timout()
        else : cp.emqeventloop.connect_events_collected_to(self.on_events_collected)

        msg = 'start presenter in %s mode' %\
              ('SELF-TIMER-UPDATING' if do_self_update else 'SIGNAL-CATCHING')
        log.info('%s %s' % (sys._getframe().f_code.co_name, msg), self._name)

#------------------------------
# Asynch. self triggering updates using timer loop

    def start_check_on_timout(self) :
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(self.dt_msec)


    def on_timeout(self) :
        """Slot for signal on_timeout
        """
        self.count_time_checks += 1
        #print 'XXX: %s.%s' % (self._name, sys._getframe().f_code.co_name)
        if  cp.flag_nevents_collected : 
            cp.flag_nevents_collected = False
            self.update_presenter()

#------------------------------

        #cp.emqeventloop.connect_events_collected_to(cp.emqpresenter.on_events_collected)
    def on_events_collected(self) :
        """Slot for signal events_collected
        """
        #log.info('XXX: %s' % sys._getframe().f_code.co_name, self._name)
        self.update_presenter()
        #sleep(3) DO NOT WORK ???

#------------------------------

#    def event(self, e) :
#        print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
#        print 'XXX event', str(e)

 
    def __del__(self) :
        #print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        log.debug('%s'%sys._getframe().f_code.co_name, self._name)
        if self.edi_fld is not None : self.edi_fld.close()

        if self.timer is not None : self.timer.stop()

        for i in range(self.nmonitors) :
            if self.wscatter[i] is not None : self.wscatter[i].close()
            if self.whistogr[i] is not None : self.whistogr[i].close()
            if self.whsig1[i]   is not None : self.whsig1[i].close()
            if self.whsig2[i]   is not None : self.whsig2[i].close()
            if self.wpearson[i] is not None : self.wpearson[i].close()

        #self.deleteLater()

#------------------------------

    def records_parser(self, recs) :
        """Decomposes list of records like 
           ['sxro5916', 24, 1200, 0, 586742.0, 15.305053710937486, 
             1, 48072616331.357925, -3.9454345703125, 2, 1.6427001953125, 1.59228515625, 
             None, None, None]
           Returns list of parameters:
           nrecs (int) number of records in the list recs,
           exp (str) experiment name, e.g. 'sxro5916', 
           run (int) - run number, 
           evnums (list(int)) - list of event numbers in recs
           mon_sig1, mon_sig2 - lists of signal1 and 2 for all monitors
                                access to particular monitor signals is through index,
                                e.g. mon_sig1[imon]
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

        #print 'XXX: EMQPresenter.update_presenter'

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

        #print 'XXX: EMQPresenter.update_presenter A'

        for i, mon in enumerate(cp.monitors) :
            if not mon.is_active() : continue
            self.update_scatter(i, np.array(mon_sig1[i]), np.array(mon_sig2[i]))
            self.update_histogr(i)
            self.update_pearson(i)

        #print 'XXX: EMQPresenter.update_presenter B'

#------------------------------

    def fit_scatter(self, imon, sig1, sig2) :

        xn = sig1.astype(dtype=np.double)
        yn = sig2.astype(dtype=np.double)        
        #en = np.ones_like(yn) * yn.std()
        en = np.ones_like(xn)

        try :
            self.pearsr, self.pearsv = pearsonr(xn, yn)
            #print 'Pearson r=%.6f  pval=%.6f' % (self.pearsr, self.pearsv)
        except :
            log.warning('Pearsonr failed...', self._name)

        a, b, cx0, cx1, cx2, cxy, cy1 = least_squares_fit(xn,yn,1)
        #print 'least_squares_fit: b, a =', b, a

        #p0 = [yn.mean(), 0]
        p0 = [b, a]

        try :
            popt, pcov = curve_fit(funcy, xn, yn, p0, en, absolute_sigma=False)

            llst = [v==np.inf for v in np.array(pcov).flatten()]
            if any(llst) :
                #print 'At least one of values in pcov is inf'
                msg = '%s: fit returns inf in pcov: %s' % (cp.tab_names[imon], str(pcov))
                log.warning(msg, self._name)
                return None, None

            perr = np.sqrt(np.diag(pcov))
            msg = '%s: fit results popt: %s  error on pars: %s' % (cp.tab_names[imon], str(popt), str(perr))
            log.debug(msg, self._name)
            
            #chi2 = np.sum(((funcy(xn, *popt) - yn) / en)**2)
            #ndof = len(xn) - 1
            #prob = chi2.sf(chi2, ndof, loc=0, scale=1)
            #print 'Fit: chi2=%.2f  ndof=%d  prob=%.6f' % (chi2, ndof, prob)

            return popt, perr

        except :
            log.warning('Fit failed...', self._name)
            return None, None


#------------------------------

    def update_scatter(self, imon, sig1, sig2, iplot=0):
        #print 'XXX In %s.%s imon: %s' % (self._name, sys._getframe().f_code.co_name, cp.tab_names[imon])
        w = self.wscatter[imon]
        self.resid = None 
        if w is None :
            if sig1 is None or sig2 is None : return
            xmin, xmax = sig1.min(), sig1.max()
            ymin, ymax = sig2.min(), sig2.max()
            if xmin is None or xmax is None or ymin is None or ymax is None : return
            rectax=QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

            w = self.wscatter[imon] = EMQGraphic(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                                 margl=0.12, margr=0.01, margt=0.01, margb=0.06, imon=imon)
            #w = self.wscatter[imon] = GUViewGraph(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
            #                                      margl=0.12, margr=0.01, margt=0.01, margb=0.06)
            #w.connect_view_is_closed_to(self.on_scatter_close)
            w.graph.connect_view_is_closed_for_imon_to(self.on_scatter_close)
            self.set_window_geometry(imon, iplot)

            self.draw_scatter(imon, sig1, sig2)
            w.show()
        else :
            self.draw_scatter(imon, sig1, sig2)
            w.raise_()

#------------------------------

    def on_scatter_close(self, imon, iplot=0): 
        msg = '%s imon=%d' % (sys._getframe().f_code.co_name, imon)
        log.debug(msg, self._name)
        self.wscatter[imon].graph.disconnect_view_is_closed_for_imon_from(self.on_scatter_close)
        self.save_window_geometry(imon, iplot)
        self.wscatter[imon] = None

#------------------------------

    def on_histogr_close(self, imon, iplot=1):
        msg = '%s imon=%d' % (sys._getframe().f_code.co_name, imon)
        log.debug(msg, self._name)
        self.whistogr[imon].hist.disconnect_view_is_closed_for_imon_from(self.on_histogr_close)
        self.save_window_geometry(imon, iplot)
        self.whistogr[imon] = None

#------------------------------

    def on_pearson_close(self, imon, iplot=2):
        msg = '%s imon=%d' % (sys._getframe().f_code.co_name, imon)
        log.debug(msg, self._name)
        self.wpearson[imon].graph.disconnect_view_is_closed_for_imon_from(self.on_pearson_close)
        self.save_window_geometry(imon, iplot)
        self.wpearson[imon] = None

#------------------------------
#------------------------------

    def win_pars(self, imon, iplot) :
        """ imon (int) index of monotor or tab
            iplot = 0,1,2,... for scatter, histogram, pearson, etc. respectively 
        """
        if iplot<0 or iplot>=cp.number_of_mon_winds : return
        win = (self.wscatter[imon],\
               self.whistogr[imon],\
               self.wpearson[imon])[iplot]

        iplot0 = iplot*4
        par_winx = cp.mon_win_pars[iplot0+0][imon]
        par_winy = cp.mon_win_pars[iplot0+1][imon]
        par_winh = cp.mon_win_pars[iplot0+2][imon]
        par_winw = cp.mon_win_pars[iplot0+3][imon]

        return win, par_winx, par_winy, par_winh, par_winw

#------------------------------

    def save_window_geometry(self, imon, iplot) : 
        win, par_winx, par_winy, par_winh, par_winw = self.win_pars(imon, iplot)

        point, size = win.mapToGlobal(QtCore.QPoint(0,0)), win.size() # Offset (-5,-22) for frame size.
        x,y,w,h = point.x(), point.y(), size.width(), size.height()
        msg = 'Save window parameters x,y,w,h : %4d, %4d, %4d, %4d' % (x,y,w,h)
        log.info(msg, self._name)

        par_winx.setValue(x)
        par_winy.setValue(y)
        par_winw.setValue(w)
        par_winh.setValue(h)

#------------------------------

    def set_window_geometry(self, imon, iplot) :

        win, par_winx, par_winy, par_winh, par_winw = self.win_pars(imon, iplot)

        dx, dy = imon*50, iplot*50
        point = point_relative_window(cp.guimain, QtCore.QPoint(dx, dy))
        win.move(point)

        if par_winx.value() is None : return
        if par_winx.is_default() : return

        win.setGeometry(par_winx.value(),\
                        par_winy.value(),\
                        par_winw.value(),\
                        par_winh.value())

#-------------------------------

    def draw_scatter(self, imon, sig1, sig2):
        w = self.wscatter[imon]
        if w is None : return
        w.graph.remove_all_graphs()
        color = color_for_imon(imon)
        #w.graph.add_graph(sig1, sig2, QtGui.QPen(color), brush=QtGui.QBrush())
        w.graph.add_points(sig1, sig2, QtGui.QPen(color), brush=QtGui.QBrush(color), fsize=0.0075)
        w.setWindowTitle('Scatter plot for %s' % cp.tab_names[imon])

        popt, perr = self.fit_scatter(imon, sig1, sig2) #, rectax)
        if popt is not None :
            rect = w.graph.rectax
            xarr = np.linspace(rect.left(), rect.right(), 100)
            yarr = [funcy(x, *popt) for x in xarr]
            self.draw_func(imon, xarr, yarr)
            self.resid = sig2 - funcy(sig1, *popt)

            msg = u'  p0: %3g \u00B1 %3g  \n  p1: %3g \u00B1 %3g  ' % (popt[0], perr[0], popt[1], perr[1])
            w.draw_info(msg)

            #print_ndarr(self.resid, name='resid', first=0, last=5)
            #print_ndarr(xarr, name='xarr', first=0, last=10)
            #print_ndarr(yarr, name='yarr', first=0, last=10)

#------------------------------

    def draw_func(self, imon, x, y):
        w = self.wscatter[imon]
        if w is None : return
        color = (Qt.cyan, Qt.blue, Qt.green, Qt.yellow, Qt.red, Qt.black)[imon%5]
        w.graph.add_graph(x, y, QtGui.QPen(color), brush=QtGui.QBrush())

#-------------------------------

    def draw_histogr(self, imon):
        w = self.whistogr[imon]
        if w is None : return
        w.hist.remove_all_graphs()
        color = color_for_imon(imon)

        arr = self.resid
        amin, amax, nhbins, values = image_to_hist_arr(arr, vmin=None, vmax=None, nbins=100)
        w.hist.add_hist(values, (amin, amax), pen=QtGui.QPen(Qt.yellow, 0), brush=QtGui.QBrush(Qt.yellow))

        #w.add_array_as_hist(self.resid, pen=QtGui.QPen(color, 0), brush=QtGui.QBrush(color), vtype=np.float32)
        w.setWindowTitle('Residuals for %s' % cp.tab_names[imon])

#------------------------------

    def update_histogr(self, imon, iplot=1):
        #print 'XXX In %s.%s imon: %s' % (self._name, sys._getframe().f_code.co_name, cp.tab_names[imon])
        if self.resid is None : return 

        #print_ndarr(self.resid, name='XXX: resid', first=0, last=5)

        w = self.whistogr[imon]
        if w is None :
            xmin, xmax = self.resid.min(), self.resid.max()
            ymin, ymax = 0, 10
            rectax=QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

            w = self.whistogr[imon] = EMQHistogram(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                                   margl=0.12, margr=0.01, margt=0.01, margb=0.06, imon=imon)

            w.hist.connect_view_is_closed_for_imon_to(self.on_histogr_close)
            self.set_window_geometry(imon, iplot)

            self.draw_histogr(imon)
            w.show()
        else :
            self.draw_histogr(imon)
            w.raise_()

#------------------------------

    def update_pearson(self, imon, iplot=2):
        #print 'XXX In %s.%s imon: %s' % (self._name, sys._getframe().f_code.co_name, cp.tab_names[imon])
        w = self.wpearson[imon]
        if w is None :
            self.dxmove = 20
            xmin, xmax = -0.5, 50.5
            ymin, ymax = -1.05, 1.05
            self.xpoint = -1
            rectax=QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

            w = self.wpearson[imon] = EMQGraphic(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                                                 margl=0.12, margr=0.01, margt=0.01, margb=0.06, imon=imon)

            w.graph.connect_view_is_closed_for_imon_to(self.on_pearson_close)
            #w.move(self.pos() + QtCore.QPoint(self.width()+80, 0))
            self.set_window_geometry(imon, iplot)

            self.draw_pearson(imon)
            w.show()
        else :

            # drug window for pearson by self.dxmove if necessary
            wg = w.graph
            rax = wg.rect_axes()
            #x, y, width, height = rax.getRect()
            #if self.xpoint >= x+width :

            if self.xpoint >= (rax.right() - 0.05*rax.width()) :
                #sc = wg.scene()
                #rs = sc.sceneRect()
                #rs.moveCenter(rs.center() + QtCore.QPointF(self.dxmove,0))
                #sc.setSceneRect(rs)
                #wg.update_my_scene()
                wg.move_scene(QtCore.QPointF(self.dxmove,0))

            self.draw_pearson(imon)
            w.raise_()

#------------------------------

    def draw_pearson(self, imon):
        w = self.wpearson[imon]
        if w is None : return
        #w.graph.remove_all_graphs()
        color = color_for_imon(imon)

        if self.pearsr is None : return

        self.xpoint += 1
        xarr = (self.xpoint,)
        yarr = np.require((self.pearsr,), dtype=np.float32)

        #npts = 50
        #xarr = range(npts)
        #yarr = np.require(0.2*np.random.standard_normal((npts,)), dtype=np.float32)

        #w.graph.add_graph(xarr, yarr, QtGui.QPen(color), brush=QtGui.QBrush())
        w.graph.add_points(xarr, yarr, QtGui.QPen(color), brush=QtGui.QBrush(color), fsize=0.0075)
        w.setWindowTitle('Pearson vs time plot for %s' % cp.tab_names[imon])

        msg = 'Pearson last\n  r=%.6f\n  v=%.6f' % (self.pearsr, self.pearsv)
        w.draw_info(msg)

#------------------------------
#------------------------------
#------------------------------
#------------------------------

    def print_signals(self, evnums, mon_sig1, mon_sig2) :
        #=========
        if True :
            for i, mon in enumerate(cp.monitors) :
                print('Records for mon %d  %s' % (i, cp.tab_names[i]))
                if not mon.is_active() : 
                    print('NON-ACTIVE')
                    continue

                for evnum, s1, s2 in zip(evnums, mon_sig1[i], mon_sig2[i]) :
                    print(evnum, s1, s2)

        #=========
        if False : # True :
            for i in range(self.nmonitors) :
                print('Records for mon %d:' % i)
                if mon_sig1[i] is None : 
                    print('NON-ACTIVE')
                    continue

                for evnum, s1, s2 in zip(evnums, mon_sig1[i], mon_sig2[i]) :
                    print(evnum, s1, s2)

#------------------------------

    def update_info_window(self) :

        if self.edi_fld is None :
            self.counter = 0
            e = self.edi_fld = QtWidgets.QTextEdit(self._name)
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

