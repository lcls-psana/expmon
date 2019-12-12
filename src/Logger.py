#------------------------------
"""Logger - logger for package detmon.

@see class :py:class:`detmon.Logger`

@see project modules
    * :py:class:`detmon.Logger`
    * :py:class:`CalibManager.Logger`
    * :py:class:`CalibManager.ConfigParameters`
    * :py:class:`detmon.EMConfigParameters`

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

@version $Id:Logger.py 11923 2016-05-17 21:14:33Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
from __future__ import print_function
#------------------------------

from CalibManager.Logger import logger as log

#------------------------------

def test_log() :

    # set level: 'debug','info','warning','error','critical'
    log.setLevel('warning') 

    # print messages of all levels: 1,2,4,8,16 for 'debug','info',...
    log.setPrintBits(0o377) 
    
    log.debug   ('This is a test message 1', __name__)
    log.info    ('This is a test message 2', __name__)
    log.warning ('This is a test message 3', __name__)
    log.error   ('This is a test message 4', __name__)
    log.critical('This is a test message 5', __name__)
    log.critical('This is a test message 6')

    print('getLogContent():\n',      log.getLogContent())
    print('getLogContentTotal():\n', log.getLogContentTotal())

    #log.saveLogInFile()
    #log.saveLogTotalInFile()

#------------------------------

if __name__ == "__main__" :
    test_log()

#------------------------------
