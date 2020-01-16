#------------------------------
"""
EMQEventLoop
Created: 2017-05-17
Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQEventLoop import EMQEventLoop
    el = EMQEventLoop()
"""
from __future__ import print_function
from __future__ import division
#------------------------------

import sys
from PyQt5 import QtCore#

from time import time, sleep
from expmon.EMConfigParameters import cp
#from expmon.Logger             import log
from expmon.PSNameManager import nm
from expmon.PSEventSupplier import pseventsupplier # use singleton PSEventSupplier

#------------------------------

class EMQEventLoop(QtCore.QObject) :
    """Uses configuration parameters to get image
    """
    events_collected = QtCore.pyqtSignal()

    def __init__(self, parent=None) :
        QtCore.QObject.__init__(self, parent)
        self._name = self.__class__.__name__
        if cp.popts.verbos : print('%s.%s' % (self._name, sys._getframe().f_code.co_name))
        self.dsname = None
        self.init_event_loop()
        #self.start_event_loop()
        #self.connect_events_collected_to(self.test_events_collected)

        cp.emqeventloop = self

#------------------------------

    def init_event_loop(self) :

        self.nevents_update = cp.nevents_update.value()

        dsname = nm.dsname()
        #print 'XXX %s.init_event_loop dsname = %s' % (self._name, dsname)
        if dsname == self.dsname : return
        self.dsname = dsname
        self.number_of_tabs = cp.number_of_tabs
        self.number_of_det_pars = cp.number_of_det_pars

        self.lst_src1  = cp.det1_src_list
        self.lst_src2  = cp.det2_src_list
        self.pars_det1 = cp.det1_list_of_pars
        self.pars_det2 = cp.det2_list_of_pars

        cp.flag_nevents_collected = False
        #self.counter_update = 0

        #self.par_winx  = det_list_of_pars[0][tabind]
        #self.par_winy  = det_list_of_pars[1][tabind]

        self.es = pseventsupplier
        #          PSEventSupplier(cp, log=None, dsname=self.dsname, calib_dir=None)\
        #          if cp.pseventsupplier is None else cp.pseventsupplier

        self.es.set_dataset(self.dsname, calib_dir=None) # in case if it was different in cp.pseventsupplier

        #self.print_pars()

#------------------------------

    def print_pars(self) :
        print('%s.%s' % (self._name, sys._getframe().f_code.co_name))
        print('dsname: %s' % self.dsname)
        print('number_of_tabs: %d' % self.number_of_tabs)
        print('number_of_det_pars: %d' % self.number_of_det_pars)

        for it in range(cp.number_of_tabs) :
            p_src1 = self.lst_src1[it]
            p_src2 = self.lst_src2[it]
            print('tab:%d  src1: %s  src2: %s' % (it, p_src1.value().ljust(32), p_src2.value().ljust(32)))
        return

        for it in range(cp.number_of_tabs) :
            for ip in range(cp.number_of_det_pars) :
                p = self.pars_det1[ip][it]
                print('%30s  %s' % (p.name(), str(p.value())))

#------------------------------

    def start_event_loop(self) :
        if cp.popts.verbos : print('%s.%s' % (self._name, sys._getframe().f_code.co_name))
        self.init_event_loop() 

        self.evcntr = 0

        if self.dsname is None : 
            print('WARNING %s.start_event_loop dataset name "%s" IS NOT DEFINED' % (self._name, self.dsname))
            #cp.guimain.emqdatacontrol.event_control().on_but_ctl()
            self.stop_event_loop()
            return

        self.event_loop()

#------------------------------

    def stop_event_loop(self) :
        if cp.popts.verbos : print('%s.%s' % (self._name, sys._getframe().f_code.co_name))
        cp.flag_do_event_loop = False

#------------------------------

    def event_loop(self) :
        self.t0_sec = time()

        count_evt_none = 0
        while cp.flag_do_event_loop :
 
            #print 'XXX EMQEventLoop.event_loop A'

            #self.evt   = self.es.event_next()
            #self.evnum = self.es.current_event_number()
            self.evt, self.evnum = self.es.event_next_and_number()

            self.evcntr += 1

            if self.evcntr < 5\
            or self.evcntr < 50 and not (self.evnum%10)\
            or not (self.evnum%100):\
                print('XXX: %s.%s evnum: %d' % (self._name, sys._getframe().f_code.co_name, self.evnum))

            if self.evt is None :
                print('XXX: %s.%s - evt is None, current evnum: %d'%\
                      (self._name, sys._getframe().f_code.co_name, self.evnum))
                count_evt_none +=1 
                if count_evt_none > 10 : 
                    self.stop_event_loop()
                    break
                else : continue

            count_evt_none = 0
            self.proc_event()

            if self.evnum>1 and (not self.evnum % self.nevents_update) :
                cp.flag_nevents_collected = True
                self.events_collected.emit()

            #print 'XXX EMQEventLoop.event_loop E'

#------------------------------

    def connect_events_collected_to(self, slot) :
        #print '%s.connect_events_collected_to'%(self._name)
        self.events_collected.connect(slot)

#------------------------------

    def disconnect_events_collected_from(self, slot) :
        #print '%s.disconnect_events_collected_from'%(self._name)
        self.events_collected.disconnect(slot)

#------------------------------

    def test_events_collected(self) :
        msg = '%s.%s - evnum %d   dt(sec/evt) = %.6f'%\
              (self._name, sys._getframe().f_code.co_name, self.evnum, (time()-self.t0_sec)/self.nevents_update)
        print(msg)
        self.t0_sec = time()

#------------------------------
#------------------------------

    def proc_event(self) :
        evt, evnum = self.evt, self.evnum
        rec = [cp.exp_name.value(), evt.run(), evnum]

        for i, mon in enumerate(cp.monitors) :
            
            rec += [i, mon.det1().signal(evt), mon.det2().signal(evt)] if mon.is_active() else\
                   [None, None, None]

        #print 'XXX: EMQEventLoop.proc_event ', rec
        cp.dataringbuffer.save_record(rec)
        #print 'XXX: EMQEventLoop.proc_event record saved'

#------------------------------

    def __del__(self) :
        print('%s.%s' % (self._name, sys._getframe().f_code.co_name))

#------------------------------
#------------------------------
#------------------------------
