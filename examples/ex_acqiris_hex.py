#!/usr/bin/env python
#------------------------------

from __future__ import print_function
import sys
import psana
import numpy as np
from Detector.WFDetector import WFDetector

import pyimgalgos.Graphics       as gr
import pyimgalgos.GlobalGraphics as gg
import pyimgalgos.GlobalUtils    as gu

dsname = 'exp=xpptut15:run=280'
src1 = 'AmoEndstation.0:Acqiris.1' # 'ACQ1'
src2 = 'AmoEndstation.0:Acqiris.2' # 'ACQ2'

print('Example for\n  dataset: %s\n  source1 : %s\n  source2 : %s' % (dsname, src1, src2))

#opts = {'psana.calib-dir':'./calib',}
#psana.setOptions(opts)
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
env = ds.env()
#nrun = evt.run()
#evt = ds.events().next()
#for key in evt.keys() : print key

det2 = WFDetector(src2, env, pbits=1022)
det1 = WFDetector(src1, env, pbits=1022)
det1.print_attributes()

#------------------------------

fig = gr.figure(figsize=(15,15), title='Image')
#gr.move_fig(fig, 200, 100)
#fig.canvas.manager.window.geometry('+200+100')



naxes = 4
dy = 1./naxes

lw = 1
w = 0.87
h = dy - 0.04
x0, y0 = 0.05, 0.03

ch = (0,1,2,3)
gfmt = ('b-', 'r-', 'g-', 'k-', )
ax = [gr.add_axes(fig, axwin=(x0, y0 + i*dy, w, h)) for i in range(naxes)]

#------------------------------
wf,wt = None, None

for i,evt in enumerate(ds.events()) :
    if i>10 : break
    print(50*'_', '\n Event # %d' % i)
    gr.set_win_title(fig, titwin='Event: %d' % i)

    print('Acqiris.1:')
    wf,wt = det1.raw(evt)

    print('Acqiris.2:')
    wf2,wt2 = det2.raw(evt)
    #gu.print_ndarr(wf, 'acqiris waveform')
    #gu.print_ndarr(wt, 'acqiris wavetime')

    for i in range(naxes) :

        ax[i].clear()
        ax[i].plot(wt[ch[i],:-1], wf[ch[i],:-1], gfmt[i], linewidth=lw)

    gr.draw_fig(fig)
    gr.show(mode='non-hold')

gr.show()

#ch=0
#fig, ax = gg.plotGraph(wt[ch,:-1], wf[ch,:-1], figsize=(15,5))
#gg.show()

#------------------------------

sys.exit(0)

#------------------------------
