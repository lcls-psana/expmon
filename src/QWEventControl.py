#------------------------------
"""
@version $Id: QWEventControl.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
from __future__ import print_function
#------------------------------
import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from expmon.EMQFrame import Frame
from graphqt.Styles import style
#------------------------------

class QWEventControl(Frame) :
    """GUI control on event number
    """
    new_event_number = QtCore.pyqtSignal(int)
    start_button = QtCore.pyqtSignal()
    stop_button = QtCore.pyqtSignal()

    def __init__ (self, cp, log, parent=None, show_mode=0) :
        """show_mode & 1 - event number
                     & 2 - step in number of events
                     & 4 - dt(msec) button
                     & 8 - start/stop button
        """
        Frame.__init__(self, parent, mlw=1, vis=False) # show_mode & 1)
        self._name = self.__class__.__name__

        self.cp  = cp
        self.log = log

        self.event_number = cp.event_number
        self.event_step   = cp.event_step
        self.wait_msec    = cp.wait_msec
        self.nevents_update = cp.nevents_update
        self.max_evt_num  = None

        #self.char_expand = cp.char_expand

        self.lab_upd = QtWidgets.QLabel('Events update:')
        self.lab_evt = QtWidgets.QLabel('Evt:')
        self.lab_stp = QtWidgets.QLabel('  Step:')
        self.lab_dtw = QtWidgets.QLabel('  t(ms):')
        self.but_bwd = QtWidgets.QPushButton('<')
        self.but_fwd = QtWidgets.QPushButton('>')
        self.but_ctl = QtWidgets.QPushButton('Start')
        self.edi_evt = QtWidgets.QLineEdit(str(self.event_number.value()))
        self.edi_stp = QtWidgets.QLineEdit(str(self.event_step.value()))
        self.edi_dtw = QtWidgets.QLineEdit(str(self.wait_msec.value()))
        self.edi_upd = QtWidgets.QLineEdit(str(self.nevents_update.value()))

        self.set_layout()
        self.set_style()
        self.set_tool_tips()

        self.but_bwd.clicked.connect(self.on_but_bwd)
        self.but_fwd.clicked.connect(self.on_but_fwd)
        self.but_ctl.clicked.connect(self.on_but_ctl)
        self.edi_evt.editingFinished.connect(self.on_edi_evt)
        self.edi_stp.editingFinished.connect(self.on_edi_stp)
        self.edi_dtw.editingFinished.connect(self.on_edi_dtw)
        self.edi_upd.editingFinished.connect(self.on_edi_upd)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timeout)

        self.set_show_mode(show_mode)


    def set_show_mode(self, show_mode=0o377):
        self.show_mode = show_mode

        self.lab_evt.setVisible(show_mode & 1)
        self.but_bwd.setVisible(show_mode & 1)
        self.edi_evt.setVisible(show_mode & 1)
        self.but_fwd.setVisible(show_mode & 1)

        self.lab_stp.setVisible(show_mode & 2)
        self.edi_stp.setVisible(show_mode & 2)

        self.lab_dtw.setVisible(show_mode & 4)
        self.edi_dtw.setVisible(show_mode & 4)

        self.but_ctl.setVisible(show_mode & 8)

        self.lab_upd.setVisible(show_mode & 16)
        self.edi_upd.setVisible(show_mode & 16)


    def set_layout(self):
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.lab_upd)
        self.hbox.addWidget(self.edi_upd)
        self.hbox.addSpacing(10)
        self.hbox.addWidget(self.lab_evt)
        self.hbox.addWidget(self.but_bwd)
        self.hbox.addSpacing(-5)
        self.hbox.addWidget(self.edi_evt)
        self.hbox.addSpacing(-5)
        self.hbox.addWidget(self.but_fwd)
        self.hbox.addSpacing(10)
        self.hbox.addWidget(self.lab_stp)
        self.hbox.addWidget(self.edi_stp)
        self.hbox.addSpacing(10)
        self.hbox.addWidget(self.lab_dtw)
        self.hbox.addWidget(self.edi_dtw)
        self.hbox.addSpacing(10)
        self.hbox.addWidget(self.but_ctl)
        self.hbox.addStretch(1)
        self.setLayout(self.hbox)
 

    def set_tool_tips(self):
        self.setToolTip('Event number control')


    def set_style(self):
        #self.setMinimumWidth(500)
        #self.setGeometry(10, 25, 400, 600)
        #self.setFixedHeight(100)
        #self.setContentsMargins(QtCore.QMargins(-5,-5,-5,-5))

        self.edi_evt.setValidator(QtGui.QIntValidator(0,100000000,self))
        self.edi_stp.setValidator(QtGui.QIntValidator(-1000000,1000000,self))
        self.edi_dtw.setValidator(QtGui.QIntValidator(0,1000000,self))
        self.edi_upd.setValidator(QtGui.QIntValidator(1,5000,self))

        self.lab_evt.setStyleSheet(style.styleLabel)
        self.lab_stp.setStyleSheet(style.styleLabel)
        self.lab_dtw.setStyleSheet(style.styleLabel)
        self.lab_upd.setStyleSheet(style.styleLabel)
        #self.but_bwd.setFixedSize(27,27)
        #self.but_fwd.setFixedSize(27,27)
        self.but_bwd.setFixedWidth(25)
        self.but_fwd.setFixedWidth(25)
        self.edi_evt.setFixedWidth(50)
        self.edi_stp.setFixedWidth(40)
        self.edi_dtw.setFixedWidth(50)
        self.edi_upd.setFixedWidth(50)
        self.but_ctl.setFixedWidth(50)
        self.but_ctl.setStyleSheet(style.styleButtonGood)


    #def on_but(self):
    #    if self.but_ins.hasFocus() : print 'on_but ins'
    #    if self.but_exp.hasFocus() : print 'on_but exp'
    #    if self.but_run.hasFocus() : print 'on_but run'


    def on_edi_evt(self):
        num = int(self.edi_evt.displayText())
        self.set_event_number(num)


    def on_edi_stp(self):
        num = int(self.edi_stp.displayText())
        self.event_step.setValue(num)
        self.log.info('Set event step: %d' % num, __name__)


    def on_edi_dtw(self):
        num = int(self.edi_dtw.displayText())
        self.wait_msec.setValue(num)
        self.log.info('Set wait time between events (msec): %d' % num, __name__)


    def on_edi_upd(self):
        num = int(self.edi_upd.displayText())
        self.nevents_update.setValue(num)
        self.log.info('Number of events to update presenter: %d' % num, __name__)


    def on_but_bwd(self):
        num = self.event_number.value() - self.event_step.value()
        self.set_event_number(num)


    def on_but_fwd(self):
        num = self.event_number.value() + self.event_step.value()
        self.set_event_number(num)


    def set_max_event_number(self, num):
        if not isinstance(num, int) : return
        self.max_evt_num = num
        self.edi_evt.setValidator(QtGui.QIntValidator(0,num,self))


    def set_event_number(self, num):
        if num<0 : num = 0
        if self.max_evt_num is not None\
        and num>self.max_evt_num : num = self.max_evt_num
        if num == int(self.event_number.value()) : return
        self.event_number.setValue(num)
        self.edi_evt.setText('%d'%num)
        self.log.info('Set event number: %d' % num, __name__)
        self.new_event_number.emit(num)


    def connect_new_event_number_to(self, recip) :
        self.new_event_number[int].connect(recip)


    def disconnect_new_event_number_from(self, recip) :
        self.new_event_number[int].disconnect(recip)


    def test_new_event_number_reception(self, evnum) :
        print('%s.test_new_event_number_reception: %d' % (self._name, evnum))


    def on_timeout(self) :
        self.on_but_fwd()
        self.timer.start(self.wait_msec.value()) 


    def on_timer_stop(self) :
        self.timer.stop()


    def on_but_ctl(self):
        s = self.but_ctl.text()
        if s=='Start' :
            self.start_button.emit()
            self.but_ctl.setText('Stop')
            self.but_ctl.setStyleSheet(style.styleButtonBad)
            #self.on_timeout() # connected on signal
        else :
            self.stop_button.emit()
            self.but_ctl.setText('Start')
            self.but_ctl.setStyleSheet(style.styleButtonGood)
            #self.timer_stop() # connected on signal


    def connect_start_button_to(self, recip) :
        self.start_button.connect(recip)


    def disconnect_start_button_from(self, recip) :
        self.start_button.disconnect(recip)


    def test_start_button_reception(self) :
        print('%s.test_start_button_reception' % (self._name))


    def connect_stop_button_to(self, recip) :
        self.stop_button.connect(recip)


    def disconnect_stop_button_from(self, recip) :
        self.stop_button.disconnect(recip)


    def test_stop_button_reception(self) :
        print('%s.test_stop_button_reception' % (self._name))

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

    #from graphqt.Logger             import log
    #from graphqt.IVConfigParameters import cp

    from expmon.Logger             import log
    from expmon.EMConfigParameters import cp

    app = QtWidgets.QApplication(sys.argv)
    w = QWEventControl(cp, log, parent=None, show_mode=0o377)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.connect_new_event_number_to(w.test_new_event_number_reception)
    w.connect_start_button_to(w.test_start_button_reception)
    w.connect_stop_button_to(w.test_stop_button_reception)
    w.show()
    app.exec_()

#------------------------------
