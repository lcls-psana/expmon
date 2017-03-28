#------------------------------
# Description:
#------------------------------

"""EMQLogger - GUI for logger

This software was developed for the SIT project.  If you use all or 
part of it, please give an appropriate acknowledgment.

@version $Id: EMQLogger.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------
import os

from expmon.EMConfigParameters import cp
from expmon.Logger             import log
from PyQt4 import QtGui, QtCore
from graphqt.Styles            import style
#from graphqt.QIcons            import icon

#------------------------------

class EMQLogger(QtGui.QWidget) :
    """GUI for Logger"""

    _name = 'EMQLogger'

    def __init__(self, parent=None, show_buttons=True) :

        QtGui.QWidget.__init__(self, parent)

        self.show_buttons = show_buttons
        
        self.setGeometry(200, 400, 500, 300)
        self.setWindowTitle(self._name)

        #icon.set_icons()
        #self.setWindowIcon(cp.icon_logger)

        self.box_txt    = QtGui.QTextEdit()
 
        #self.tit_title = QtGui.QLabel('Logger')
        self.tit_status = QtGui.QLabel('Status:')
        self.tit_level  = QtGui.QLabel('Verbosity level:')
        self.but_close  = QtGui.QPushButton('&Close') 
        self.but_save   = QtGui.QPushButton('&Save log-file') 

        self.list_of_levels = log.getListOfLevels()
        self.box_level      = QtGui.QComboBox(self) 
        self.box_level.addItems(self.list_of_levels)
        self.box_level.setCurrentIndex(self.list_of_levels.index(cp.log_level.value()))
        
        self.hboxM = QtGui.QHBoxLayout()
        self.hboxM.addWidget(self.box_txt)

        self.hboxB = QtGui.QHBoxLayout()
        self.hboxB.addWidget(self.tit_status)
        self.hboxB.addStretch(4)     
        self.hboxB.addWidget(self.tit_level)
        self.hboxB.addWidget(self.box_level)
        self.hboxB.addStretch(1)     
        self.hboxB.addWidget(self.but_save)
        self.hboxB.addWidget(self.but_close)

        self.vbox  = QtGui.QVBoxLayout()
        #self.vbox.addWidget(self.tit_title)
        self.vbox.addLayout(self.hboxM)
        self.vbox.addLayout(self.hboxB)
        self.setLayout(self.vbox)

        if self.show_buttons :
          self.connect(self.but_close, QtCore.SIGNAL('clicked()'), self.onClose)
          self.connect(self.but_save,  QtCore.SIGNAL('clicked()'), self.onSave)
          self.connect(self.box_level, QtCore.SIGNAL('currentIndexChanged(int)'), self.onBox)
 
        self.startGUILog()

        self.set_tool_tips()
        self.set_style()

        cp.emqlogger = self


    def set_tool_tips(self):
        #self           .setToolTip('This GUI is for browsing log messages')
        self.box_txt    .setToolTip('Window for log messages')
        self.but_close  .setToolTip('Close this window')
        self.but_save   .setToolTip('Save current content of the GUI Logger\nin work directory file: '+os.path.basename(self.fname_log))
        self.tit_status .setToolTip('The file name, where this log \nwill be saved at the end of session')
        self.box_level  .setToolTip('Click on this button and \nselect the level of messages \nwhich will be displayed')


    def set_style(self):
        self.           setStyleSheet(style.styleBkgd)
        #self.tit_title.setStyleSheet(style.styleTitleBold)
        self.tit_status.setStyleSheet(style.styleTitle)
        self.tit_level .setStyleSheet(style.styleTitle)
        self.but_close .setStyleSheet(style.styleButton)
        self.but_save  .setStyleSheet(style.styleButton) 
        self.box_level .setStyleSheet(style.styleButton) 
        self.box_txt   .setReadOnly(True)
        self.box_txt   .setStyleSheet(style.styleWhiteFixed) 
        #self.box_txt   .ensureCursorVisible()
        #self.tit_title.setAlignment(QtCore.Qt.AlignCenter)
        #self.titTitle.setBold()

        self.tit_status.setVisible(self.show_buttons)
        self.tit_level .setVisible(self.show_buttons)
        self.box_level .setVisible(self.show_buttons)
        self.but_save  .setVisible(self.show_buttons)
        self.but_close .setVisible(self.show_buttons)

        if not self.show_buttons : self.setContentsMargins(QtCore.QMargins(-9,-9,-9,-9))
        self.setMinimumHeight(50)
        self.setMinimumSize(300,50)
        #self.setBaseSize(500,200)


    def setParent(self,parent) :
        self.parent = parent


    #def resizeEvent(self, e):
        #log.debug('resizeEvent', self._name) 
        #pass


    #def moveEvent(self, e):
        #log.debug('moveEvent', self._name) 
        #cp.posGUIMain = (self.pos().x(),self.pos().y())
        #pass


    def closeEvent(self, e):
        log.debug('closeEvent', self._name)
        #log.info('%s.closeEvent' % self._name)
        #self.saveLogTotalInFile() # It will be saved at closing of GUIMain
        QtGui.QWidget.closeEvent(self, e)


    def onClose(self):
        log.debug('onClose', self._name)
        self.close()


    def onSave(self):
        log.debug('onSave:', self._name)
        self.saveLogInFile()


    def onBox(self):
        level_selected = self.box_level.currentText()
        cp.log_level.setValue( level_selected ) 
        log.info('onBox - selected ' + self.tit_level.text() + ' ' + cp.log_level.value(), self._name)
        log.setLevel(cp.log_level.value())
        self.box_txt.setText(log.getLogContent())


    def saveLogInFile(self):
        log.info('saveLogInFile ' + self.fname_log, self._name)
        path = str(QtGui.QFileDialog.getSaveFileName(self,
                                                     caption   = 'Select the file to save log',
                                                     directory = self.fname_log,
                                                     filter    = '*.txt'
                                                     ))
        if path == '' :
            log.debug('Saving is cancelled.', self._name)
            return 
        log.info('Output file: ' + path, self._name)
        log.saveLogInFile(path)
        self.fname_log = path
        cp.log_file.setValue(path)


    def saveLogTotalInFile(self):
        log.info('saveLogTotalInFile' + self.fname_log_total, self._name)
        log.saveLogTotalInFile(self.fname_log_total)


    def getConfirmation(self):
        """Pop-up box for confirmation"""
        msg = QtGui.QMessageBox(self, windowTitle='Confirm closing!',
            text='You are about to close GUI Logger...\nIf the log-file is not saved it will be lost.',
            standardButtons=QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
        msg.setDefaultButton(msg.Save)

        clicked = msg.exec_()

        if   clicked == QtGui.QMessageBox.Save :
            log.info('Saving is requested', self._name)
        elif clicked == QtGui.QMessageBox.Discard :
            log.info('Discard is requested', self._name)
        else :
            log.info('Cancel is requested', self._name)
        return clicked


    def onShow(self):
        log.info('onShow - is not implemented yet...', self._name)


    def startGUILog(self) :
        self.fname_log = cp.log_file.value()
        #self.fname_log_total = cp.log_file_total.value()
        self.setStatus(0, 'Log-file: ' + os.path.basename(self.fname_log))

        log.setLevel(cp.log_level.value())
        self.box_txt.setText(log.getLogContent())
        
        log.setGUILogger(self) 
        log.debug('EMQLogger is open', self._name)
        self.box_txt.moveCursor(QtGui.QTextCursor.End)


    def appendGUILog(self, msg='...'):
        self.box_txt.append(msg)
        self.scrollDown()


    def scrollDown(self):
        #print 'scrollDown'
        #scrol_bar_v = self.box_txt.verticalScrollBar() # QScrollBar
        #scrol_bar_v.setValue(scrol_bar_v.maximum()) 
        self.box_txt.moveCursor(QtGui.QTextCursor.End)
        self.box_txt.repaint()
        #self.raise_()
        #self.box_txt.update()

        
    def setStatus(self, status_index=0, msg=''):
        list_of_states = ['Good','Warning','Alarm']
        if status_index == 0 : self.tit_status.setStyleSheet(style.styleStatusGood)
        if status_index == 1 : self.tit_status.setStyleSheet(style.styleStatusWarning)
        if status_index == 2 : self.tit_status.setStyleSheet(style.styleStatusAlarm)

        #self.tit_status.setText('Status: ' + list_of_states[status_index] + msg)
        self.tit_status.setText(msg)

#------------------------------

if __name__ == "__main__" :
    import sys
    app = QtGui.QApplication(sys.argv)
    widget = EMQLogger()
    widget.show()
    app.exec_()
    sys.exit(0)

#------------------------------
