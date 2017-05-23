#------------------------------
"""
EMEventLoop
Created: 2017-05-17
Author : Mikhail Dubrovin

Usage ::
    from expmon.EMEventLoop import EMEventLoop
    el = EMEventLoop()
"""
#------------------------------

import sys

from time import time, sleep
from expmon.EMConfigParameters import cp
from expmon.PSNameManager import nm
from expmon.PSEventSupplier import PSEventSupplier

#------------------------------

class EMEventLoop :
    """Uses configuration parameters to get image
    """
    def __init__(self) :
        self._name = self.__class__.__name__
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        self.init_event_loop()
        #self.start_event_loop()

#------------------------------

    def init_event_loop(self) :
        self.dsname = nm.dsname()
        self.number_of_tabs = cp.number_of_tabs
        self.number_of_det_pars = cp.number_of_det_pars

        self.nevents_update = cp.nevents_update.value()

        self.lst_src1  = cp.det1_src_list
        self.lst_src2  = cp.det2_src_list
        self.pars_det1 = cp.det1_list_of_pars
        self.pars_det2 = cp.det2_list_of_pars

        cp.flag_nevents_collected = False

        #self.par_winx  = det_list_of_pars[0][tabind]
        #self.par_winy  = det_list_of_pars[1][tabind]

        self.es = PSEventSupplier(cp, log=None, dsname=self.dsname, calib_dir=None)

        self.print_pars()

#------------------------------

    def print_pars(self) :
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)

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
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        self.event_loop()

#------------------------------

    def stop_event_loop(self) :
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)

#------------------------------

    def event_loop(self) :
        while cp.flag_do_event_loop :
            t0_sec = time()
            #self.evt   = self.es.event_next()
            #self.evnum = self.es.current_event_number()
            self.evt, self.evnum = self.es.event_next_and_number()

            #print 'XXX %s.event_loop evnum: %d' % (self._name, self.evnum)

            if self.evt is None :
                print '%s.%s - evt is None, current evnum: %d'%\
                      (self._name, sys._getframe().f_code.co_name, self.evnum)
                self.stop_event_loop()
                break

            self.proc_event()

            if not self.evnum % self.nevents_update :
                print '%s.%s - evnum %d   dt(sec/evt) = %.6f'%\
                      (self._name, sys._getframe().f_code.co_name, self.evnum, (time()-t0_sec)/self.nevents_update)

                cp.flag_nevents_collected = True
                print 100*'_', 'flag is set'

#------------------------------

    def proc_event(self) :
        evt, evnum = self.evt, self.evnum
        #print 'In %s.%s  evnum=%d' % (self._name, sys._getframe().f_code.co_name, evnum)

        #if False :
        #  for it in range(cp.number_of_tabs) :
        #    p_src1 = self.lst_src1[it]
        #    p_src2 = self.lst_src2[it]
        #    print 'tab:%d  src1: %s  src2: %s' % (it, p_src1.value().ljust(32), p_src2.value().ljust(32))

        # define data record as a triplet of values
        rec = [[None, None, None],] * self.number_of_tabs

        #print 'XXX %s.proc_event evnum: %d'% (self._name, self.evnum)
        #print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)

        for i, mon in enumerate(cp.monitors) :
            mon_is_active = mon.is_active()
            if not mon_is_active : continue

            #print 'XXX %s.proc_event is_active mon: %d' % (self._name, i)

            #signals = [det.signal(evt) for det in mon.detectors()]
            signal1, signal2 = mon.det1().signal(evt), mon.det2().signal(evt)

            msg = '%s  src1: %s  src2: %s  signals: %s %s'%\
                  (cp.tab_names[i], mon.det1().src().ljust(32), mon.det2().src().ljust(32), signal1, signal2)
            print msg

            rec[i] = [i, signal1, signal2] 

        cp.dataringbuffer.save_record(rec)

#------------------------------

    def __del__(self) :
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)

#------------------------------
#------------------------------
#------------------------------
