#!/usr/bin/env python

"""
This script submits jobs for processing of a few runs in batch.

1) edit a list of runs for processing

2) run this script :
   python submit_jobs_in_batch.py
"""
from __future__ import print_function

#------------------------------

import os

runs = (12, 13, 14)

for runnum in runs :
   cmd = 'bsub -q psfehq -o log-r%04d.log python kbFluorescenceIntensityMonitor.py %d' % (runnum,runnum)
   print(cmd)
   os.system(cmd)

#------------------------------
