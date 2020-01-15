#------------------------------
""" Set of utilities involving psana library
Usage ::
    import expmon.PSUtils as psu
    srcs = psu.list_of_sources(dsname)


    #or 
    from expmon.EMConfigParameters import cp # to get exp, run
    nm.set_config_pars(cp) # to get dsname
    srcs = psu.list_of_sources(dsname)

@version $Id: PSUtils.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
from __future__ import print_function
from __future__ import division
#------------------------------
import os
import sys
import numpy as np

from time import time
import psana
#from psana import DataSource, EventId, EventTime
#from Detector.AreaDetector import AreaDetector
#from expmon.Logger import log
from expmon.PSNameManager import nm

from pyimgalgos.GlobalUtils import table_from_cspad_ndarr, reshape_to_2d, print_ndarr #subtract_bkgd
from PSCalib.GeometryObject import data2x2ToTwo2x1 #, two2x1ToData2x2
from expmon.PSEventSupplier import pseventsupplier # singleton PSEventSupplier object

#------------------------------

def detector(src, env) : # src='CxiDs2.0:Cspad.0'
    return psana.Detector(src, env)

#------------------------------

def dataset(dsname, calib_dir=None) : # dsname='exp=cxi12316:run=1234', src='CxiDs2.0:Cspad.0'
    #print 'XXX DataSource open in PSUtils dataset %s' % dsname
    #return psana.DataSource(dsname)
    pseventsupplier.set_dataset(dsname, calib_dir)
    return pseventsupplier.dataset()

#------------------------------

def exp_run_from_dsname(dsname='exp=xpptut15:run=390:smd'):
    """Returns (str) experiment and (str) run from dataset name,
       e.g. returns 'xpptut15' and '390' from 'exp=xpptut15:run=390:smd'
    """
    exp, run = None, None
    fields = dsname.split(':')
    for f in fields :
        s = f.split('=')
        if len(s)==2 :
            if s[0]=='exp' : exp=s[1]
            if s[0]=='run' : run=s[1].lstrip('0')
    return exp, run

#------------------------------

def event_time(evt) :
    evtId = evt.get(psana.EventId)
    (sec, nsec), fid = evtId.time(), evtId.fiducials()
    return psana.EventTime(int((sec<<32)|nsec),fid)

#------------------------------

def dataset_times(ds) :
    """Too... slow, Works for :smd ds mode
       Returns list of psana.EventTime objects
    """
    return [event_time(evt) for evt in ds.events()]

#------------------------------

def run_times(run) :
    """Works for :idx ds mode only
       run = ds.runs().next() # psana.Run object
       Returns list of psana.EventTime objects
    """
    return run.times()

#------------------------------

def dict_evnum_times(run) :
    """Works for :idx ds mode only
       run = ds.runs().next() # psana.Run object
       Returns dictionary of enumerated psana.EventTime objects

       Usage::
           import expmon.PSUtils as psu
           ds = psana.DataSource('exp=xpptut15:run=54:idx')
           run = ds.runs().next()
           d=psu.dict_evnum_times(run)
           evnum=5
           et = dt[evnum]
           evt = psu.event_for_time(run, et)
    """
    return dict(enumerate(run.times()))

#------------------------------

def dataset_events(ds) :
    return ds.events()

#------------------------------

def event_for_time(run, et) :
    """run = ds.runs().next() # psana.Run object
       et = psana.EventTime
       Returns psana.Event() object
    """
    return run.event(et)

#------------------------------

    #env = ds.env()
    #runnum = evt.run()
    #evt = ds.events().next()
    #run = ds.runs().next()
    #runnum = run.run()
    #det = AreaDetector(src, env)

#------------------------------

def list_of_pv_names(dsname=None) : # dsname i.e. 'exp=cxi12316:run=1234:...'
    """ returns a list of tuples (Full-Name, DAQ-Alias, User-Alias)
    """
    dsn = nm.dsname() if dsname is None else dsname
    pseventsupplier.set_dataset(dsn, calib_dir=None)
    ds = pseventsupplier.dataset()
    return psana.DetNames('epics') # list of ('HX2:SB1:IPM:01:ChargeAmpRangeCH0', 'ipm1_gain', '')


#------------------------------

def list_of_sources_v1(dsname=None) : # dsname i.e. 'exp=cxi12316:run=1234:...'
    """ returns a list of tuples (Full-Name, DAQ-Alias, User-Alias)
    """
    dsn = nm.dsname() if dsname is None else dsname

    if dsn is None\
    or ('Select' in dsn)\
    or ('Last' in dsn) :
        #print 'Exit expmon.PSUtils.list_of_sources dsn: %s' % dsn
        return None

    pseventsupplier.set_dataset(dsn, calib_dir=None)
    ds = pseventsupplier.dataset()
    return psana.DetNames() # list of ('HX2:SB1:IPM:01:ChargeAmpRangeCH0', 'ipm1_gain', '')

#------------------------------

#def list_of_sources_test(dsname=None) : 
#    return ['SxrBeamline.0:Opal1000.0', 'SxrEndstation.0:Acqiris.2', 'NoDetector.0:Evr.0']


def list_of_sources(dsname=None) : # dsname i.e. 'exp=cxi12316:run=1234:...'
    """Returns list of (str) sources like 'CxiDs2.0:Cspad.0'"""

    dsn = nm.dsname() if dsname is None else dsname
    #print 'expmon.PSUtils.list_of_sources dsn:', dsn

    if dsn is None\
    or ('Select' in dsn)\
    or ('Last' in dsn) :
        #print 'Exit expmon.PSUtils.list_of_sources dsn: %s' % dsn
        return None

    #print 'expmon.PSUtils.list_of_sources if is passed'
            
    #print 'XXX DataSource open in PSUtils list_of_sources %s' % dsn
    #ds = psana.DataSource(dsn)
    pseventsupplier.set_dataset(dsn, calib_dir=None)
    ds = pseventsupplier.dataset()
    cfg = ds.env().configStore()
    sources = [str(k.src()) for k in cfg.keys()] # DetInfo(CxiDs2.0:Cspad.0)
    srcs_cfg = set([s[8:-1] for s in sources if s[:7]=='DetInfo']) # selects CxiDs2.0:Cspad.0

    #evt0 = ds.events().next()
    try : 
        evt0 = next(ds.events())
    #except StopIteration, reason:
        #print "ERROR: failed to get next event: ", reason
    except : # StopIteration, reason:
        print("ERROR: StopIteration for dsname=%s" % dsn)
        pseventsupplier.set_dataset(dsn, calib_dir=None)
        ds = pseventsupplier.dataset()
        #ds = psana.DataSource(dsn)
        evt0 = next(ds.events())

    sources = [str(k.src()) for k in evt0.keys()] # DetInfo(CxiDs2.0:Cspad.0)
    srcs_evt = set([s[8:-1] for s in sources if s[:7]=='BldInfo']) # selects CxiDs2.0:Cspad.0

    #print 'cfg.keys:'
    #for k in srcs_cfg : print 'XXX:', k
    #print 'evt0.keys:'
    #for k in srcs_evt : print 'XXX:', k

    #for k in sources : print 'XXX:', k
    #for k in cfg.keys() : print 'XXX:', k
    #for k in evt0.keys() : print 'XXX:', k
    #for s in srcs : print 'XXX:', s
    #print 'Exit expmon.PSUtils.list_of_sources'

    #return srcs_cfg 
    return srcs_cfg.union(srcs_evt) 

#------------------------------

def list_of_sources_for_dataset(dsname, evts_max=50) : # dsname i.e. 'exp=cxi12316:run=1234:...'
    """Returns list of (str) sources like 'CxiDs2.0:Cspad.0'

       Differs from list_of_sources: defines ds=psana.DataSource(dsname) directly, not a singleton, no caching
    """
    #print 'XXX DataSource open in PSUtils list_of_sources %s' % dsname
    ds = psana.DataSource(dsname)
    cfg = ds.env().configStore()
    sources = [str(k.src()) for k in cfg.keys()] # DetInfo(CxiDs2.0:Cspad.0)
    srcs_cfg = set([s[8:-1] for s in sources if s[:7]=='DetInfo']) # selects CxiDs2.0:Cspad.0

    event_keys = []
    for i,evt in enumerate(ds.events()) :
        if evt is None : continue
        if i>evts_max : break
        event_keys += list(evt.keys())

    sources = [str(k.src()) for k in event_keys] # DetInfo(CxiDs2.0:Cspad.0)
    srcs_evt = set([s[8:-1] for s in sources if s[:7] in ('BldInfo','DetInfo')]) # selects CxiDs2.0:Cspad.0

    del ds
    #return srcs_cfg
    #return srcs_evt
    return srcs_cfg.union(srcs_evt) 

#------------------------------

def load_arr_from_f5(fname):
    import h5py
    f = h5py.File(fname, 'r')
    ds = f['/data/data']
    arr = ds[()]
    photon_energy_eV = f['/photon_energy_eV'][0]
    print('photon_energy_eV', photon_energy_eV)
    try :
      dsspec = f['/spectrum']
      if dsspec is not None :
        print('number_of_samples', dsspec['number_of_samples'][0:3])
        print('wavelengths_A', dsspec['wavelengths_A'][0])
        print('weights', dsspec['weights'][:])
    except : pass
    return arr

#------------------------------

def load_binary_old(ifname  = 'data.bin',\
                    npixels = 32*185*388,\
                    dtype   = np.int16,\
                    verbos  = False) :
    """Test read/unpack binary file.
       Binary file does not have shape, so image size in pixels and data type should be provided.
    """

    if verbos : print('Read file %s' % ifname)

    BUF_SIZE_BYTE = npixels*2

    f = open(ifname,'rb')
    buf = f.read()
    f.close()
    nmax = len(buf)//BUF_SIZE_BYTE
    if verbos : print('len(buf)', len(buf), 'nmax', nmax)

    for nevt in range(nmax) :
        nda = np.frombuffer(buf, dtype=dtype, count=npixels, offset=nevt*BUF_SIZE_BYTE)
        if verbos : print_ndarr(nda, name='%4d nda'%(nevt), first=0, last=10)

#------------------------------

def load_binary(ifname, dtype=None, shape=None) :
    dt = np.int16 if dtype is None else dtype
    #dt = np.float32 if dtype is None else dtype
    f = open(ifname,'rb')
    buf = f.read()
    nbytes = len(buf)
    wsize = np.dtype(dt).itemsize
    nwords = nbytes//wsize
    #print 'XXX: nwords, dt.itemsize', nwords, wsize
    nda = np.frombuffer(buf, dtype=dt, count=nwords)
    f.close()

    # Try to guess array shape for binary file, which can be returned absolutely wrong
    #EPIX (1,704,768).
    #Rayonix (1, 1, 1920, 1920)
    size = nda.size   
    w = 388  if not(size%388) else\
        1920 if not(size%1920) else\
        768  if not(size%768) else\
        1023 if not(size%1023) else\
        2048 if not(size%2048) else\
        1024 if not(size%1024) else\
        512  if not(size%512) else\
        2    if not(size%2) else\
        3    if not(size%3) else\
        1
    nda.shape = (size//w, w)
    return nda

#------------------------------

def get_array_from_file(fname, dtype=None) :

    if fname is None : return None
    ifname = fname.rstrip('@') # removes sign of reference at the end of the file name

    if os.path.lexists(ifname) :
        ext = os.path.splitext(ifname)[1]
        arr = np.load(ifname)            if ext == '.npy'  else\
              load_arr_from_f5(ifname)   if ext == '.h5'   else\
              load_binary(ifname, dtype) if ext == '.bin'  else\
              np.loadtxt(ifname)         if ext in ('.txt','.data') else\
              np.loadtxt(ifname)
        return arr if dtype is None else arr.astype(dtype)
    return None

#------------------------------

def get_image_array_from_file(ifname=None, dtype=None) :

    arr = get_array_from_file(ifname, dtype)
    if arr is None : return None

    if arr.size == 32*185*388 : # CSPAD
        arr = table_from_cspad_ndarr(arr)

    elif arr.size == 2*185*388 and arr.shape[-1]==2: # CSPAD2x2
        #print_ndarr(arr, name='nda', first=0, last=10)
        arr = data2x2ToTwo2x1(arr) # DAQ:(185, 388, 2) -> Natural:(2, 185, 388)

    return arr if arr.ndim==2 else reshape_to_2d(arr)

#------------------------------
#------------------------------
#------------------------------

def test_list_of_sources(tname) :

    from expmon.EMConfigParameters import cp # !!! PASSED AS PARAMETER
    #from expmon.PSQThreadWorker import PSQThreadWorker
    nm.set_config_pars(cp)

    print('%s:' % sys._getframe().f_code.co_name)
    for s in list_of_sources() : print(s)

#------------------------------

def test_list_of_sources_for_dataset() :
    dsname = 'exp=xpptut15:run=54:smd'
    print('%s dsname "%s"' % (sys._getframe().f_code.co_name, dsname))
    list_of_sources = list_of_sources_for_dataset(dsname, evts_max=10)
    for i,s in enumerate(list_of_sources) : print('%4d  %s' % (i+1,s))

#------------------------------

def test_dataset_times(tname) :
    #ds = DataSource('exp=xpptut15:run=54:smd')
    #ds = psana.DataSource('exp=cxif5315:run=169:smd')
    pseventsupplier.set_dataset('exp=cxif5315:run=169:smd', calib_dir=None)
    ds = pseventsupplier.dataset()
    t0_sec = time()
    dst = dataset_times(ds)
    print('consumed time(sec) = %.6f' % (time()-t0_sec))
    print(len(dst), dst[0].seconds(), dst[0].nanoseconds(), dst[0].fiducial())

#------------------------------

def test_steps(tname) :
    #ds = DataSource('exp=xpptut15:run=54:idx')
    #ds = psana.DataSource('exp=cxif5315:run=169:idx')
    pseventsupplier.set_dataset('exp=cxif5315:run=169:idx', calib_dir=None)
    ds = pseventsupplier.dataset()
    run = next(ds.runs())
    #nsteps = run.nsteps()
    #print 'nsteps = %d' % nsteps
    print('run:', run)

    t0_sec = time()
    #for i in range(nsteps):
    times = run.times()
    print(len(times), times[0])

    evt = event_for_time(run, times[0])
    print('evt:', evt)

    print('consumed time(sec) = %.6f' % (time()-t0_sec))


#------------------------------

def get_login() :
    """Returns login name
    """
    import getpass
    return getpass.getuser()

#------------------------------

def get_pid() :
    """Returns pid - process id
    """
    return os.getpid()
 
#------------------------------

def get_cwd() :
    """get corrent work directory"""
    return os.getcwd()

#------------------------------

def get_hostname() :
    #return os.uname()[1]
    import socket
    return socket.gethostname()

#------------------------------

def get_enviroment(env='USER') :
    """Returns the value of specified by string name environment variable or (str) 'None'
    """
    return str(os.environ.get(env))

#------------------------------

def create_directory(dir, mode=0o777) :
    #print 'create_directory: %s' % dir
    if os.path.exists(dir) :
        #logger.info('Directory exists: ' + dir, __name__) 
        pass
    else :
        os.makedirs(dir)
        os.chmod(dir, mode)
        #os.system(cmd)
        #logger.info('Directory created: ' + dir, __name__) 

#------------------------------

def create_path(path, depth=5, mode=0o777) : 
    # Creates missing path for /reg/g/psdm/logs/calibman/2016/07/2016-07-19-12:20:59-log-dubrovin-562.txt
    # if path to file exists return True, othervise False
    subdirs = path.strip('/').split('/')
    cpath = ''
    for i,sd in enumerate(subdirs[:-1]) :
        cpath += '/%s'% sd 
        if i<depth : continue
        create_directory(cpath, mode)
        #print 'create_path: %s' % cpath

    return os.path.exists(cpath)
 
#------------------------------
#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print(50*'_', '\nTest %s' % tname)
    t0_sec = time()
    if   tname == '0': test_list_of_sources(tname)
    elif tname == '1': test_list_of_sources(tname) 
    elif tname == '2': test_dataset_times(tname) 
    elif tname == '3': test_steps(tname) 
    elif tname == '4': test_list_of_sources_for_dataset()
    else : print('WARNING: Test %s is not defined' % tname)
    print('consumed time(sec) = %.6f' % (time()-t0_sec))
    sys.exit('End of Test %s' % tname)

#------------------------------
