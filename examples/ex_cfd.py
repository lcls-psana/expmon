from __future__ import print_function
from psana import DataSource, Detector 
from pypsalg import find_edges

ds = DataSource('exp=amox27716:run=100')
det = Detector('ACQ2') # 'AmoEndstation.0:Acqiris.1')

for nevent,evt in enumerate(ds.events()):
    r = det.raw(evt)
    if r is None : continue
    waveforms,times = r
    # find edges for channel 0
    # parameters: baseline, threshold, fraction, deadtime, leading_edges
    edges = find_edges(waveforms[0],0.0,-0.05,1.0,5.0,True)
    # pairs of (amplitude,sampleNumber)
    print(edges)
    break

import matplotlib.pyplot as plt
plt.plot(waveforms[0])
plt.show()
