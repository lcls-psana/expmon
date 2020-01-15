#------------------------------
"""
Test speed of the psana event access in python loop using 
   1) evt in ds.events() : 
   2) evt = events.next()
Conclusion: speed is the same, <~1kHz on psanaphi102

Created: 2017-05-18
Author : Mikhail Dubrovin
"""
from __future__ import print_function
from __future__ import division
#------------------------------

from psana import DataSource, EventId, EventTime, setOption
from time import time

#dsname = 'exp=sxro5916:run=24'
dsname = 'exp=xpptut15:run=390'
ds = DataSource(dsname)
events = ds.events()

nevbuf = 100
nevmax = 2000

t0_sec = time()

#------------------------------

if True :
  print('Test evt = ds.events().next()')
  t0_sec = tt_sec = time()
  for n in range(nevmax) :
    evt = next(events)
    if not n%nevbuf :
      print('evt %6d   dt(sec/evt) = %.6f'%\
            (n, (time()-t0_sec)/nevbuf))
      t0_sec = time()
  print('Processed %d events, consumed time (sec) = %.6f'% (nevmax, time()-tt_sec))

#------------------------------

if True :
  print('Test  evt in ds.events()')
  t0_sec = tt_sec = time()
  for n, evt in enumerate(events) :
    if n > nevmax : break
    if not n%nevbuf : 
      print('evt %6d   dt(sec/evt) = %.6f'%\
            (n, (time()-t0_sec)/nevbuf))
      t0_sec = time()
  print('Processed %d events, consumed time (sec) = %.6f'% (nevmax, time()-tt_sec))

#------------------------------
