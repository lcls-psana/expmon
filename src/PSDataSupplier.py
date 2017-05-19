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
        #nda = dso.det().raw(evt)
        #img = dso.image(n, nda)
        img = dso.image(n)
        print_ndarr(img, name='img %d' % n, first=0, last=10)
"""
#------------------------------

from expmon.PSNameManager import nm
from expmon.PSEventSupplier import PSEventSupplier
#from Detector.AreaDetector import AreaDetector    
#from psana import Detector  
from psana import Detector, Source    

#------------------------------

class PSDataSupplier :
    """Uses configuration parameters to get image
    """
    _name = 'PSDataSupplier'

    def __init__(self, cp, log, dsname=None, detname=None) :
        log.debug('In __init__', self._name)
        self.cp  = cp
        self.log = log
        self.es = None

        self.set_dataset(dsname)
        self.set_detector(detname)


    def set_dataset(self, dsname=None) :
        self.dsname = nm.dsname() if dsname is None else dsname
        self.log.info('set_dataset %s' % self.dsname, self._name)

        self.calib_dir = nm.dir_calib()
        self.log.info('dir_calib %s' % self.calib_dir, self._name)

        if self.es is None : self.es = PSEventSupplier(self.cp, self.log, self.dsname, self.calib_dir) 
        else :               self.es.set_dataset(self.dsname)


    def set_detector(self, detname=None) :
        self.detname = self.cp.data_source.value() if detname is None else detname
        self.log.info('set_detector %s' % self.detname, self._name)
        env = self.es.env()
        self.det = Detector(self.detname, env) if env is not None else None
        #self.det = AreaDetector(self.detname, self.es.env(), pbits=0)        


    def image(self, evnum=None, nda=None) :
        evt = self.es.event_for_number(evnum)
        return self.det.image(evt, nda) if self.det is not None else None


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
    print 'PSDataSupplier initialization time(sec) = %.6f' % (time()-t0_sec)

    #evt = ip.event_next()
    #ip.detector().print_attributes()

    print 'run number:', ip.run().run()
    print 'calib dir :', ip.env().calibDir()
    print 'number_of_events :', ip.number_of_events()

    #======
    return
    #======

    for n in range(5) :
        #evt = ip.event_for_number(n)
        #nda = ip.raw(evt)
        #img = ip.image(n, nda)
        img = ip.image(n)
        print_ndarr(img, name='img %d' % n, first=0, last=10)

#------------------------------

if __name__ == "__main__" :
    test_all()

#------------------------------
