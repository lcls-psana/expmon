#------------------------------
""" Set of utilities involving PyQt4

@version $Id: EMQUtils.py 13119 2017-02-06 18:54:12Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin

Usege ::
    from expmon.EMQUtils import point_relative_window

"""
from __future__ import print_function
#------------------------------

from CalibManager.GUIPopupSelectExp import select_experiment_v3 as popup_select_experiment
from PyQt5 import QtCore, QtWidgets

#------------------------------

def test_popup_select_experiment() :
    import expmon.EMUtils as emu
    lexps = emu.list_of_experiments()
    selexp = popup_select_experiment(None, lexps)
    print('Selected experiment: %s' % selexp)


def point_relative_window(win, dp=QtCore.QPoint(0,0)) :
    point, size = win.mapToGlobal(dp), win.size()
    x,y,w,h = point.x(), point.y(), size.width(), size.height()
    #self.guview.move(QtCore.QPoint(x,y) + QtCore.QPoint(w+10, 100))
    return QtCore.QPoint(x+w, y)

#------------------------------
#------------------------------
#------------------------------
 
def test_all(tname) :
    from PyQt5 import QtCore, QtGui#, QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    if tname == '0': test_popup_select_experiment()

#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print(50*'_', '\nTest %s' % tname)
    test_all(tname)
    sys.exit('End of Test %s' % tname)

#------------------------------
