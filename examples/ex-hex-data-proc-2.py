#!/usr/bin/env python
#--------------------------------------------------------     
""" 
Example of hexanode data processing in psana using DataSource created inside HexDataIO object

Usage:      python expmon/examples/ex-hex-data-proc-2.py
or:
mpirun -n 2 python expmon/examples/ex-hex-data-proc-2.py
"""
from __future__ import print_function
#----------------------------------------------------------    

from expmon.HexDataIOExt import HexDataIOExt

def test_HexDataIOExt() :

    # Parameters for initialization of the data source, channels, number of events etc.
    kwargs = {'command'  : 1,
              'srcchs'   : {'AmoETOF.0:Acqiris.0':(6,7,8,9,10,11),'AmoITOF.0:Acqiris.0':(0,)},
              'numchs'   : 7,
              'numhits'  : 16,
              'dsname'   : 'exp=xpptut15:run=390:smd',
              'evskip'   : 0,
              'events'   : 600,
              'ofprefix' : './',
              'verbose'  : False,
             }

    o = HexDataIOExt(**kwargs)       # Line # 1

    while o.read_next_event() :      # Line # 2

        o.print_sparsed_event_info() # print sparsed event number and time consumption 

        if o.skip_event()       : continue # event loop control
        if o.break_event_loop() : break    # event loop control

        x, y, t = o.hits_xyt()       # Line # 3 get arrays of x, y, z hit coordinates

        #print 'x:', x
        #print 'y:', y
        #print 't:', t
        #print 'methods:', o.hits_method()

        o.print_hits()               # prints x, y, time, method for found in event hits

    o.print_summary() # print number of events, processing time total, instant and frequency

#------------------------------

if __name__ == "__main__" :
    import sys
    test_HexDataIOExt()
    print('End of %s' % sys.argv[0].split('/')[-1])

#------------------------------
