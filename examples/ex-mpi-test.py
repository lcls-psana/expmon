#!/usr/bin/env python
#------------------------------
""" 
Example 1 - hexanode data processing in psana

Usage:      python expmon/examples/ex-hex-data-proc.py
or:
mpirun -n 2 python expmon/examples/ex-hex-data-proc.py
"""
#------------------------------

""" 
Example 1 - hexanode data processing in psana

Usage:      python ex-mpi-test.py
or:
mpirun -n 2 python ex-mpi-test.py
"""
from __future__ import print_function

#from expmon.PSUtils import event_time
import psana

ds = psana.MPIDataSource('exp=xpptut15:run=390:smd')

print('Before event loop: size:%2d rank:%2d' % (ds.size, ds.rank))

for n, evt in enumerate(ds.events()) :
    #evtime = event_time(evt)
    fid = evt.get(psana.EventId).fiducials()
    print('XXX: ev:%4d size:%2d rank:%2d fid: %7d' % (n, ds.size, ds.rank, fid))
    #if n%ds.size != ds.rank : continue
    if n > 100 : break

print('After event loop: size:%2d rank:%2d' % (ds.size, ds.rank))
if ds.master : print('master: size:%2d rank:%2d' % (ds.size, ds.rank))

#------------------------------
