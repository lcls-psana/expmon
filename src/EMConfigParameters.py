#------------------------------
"""EMConfigParameters - class supporting configuration parameters for application.

@see class :py:class:`expmon.EMConfigParameters`

@see project modules
    * :py:class:`expmon.EMConfigParameters`
    * :py:class:`expmon.Logger`
    * :py:class:`CalibManager.Logger`
    * :py:class:`CalibManager.ConfigParameters`

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

@version $Id:EMConfigParameters.py 11923 2016-11-22 14:28:00Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------

# import os
from expmon.PSConfigParameters import PSConfigParameters
from expmon.PSNameManager      import nm # It is here for initialization

#------------------------------

class EMConfigParameters(PSConfigParameters) :
    """A storage of configuration parameters for Experiment Monitor (EM) project.
    """
    MON1 = 1
    MON2 = 2
    tab_names = ['Mon-A', 'Mon-B', 'Mon-C', 'Mon-D']
    tab_types = [ MON1,    MON1,    MON1,    MON2]

    number_of_tabs = len(tab_names)
    number_of_det_pars = 16
    number_of_mon_winds = 3 # scatter, histogram, pearson vs time

    def __init__(self, fname=None) :
        """fname : str - the file name with configuration parameters, if not specified then use default.
        """
        PSConfigParameters.__init__(self)
        #self._name = self.__class__.__name__
        #log.debug('In c-tor', self._name)
        #print 'EMConfigParameters c-tor'# % self._name

        #self.fname_cp = '%s/%s' % (os.path.expanduser('~'), '.confpars-montool.txt') # Default config file name
        self.fname_cp = './emon-confpars.txt' # Default config file name

        self.declareParameters()
        self.readParametersFromFile()

        self.guimain = None
        self.emqmain = None
        #self.emqthreadworker = None
        self.emqpresenter = None
        self.emqdatacontrol = None
        self.emqeventloop = None
        self.emqthreadeventloop = None
        #self.pseventsupplier = None # is used as singleton from PSEventSupplier

        self.list_of_sources = None # if None - updated in the ThreadWorker

        self.flag_do_event_loop = False
        self.flag_nevents_collected = False

        nm.set_config_pars(self)

#------------------------------
        
    def declareParameters(self) :
        # Possible typs for declaration : 'str', 'int', 'long', 'float', 'bool'
        self.log_level = self.declareParameter(name='LOG_LEVEL_OF_MSGS', val_def='info', type='str')
        #self.log_file  = self.declareParameter(name='LOG_FILE_NAME', val_def='/reg/g/psdm/logs/montool/log.txt', type='str')
        self.log_file  = self.declareParameter(name='LOG_FILE_NAME', val_def='emon-log.txt', type='str')

        self.save_log_at_exit = self.declareParameter( name='SAVE_LOG_AT_EXIT', val_def=True,  type='bool')
        self.dir_log_repo    = self.declareParameter(name='DIR_LOG_REPO', val_def='/reg/g/psdm/logs/emon', type='str')

        self.current_tab     = self.declareParameter(name='CURRENT_TAB', val_def='Status', type='str')

        self.data_buf_size   = self.declareParameter(name='DATA_BUF_SIZE', val_def=5000, type='int')
        self.nevents_update  = self.declareParameter(name='EVENTS_UPDATE', val_def=100, type='int')

        self.main_win_pos_x  = self.declareParameter(name='MAIN_WIN_POS_X',  val_def=5,   type='int')
        self.main_win_pos_y  = self.declareParameter(name='MAIN_WIN_POS_Y',  val_def=5,   type='int')
        self.main_win_width  = self.declareParameter(name='MAIN_WIN_WIDTH',  val_def=900, type='int')
        self.main_win_height = self.declareParameter(name='MAIN_WIN_HEIGHT', val_def=600, type='int')

        # LISTS of parameters

        #tab_names = [('TAB_NAME', 'TAB_NAME_DEF' ,'str') for i in range(self.number_of_tabs)]
        #self.tab_name_list = self.declareListOfPars('TAB_NAME', tab_names)

        det1_srcs = [('None', 'None', 'str') for i in range(self.number_of_tabs)]
        det2_srcs = [('None', 'None', 'str') for i in range(self.number_of_tabs)]

        self.det1_src_list = self.declareListOfPars('DET1_SRC', det1_srcs)
        self.det2_src_list = self.declareListOfPars('DET2_SRC', det2_srcs)


        # List of 16 parameters for all tabs,
        # addressed as cp.det1_list_of_pars[parnum][tabind]

        det_par_tabs = [(None, None, 'float') for i in range(self.number_of_tabs)]
        self.det1_list_of_pars = [None] * self.number_of_det_pars
        self.det2_list_of_pars = [None] * self.number_of_det_pars
        for p in range(self.number_of_det_pars) :
            self.det1_list_of_pars[p] = self.declareListOfPars('DET1_PAR%02d'%p, det_par_tabs)
            self.det2_list_of_pars[p] = self.declareListOfPars('DET2_PAR%02d'%p, det_par_tabs)

        # List of 4(x,y,w,h) * number_of_mon_winds parameters for presentation windows of all tabs/mons,
        # addressed as cp.mon_win_pars[parnum][tabind]

        win_par_tabs = [(None, None, 'float') for i in range(self.number_of_tabs)]
        self.mon_win_pars = [None] * self.number_of_mon_winds * 4
        for p in range(self.number_of_mon_winds * 4) :
            self.mon_win_pars[p] = self.declareListOfPars('WIN_PAR%02d'%p, win_par_tabs)

#------------------------------

cp = EMConfigParameters()

#------------------------------

def test_EMConfigParameters() :
    from expmon.Logger import log

    log.setPrintBits(0o377)
    cp.readParametersFromFile()
    cp.printParameters()
    cp.log_level.setValue('debug')
    cp.saveParametersInFile()

#------------------------------

if __name__ == "__main__" :
    import sys
    test_EMConfigParameters()
    sys.exit(0)

#------------------------------
