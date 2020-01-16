#------------------------------
"""
Module EMQThreadEventLoop is a QThread for event processing in a separate thread.
Created: 2017-05-18
Author : Mikhail Dubrovin

Usage ::
    o = EMQThreadEventLoop(parent=None, dt_msec=500, pbits=0377)
    o._check_flags() # checks cp.flag_do_event_loop and launch EMQEventLoop
    o.run()          # keeps thread alive, calls _check_flags and sleeps
    o.update_dataset() # should be callsed if dataset is changed, deletes EMQEventLoop object
"""
from __future__ import print_function
#------------------------------
import sys
import os
import random
#from time import time

from PyQt5 import QtCore # QtGui
from expmon.EMConfigParameters import cp
from expmon.EMQEventLoop import EMQEventLoop
#from expmon.Logger  import log # CAN'T USE LOGGER->GUI IN THREAD

#------------------------------

class EMQThreadEventLoop(QtCore.QThread) :
    update = QtCore.pyqtSignal('QString')

    def __init__ (self, parent=None, dt_msec=500, pbits=0o377) :
        """cp (ConfigParameters) object in the list of parameters 
           allows to re-use EMQThreadEventLoop in other projects

           uses/updates cp.emon_data
        """
        QtCore.QThread.__init__(self, parent)        
        self._name = self.__class__.__name__
        #print 'XXX Start %s' % self._name

        self.dt_msec   = dt_msec
        self.thread_id = random.random()
        self.counter   = 0
        self.pbits     = pbits
        self.do_check_flags = True

        #self.connect_signal_to_slot(self.test_connection)

        #self.set_request_process_data()

        cp.flag_do_event_loop = False

        self.emqeventloop = EMQEventLoop()
        
        cp.emqthreadeventloop = self

#------------------------------

    def __del__(self) :
        print('XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name))
        #log.debug('%s'%sys._getframe().f_code.co_name, self._name)
        #self.timer.stop()
        self.do_check_flags = False
        self.emqeventloop.__del__()

#------------------------------

    def update_dataset(self) :
        if self.emqeventloop is None : 
           del self.emqeventloop
        self.emqeventloop = None

#------------------------------

# DOES NOT WORK ????

        #self.timer = QtCore.QTimer()
        #self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timeout)

#    def start_event_loop(self) :
#        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)
#        self.emqeventloop.start_event_loop()

#    def stop_event_loop(self) :
#        print '%s.%s' % (self._name, sys._getframe().f_code.co_name)
#        self.emqeventloop.stop_event_loop()

#    def run_v2(self) :
#        print 'XXX: In EMQThreadEventLoop run - just sleep'
#        self.msleep(self.dt_msec)

#    def run(self) :     
#        print 'XXX In %s.%s' % (self._name, sys._getframe().f_code.co_name)
#        self.timer.start(self.dt_msec)


#    def on_timeout(self) :
#        if not self.do_check_flags : return

#        self.counter += 1
#        if self.pbits & 2 : print '%s  i:%4d  id:%f' % (self._name, self.counter, self.thread_id)
#        self._check_flags()

#------------------------------

    def _check_flags(self) :
        if not self.do_check_flags : return # works after closing

        if self.pbits & 1 : 
            msg = 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
            print('%s  flag_do_event_loop: %s' % (msg, cp.flag_do_event_loop))

        if  cp.flag_do_event_loop :
            #if self.emqeventloop is None : self.emqeventloop = EMQEventLoop()
            self.emqeventloop.start_event_loop()

#------------------------------

    def run(self) :
        """Supports alive this thread, checks flags by the timer.
        """
        while self.do_check_flags :
            self.counter += 1
            if self.pbits & 2 : print('%s  i:%4d  id:%f' % (self._name, self.counter, self.thread_id))
            self._check_flags()
            self.msleep(self.dt_msec)
            #self.emit_check_status_signal()

#------------------------------

    def emit_check_status_signal(self) :
        msg = 'from work thread ' + str(self.thread_id) + '  check counter: ' + str(self.counter)
        self.update.emit(msg)
        if self.pbits & 1 : print(msg)
        #self.emit(QtCore.SIGNAL('update(QString)'), \
        #          'from work thread ' + str(self.thread_id) +\
        #          '  check counter: ' + str(self.counter))
        #print status_str

#------------------------------

    def connect_signal_to_slot(self, slot) :
        print('%s.connect_signal_to_slot'%(self._name))
        self.update['QString'].connect(slot)

#------------------------------

    def test_connection(self, text) :
        print('%s: Signal is recieved: %s'%(self._name, text))

#------------------------------
