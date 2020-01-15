#------------------------------
"""
PSDataSupplier - access to detector data
Created: 2017-02-18
Author : Mikhail Dubrovin

Usage ::
    from expmon.PSDataSupplier import PSDataSupplier
    from graphqt.Logger import log
    from graphqt.IVConfigParameters import cp

    log.setPrintBits(0377)

    dso = PSDataSupplier(cp, log, dsname=None, detname=None)

    evt = dso.es.event_next()
    evt = dso.event_for_number(123)
    env = dso.env()
    run = dso.run()
    det = dso.detector()

    dso.det().print_attributes()    

    for n in range(5) :
        #evt = dso.event_for_number(n)
        evt = dso.es.event_next()
        #nda = self.raw(evt)
        peds = self.pedestals(n)
        cmpars = self.common_mode(n)
        #img = self.image(n, nda)
        img = self.image(n)
        # or
        peds = self.pedestals(evt)
        img = self.image(evt)
        img = self.raw(evt)
        print_ndarr(img, name='img %d' % n, first=0, last=10)
"""
from __future__ import print_function
#------------------------------

from expmon.PSNameManager import nm
from expmon.PSEventSupplier import pseventsupplier # use singleton PSEventSupplier
#from Detector.AreaDetector import AreaDetector    
#from psana import Detector  
from psana import Detector, Source

#------------------------------

class PSDataSupplier(object) :
    """Uses configuration parameters to get image
    """
    _name = 'PSDataSupplier'

    def __init__(self, cp, log, dsname=None, detname=None) :
        log.debug('In __init__', self._name)
        self.cp  = cp
        self.log = log
        self.es = pseventsupplier

        self.set_dataset(dsname)
        self.set_detector(detname)


    def set_dataset(self, dsname=None) :
        self.dsname = nm.dsname() if dsname is None else dsname
        self.calib_dir = nm.dir_calib()
        self.log.debug('dataset: %s dir_calib: %s' % (self.dsname, self.calib_dir), self._name)
        #if self.es is None : 
        #    self.es = PSEventSupplier(self.cp, self.log, self.dsname, self.calib_dir)\
        #              if self.cp.pseventsupplier is None else self.cp.pseventsupplier 
        self.es.set_dataset(self.dsname, self.calib_dir)


    def set_detector(self, detname=None) :
        self.detname = self.cp.data_source.value() if detname is None else detname
        self.log.debug('detector %s' % self.detname, self._name)
        env = self.es.env()
        self.det = Detector(self.detname, env) if env is not None else None
        #self.det = AreaDetector(self.detname, self.es.env(), pbits=0)        


    def raw(self, evt) :
        if self.det is None : return None
        return self.det.raw(evt)


    def pedestals(self, evt) :
        if self.det is None : return None
        return self.det.pedestals(evt)


    def common_mode(self, evt) :
        if self.det is None : return None
        return self.det.common_mode(evt)


    def image(self, par=None, nda=None) :
        """ par psana.Event or int event number
        """
        if self.det is None : return None
        evt = self.es.event_for_number(par) if isinstance(par, int) else par
        return self.det.image(evt, nda)


    def detector(self) :
        """Returns Detector.AreaDetector object
        """        
        return self.det


    def dataset(self) :
        """Returns psana.DataSource object
        """        
        return self.es.dataset()


    def event_for_number(self, n=None) :
        """Returns psana.Event object for enent n in the dataset run, or next event for n=None 
        """        
        return self.es.event_for_number(n)


    def event_next(self) :
        """Returns psana.Event object next in the dataset.
        """        
        return self.es.event_next()


    def env(self) :
        """Returns psana.Env object
        """        
        return self.es.env()


    def run(self) :
        """Returns psana.Run object
        """        
        return self.es.run()


    def number_of_events(self) :
        return self.es.number_of_events()

#------------------------------

def test_all() :
    from pyimgalgos.GlobalUtils import print_ndarr # table_from_cspad_ndarr, reshape_to_2d
    from graphqt.Logger import log
    from graphqt.IVConfigParameters import cp
    from time import time

    log.setPrintBits(0) # 0377)

    t0_sec = time()
    ip = PSDataSupplier(cp, log)
    print('PSDataSupplier initialization time(sec) = %.6f' % (time()-t0_sec))

    #evt = ip.event_next()
    #ip.detector().print_attributes()

    print('run number:', ip.run().run())
    print('calib dir :', ip.env().calibDir())
    print('number_of_events :', ip.number_of_events())

    #======
    return
    #======

    for n in range(5) :
        evt = ip.event_for_number(n)
        #nda = ip.raw(evt)
        #img = ip.image(n, nda)
        img = ip.image(evt)
        print_ndarr(img, name='img %d' % n, first=0, last=10)

#------------------------------

if __name__ == "__main__" :
    test_all()

#------------------------------
