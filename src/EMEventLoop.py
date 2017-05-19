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

from time import time

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
        self.lst_src1  = cp.det1_src_list
        self.lst_src2  = cp.det2_src_list
        self.pars_det1 = cp.det1_list_of_pars
        self.pars_det2 = cp.det2_list_of_pars

        self.nevbuf = 100 

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
        t0_sec = time()
        #while self._event_loop_is_on :
        while cp.flag_do_event_loop :
            evt = self.es.event_next()
            evnum = self.es.current_event_number()
            if not evnum%self.nevbuf : 
                print '%s.%s - evnum %d   dt(sec/evt) = %.6f'%\
                      (self._name, sys._getframe().f_code.co_name, evnum, (time()-t0_sec)/self.nevbuf)
                t0_sec = time()

            if evt is None :
                print '%s.%s - evt is None, current evnum: %d'%\
                      (self._name, sys._getframe().f_code.co_name, evnum)
                self.stop_event_loop()
                break

#------------------------------

    def __del__(self) :
        print 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        
#------------------------------
#------------------------------
#------------------------------
