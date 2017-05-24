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
#------------------------------
import sys
import os
import random
#from time import time

from PyQt4 import QtCore # QtGui
from expmon.EMConfigParameters import cp
from expmon.EMQEventLoop import EMQEventLoop
#from expmon.Logger  import log # CAN'T USE LOGGER->GUI IN THREAD

#------------------------------

class EMQThreadEventLoop(QtCore.QThread) :

    def __init__ (self, parent=None, dt_msec=500, pbits=0377) :
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
        self.pbits  = pbits
        #self.connect_signal_to_slot(self.test_connection)

        #self.set_request_process_data()

        cp.flag_do_event_loop = False

        cp.emqeventloop = EMQEventLoop() # None
        cp.emqthreadeventloop = self

#------------------------------

    def update_dataset(self) :
        if cp.emqeventloop is None : 
           del cp.emqeventloop
        cp.emqeventloop = None

#------------------------------

    def _check_flags(self) :
        msg = 'In %s.%s' % (self._name, sys._getframe().f_code.co_name)
        if self.pbits & 1 : 
            print '%s  flag_do_event_loop: %s' % (msg, cp.flag_do_event_loop)

        if  cp.flag_do_event_loop :
            #if cp.emqeventloop is None : cp.emqeventloop = EMQEventLoop()
            cp.emqeventloop.start_event_loop()

#------------------------------

    def run(self) :
        """Supports alive this thread, checks flags by the timer.
        """
        while True :
            self.counter += 1
            if self.pbits & 2 : print '%s  i:%4d  id:%f' % (self._name, self.counter, self.thread_id)
            self._check_flags()
            self.msleep(self.dt_msec)
            #self.emit_check_status_signal()

#------------------------------

    def emit_check_status_signal(self) :
        msg = 'from work thread ' + str(self.thread_id) + '  check counter: ' + str(self.counter)
        self.emit(QtCore.SIGNAL('update(QString)'), msg)
        if self.pbits & 1 : print msg
        #self.emit(QtCore.SIGNAL('update(QString)'), \
        #          'from work thread ' + str(self.thread_id) +\
        #          '  check counter: ' + str(self.counter))
        #print status_str

#------------------------------

    def connect_signal_to_slot(self, slot) :
        print '%s.connect_signal_to_slot'%(self._name)
        self.connect(self, QtCore.SIGNAL('update(QString)'), slot)

#------------------------------

    def test_connection(self, text) :
        print '%s: Signal is recieved: %s'%(self._name, text)

#------------------------------
