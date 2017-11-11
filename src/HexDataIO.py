"""
Class :py:class:`HexDataIO` a set of methods to access psana data of hexanode detector
======================================================================================

HexDataIO - a set of methods to access data, resembling hexanode/src/LMF_IO.cpp

Usage ::

    Create object and access methods
    --------------------------------
    from expmon.HexDataIO import HexDataIO

    o = HexDataIO(dic_src_channels={'AmoETOF.0:Acqiris.0':(6,7,8,9,10,11),'AmoITOF.0:Acqiris.0':(0,)})
    o.open_input_dataset('exp=xpptut15:run=390')

    status = o.read_next_event()           # gets next event from dataset, returns True if event is available

    nhits   = o.get_number_of_hits_array() # number of hits per channel, shape=(NUM_CHANNELS,)
    tdc_ns  = o.get_tdc_data_array()       # array of hit time [ns], shape=(NUM_CHANNELS, NUM_HITS)
    tdc_ind = o.get_tdc_index_array()      # array of hit index, shape=(NUM_CHANNELS, NUM_HITS)
    wf      = o.get_wf(channel=1)          # per channel array of intensities
    wt      = o.get_wt(channel=1)          # per channel array of times [s]
    nch     = o.get_number_of_channels()   # returns a number of channels
    tstamp  = o.tdc_resolution()           # returns TDC bin width in ns

    tstamp  = o.start_time()               # returns (str) time stamp like '2017-10-23T17:00:00'
    tstamp  = o.stop_time()                # returns (str) time stamp like '2017-10-23T17:00:00'

    o.open_output_h5file(ofname='./test.h5')
    o.close_output_h5file()
    o.close_input_h5file()
    o.add_event_to_h5file()

    o.open_input_h5file(ofname='./test.h5')

    o.print_tdc_data()
    o.print_times()

Created on 2017-10-23 by Mikhail Dubrovin
"""
#------------------------------

import numpy as np
import psana
from Detector.WFDetector import WFDetector
import pyimgalgos.GlobalUtils as gu
import Detector.PyDataAccess as pda

#------------------------------
from pypsalg import find_edges

from PSCalib.DCUtils import env_time, str_tstamp

#------------------------------
# Waveform hit-finder parameters

BASE = 0.
THR = -0.04
CFR = 0.9
DEADTIME = 5.0
LEADINGEDGE = True # False
IOFFSETBEG = 0
IOFFSETEND = 1000

#------------------------------
# IO array shape parameters:

NUM_CHANNELS = 7 #  (int) - number of channels for u1,u2,v1,v2,w1,w2,mcp signals
NUM_HITS    = 16 # (int) - maximal number of time signals per channel 
#------------------------------
# Test parameters
EVSKIP = 0
EVENTS = EVSKIP + 100
#------------------------------

class HexDataIO :
    def __init__(self, dic_src_channels={'AmoETOF.0:Acqiris.0':(6,7,8,9,10,11),\
                                         'AmoITOF.0:Acqiris.0':(0,)}) :
        """Parameters

           - dic_src_channels (dict) - dictionary of pairs (source:list-of-channels)
             where list-of-channels should be for u1,u2,v1,v2,w1,w2,mcp signals
        """
        self._dic_src_channels = dic_src_channels
        self._tdc_resolution = None
        self._env = None
        self._init_arrays()
        self._ofile = None
        self._ifile = None
        self.evnum = 0


    def _init_arrays(self) :
        self.error_flag = 0
        self._event_is_processed = False
        self._number_of_hits = np.zeros((NUM_CHANNELS),   dtype=np.int)
        self._tdc_ns  = np.zeros((NUM_CHANNELS, NUM_HITS), dtype=np.double)
        self._tdc_ind = np.zeros((NUM_CHANNELS, NUM_HITS), dtype=np.int)
        self._dic_wf = {}
        self._dic_wt = {}


    def events(self) : return self._events

    def env(self) :    return self._env


    def open_input_dataset(self, dsname='exp=xpptut15:run=390', pbits=1022, do_mpids=False) :
        self.ds = psana.MPIDataSource(dsname) if do_mpids else psana.DataSource(dsname)
        self._env = self.ds.env()

        self.evt = None
        self._events = self.ds.events()
        self.pbits = pbits

        #nrun = evt.run()
        #evt = ds.events().next()
        #for key in evt.keys() : print key

        self.sources  = self._dic_src_channels.keys()
        self.channels = self._dic_src_channels.values()

        self.wfdets = [WFDetector(src, self._env, pbits) for src in self.sources]
        self.srcs_dets_channels = zip(self.sources, self.wfdets, self.channels)

        if pbits & 1 :
            for wfd in self.wfdets :
                wfd.print_attributes()

        co = pda.get_acqiris_config_object(self._env, self.wfdets[0].source)
        self._tdc_resolution = co.horiz().sampInterval() * 1e9 # sec -> ns


    def open_output_h5file(self, fname='./test.h5') :
        import h5py
        self._nevmax = 1000
        self._ofile = h5py.File(fname,'w')

        self.h5ds_nhits = self._ofile.create_dataset('nhits', (self._nevmax, NUM_CHANNELS), dtype='i', maxshape=(None, NUM_HITS))
        self.h5ds_tdcns = self._ofile.create_dataset('tdcns', (self._nevmax, NUM_CHANNELS, NUM_HITS), dtype='f',\
                                                             maxshape=(None, NUM_CHANNELS, NUM_HITS))

    def close_output_h5file(self, pbits=0) :
        if self._ofile is None : return
        if pbits : print 'Close output file: %s' % self._ofile.filename
        self._ofile.close()
        self._ofile = None


    def close_input_h5file(self, pbits=0) :
        if self._ifile is None : return
        if pbits : print 'Close input file: %s' % self._ifile.filename
        self._ifile.close()
        self._ifile = None


    def _resize_h5_datasets(self) :
        self._nevmax *= 2
        self._ofile.flush()
        self.h5ds_nhits.resize(self._nevmax, axis=0)   # or dset.resize((20,1024))
        self.h5ds_tdcns.resize(self._nevmax, axis=0)   # or dset.resize((20,1024))


    def add_event_to_h5file(self) :
        i = self.evnum-1
        if i >= self._nevmax : self._resize_h5_datasets()
        self._proc_waveforms()

        #gu.print_ndarr(self._number_of_hits, '  _number_of_hits')
        #gu.print_ndarr(self._tdc_ns, '  _tdc_ns')

        self.h5ds_nhits[i] = self._number_of_hits
        self.h5ds_tdcns[i] = self._tdc_ns
        self.h5ds_nhits.attrs['events'] = i


    def open_input_h5file(self, fname='./test.h5') :
        import h5py
        self._ifile = h5py.File(fname,'r')
        self.h5ds_nhits = self._ifile['nhits']
        self.h5ds_tdcns = self._ifile['tdcns']
        print 'File %s has %d records in "nhits" and "tdcns" datasets' % (fname, self.h5ds_nhits.attrs['events']+1)


    def fetch_event_data_from_h5file(self) :
        i = self.evnum-1
        if i>self.h5ds_nhits.attrs['events'] : 
             return False

        self._number_of_hits = self.h5ds_nhits[i]
        self._tdc_ns         = self.h5ds_tdcns[i]
        return True


    def __del__(self) :
        self.close_output_h5file()
        self.close_input_h5file()


    def tdc_resolution(self) :
        return self._tdc_resolution


    def start_time(self) :
        #return '2017-10-23T17:00:00'
        tsec = env_time(self._env)
        return str_tstamp(fmt='%Y-%m-%dT%H:%M:%S', time_sec=int(tsec))


    def stop_time(self) :
        tsec = env_time(self._env) + 1234
        return str_tstamp(fmt='%Y-%m-%dT%H:%M:%S', time_sec=int(tsec))


    def get_number_of_channels(self) :
        return self.numch


    def read_next_event(self) :
        self.evnum += 1

        if self._ifile is not None :
            if self.evt is None : 
                self._init_arrays()
                self.evt = self._events.next()
            return self.fetch_event_data_from_h5file()

        self._init_arrays()
        self.evt = self._events.next()
        return self.evt is not None


    def get_event_number(self) :
        return self.evnum


    def get_number_of_hits_array(self, arr=None) :
        self._proc_waveforms()
        if arr is not None : arr[:] = self._number_of_hits[:]
        return self._number_of_hits


    def get_tdc_data_array(self, arr=None) :
        self._proc_waveforms()
        if arr is not None : arr[:] = self._tdc_ns[:]
        return self._tdc_ns


    def get_tdc_index_array(self) :
        self._proc_waveforms()
        return self._tdc_ind


    def get_wf(self, channel=0) :
        self._proc_waveforms()
        #wf = self._dic_wf.get(channel, None)
        #gu.print_ndarr(wf, '    XXX waveform')
        return self._dic_wf.get(channel,None)


    def get_wt(self, channel=0) :
        self._proc_waveforms()
        return self._dic_wt.get(channel, None)


    def _proc_waveforms(self) :
        if self._ifile is not None  : return
        if self._event_is_processed : return
        self.proc_waveforms_for_evt(self.evt)
        self._event_is_processed = True


    def proc_waveforms_for_evt(self, evt) :
        ch_max, nhits_max = NUM_CHANNELS, NUM_HITS
        ch_tdc = -1
        for src, wfd, channels in self.srcs_dets_channels :
            res = wfd.raw(evt)
            if res is None : continue
            wf,wt = res
            for ch in channels :
                ch_tdc+=1
                if ch_tdc == ch_max :
                    raise IOError('HexDataIO._proc_waveforms: input tdc_ns shape=%s ' % str(tdc_ns.shape)\
                                  +' does not have enough rows for quad-/hex-anode channels')

                wfch = wf[ch,:]
                wfch -= wfch[IOFFSETBEG:IOFFSETEND].mean()
                self._dic_wf[ch_tdc] = wfch
                self._dic_wt[ch_tdc] = wtch = wt[ch,:] * 1e9 # sec -> ns

                edges = find_edges(wfch, BASE, THR, CFR, DEADTIME, LEADINGEDGE)

                nedges = len(edges)
                if nedges >= nhits_max :
                    if self.pbits :
                        msg = 'HexDataIO._proc_waveforms: input tdc_ns shape=%s ' % str(self._tdc_ns.shape)\
                            + ' does not have enough columns for %d time records,' % nedges\
                            + '\nWARNING: NUMBER OF SIGNAL TIME RECORDS TRANCATED'
                        print msg
                    continue

                nhits = min(nhits_max, nedges) 
                self._number_of_hits[ch_tdc] = nhits

                for i in range(nhits):
                    amp,ind = edges[i]
                    self._tdc_ind[ch_tdc, i] = int(ind)
                    self._tdc_ns [ch_tdc, i] = wtch[int(ind)]


    def print_tdc_data(self) :
        for src, wfd, channels in self.srcs_dets_channels :
            print 'source: %s channels: %s' % (src, str(channels))
            res = wfd.raw(self.evt)
            if res is None : continue
            wf,wt = res
            gu.print_ndarr(wf, '    waveform')
            gu.print_ndarr(wt, '    wavetime')


    def print_times(self) :
        arr_nhits   = self.get_number_of_hits_array()
        arr_tdc_ns  = self.get_tdc_data_array()
        arr_tdc_ind = self.get_tdc_index_array()
        print 'HexDataIO.print_times - event waveform times'
        print 'Ch.#   Nhits   Index/Time[ns]'
        for ch in range(arr_nhits.size) :
            nhits = arr_nhits[ch]
            print '%4d   %4d:' % (ch, nhits),
            for ihit in range(nhits) :
                print ' %9d' % (arr_tdc_ind[ch, ihit]),
            print '\n              ',
            for ihit in range(nhits) :
                print '  %8.1f' % (arr_tdc_ns[ch, ihit]),
            print ''


    def get_error_text(self, error_flag) :
        #self.error_flag = 0
        return 'no-error'


#------------------------------
#------------ TEST ------------
#------------------------------

def hexdataio(pbits=1022) :
    o = HexDataIO(dic_src_channels={'AmoETOF.0:Acqiris.0':(6,7,8,9,10,11),'AmoITOF.0:Acqiris.0':(0,)})
    o.open_input_dataset('exp=xpptut15:run=390', pbits)
    return o

#------------------------------

def test_hexdataio() :
    o = hexdataio()
    while o.get_event_number() < 10 :
        print '%s\nEvent %d' % (80*'_', o.get_event_number())
        o.read_next_event()
        o.print_tdc_data()
        nhits = o.get_number_of_hits_array()
        gu.print_ndarr(nhits, '    nhits', first=0, last=7)
        print '\nTDC resolution [ns]: %.3f' % o.tdc_resolution()
        o.print_times()

#------------------------------

def draw_times(ax, wf, wt, nhits, hit_inds) :
    print 'nhits:%2d'%nhits,
    for i in range(nhits) :
        hi = hit_inds[i]
        ti = wt[hi] # hit time
        ai = wf[hi] # hit intensity
        print ' %.1f' % ti,
        gg.drawLine(ax, (ti,ti), (ai,-ai), s=10, linewidth=1, color='k')
    print ''

#------------------------------

def test_hexdataio_graph() :

    import pyimgalgos.Graphics       as gr; global gr
    import pyimgalgos.GlobalGraphics as gg; global gg

    fig = gr.figure(figsize=(15,15), title='Image')

    nchans = 7
    dy = 1./nchans

    lw = 1
    w = 0.87
    h = dy - 0.04
    x0, y0 = 0.07, 0.03

    gfmt = ('b-', 'r-', 'g-', 'k-', 'm-', 'y-', 'c-', )
    ylab = ('Y1', 'Y2', 'Z1', 'Z2', 'X1', 'X2', 'MCP', )
    ax = [gr.add_axes(fig, axwin=(x0, y0 + i*dy, w, h)) for i in range(nchans)]

    o = hexdataio(pbits=0)
    evnum = 0
    while evnum < EVENTS :
        evnum = o.get_event_number()
        print '%s\nEvent %d' % (80*'_', evnum)
        o.read_next_event()
        if evnum < EVSKIP : continue

        o.print_times()

        nhits = o.get_number_of_hits_array()
        hit_inds = o.get_tdc_index_array()
        gu.print_ndarr(nhits, 'nhits', first=0, last=7)

        for c in range(len(nhits)) :
            gu.print_ndarr(o.get_wf(c), 'ch:%2d wf'%c, first=0, last=5)
        gu.print_ndarr(o.get_wt(0), 'ch:%2d wt'%c, first=0, last=4)

        gr.set_win_title(fig, titwin='Event: %d' % o.get_event_number())

        for c in range(nchans) :
            ax[c].clear()
            ax[c].set_xlim((2500,4500)) # [ns]
            ax[c].set_ylabel(ylab[c], fontsize=14)
 
            wt, wf = o.get_wt(c), o.get_wf(c)
            if None in (wt, wf) : continue
            wtsel = wt[:-1]
            wfsel = wf[:-1]

            ax[c].plot(wtsel, wfsel, gfmt[c], linewidth=lw)
            gg.drawLine(ax[c], ax[c].get_xlim(), (THR,THR), s=10, linewidth=1, color='k')
            draw_times(ax[c], wfsel, wtsel, nhits[c], hit_inds[c,:])
        gr.draw_fig(fig)
        gr.show(mode='non-hold')
    gr.show()

#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    import numpy as np; global np
    tname = sys.argv[1] if len(sys.argv) > 1 else '1'
    print 50*'_', '\nTest %s' % tname
    if   tname == '1' : test_hexdataio()
    elif tname == '2' : test_hexdataio_graph()
    else : print 'Not-recognized test name: %s' % tname
    sys.exit('End of Test %s' % tname)

#------------------------------
#------------------------------
#------------------------------
 
