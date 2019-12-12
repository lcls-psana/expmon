#!/usr/bin/env python

#import sysi
#import pyimgalgos.GlobalGraphics as gg

from __future__ import print_function
import psana
import numpy as np
import pyimgalgos.GlobalUtils as gu
from Detector.WFDetector import WFDetector
import Detector.PyDataAccess as pda

dsname, src = 'exp=xpptut15:run=390', 'AmoETOF.0:Acqiris.0'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, src))

ds  = psana.DataSource(dsname)
evt1= next(ds.events())
evt = next(ds.events())
env = ds.env()
nrun = evt.run()

source = psana.Source(src)

dato = evt.get(psana.Acqiris.DataDescV1, source)
cfg = env.configStore()
cfgo = cfg.get(psana.Acqiris.ConfigV1, source)
 
c = pda.get_acqiris_config_object(env,source)
tdc_resolution = c.horiz().sampInterval()



for key in evt.keys() : print(key)

det = WFDetector(src, env, pbits=1022)
print(80*'_', '\nInstrument: ', det.instrument())

gu.print_ndarr(arr_nhits, '    arr_nhits', first=0, last=7)


