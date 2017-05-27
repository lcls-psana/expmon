#------------------------------
"""
EMQEventLoop
Created: 2017-05-17
Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQEventLoop import EMQEventLoop
    el = EMQEventLoop()
"""
#------------------------------

import sys
from PyQt4 import QtCore#, QtGui

from time import time, sleep
from expmon.EMConfigParameters import cp
#from expmon.Logger             import log
from expmon.PSNameManager import nm
from expmon.PSEventSupplier import PSEventSupplier

#------------------------------

class EMQEventLoop(QtCore.QObject) :
    """Uses configuration parameters to get image
    """
    def __init__(self, parent=None) :
        QtCore.QObject.__init__(self, parent)
        self._name = self.__class__.__name__
        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)
        self.dsname = None
        self.init_event_loop()
        #self.start_event_loop()
        #self.connect_events_collected_to(self.test_events_collected)

        cp.emqeventloop = self

#------------------------------

    def init_event_loop(self) :
        dsname = nm.dsname()
        #print 'XXX %s.init_event_loop dsname = %s' % (self._name, dsname)
        if dsname == self.dsname : return
        self.dsname = dsname
        self.number_of_tabs = cp.number_of_tabs
        self.number_of_det_pars = cp.number_of_det_pars

        self.nevents_update = cp.nevents_update.value()

        self.lst_src1  = cp.det1_src_list
        self.lst_src2  = cp.det2_src_list
        self.pars_det1 = cp.det1_list_of_pars
        self.pars_det2 = cp.det2_list_of_pars

        cp.flag_nevents_collected = False
        #self.counter_update = 0

        #self.par_winx  = det_list_of_pars[0][tabind]
        #self.par_winy  = det_list_of_pars[1][tabind]

        self.es = PSEventSupplier(cp, log=None, dsname=self.dsname, calib_dir=None)

        self.print_pars()

#------------------------------

    def print_pars(self) :
        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)

        print 'dsname: %s' % self.dsname
        print 'number_of_tabs: %d' % self.number_of_tabs
        print 'number_of_det_pars: %d' % self.number_of_det_pars

        for it in range(cp.number_of_tabs) :
            p_src1 = self.lst_src1[it]
            p_src2 = self.lst_src2[it]
            print 'tab:%d  src1: %s  src2: %s' % (it, p_src1.value().ljust(32), p_src2.value().ljust(32))

        return

        for it in range(cp.number_of_tabs) :
            for ip in range(cp.number_of_det_pars) :
                p = self.pars_det1[ip][it]
                print '%30s  %s' % (p.name(), str(p.value()))

#------------------------------

    def start_event_loop(self) :
        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)
        self.init_event_loop() 

        if self.dsname is None : 
            print 'WARNING %s.start_event_loop dataset name "%s" IS NOT DEFINED' % (self._name, self.dsname)
            #cp.guimain.emqdatacontrol.event_control().on_but_ctl()
            self.stop_event_loop()
            return

        self.event_loop()

#------------------------------

    def stop_event_loop(self) :
        cp.flag_do_event_loop = False
        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)

#------------------------------

    def event_loop(self) :
        self.t0_sec = time()

        count_evt_none = 0
        while cp.flag_do_event_loop :
            #self.evt   = self.es.event_next()
            #self.evnum = self.es.current_event_number()
            self.evt, self.evnum = self.es.event_next_and_number()

            #print 'XXX %s.%s evnum: %d' % (self._name, sys._getframe().f_code.co_name, self.evnum)

            if self.evt is None :
                print '%s.%s - evt is None, current evnum: %d'%\
                      (self._name, sys._getframe().f_code.co_name, self.evnum)
                count_evt_none +=1 
                if count_evt_none > 10 : 
                    self.stop_event_loop()
                    break
                else : continue

            count_evt_none = 0
            self.proc_event()

            if self.evnum>1 and (not self.evnum % self.nevents_update) :
                cp.flag_nevents_collected = True
                self.emit(QtCore.SIGNAL('events_collected()'))

#------------------------------

    def connect_events_collected_to(self, slot) :
        #print '%s.connect_events_collected_to'%(self._name)
        self.connect(self, QtCore.SIGNAL('events_collected()'), slot)

#------------------------------

    def disconnect_events_collected_from(self, slot) :
        #print '%s.disconnect_events_collected_from'%(self._name)
        self.disconnect(self, QtCore.SIGNAL('events_collected()'), slot)

#------------------------------

    def test_events_collected(self) :
        msg = '%s.%s - evnum %d   dt(sec/evt) = %.6f'%\
              (self._name, sys._getframe().f_code.co_name, self.evnum, (time()-self.t0_sec)/self.nevents_update)
        print msg
        self.t0_sec = time()

#------------------------------
#------------------------------

    def proc_event(self) :
        evt, evnum = self.evt, self.evnum
        rec = [cp.exp_name.value(), evt.run(), evnum]

        for i, mon in enumerate(cp.monitors) :
            rec += [i, mon.det1().signal(evt), mon.det2().signal(evt)] if mon.is_active() else\
                   [None, None, None]

        cp.dataringbuffer.save_record(rec)

#------------------------------

    def __del__(self) :
        print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        #log.debug('%s'%sys._getframe().f_code.co_name, self._name)

#------------------------------

    def __del__(self) :
        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)

#------------------------------
#------------------------------
#------------------------------
