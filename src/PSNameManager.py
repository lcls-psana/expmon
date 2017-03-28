#------------------------------
"""
@version $Id: PSNameManager.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin

Usage ::
    see method test_all()
"""
#------------------------------
#import sys
#import os
from expmon.Logger import log
#------------------------------

class PSNameManager :

    def __init__(self, cp=None) :
        log.info('object is init-ed', 'PSNameManager')
        self.cp = cp
        
    def set_config_pars(self, cp) :
        log.info('config pars object is set from file: %s' % cp.fname_cp, 'PSNameManager')
        self.cp = cp
    
    def cpars(self) :
        if self.cp is None :
            from expmon.PSConfigParameters import PSConfigParameters
            self.cp = PSConfigParameters()
        return self.cp

#------------------------------

    def dir_exp(self) :
        """Returns directory of experiments, e.g.: /reg/d/psdm/CXI"""
        return '%s/%s' % (self.cpars().instr_dir.value(), self.cpars().instr_name.value())

#------------------------------

    def dir_xtc(self) :
        """Returns xtc directory, e.g.: /reg/d/psdm/CXI/cxi02117/xtc"""
        return '%s/%s/%s/%s' % (self.cpars().instr_dir.value(), self.cpars().instr_name.value(), self.cpars().exp_name.value(), 'xtc')
    
#------------------------------

    def dir_calib(self) :
        """Returns calib directory, e.g.: /reg/d/psdm/CXI/cxi02117/calib"""
        return '%s/%s/%s/%s' % (self.cpars().instr_dir.value(), self.cpars().instr_name.value(), self.cpars().exp_name.value(), 'calib')

#------------------------------

    def dsname(self, ext=None) :
        """Returns string like exp=cxi12316:run=1234:..."""
        base = 'exp=%s:run=%s' % (self.cpars().exp_name.value(), self.cpars().str_runnum.value().lstrip('0'))
        dsn = base if ext is None else '%s:%s' % (base, ext)
        #print 'XXX: EMNameManager.dsname dsn:', dsn
        return dsn

#------------------------------

nm = PSNameManager()

#------------------------------

def test_all() :

    log.setPrintBits(0377)

    #from expmon.PSNameManager import nm
    from expmon.EMConfigParameters import cp
    nm.set_config_pars(cp)

    print 'dir_exp   :', nm.dir_exp()
    print 'dir_xtc   :', nm.dir_xtc()
    print 'dir_calib :', nm.dir_calib()
    print 'dsname    :', nm.dsname('<some-extension-is-here>')

#------------------------------

if __name__ == "__main__" :
    test_all()

#------------------------------
