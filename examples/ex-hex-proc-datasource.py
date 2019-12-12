#!/usr/bin/env python
#------------------------------
""" 
Example of hexanode data processing in psana DataSource with MPI

Usage:      python expmon/examples/ex-hex-data-datasource.py
or:
mpirun -n 2 python expmon/examples/ex-hex-proc-datasource.py
"""
from __future__ import print_function
#------------------------------

import psana
from expmon.HexDataIOExt import HexDataIOExt  # Line 0 - import

from mpi4py import MPI
rank = MPI.COMM_WORLD.Get_rank()
size = MPI.COMM_WORLD.Get_size()

# Parameters: data set name, data source, channels, number of events, CFD etc.
kwargs = {'command'  : 1,
          'srcchs'   : {'AmoETOF.0:Acqiris.0':(6,7,8,9,10,11),'AmoITOF.0:Acqiris.0':(0,)},
          'numchs'   : 7,
          'numhits'  : 16,
          'dsname'   : 'exp=xpptut15:run=390:smd',
          'evskip'   : 0,
          'events'   : 500,
          'ofprefix' : './',
          'verbose'  : False,
          'cfd_base'        :  0.  ,        
          'cfd_thr'         : -0.04,         
          'cfd_cfr'         :  0.9 ,         
          'cfd_deadtime'    :  5.0 ,    
          'cfd_leadingedge' :  True, 
          'cfd_ioffsetbeg'  :  0   ,  
          'cfd_ioffsetend'  :  1000, 
         }

ds = psana.DataSource(kwargs['dsname'])    # Open psana dataset using mpi
o = HexDataIOExt(ds, **kwargs)                # Line 1 - object initialization

print('MPI size: %2d rank: %2d' % (size, rank))

for nevent, evt in enumerate(ds.events()) :

    #print 'XXX event %4d rank %2d' % (nevent, rank)
    if nevent%size != rank : continue

    if o.skip_event(evt, nevent) : continue   # Line 2 - loop control method passes evt to the object
    if nevent > o.EVENTS : break

    #x, y, t = o.hits_xyt()                   # Line 3 - get arrays x, y, t of hits' coordinates and time
    #o.print_hits()                           # Line 3 alternative - prints x, y, time for all hits in the event

if rank==0 :
    o.print_summary()                         # print number of events, processing time total, instant and frequency

#------------------------------
