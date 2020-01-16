#------------------------------
"""
@version $Id: QWDataControl.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
from __future__ import print_function
#------------------------------
import sys
import os
from expmon.EMQFrame import Frame
from PyQt5 import QtCore, QtGui, QtWidgets

import graphqt.QWUtils         as qwu
from graphqt.QWDirName         import QWDirName
from expmon.QWEventControl     import QWEventControl
from expmon.QWDataSource       import QWDataSource
from expmon.QWDataSetExtension import QWDataSetExtension
import expmon.EMUtils          as emu
from expmon.EMQUtils           import popup_select_experiment
from graphqt.QWPopupSelectItem import popup_select_item_from_list
from expmon.PSNameManager      import nm
from graphqt.Styles            import style

#------------------------------

class QWDataControl(Frame) :
    """GUI to input instrument, experiment, and run number
    """
    expname_is_changed = QtCore.pyqtSignal()
    runnum_is_changed = QtCore.pyqtSignal()

    def __init__(self, cp, log, parent=None, orient='V', show_mode=1) :
        """cp (ConfigParameters) is passed as a parameter in order to use this widget in different apps
           Depends on:
           cp.char_expand
           cp.list_of_instr
           cp.list_of_sources

           cp.instr_name  - par
           cp.exp_name    - par
           cp.str_runnum  - par
           cp.calib_dir   - par
           cp.data_source - par

           show_mode & 1 - calib
                     & 2 - source
                     & 4 - event control
                     & 8 - dataset extension
        """

        Frame.__init__(self, parent, mlw=1)
        self._name = self.__class__.__name__

        self.cp     = cp
        self.log    = log
        self.parent = parent
        self.orient = orient
        self.show_mode = show_mode

        # Constants
        self.char_expand   = cp.char_expand
        self.list_of_instr = cp.list_of_instr

        # Parameters
        self.instr_name = cp.instr_name
        self.exp_name   = cp.exp_name
        self.str_runnum = cp.str_runnum
        self.calib_dir  = cp.calib_dir

        self.lab_ins = QtWidgets.QLabel('Ins:')
        self.lab_exp = QtWidgets.QLabel('Exp:')
        self.lab_run = QtWidgets.QLabel('Run:')

        self.but_ins = QtWidgets.QPushButton(self.instr_name.value()) # + self.char_expand)
        self.but_exp = QtWidgets.QPushButton(self.exp_name.value())
        self.but_run = QtWidgets.QPushButton(self.str_runnum.value())
        self.w_dsext = QWDataSetExtension(cp, log)
        self.w_calib = QWDirName(None, butname='Select', label='Clb:',\
                                 path=self.calib_dir.value(), show_frame=False)
        self.w_calib.connect_path_is_changed_to_recipient(self.on_but_calib)

        self.w_src = QWDataSource(cp, log)
        self.w_evt = QWEventControl(cp, log, show_mode=0o377)

        if self.orient=='H' : self.set_layout_hor()
        else                : self.set_layout_ver()
 
        self.set_style()
        self.set_show_mode(show_mode)
        self.set_tool_tips()

        self.but_ins.clicked.connect(self.on_but_ins)
        self.but_exp.clicked.connect(self.on_but_exp)
        self.but_run.clicked.connect(self.on_but_run)


    def event_control(self):
        return self.w_evt


    def set_layout_hor(self):
        self.box = QtWidgets.QHBoxLayout(self)
        self.box.addWidget(self.lab_ins)
        self.box.addWidget(self.but_ins)
        #self.box.addStretch(1)
        self.box.addWidget(self.lab_exp)
        self.box.addWidget(self.but_exp)
        #self.box.addStretch(1)
        self.box.addWidget(self.lab_run)
        self.box.addWidget(self.but_run)
        self.box.addStretch(1)
        self.box.addWidget(self.w_calib)
        #self.box.addLayout(self.box)

        self.setLayout(self.box)
 

    def set_layout_ver(self):
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.lab_ins)
        self.hbox.addWidget(self.but_ins)
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.lab_exp)
        self.hbox.addWidget(self.but_exp)
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.lab_run)
        self.hbox.addWidget(self.but_run)
        self.hbox.addSpacing(20)
        self.hbox.addWidget(self.w_dsext)
        self.hbox.addStretch(1)

        self.w_dset = QtWidgets.QWidget(self)
        self.w_dset.setLayout(self.hbox)

        self.vbox = QtWidgets.QVBoxLayout()
        #self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.w_dset)
        self.vbox.addWidget(self.w_calib)
        self.vbox.addWidget(self.w_src)
        self.vbox.addWidget(self.w_evt)

        self.setLayout(self.vbox)
 

    def set_tool_tips(self):
       self.setToolTip('Data-set control')


    def set_style(self):
        self.setWindowTitle(self._name)
        #self.setMinimumWidth(500)
        #self.setGeometry(10, 25, 400, 600)
        #self.setFixedHeight(100)

        self.w_dsext.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        self.w_dset .setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        self.w_src  .setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        self.w_evt  .setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))

        self.lab_ins.setStyleSheet(style.styleLabel)
        self.lab_exp.setStyleSheet(style.styleLabel)
        self.lab_run.setStyleSheet(style.styleLabel)
        self.w_calib.lab.setStyleSheet(style.styleLabel)
        #self.w_calib.setMinimumWidth(280)
        #self.w_calib.edi.setMinimumWidth(180)

        width = 50
        self.but_ins.setFixedWidth(40)
        self.but_exp.setFixedWidth(80)
        self.but_run.setFixedWidth(width)
        self.w_calib.but.setFixedWidth(width)

        if self.exp_name.is_default() : 
            if self.instr_name.is_default() : self.set_ins()
            self.set_exp()


    def set_show_mode(self, show_mode=0o377):
        self.show_mode = show_mode
        self.w_calib.setVisible(self.show_mode & 1)
        self.w_src  .setVisible(self.show_mode & 2)
        self.w_evt  .setVisible(self.show_mode & 4)
        self.w_dsext.setVisible(self.show_mode & 8)


    def on_but(self):
        if self.but_ins.hasFocus() : print('on_but ins')
        if self.but_exp.hasFocus() : print('on_but exp')
        if self.but_run.hasFocus() : print('on_but run')
        #self.but_current = self.butIns
        #item_selected = gu.selectFromListInPopupMenu(self.list_of_instr)
        #if item_selected is None : return            # selection is cancelled
        #if item_selected == self.instr_name.value() : return # selected the same item  

        #self.setIns(item_selected)
        #self.setExp('Select')
        #self.setDir('Select')
        #self.setDet('Select')
        #self.setStyleButtons()
        #self.lab_run.setStyleSheet(style.styleLabel)

        #self.but_ins.setStyleSheet(style.styleButton)
        #self.but_exp.setStyleSheet(style.styleButton)
        #self.but_run.setStyleSheet(style.styleButton)


    def on_but_ins(self):
        #print 'on_but ins'
        sel = qwu.selectFromListInPopupMenu(self.list_of_instr)
        if sel is None : return

        self.set_exp()
        if sel != self.instr_name.value() :
            #self.set_exp()
            self.set_run()
            self.set_calib()
        self.set_ins(sel, cmt='instrument')


    def on_but_exp(self):
        #print 'XXXXX on_but exp'
        exps = emu.list_of_experiments()
        sel = popup_select_experiment(None, exps)
        if sel is None : return

        if sel != self.exp_name.value() :
            self.set_ins(val=self.instr_name.value(), cmt='instrument')
            self.set_run()

        self.set_exp(sel, cmt='experiment')
        self.set_calib(sel)
        self.expname_is_changed.emit()


    def connect_expname_is_changed_to(self, slot) :
        self.expname_is_changed.connect(slot)


    def disconnect_expname_is_changed_from(self, slot) :
        self.expname_is_changed.disconnect(slot)


    def test_expname_is_changed(self) :
        print('XXX %s.expname_is_changed to %s' % (self._name, self.cp.exp_name.value()))


    def on_but_run(self):
        #print 'on_but run'
        runs = emu.list_of_runs_in_xtc_dir()
        sel = popup_select_item_from_list(None, runs)

        if sel is None : return
        self.set_run(sel, cmt='run')


    def on_but_calib(self, cdir):
        w = self.w_calib
        if str(cdir).rsplit('/',1)[1] != 'calib' :
            self.log.warning('NOT A calib DIRECTORY: %s'%(cdir), self._name)
            w.edi.setStyleSheet(style.styleButtonBad)
            w.but.setStyleSheet(style.styleButtonGood)
            return

        w.edi.setStyleSheet(style.styleWhiteFixed)
        w.but.setStyleSheet(style.styleButton)
        par = self.calib_dir
        par.setValue(cdir)
        w.edi.setText(par.value())


    def set_but_for_par(self, but, par, val=None, cmt=''):
        if val is None :
            par.setDefault()
            but.setStyleSheet(style.styleButtonGood)
        else :
            par.setValue(val)
            self.log.info('selected %s: %s'%(cmt,val), self._name)
            but.setStyleSheet(style.styleButton)
        but.setText(par.value())


    def set_run(self, val=None, cmt=''):
        but_txt_old = str(self.but_run.text())
        if val != self.str_runnum.value() and val is not None :
            # set flag to evaluate list of sources in separate thread
            #self.log.info('set request to find sources for run: %s'% val, self._name)
            #cp.emqthreadworker.set_request_find_sources()
            self.cp.list_of_sources = None # to initiate ThreadWorker to evaluate it
        self.set_but_for_par(self.but_run, self.str_runnum, val, cmt)

        if str(self.but_run.text()) != but_txt_old :
            self.runnum_is_changed.emit()


    def connect_runnum_is_changed_to(self, slot) :
        self.runnum_is_changed.connect(slot)


    def disconnect_runnum_is_changed_from(self, slot) :
        self.runnum_is_changed.disconnect(slot)


    def test_runnum_is_changed(self) :
        print('XXX %s.runnum_is_changed to %s' % (self._name, self.str_runnum.value()))


    def set_exp(self, val=None, cmt=''):
        self.set_but_for_par(self.but_exp, self.exp_name, val, cmt)


    def set_ins(self, val=None, cmt=''):
        self.set_but_for_par(self.but_ins, self.instr_name, val, cmt)


    def set_calib(self, exp=None):
        #print 'XXX: %s.set_calib' % self._name
        par = self.calib_dir
        but = self.w_calib.but
        edi = self.w_calib.edi

        if exp is None :
            par.setDefault()
            but.setStyleSheet(style.styleButtonGood)
        else :
            but.setStyleSheet(style.styleButton)
            par.setValue(nm.dir_calib())

        edi.setText(par.value())
        if self.exp_name.value() == self.exp_name.value_def() : return
        self.log.info('set calib directory: %s'%par.value(), self._name)

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

    #from expmon.PSNameManager      import nm
    from expmon.EMConfigParameters import cp # !!! PASSED AS PARAMETER
    from expmon.PSQThreadWorker import PSQThreadWorker
    from expmon.Logger import log

    nm.set_config_pars(cp)

    app = QtWidgets.QApplication(sys.argv)

    t1 = PSQThreadWorker(cp, parent=None, dt_msec=5000, pbits=0) #0177777)
    t1.start()

    #w = QWDataControl(cp, log, show_mode=0) 
    w = QWDataControl(cp, log, show_mode=0o17) 
    #w.event_control().set_show_mode(show_mode=0)
    #w.event_control().set_show_mode(show_mode=010)
    w.move(QtCore.QPoint(50,50))
    w.show()
    
    t1.quit()
    app.exec_()

#------------------------------
