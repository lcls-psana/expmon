
#------------------------------
"""EMQMain.py
   Created: 2017-02-18
   Author : Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------

#import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from expmon.EMConfigParameters import cp
from expmon.Logger             import log
from expmon.RingBuffer   import RingBuffer
#from expmon.EMQLogger          import EMQLogger
from expmon.EMQTabs            import EMQTabs
from expmon.EMQPresenter       import EMQPresenter
from expmon.EMQDataControl     import EMQDataControl
from graphqt.QWLogger          import QWLogger
from graphqt.QIcons            import icon
from graphqt.Styles            import style
import expmon.PSUtils as psu
from expmon.PSNameManager import nm

#import time   # for sleep(sec)

#------------------------------

class EMQMain(QtWidgets.QWidget) : # Frame)
    """Main GUI
    """
    def __init__(self, parser=None) : # **dict_opts) :
        #Frame.__init__(self, parent=None, mlw=5)
        QtWidgets.QWidget.__init__(self, parent=None)
        self._name = self.__class__.__name__

        #log.setPrintBits(0377)
        self.log_rec_on_start()
        self.save_log_file()

        self.init_parameters(parser)

        cp.dataringbuffer = RingBuffer(size=cp.data_buf_size.value())
        cp.emqpresenter = EMQPresenter(do_self_update=True)

        self.main_win_width  = cp.main_win_width 
        self.main_win_height = cp.main_win_height
        self.main_win_pos_x  = cp.main_win_pos_x 
        self.main_win_pos_y  = cp.main_win_pos_y  

        self.setGeometry(self.main_win_pos_x .value(),\
                         self.main_win_pos_y .value(),\
                         self.main_win_width .value(),\
                         self.main_win_height.value())

        self.setWindowTitle(self._name)

        icon.set_icons()
        self.setWindowIcon(icon.icon_monitor)

        self.emqdatacontrol = EMQDataControl(cp, log, show_mode=0o15)
        self.emqdatacontrol.event_control().set_show_mode(show_mode=0o30)

        self.emqtabs   = EMQTabs(self) # QtWidgets.QTextEdit()
        self.emqlogger = QWLogger(log, cp, show_buttons=False)

        self.vsplit = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.vsplit.addWidget(self.emqdatacontrol)
        self.vsplit.addWidget(self.emqtabs)
        self.vsplit.addWidget(self.emqlogger)
        #self.vsplit.moveSplitter(0,200)

        self.vbox = QtWidgets.QVBoxLayout() 
        #self.vbox.addWidget(self.guibuttonbar)
        #self.vbox.addWidget(self.guiinsexpdirdet)
        #self.vbox.addLayout(self.hboxB) 
        #self.vbox.addStretch(1)
        self.vbox.addWidget(self.vsplit) 

        self.setLayout(self.vbox)

        self.set_tool_tips()
        self.set_style()

        self.move(self.main_win_pos_x.value(), self.main_win_pos_y.value())

        # DOES NOT WORK ???
        #ec = cp.emqdatacontrol.event_control()
        #ro = cp.emqeventloop
        #ro = cp.emqthreadeventloop
        #ec.connect_start_button_to(ro.start_event_loop) # self.on_event_loop
        #ec.connect_stop_button_to(ro.stop_event_loop)
        #ec.connect_new_event_number_to(self.emqeventloop.on_new_event_number)

        #self.connect(self, QtCore.SIGNAL('update(QString)'), self.emqtabs.reset_monitors)
        #cp.emqdatacontrol.connect_expname_is_changed_to(cp.emqdatacontrol.test_expname_is_changed)
        cp.emqdatacontrol.connect_expname_is_changed_to(self.emqtabs.reset_monitors)

        cp.guimain = self

    #-------------------

    def on_event_loop(self) :
        print('XXX EMQMain.on_event_loop')

    #-------------------

    def init_parameters(self, parser):
        self.parser = parser
        (popts, pargs) = parser.parse_args()

        self.args = pargs
        self.opts = vars(popts)
        self.defs = vars(parser.get_default_values())

        verbos = popts.verbos # True
        exp    = popts.exp    # 'mfxn8316' 
        run    = popts.run    # 11
        clb    = popts.clb    # ''
        #nwin1  = popts.nwin1  # 2
        #nwin2  = popts.nwin2  # 3
 
        if exp != self.defs['exp'] :
            cp.exp_name.setValue(exp)
            cp.instr_name.setValue(exp[:3].upper())

        if run != self.defs['run'] : cp.str_runnum.setValue('%d'%run)
        if clb != self.defs['clb'] : cp.calib_dir .setValue(clb)

        #print '%s.init_parameters: TODO assign optional parameters to cp' % self._name

    #-------------------

    def print_style_info(self):
        qstyle     = self.style()
        qpalette   = qstyle.standardPalette()
        qcolor_bkg = qpalette.color(1)
        #r,g,b,alp  = qcolor_bkg.getRgb()
        msg = 'Background color: r,g,b,alpha = %d,%d,%d,%d' % ( qcolor_bkg.getRgb() )
        log.debug(msg, self._name)


    def set_tool_tips(self):
        self.setToolTip('Experiment Monitor Control GUI')


    def set_style(self):
        self.setMinimumSize(400,500)
        self.setContentsMargins(QtCore.QMargins(-5,-5,-5,-5))

        #self.setFixedSize(800,500)
        #self.setMaximumHeight(700)
        #self.vsplit.setMinimumHeight(700)
        
        #self.        setStyleSheet(style.styleBkgd)
        #self.butSave.setStyleSheet(style.styleButton)
        #self.butExit.setStyleSheet(style.styleButton)
        #self.butELog.setStyleSheet(style.styleButton)
        #self.butFile.setStyleSheet(style.styleButton)

        #self.butELog    .setVisible(False)
        #self.butFBrowser.setVisible(False)

        #self.butSave.setText('')
        #self.butExit.setText('')
        #self.butExit.setFlat(True)

        #self.vsplit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)


    def resizeEvent(self, e):
        #log.debug('resizeEvent', self._name) 
        #print 'EMQMain resizeEvent: %s' % str(self.size())
        pass


    def moveEvent(self, e):
        #log.debug('moveEvent', self._name) 
        #self.position = self.mapToGlobal(self.pos())
        #self.position = self.pos()
        #log.debug('moveEvent - pos:' + str(self.position), __name__)       
        #print 'Move window to x,y: ', str(self.mapToGlobal(QtCore.QPoint(0,0)))
        pass


    def closeEvent(self, e):
        log.info('closeEvent', self._name)

        try    : self.emqdatacontrol.close()
        except : pass
     
        try    : self.emqtabs.close()
        except : pass
        
        try    : cp.emqlogger.close()
        except : pass

        cp.emqpresenter.__del__()

        #cp.emqeventloop.__del__()
        #cp.emqthreadeventloop.__del__()

        self.on_save()

        QtWidgets.QWidget.closeEvent(self, e)


    def on_save(self):

        point, size = self.mapToGlobal(QtCore.QPoint(-5,-22)), self.size() # Offset (-5,-22) for frame size.
        x,y,w,h = point.x(), point.y(), size.width(), size.height()
        msg = 'Save main window x,y,w,h : %d, %d, %d, %d' % (x,y,w,h)
        log.info(msg, self._name)
        #print msg

        #Save main window position and size
        self.main_win_pos_x .setValue(x)
        self.main_win_pos_y .setValue(y)
        self.main_win_width .setValue(w)
        self.main_win_height.setValue(h)

        #cp.printParameters()
        cp.saveParametersInFile()

        self.save_log_file()


    def save_log_file(self):

        if cp.save_log_at_exit.value() :
            #log.saveLogInFile(cp.log_file.value())
            #print 'Saved log file: %s' % cp.log_file.value()
            #log.saveLogTotalInFile(fnm.log_file_total())

            nm.set_cp_and_log(cp, log)
            path = nm.log_file_repo()

            if psu.create_path(path) :
                log.saveLogInFile(path)
                print('Saved log file: %s' % path)
            else : log.warning('onSave: path for log file %s was not created.' % path, self.name)
  
#------------------------------

    def log_rec_on_start(self) :
        msg = 'user: %s@%s  cwd: %s\n    command: %s'%\
              (psu.get_login(), psu.get_hostname(), psu.get_cwd(), ' '.join(sys.argv))
        log.info(msg, self._name)

#------------------------------

    #def mousePressEvent(self, event):
    #    print 'event.x, event.y, event.button =', str(event.x()), str(event.y()), str(event.button())         

    #def mouseReleaseEvent(self, event):
    #    print 'event.x, event.y, event.button =', str(event.x()), str(event.y()), str(event.button())                

    # http://doc.qt.nokia.com/4.6/qt.html#Key-enum
    def keyPressEvent(self, event):
        #print 'event.key() = %s' % (event.key())
        if event.key() == QtCore.Qt.Key_Escape:
            #self.close()
            self.SHowIsOn = False    
            pass

        if event.key() == QtCore.Qt.Key_B:
            #print 'event.key() = %s' % (QtCore.Qt.Key_B)
            pass

        if event.key() == QtCore.Qt.Key_Return:
            #print 'event.key() = Return'
            pass

        if event.key() == QtCore.Qt.Key_Home:
            #print 'event.key() = Home'
            pass

#------------------------------
#  In case someone decides to run this module
#
if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    ex  = EMQMain(parser=None)
    ex.show()
    app.exec_()
#------------------------------
