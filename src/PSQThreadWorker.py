
#------------------------------
"""PSQThreadWorker.
   Created: 2017-02-18
   Author : Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------
import sys
import os
import random
from time import time

from PyQt5 import QtCore # QtGui
#from expmon.PSConfigParameters import cp
import expmon.PSUtils as psu
#import expmon.EMUtils as emu

#------------------------------

class PSQThreadWorker(QtCore.QThread) :
    update = QtCore.pyqtSignal('QString')

    def __init__ (self, cp, parent=None, dt_msec=5, pbits=0) :
        """cp (ConfigParameters) object in the list of parameters 
           allows to re-use PSQThreadWorker in other projects

           uses/updates cp.list_of_sources
        """
        QtCore.QThread.__init__(self, parent)        
        self._name = self.__class__.__name__
        #print 'Start %s' % self._name

        self.cp        = cp
        self.dt_msec   = dt_msec
        self.pbits     = pbits
        self.thread_id = random.random()
        self.counter   = 0

        self.set_request_find_sources()
        
        #self.connect_signal_to_slot(self.test_connection)


    def set_request_find_sources(self) :
        self.cp.list_of_sources = None


    def check_flags(self) :
        if self.cp.list_of_sources is None : 
           t0_sec = time()
           self.cp.list_of_sources = psu.list_of_sources()
           #msg = 'XXX %s.%s consumed time (sec) = %.3f' % (self._name, sys._getframe().f_code.co_name, time()-t0_sec)
           #print msg


    def run(self) :
        while True :
            self.counter += 1
            if self.pbits & 2 : print('%s  i:%4d  id:%f' % (self._name, self.counter, self.thread_id))
            self.check_flags()
            #self.emit_check_status_signal()
            self.msleep(self.dt_msec)

#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------

    def emit_check_status_signal(self) :
        msg = 'from work thread ' + str(self.thread_id) + '  check counter: ' + str(self.counter)
        self.update.emit(msg)

        if self.pbits & 1 : print(msg)

        #self.emit(QtCore.SIGNAL('update(QString)'), \
        #          'from work thread ' + str(self.thread_id) +\
        #          '  check counter: ' + str(self.counter))
        #print status_str


    def connect_signal_to_slot(self, slot) :
        print('%s.connect_signal_to_slot'%(self._name))
        self.update['QString'].connect(slot)


    def test_connection(self, text) :
        print('%s: Signal is recieved: %s'%(self._name, text))

#------------------------------
