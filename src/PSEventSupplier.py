#------------------------------
"""
Class PSEventSupplier - access to events in dataset
Created: 2017-02-18
Author : Mikhail Dubrovin

Usage ::
    # as singleton
    #=============
    from expmon.PSEventSupplier import pseventsupplier
    pseventsupplier.set_dataset('exp=cxif5315:run=169:idx', calib_dir=None)

    # as object WARNING: opens DataSource for each object that myy be bad for shmem mode
    #==========

    from expmon.PSEventSupplier import PSEventSupplier
    es = PSEventSupplier(dsname='exp=xpptut15:run=54:idx', calib_dir=None)

    et = es.event_time(evt)     # returns psana.EventTime  object using EventId
    dic_et = dict_event_time(nev_begin=0, nev_end=1000) # Returns dictionary {event_number : psana.EventTime} in :idx mode

    es._set_dataset_idx(dsname, calib_dir=None) # direct call to _idx method with dsname='exp=xpptut15:run=54:idx'
    es.set_dataset('exp=cxif5315:run=169:idx', calib_dir=None)

    stat = es.is_direct_access()

    events = es.events()                # returns event iterator for non-index mode, or None
    evt = es.event_next()               # psana.Event - for non-idx mode
    evt, n = es.event_next_and_number() # psana.Event and its int number
    evt = es.event_for_num(num)         # psana.Event - for idx mode
    evn = es.current_event_number()     # int
    nev = es.number_of_events()         # int
    ds  = es.dataset()                  # psana.DataSource
    env = es.env()                      # psana.Environment
    run = es.run()                      # psana.Run
"""
from __future__ import print_function
#------------------------------

from psana import DataSource, EventId, EventTime, setOption
from expmon.PSNameManager import nm

#------------------------------

class PSEventSupplier(object) :
    _name = 'PSEventSupplier'

    def __init__(self, dsname=None, calib_dir=None) : #dsname='exp=xpptut15:run=54:idx', calib_dir='./calib'
        self.reset()
        self.set_dataset(dsname, calib_dir)
        #cp.pseventsupplier = self


    def reset(self) : 
        self.dsname = None
        self.events = None
        self._evnum = -1
        self.is_idx_mode = False
        self._run = None
        self.ds = None


    def event_time(self, evt) : # psana.Event object
        """Returns psana.EventTime object for input psana.Event
        """
        evtId = evt.get(EventId)
        (sec, nsec), fid = evtId.time(), evtId.fiducials()
        return EventTime(int((sec<<32)|nsec), fid)


    def dict_event_time(self, nev_begin=0, nev_end=1000) :
        """Makes dictionary {event_number : psana.EventTime} FOR NON :idx mode!
        """
        self.dic_evtimes = {}
        for nev,evt in enumerate(self.ds.events()):
            if nev<nev_begin : continue
            if nev>nev_end : break
            self.dic_evtimes[nev] = self.event_time(evt)


    def _set_dataset_idx(self, dsname, calib_dir=None) : #dsname='exp=xpptut15:run=54:idx'
        """Sets dictionary of pairs {event_number : psana.EventTime} in :idx mode
        """
        #print 'XXX: open DataSource in PSEventSupplier._set_dataset_idx  %s' % dsname
        self.ds = DataSource(dsname)
        self.dsname = dsname
        self._run = next(self.ds.runs())
        self.dic_evtimes = dict(enumerate(self._run.times()))


    def set_dataset(self, dsname, calib_dir=None) : #dsname='exp=xpptut15:run=54:idx'
        """Sets dataset for direct access idx and regular even mode
        """
        if dsname is None : 
            self.reset()
            return

        elif dsname == self.dsname :
            return

        
        self.calib_dir = calib_dir if calib_dir is not None else\
                         nm.dir_calib()
        #print 'XXX: PSEventSupplier.set_dataset calib_dir: %s' % self.calib_dir
        setOption('psana.calib-dir', self.calib_dir)


        if self.ds is not None : 
            #print 'XXX: delete DataSource in PSEventSupplier.set_dataset  %s' % self.dsname
            del self.ds
            self.reset()


        if 'idx' in dsname :
            self._set_dataset_idx(dsname, calib_dir)
            self.is_idx_mode = True
            return

        self.is_idx_mode = False

        try : 
            #print 'XXX: open DataSource in PSEventSupplier.set_dataset  %s' % dsname
            self.ds = DataSource(dsname)

            self.dsname = dsname
        except : 
            self.reset()
            print('XXX: WARNING: DataSource is not open in PSEventSupplier.set_dataset  %s' % dsname)
            #raise IOError('Dataset is not created for dsname: %s' % dsname)
            return
        
        #self.log.info('open dataset: %s'%dsname, self._name)
        #print '%s.set_dataset open dataset: %s'%(self._name, dsname)

        self.events = self.ds.events() # for event_next() method


    def is_direct_access(self) :
        """Returns True for idx - index direct access mode, False othervise
        """
        return self.is_idx_mode


    def events(self) :
        """Returns event iterator for non-index mode
        """
        return self.events


    def event_next(self) :
        """Returns next psana.Event object
        """
        if self.is_idx_mode :
            n = self._evnum+1
            return self.event_for_number(n)
        else :
            if self.events is None : return None
            self._evnum += 1

            try :
               evt = next(self.events)
            except :                
               print('XXX WARNING: PSEventSupplier.event_next returns evt=None')
               return None

            return evt


    def current_event_number(self) :
        return self._evnum


    def event_next_and_number(self) :
        return self.event_next(), self._evnum


    def event_for_number(self, n=None) :
        """Returns psana.Event object for input event number n
        """
        if n is None :
            return self.event_next()

        elif self.is_idx_mode :
            et = self.dic_evtimes[n]
            self._evnum = n
            return self._run.event(et)
        else :
            #if self.log is not None: self.log.debug('dataset is in non-idx mode: NEXT event is returned.', self._name)
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
        return self.ds.env() if self.ds is not None else None


    def __del__(self) :
        del self.ds
        self.reset()
#        cp.pseventsupplier = None


#------------------------------

pseventsupplier = PSEventSupplier() # singleton

#------------------------------

def test_all() :

    #from expmon.Logger import log
    #from expmon.EMConfigParameters import cp
    from time import time
    #log.setPrintBits(0377)

    es = PSEventSupplier('exp=cxif5315:run=169:idx')
    #es = PSEventSupplier(cp, log, 'exp=xpptut15:run=54:idx')
    #es = PSEventSupplier(cp, log, 'exp=xpptut15:run=54')


    print('Sequential mode:')
    for n in range(10) :
        et = es.event_time(es.event_next())
        print('%4d fid:%d' % (es.current_event_number(), et.fiducial()))

    #t0_sec = time()
    #es.set_dataset('exp=cxif5315:run=169:idx')
    #print 'set_dataset consumed time(sec) = %.6f' % (time()-t0_sec)


    print('idx mode:')
    print('   5 fid:%d' % es.event_time(es.event_for_number(5)).fiducial()) 
    print('   0 fid:%d' % es.event_time(es.event_for_number(0)).fiducial()) 
    print('number_of_events:', es.number_of_events())

#------------------------------

if __name__ == "__main__" :
    test_all()

#------------------------------
