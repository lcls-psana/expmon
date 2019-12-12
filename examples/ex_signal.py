#!/usr/bin/env python
#------------------------------

from __future__ import print_function
import sys
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

#------------------------------
_sep_ = 20*'_'
fr = sys._getframe
#------------------------------

def metname(fr) :
    return fr.f_code.co_name

#------------------------------

def print_vector(vec) :
    print(vec, '\n len=%d' % len(vec))

#------------------------------

def plot_vector(vec) :
    print('  len=%d' % len(vec))
    plt.plot(vec)
    plt.show()

#------------------------------

def test_ricker() :
    print(_sep_, '\n%s' % metname(fr()))

    points = 100
    a = 4.0
    vec = signal.ricker(points, a)
    plot_vector(vec)

#------------------------------

def test_morlet() :
    print(_sep_, '\n%s' % metname(fr()))

    points = 100
    vec = signal.morlet(points, w=5.0, s=1.0, complete=True)
    plot_vector(vec)

#------------------------------

def test_daub() :
    p = 24 # 1-32
    print(20*'_', '\n%s(%d)' % (metname(fr()), p))
    plot_vector(signal.daub(p))

#------------------------------

def test_qmf() :
    print(_sep_, '\n%s' % metname(fr()))
    hk=np.array(range(100))
    signal.qmf(hk)
    plot_vector(hk)

#------------------------------

def test_cwt() :
    print(_sep_, '\n%s' % metname(fr()))

    t = np.linspace(-1, 1, 200, endpoint=False)
    sig  = np.cos(2 * np.pi * 7 * t) + signal.gausspulse(t - 0.4, fc=2)
    plt.plot(sig)
    plt.show()
    widths = np.arange(1, 31)
    cwtmatr = signal.cwt(sig, signal.ricker, widths)
    plt.imshow(cwtmatr, extent=[-1, 1, 31, 1], cmap='PRGn', aspect='auto',
               vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
    plt.show()

#------------------------------

def test_find_peaks_cwt() :
    print(_sep_, '\n%s' % metname(fr()))
    xs = np.arange(0, np.pi, 0.05)
    data = np.sin(xs)
    
    plot_vector(data)

    peakind = signal.find_peaks_cwt(data, np.arange(1,10))
    print(peakind, xs[peakind], data[peakind])

#------------------------------

def test_all() :
    print(_sep_, '\n%s' % metname(fr()))
    test_ricker()
    test_morlet()
    test_daub()
    test_qmf()
    test_cwt()
    test_find_peaks_cwt()

#------------------------------

if __name__ == "__main__" :
    from time import time

    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print(50*'_', '\nTest %s:' % tname)
    t0_sec = time()
    if   tname == '0': test_all() 
    elif tname == '1': test_ricker()
    elif tname == '2': test_morlet()
    elif tname == '3': test_daub()
    elif tname == '4': test_qmf()
    elif tname == '5': test_cwt()
    elif tname == '6': test_find_peaks_cwt()
    else : print('Not-recognized test name: %s' % tname)

    msg = 'End of test %s, consumed time (sec) = %.6f' % (tname, time()-t0_sec)
    sys.exit(msg)

#------------------------------

