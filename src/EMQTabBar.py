
#------------------------------
"""Re-implementation of QTabBar

@version $Id: EMQTabBar.py 13131 2017-02-08 00:59:11Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------
import sys
#import os

from PyQt5 import QtCore, QtGui, QtWidgets
#------------------------------

class EMQTabBar(QtWidgets.QTabBar) :
    """Re-implementation of QTabBar - add "+" tab
    """

    def __init__ (self, parent=None, width=80) :
        QtWidgets.QTabBar.__init__(self, parent)
        self.showToolTips()
        self.tab_width = width
        self.tabi_add = None
        self.setTabsClosable(True)
        self.setExpanding(False) # need it to lock tab width
        self.setMinimumWidth(300)
        #self.setGeometry(10, 25, 500, 50)

    #-------------------

    def showToolTips(self):
        self.setToolTip('This is a tabbar') 


    def enterEvent(self, e) :
        #print '%s.enterEvent' % self.__class__.__name__, e.type()
        #if e.type() == QtCore.QEvent.Enter :
        #self.setTabEnabled(self.tabi_add, True)
        #self.setTabsClosable(True)
        self.tabi_add = self.addTab('+')
        self.tabButton(self.tabi_add, QtWidgets.QTabBar.RightSide).resize(0, 0) # hide closing button
        #self.tabButton(self.tabi_add, QtGui.QTabBar.RightSide).hide() # hide closing button


    def leaveEvent(self, e) :
        #print '%s.leaveEvent' % self.__class__.__name__, e.type()
        #if e.type() == QtCore.QEvent.Leave :
        #self.setTabEnabled(self.tabi_add, False)
        #self.setTabsClosable(False)
        if self.tabi_add is not None : self.removeTab(self.tabi_add)
        self.tabi_add = None


    def tabSizeHint(self, index):
        w = self.tab_width
        if index==self.tabi_add or (self.tabText(index)[0] == '+') : w = 30
        h = QtWidgets.QTabBar.tabSizeHint(self, index).height()
        return QtCore.QSize(w, h)


#    def event(self, e) :
#        QtGui.QWidget.event(self, e)
#        print '%s.event' % self.__class__.__name__, e.type()


    #def setExpanding(self, enabled) :
    #    QtGui.QTabBar.setExpanding(self, False)


    #def mouseMoveEvent(self, e) :
    #    print '%s.mouseMoveEvent x,y=' % self.__class__.__name__, e.x(), e.y()


    #def mouseHoverEvent(self, e) :
    #    print '%s.mouseHoverEvent' % self.__class__.__name__


    #def closeEvent(self, event):
        #print '%s.closeEvent' % self.__class__.__name__
        #log.info('closeEvent', self.name)

        #try    : self.gui_win.close()
        #except : pass

#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    ex  = EMQTabBar()
    it1 = ex.addTab('Tab1')
    it2 = ex.addTab('Tab2')
    ex.move(QtCore.QPoint(50,50))
    ex.show()
    app.exec_()

#------------------------------
