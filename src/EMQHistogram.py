#------------------------------
"""EMQHistogram - widget around EMQHistogram with statistical information and possibly other pannels.
   Created: 2017-06-06
   Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQHistogram import EMQHistogram

    then see example in test_emqhistogram below
"""
from __future__ import print_function
#------------------------------

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt
from graphqt.Styles import style
from expmon.EMQViewHist import EMQViewHist, image_to_hist_arr
from expmon.Logger import log

#------------------------------

class EMQHistogram(QtWidgets.QWidget) :
    """
    """
    def __init__(self, parent, rectax=QtCore.QRectF(0, 0, 1, 1), origin='DL', scale_ctl='H', rulers='BL',\
                 margl=None, margr=None, margt=None, margb=None,
                 imon=-1) :

        QtWidgets.QWidget.__init__(self, parent)
        self._name = self.__class__.__name__

        self.lab_stat = QtWidgets.QLabel('Histogram\nstatistics')
 
        self.hist = EMQViewHist(self, rectax, origin, scale_ctl, rulers,\
                                margl, margr, margt, margb, imon)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.hist,     0,  0, 100, 100)
        grid.addWidget(self.lab_stat, 0, 80,  10,  20)
        self.setLayout(grid) 
 
        self.set_tool_tips()
        self.set_style()

        self.hist.connect_mean_std_updated_to(self.draw_mean_std)
        self.hist.connect_statistics_updated_to(self.draw_stat)
 
#------------------------------

    def set_tool_tips(self) :
        self.setToolTip('Histogram for monitor %d' % self.hist.imon) 

#------------------------------

    def set_style(self) :
        self.setMinimumSize(500,400)
        self.lab_stat.setStyleSheet(style.styleStat)

#------------------------------
 
    def draw_mean_std(self, mean, std) :
        txt = '    Mean: %.2f\n    RMS: %.2f' % (mean, std)
        #print txt
        self.lab_stat.setText(txt)

#------------------------------
 
    def draw_stat(self, mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w) :
        #print 'XXX: mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w',\
        #            mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w
        txt = u'  Entries: %d\n  Mean: %.2f \u00B1 %.2f\n  RMS: %.2f \u00B1 %.2f\n  \u03B31=%.2f   \u03B32=%.2f'%\
              (neff, mean, err_mean, rms, err_rms, skew, kurt)
        #print txt
        self.lab_stat.setText(txt)

#------------------------------

    def closeEvent(self, e):
        log.debug('closeEvent', self._name)
        #print '%s.closeEvent' % self._name

        try : self.hist.close()
        except : pass

        #QtGui.QWidget.closeEvent(self, e)

#------------------------------

def test_emqhistogram(tname) :
    print('%s:' % sys._getframe().f_code.co_name)
    import numpy as np

    app = QtWidgets.QApplication(sys.argv)

    mu, sigma = 200, 25
    arr = np.require(mu + sigma*np.random.standard_normal((100,)), dtype=np.float32)

    xmin, xmax = arr.min(), arr.max()
    ymin, ymax = 0, 10
    rectax=QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

    w = EMQHistogram(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                     margl=0.12, margr=0.01, margt=0.01, margb=0.06, imon=0)

    amin, amax, nhbins, values = image_to_hist_arr(arr, vmin=None, vmax=None, nbins=100)
    w.hist.add_hist(values, (amin, amax), pen=QtGui.QPen(Qt.yellow, 0), brush=QtGui.QBrush(Qt.yellow))

    w.setWindowTitle('Histogram with stat panel')

    #w.connect_color_table_is_changed_to(w.test_color_table_is_changed_reception)
    #w.hist.connect_axes_limits_changed_to(w.hist.test_axes_limits_changed_reception)
    #w.hist.connect_histogram_updated_to(w.hist.test_histogram_updated_reception)

    w.show()
    app.exec_()

#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    import numpy as np; global np
    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print(50*'_', '\nTest %s' % tname)
    test_emqhistogram(tname)
    sys.exit('End of Test %s' % tname)

#------------------------------
