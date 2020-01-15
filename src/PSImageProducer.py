#------------------------------
"""
Class :py:class:`PSImageProducer' - supplies image for dataset
==============================================================

Usage ::
    from expmon.PSImageProducer import PSImageProducer
    from graphqt.Logger import log
    from graphqt.IVConfigParameters import cp
    log.setPrintBits(0377)
    ip = PSImageProducer(cp, log)
    evt = ip.es.event_next()
    evt = ip.event_for_number(123)
    env = ip.env()
    run = ip.run()
    det = ip.detector()
    ip.det().print_attributes()    
    for n in range(5) :
        #evt = ip.event_for_number(n)
        #nda = ip.det().raw(evt)
        #img = ip.image(n, nda)
        img = ip.image(n)
        print_ndarr(img, name='img %d' % n, first=0, last=10)

See:
    - :class:`PSConfigParameters`
    - :class:`PSDataSupplier`
    - :class:`PSEventSupplier`
    - :class:`PSImageProducer`
    - :class:`PSNameManager`
    - :class:`PSQThreadWorker`
    - :class:`PSUtils`
    - `go to top<https://lcls-psana.github.io/graphqt/py-modindex.html>`_.

Author: Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------

import numpy as np
from expmon.PSNameManager import nm
from expmon.PSEventSupplier import PSEventSupplier
from Detector.AreaDetector import AreaDetector

#------------------------------

class PSImageProducer(object) :
    """Uses configuration parameters to get image
    """
    _name = 'PSImageProducer'

    def __init__(self, cp, log) :
        log.debug('In __init__', self._name)
        self.cp  = cp
        self.log = log
        self.es = None

        self.set_dataset()
        self.set_detector()


    def set_dataset(self, dsname=None) :
        self.dsname = nm.dsname() if dsname is None else dsname
        self.log.info('set_dataset %s' % self.dsname, self._name)

        self.calib_dir = nm.dir_calib()
        self.log.info('dir_calib %s' % self.calib_dir, self._name)

        if self.es is None : self.es = PSEventSupplier(self.dsname, self.calib_dir) 
        else :               self.es.set_dataset(self.dsname)


    def set_detector(self, detname=None) :
        self.detname = self.cp.data_source.value() if detname is None else detname
        self.log.info('set_detector %s' % self.detname, self._name)
        self.det = AreaDetector(self.detname, self.es.env(), pbits=0)        


    def image(self, evnum=None, nda=None) :
        evt = self.es.event_for_number(evnum)
        _nda = nda
        if nda is None :
            raw = self.det.raw(evt)
            if raw is not None :
                _nda = np.array(raw, dtype=np.float32)
                #t0_sec = time()
                peds = self.det.pedestals(evt)
                #print 'det.pedestals time(sec) = %.6f' % (time()-t0_sec)
                if peds is not None : _nda -= peds
                #print_ndarr(raw,  'XXX raw ', first=0, last=5)
                #print_ndarr(peds, 'XXX peds', first=0, last=5)
                #print_ndarr(_nda, 'XXX _nda', first=0, last=5)
        return self.det.image(evt, _nda)


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
    ip = PSImageProducer(cp, log)
    print('PSImageProducer initialization time(sec) = %.6f' % (time()-t0_sec))

    #evt = ip.event_next()
    #ip.detector().print_attributes()

    print('run number:', ip.run().run())
    print('calib dir :', ip.env().calibDir())
    print('number_of_events :', ip.number_of_events())

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
