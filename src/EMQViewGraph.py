
#------------------------------
"""Subclass of GUViewGraph adds parameter imon and intercepts closeEvent returning imon
   Created: 2017-05-26
   Author : Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------
import sys
from expmon.Logger import log
from graphqt.GUViewGraph import *
#------------------------------

class EMQViewGraph(GUViewGraph) :
    """Extends GUViewGraph features.
    """
    view_is_closed_for_imon = QtCore.pyqtSignal(int)

    def __init__(self, parent, rectax=QtCore.QRectF(0, 0, 1, 1), origin='DL', scale_ctl='HV', rulers='TBLR',\
                 margl=None, margr=None, margt=None, margb=None,
                 imon=-1) :
        GUViewGraph.__init__(self, parent, rectax, origin, scale_ctl, rulers,\
                             margl, margr, margt, margb)

        self._name = self.__class__.__name__
        self.imon = imon
        log.debug('%s for imon=%d' % (sys._getframe().f_code.co_name, imon), self._name)

        #self.lab_info = QtGui.QLabel('EXTRA INFO')
        #self.layout().addWidget(self.lab_info)

        #self.connect_view_is_closed_for_imon_to(self.test_view_is_closed_for_imon)

#------------------------------

    def closeEvent(self, e):
        log.debug('closeEvent imon=%d' % self.imon, self._name)
        GUViewGraph.closeEvent(self, e)
        self.view_is_closed_for_imon.emit(self.imon)

#------------------------------

    def connect_view_is_closed_for_imon_to(self, slot) :
        #print 'XXX %s.connect_view_is_closed_for_imon_to'%(self._name)
        self.view_is_closed_for_imon[int].connect(slot)


    def disconnect_view_is_closed_for_imon_from(self, slot) :
        #print 'XXX %s.disconnect_view_is_closed_for_imon_from'%(self._name)
        self.view_is_closed_for_imon[int].disconnect(slot)


    def test_view_is_closed_for_imon(self, imon) :
        print('XXX %s.test_view_is_closed_for_imon imon=%d' % (self._name, imon))

#------------------------------

#EMQViewGraph(None, rectax, origin='DL', scale_ctl='HV', rulers='DL',\
#                                                  margl=0.12, margr=0.01, margt=0.01, margb=0.06)
#------------------------------
