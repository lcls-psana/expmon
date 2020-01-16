#------------------------------
"""SSQSourceSelector.py
   Created: 2017-07-28
   Author : Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------

import sys
import collections

from time import time
from PyQt5 import QtCore, QtGui, QtWidgets

from graphqt.QWCheckList import QWCheckList, print_dic
import expmon.PSUtils as psu
from expmon.QWDataControl import QWDataControl
from expmon.PSNameManager import nm

#------------------------------

class SSQSourceSelector(QtWidgets.QWidget) :
    """GUI to input instrument, experiment, and run number
    """

    def __init__(self, cp, log) :
        """
        """
        QtWidgets.QWidget.__init__(self, parent=None)
        self._name = self.__class__.__name__

        self.cp     = cp
        self.log    = log

        self.log_rec_on_start()
#        self.save_log_file()

        self.w_dset = QWDataControl(cp, log, show_mode=0)
        #self.w_chkl = QWCheckList(parent=None, dic_item_state={'a':True, 'b':False, 'c':True})
        self.w_chkl = QWCheckList(parent=None, dic_item_state={}) #self.dic_srcs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.w_dset)
        self.vbox.addWidget(self.w_chkl)
        self.setLayout(self.vbox)
 
        self.set_style()
        self.set_tool_tips()

        self.update_sources()

        #self.w_dset.connect_runnum_is_changed_to(self.w_dset.test_runnum_is_changed)
        self.w_dset.connect_runnum_is_changed_to(self.on_runnum_is_changed)


    def set_tool_tips(self):
       self.setToolTip('Select sources')


    def set_style(self):
        self.setWindowTitle(self._name)
        self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))

        #self.setMinimumWidth(500)
        #self.setGeometry(10, 25, 400, 600)
        #self.setFixedHeight(100)

        #self.lab_ins.setStyleSheet(style.styleLabel)
        #self.lab_exp.setStyleSheet(style.styleLabel)
        #self.lab_run.setStyleSheet(style.styleLabel)
        #self.w_calib.lab.setStyleSheet(style.styleLabel)
        #self.w_calib.setMinimumWidth(280)
        #self.w_calib.edi.setMinimumWidth(180)


    def set_show_mode(self, show_mode=0o377):
        self.show_mode = show_mode
        self.w_dset.setVisible(self.show_mode & 1)
        self.w_chkl.setVisible(self.show_mode & 2)

#------------------------------

    def closeEvent(self, e):
        self.print_list_of_selected_sources()
        self.copy_list_of_selected_sources_to_cp()
        #if self.cp.save_log_at_exit.value() : self.save_log_file()
        QtWidgets.QWidget.closeEvent(self, e)

#------------------------------

    def log_rec_on_start(self) :
        msg = 'user: %s@%s  cwd: %s\n    command: %s'%\
              (psu.get_login(), psu.get_hostname(), psu.get_cwd(), ' '.join(sys.argv))
        self.log.info(msg, self._name)

#------------------------------

    def save_log_file(self, verb=True):
        #self.log.saveLogInFile(self.cp.log_file.value())
        #print 'Log saved in file: %s' % self.cp.log_file.value()
        ##self.log.saveLogTotalInFile(fnm.log_file_total())

        nm.set_cp_and_log(self.cp, self.log)
        path = nm.log_file_repo()
        if psu.create_path(path) :
            self.log.saveLogInFile(path)
            if verb : print('Log saved in file: %s' % path)
        else : self.log.warning('onSave: path for log file %s was not created.' % path, self.name)

#------------------------------

    def update_sources(self):
        t0_sec = time()
        lst_srcs = psu.list_of_sources() # get sources from data
        #lst_det_names = psu.list_of_sources_v1() # get sources from data
        #lst_srcs = ['%s %32s'%(rec[0].ljust(32),rec[1].ljust(32)) for rec in lst_det_names]
        #lst_srcs = ['%s   %s'%(rec[0],rec[1]) for rec in lst_det_names]
        #lst_srcs = [rec[0] for rec in lst_det_names]
        msg = 'Get sources from dataset %s, consumed time (sec) = %.6f' % (nm.dsname(), time()-t0_sec)
        self.log.info(msg, self._name)    

        if lst_srcs is None : 
            self.log.warning('List of sources is empty!', self._name)
            return

        lst_pv_names = psu.list_of_pv_names()
        #lst_pvs = ['%s %32s'%(rec[0].ljust(32),rec[1]) for rec in lst_pv_names]
        lst_pvs = [rec[0] for rec in lst_pv_names]
        msg = 'List of epics names in dataset %s\n' % nm.dsname()
        for i,s in enumerate(lst_pv_names) : msg += '  %03d  %s\n' % (i,str(s))
        #for i,s in enumerate(lst_pvs) : msg += '  %03d  %s\n' % (i,str(s))
        self.log.debug(msg, self._name)

        msg = 'List of sources in dataset %s\n' % nm.dsname()
        for i,s in enumerate(lst_srcs) : msg += '  %02d  %s\n' % (i,s)
        #for i,s in enumerate(lst_det_names) : msg += '  %02d  %s\n' % (i,str(s))
        self.log.info(msg, self._name)    

        self.print_list_of_sources_in_cp()

        lst_tot = list(lst_srcs) + lst_pvs

        #print 'lst_tot\n'
        #for i,s in enumerate(lst_tot) : print '  XXX: %03d  %s' % (i,s)

        # make dictionary for GUI
        #self.dic_srcs = dict(zip(lst_tot, len(lst_tot)*[False]))
        self.dic_srcs = collections.OrderedDict(zip(lst_tot, len(lst_tot)*[False]))

        for p in self.cp.det_src_list :
            src = p.value()
            if src is None : continue
            if src in lst_tot : self.dic_srcs[src]=True

        self.w_chkl.set_dic_item_state(self.dic_srcs)

        #print_dic(self.dic_srcs)

#------------------------------

    def print_list_of_sources_in_cp(self) :
        msg = 'Sources in configpars (cp.number_of_sources_max = %d)\n' %  self.cp.number_of_sources_max     
        for i, p in enumerate(self.cp.det_src_list) :
            src = p.value()
            if src is 'None' : continue
            msg += '  %02d  %s\n' % (i, src)
        self.log.info(msg, self._name)    

#------------------------------

    def print_list_of_selected_sources(self) :
        msg = 'List of selected sources for dataset %s :\n' % nm.dsname()
        for s in self.list_of_selected_sources() : 
            msg += '  %s\n' % s
        self.log.info(msg, self._name)    

#------------------------------

    def copy_list_of_selected_sources_to_cp(self) :
        lst_srcs_sel = self.list_of_selected_sources()
        num_src_sel = len(lst_srcs_sel)

        if num_src_sel > self.cp.number_of_sources_max :
            msg = 'Number of selected sources %d exceeds maximal number of sources %d reserved in configuration parameters'%\
                  (num_src_sel, self.cp.number_of_sources_max)
            self.log.warning(msg, self._name) 

        for i, p in enumerate(self.cp.det_src_list) :
            if i>=num_src_sel : p.setDefault()
            else : p.setValue(lst_srcs_sel[i]) 

#------------------------------

    def list_of_selected_sources(self) :
        return [src for src,status in self.dic_of_sources().items() if status]

#------------------------------

    def dic_of_sources(self):
        return self.w_chkl.get_dic_item_state()

#------------------------------

    def on_runnum_is_changed(self) :
        msg = 'Run number is changed to %s' % (self.cp.str_runnum.value())
        self.log.debug(msg, self._name)    
        self.update_sources()

#------------------------------
#------------------------------
#------------------------------

def select_data_sources(fname=None, verb=1, bwlog=0) :
    from expmon.SSConfigParameters import cp
    from expmon.Logger import log
    global app # to fix issue with message "QObject::startTimer: QTimer can only be used..."

    log.setPrintBits(bwlog)
    if fname is not None : cp.readParametersFromFile(fname=fname)

    nm.set_config_pars(cp)

    app = QtWidgets.QApplication(sys.argv)

    w = SSQSourceSelector(cp, log) 
    w.setWindowTitle('Data source selector')
    w.setMinimumWidth(350)
    w.move(QtCore.QPoint(50,50))
    w.show()

    app.exec_()

    cp.saveParametersInFile(fname)
    if verb : print('Configuration parameters saved in file: %s' % cp.fname)

    if cp.save_log_at_exit.value() : 
        w.save_log_file(verb & 2)

    return w.list_of_selected_sources()

#------------------------------

if __name__ == "__main__" :
    lst_srcs = select_data_sources(fname='sourse-selector-confpars-my.txt', verb=0o377, bwlog=0o377)
    print('List of selected sources:')
    for s in lst_srcs : print(s)
    sys.exit()

#------------------------------
