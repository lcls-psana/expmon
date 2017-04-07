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
#------------------------------
import os
import sys
import numpy as np

from time import time
from psana import DataSource
#from expmon.Logger import log
from expmon.PSNameManager import nm
#------------------------------

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

    ds = DataSource(dsn)
    cfg = ds.env().configStore()
    sources = [str(k.src()) for k in cfg.keys()] # DetInfo(CxiDs2.0:Cspad.0)
    srcs = set([s[8:-1] for s in sources if s[:7]=='DetInfo']) # selects CxiDs2.0:Cspad.0
    #for k in cfg.keys() : print 'XXX:', k
    #for s in srcs : print 'XXX:', s
    #print 'Exit expmon.PSUtils.list_of_sources'

    return srcs

#------------------------------

def load_arr_from_f5(fname):
    import h5py
    f = h5py.File(fname, 'r')
    ds = f['/data/data']
    arr = ds[()]
    photon_energy_eV = f['/photon_energy_eV'][0]
    print 'photon_energy_eV', photon_energy_eV
    try :
      dsspec = f['/spectrum']
      if dsspec is not None :
        print 'number_of_samples', dsspec['number_of_samples'][0:3]
        print 'wavelengths_A', dsspec['wavelengths_A'][0]
        print 'weights', dsspec['weights'][:]
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

    if verbos : print 'Read file %s' % ifname

    BUF_SIZE_BYTE = npixels*2

    f = open(ifname,'rb')
    buf = f.read()
    f.close()
    nmax = len(buf)/BUF_SIZE_BYTE
    if verbos : print 'len(buf)', len(buf), 'nmax', nmax

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
    nwords = nbytes/wsize
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
    nda.shape = (size/w, w)
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
    #import pyimgalgos.GlobalUtils as gu
    from pyimgalgos.GlobalUtils import table_from_cspad_ndarr, reshape_to_2d
    from PSCalib.GeometryObject import data2x2ToTwo2x1 #, two2x1ToData2x2

    arr = get_array_from_file(ifname, dtype)
    if arr is None : return None

    if arr.size == 32*185*388 : # CSPAD
        arr = table_from_cspad_ndarr(arr)

    elif arr.size == 2*185*388 and arr.shape[0]==185: # CSPAD2x2
        arr = data2x2ToTwo2x1(arr) # DAQ:(185, 388, 2) -> Natural:(2, 185, 388)

    return arr if arr.ndim==2 else reshape_to_2d(arr)

#------------------------------
#------------------------------
#------------------------------

def test_list_of_sources(tname) :

    from expmon.EMConfigParameters import cp # !!! PASSED AS PARAMETER
    #from expmon.PSQThreadWorker import PSQThreadWorker
    nm.set_config_pars(cp)

    print '%s:' % sys._getframe().f_code.co_name
    for s in list_of_sources() : print s

#------------------------------

def test_all(tname) :
    lexps = []
    if tname == '0': test_list_of_sources(tname)
    if tname == '1': test_list_of_sources(tname) 
    else : return

#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print 50*'_', '\nTest %s' % tname
    test_all(tname)
    sys.exit('End of Test %s' % tname)

#------------------------------
