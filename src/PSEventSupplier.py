#------------------------------
"""
@version $Id: PSEventSupplier.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin

Usage ::
    from expmon.Logger import log
    from expmon.EMConfigParameters import cp
    from expmon.PSEventSupplier import PSEventSupplier

    es = PSEventSupplier(cp, log, 'exp=xpptut15:run=54:idx')
    es.set_dataset('exp=cxif5315:run=169:idx')

    evt = es.event_for_num(num) # psana.Event - for idx mode
    evt = es.event_next()       # psana.Event - for non-idx mode

    nev = es.number_of_events()
    env = es.env() # psana.Environment
    run = es.run() # psana.Run
"""
#------------------------------

from psana import DataSource, EventId, EventTime, setOption

#------------------------------

class PSEventSupplier :
    _name = 'PSEventSupplier'
    def __init__(self, cp, log, dsname, calib_dir=None) : #dsname='exp=xpptut15:run=54:idx'
        log.debug('In __init__', self._name)
        self.cp  = cp
        self.log = log
        self.is_idx_mode = False
        self._num = -1
        self.set_dataset(dsname, calib_dir)
        

    def set_dataset_idx(self, dsname, calib_dir=None) : #dsname='exp=xpptut15:run=54:idx'
        """Returns dictionary of pairs {event_number : psana.EventTime} in :idx mode
        """
        self.ds = DataSource(dsname)
        self._run = self.ds.runs().next()
        self.dic_evtimes = dict(enumerate(self._run.times()))


    def event_time(self, evt) : # psana.Event object
        """Returns psana.EventTime object for input psana.Event
        """
        evtId = evt.get(EventId)
        (sec, nsec), fid = evtId.time(), evtId.fiducials()
        return EventTime(int((sec<<32)|nsec), fid)


    def dict_event_time(self, nev_begin=0, nev_end=1000) :
        """Makes dictionary of pairs {event_number : psana.EventTime} FOR NON :idx mode!
        """
        self.dic_evtimes = {}
        for nev,evt in enumerate(self.ds.events()):
            if nev<nev_begin : continue
            if nev>nev_end : break
            self.dic_evtimes[nev] = event_time(self, evt)


    def set_dataset(self, dsname, calib_dir) : #dsname='exp=xpptut15:run=54:idx'
        """Sets dataset for direct access idx and regular even mode
        """
        if calib_dir is not None : setOption('psana.calib-dir', calib_dir)

        ext = self.cp.dsextension.value()
        if 'idx' in dsname :
            self.set_dataset_idx(dsname, calib_dir)
            self.is_idx_mode = True
            return

        self.ds = DataSource(dsname)
        self._run = self.ds.runs().next()
        self.events = self.ds.events() # for event_next() method


    def is_direct_access(self) :
        """Returns True for idx - index direct access mode, False othervise
        """
        return self.is_idx_mode


    def event_next(self) :
        """Returns next psana.Event object
        """
        if self.is_idx_mode :
            n = self._num+1
            return self.event_for_number(n)
        else :
            self._num += 1
            return self.events.next()


    def current_event_number(self) :
        return self._num


    def event_for_number(self, n=None) :
        """Returns psana.Event object for input event number n
        """
        if n is None :
            return self.event_next()

        elif self.is_idx_mode :
            et = self.dic_evtimes[n]
            self._num = n
            return self._run.event(et)
        else :
            self.log.warning('dataset is in non-idx mode: NEXT event is returned.', self._name)
            return self.event_next()


    def number_of_events(self) :
        """Returns number of events in current dataset
        """
        return len(self.dic_evtimes) if self.is_idx_mode else 1


    def dataset(self) :
        """Returns current psana.DataSource object
        """
        return self.ds


    def run(self) :
        """Returns current psana.Run object
        """
        return self._run


    def env(self) :
        """Returns current psana.Env object
        """
        return self.ds.env()

#------------------------------

def test_all() :

    from expmon.Logger import log
    from expmon.EMConfigParameters import cp
    from time import time
    log.setPrintBits(0377)

    es = PSEventSupplier(cp, log, 'exp=cxif5315:run=169:idx')
    #es = PSEventSupplier(cp, log, 'exp=xpptut15:run=54:idx')
    #es = PSEventSupplier(cp, log, 'exp=xpptut15:run=54')


    print 'Sequential mode:'
    for n in range(10) :
        et = es.event_time(es.event_next())
        print '%4d fid:%d' % (es.current_event_number(), et.fiducial())

    #t0_sec = time()
    #es.set_dataset('exp=cxif5315:run=169:idx')
    #print 'set_dataset consumed time(sec) = %.6f' % (time()-t0_sec)


    print 'idx mode:'
    print '   5 fid:%d' % es.event_time(es.event_for_number(5)).fiducial() 
    print '   0 fid:%d' % es.event_time(es.event_for_number(0)).fiducial() 
    print 'number_of_events:', es.number_of_events()

#------------------------------

if __name__ == "__main__" :
    test_all()

#------------------------------
