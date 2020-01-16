#------------------------------
"""
EMQDataControl.py
Created: 2017-04-12
Author : Mikhail Dubrovin
"""
#------------------------------

import sys
from expmon.QWDataControl import QWDataControl

#------------------------------

class EMQDataControl(QWDataControl) :
    """ Data control parameters derived from QWDataControl to connect signals with EM-app recipients
    """
    def __init__(self, cp, log, parent=None, show_mode=4) :
        QWDataControl.__init__(self, cp, log, parent=None, orient='V', show_mode=show_mode)
        self._name = self.__class__.__name__

        self.event_control().connect_new_event_number_to(self.on_new_event_number)
        self.event_control().connect_start_button_to(self.on_start_button)
        self.event_control().connect_stop_button_to(self.on_stop_button)

        # Can't use signal to thread, they intercept control
        #self.event_control().connect_start_button_to(cp.emqthreadeventloop.on_start_button)
        #self.event_control().connect_stop_button_to (cp.emqthreadeventloop.on_stop_button)

        cp.emqdatacontrol = self

#------------------------------

    def on_new_event_number(self, num) :
        msg = '%s.%s: num=%s' % (self._name, sys._getframe().f_code.co_name, num)
        self.log.debug(msg, self._name)

#------------------------------

    def on_start_button(self) :
        """1. prints message about received signal
           2. sets flag
        """
        msg = '%s' % (sys._getframe().f_code.co_name)
        self.log.info(msg, self._name)
        self.cp.flag_do_event_loop = True

#------------------------------

    def on_stop_button(self) :
        """1. prints message about received signal
           2. sets flag
        """
        msg = '%s' % (sys._getframe().f_code.co_name)
        self.log.info(msg, self._name)
        self.cp.flag_do_event_loop = False

#------------------------------

    def test_on_new_event_number_reception(self, num) :
        msg = '%s: num=%s' % (sys._getframe().f_code.co_name, num)
        self.log.debug(msg, self._name)

#------------------------------

    def closeEvent(self, e):
        self.on_stop_button()
        QWDataControl.closeEvent(self, e)

#------------------------------
#------------------------------

if __name__ == "__main__" :
    import sys
    from PyQt5 import QtCore, QtGui, QtWidgets

    from expmon.EMConfigParameters import cp
    from expmon.Logger import log

    app = QtWidgets.QApplication(sys.argv)
    w = EMQDataControl(cp, log, show_mode=0o377)
    #w.event_control().set_show_mode(show_mode=030)
    w.move(QtCore.QPoint(50,50))
    w.setWindowTitle(w._name)
    w.event_control().connect_new_event_number_to(w.test_on_new_event_number_reception)
    w.show()
    app.exec_()

#------------------------------
