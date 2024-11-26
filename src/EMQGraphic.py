#------------------------------
"""EMQGraphic - widget around EMQGraphic with information and possibly other pannels.
   Created: 2017-06-06
   Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQGraphic import EMQGraphic

    then see example in test_emqhistogram below
"""
from __future__ import print_function
#------------------------------

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt
from graphqt.Styles import style
from expmon.EMQViewGraph import EMQViewGraph
from expmon.Logger import log

#------------------------------

class EMQGraphic(QtWidgets.QWidget) :
    """
    """
    def __init__(self, parent, rectax=QtCore.QRectF(0, 0, 1, 1), origin='DL', scale_ctl='H', rulers='BL',\
                 margl=None, margr=None, margt=None, margb=None,
                 imon=-1) :

        QtWidgets.QWidget.__init__(self, parent)
        self._name = self.__class__.__name__

        self.lab_info = QtWidgets.QLabel('Graphic\ninfo')
 
        self.graph = EMQViewGraph(self, rectax, origin, scale_ctl, rulers,\
                                  margl, margr, margt, margb, imon)

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.graph,    0,  0, 100, 100)
        self.grid.addWidget(self.lab_info, 0, 80,  10,  20)
        self.setLayout(self.grid) 
 
        self.set_tool_tips()
        self.set_style()

        #self.graph.connect_mean_std_updated_to(self.draw_mean_std)
        #self.graph.connect_statistics_updated_to(self.draw_stat)
 
#------------------------------

    def set_tool_tips(self) :
        self.setToolTip('Graphic for monitor %d' % self.graph.imon) 

#------------------------------

    def set_style(self) :
        self.setMinimumSize(500,400)
        self.lab_info.setStyleSheet(style.styleStat)

#------------------------------
 
    def draw_info(self, txt) :
        self.lab_info.setText(txt)

#------------------------------
 
    def graph(self) :
        return self.graph

#------------------------------

    def closeEvent(self, e):
        log.debug('closeEvent', self._name)
        #print '%s.closeEvent' % self._name

        try : self.graph.close()
        except : pass

        #QtGui.QWidget.closeEvent(self, e)
 
#------------------------------

def test_emqgraphic(tname) :
    print('%s:' % sys._getframe().f_code.co_name)
    import numpy as np

    app = QtWidgets.QApplication(sys.argv)

    mux, sigmax = 200, 25
    muy, sigmay = 100, 40
    arrx = np.require(mux + sigmax*np.random.standard_normal((100,)), dtype=np.float32)
    arry = np.require(muy + sigmay*np.random.standard_normal((100,)), dtype=np.float32)

    xmin, xmax = arrx.min(), arrx.max()
    ymin, ymax = arry.min(), arry.max()
    rectax=QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

    w = EMQGraphic(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
                   margl=0.12, margr=0.01, margt=0.01, margb=0.06, imon=0)
    
    #amin, amax, nhbins, values = image_to_hist_arr(arr, vmin=None, vmax=None, nbins=100)
    #w.graph.add_hist(values, (amin, amax), pen=QtGui.QPen(Qt.yellow, 0), brush=QtGui.QBrush(Qt.yellow))
    w.graph.add_points(arrx, arry, QtGui.QPen(Qt.yellow), brush=QtGui.QBrush(Qt.yellow), fsize=0.0075)

    w.setWindowTitle('Graphic with info panel')

    #w.connect_color_table_is_changed_to(w.test_color_table_is_changed_reception)
    #w.graph.connect_axes_limits_changed_to(w.graph.test_axes_limits_changed_reception)
    #w.graph.connect_histogram_updated_to(w.graph.test_histogram_updated_reception)

    w.show()
    app.exec_()

#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    import numpy as np; global np
    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print(50*'_', '\nTest %s' % tname)
    test_emqgraphic(tname)
    sys.exit('End of Test %s' % tname)

#------------------------------
