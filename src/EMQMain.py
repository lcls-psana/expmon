
#------------------------------
"""
@version $Id: EMQMain.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------

#import os
import sys

from PyQt4 import QtGui, QtCore
from expmon.EMConfigParameters import cp
from expmon.Logger             import log
#from expmon.EMQLogger          import EMQLogger
from expmon.EMQTabs            import EMQTabs
from expmon.QWInsExpRun        import QWInsExpRun
from graphqt.QWLogger          import QWLogger
from graphqt.QIcons            import icon
from graphqt.Styles            import style
#import time   # for sleep(sec)

#------------------------------

class EMQMain(QtGui.QWidget) : # Frame)
    """Main GUI
    """
    def __init__(self, parser=None) : # **dict_opts) :
        #Frame.__init__(self, parent=None, mlw=5)
        QtGui.QWidget.__init__(self, parent=None)
        self._name = self.__class__.__name__

        log.setPrintBits(0377)

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

        self.emqinsexprun = QWInsExpRun(cp, log) # QtGui.QPushButton('button') 
        self.emqtabs      = EMQTabs(self) # QtGui.QTextEdit()
        self.emqlogger    = QWLogger(log, cp, show_buttons=False)

        self.vsplit = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.vsplit.addWidget(self.emqinsexprun)
        self.vsplit.addWidget(self.emqtabs)
        self.vsplit.addWidget(self.emqlogger)
        #self.vsplit.moveSplitter(0,200)

        self.vbox = QtGui.QVBoxLayout() 
        #self.vbox.addWidget(self.guibuttonbar)
        #self.vbox.addWidget(self.guiinsexpdirdet)
        #self.vbox.addLayout(self.hboxB) 
        #self.vbox.addStretch(1)
        self.vbox.addWidget(self.vsplit) 

        self.setLayout(self.vbox)

        self.set_tool_tips()
        self.set_style()

        self.move(self.main_win_pos_x.value(), self.main_win_pos_y.value())
        cp.guimain = self

    #-------------------

    def printStyleInfo(self):
        qstyle     = self.style()
        qpalette   = qstyle.standardPalette()
        qcolor_bkg = qpalette.color(1)
        #r,g,b,alp  = qcolor_bkg.getRgb()
        msg = 'Background color: r,g,b,alpha = %d,%d,%d,%d' % ( qcolor_bkg.getRgb() )
        log.debug(msg)


    def set_tool_tips(self):
        self.setToolTip('Experiment Monitor Control GUI')

    def set_style(self):
        self.setMinimumSize(770,500)
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

        try    : self.emqinsexprun.close()   
        except : pass
     
        try    : self.emqtabs.close()
        except : pass
        
        try    : cp.emqlogger.close()
        except : pass

        self.on_save()

        QtGui.QWidget.closeEvent(self, e)


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

        #try :
        #    ndb = NotificationDB()
        #    ndb.add_record()
        #except :
        #    pass
 
        #cp.close()

        cp.printParameters()
        cp.saveParametersInFile()

        if cp.save_log_at_exit.value() :
            log.saveLogInFile(cp.log_file.value())
            #print 'Saved log file: %s' % cp.log_file.value()
            #log.saveLogTotalInFile(fnm.log_file_total())

#------------------------------
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
    app = QtGui.QApplication(sys.argv)
    ex  = EMQMain(parser=None)
    ex.show()
    app.exec_()
#------------------------------
