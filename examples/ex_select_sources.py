#!/usr/bin/env python

#------------------------------

from __future__ import print_function
def print_list_of_sources(lst, cmt='List of sources:') :
    print(cmt)
    for i,src in enumerate(lst) : print('  %02d  %s'%(i,src))

#------------------------------

def test_select_sources_on_flight(fname=None) :
    print('%s.%s' % (__name__, sys._getframe().f_code.co_name))
    from expmon.SSQSourceSelector import select_data_sources
    list_of_sources = select_data_sources(fname=fname, verb=1)
    print_list_of_sources(list_of_sources, cmt='List of selected sources:')

#------------------------------

def test_select_sources_from_config_file(fname=None) :
    print('%s.%s' % (__name__, sys._getframe().f_code.co_name))
    from expmon.SSConfigParameters import cp
    if fname is not None : cp.readParametersFromFile(fname=fname)
    list_of_sources = [p.value() for p in cp.det_src_list if p.value() is not 'None']
    print_list_of_sources(list_of_sources, cmt='List of selected sources:')

#------------------------------

def test_access_to_other_config_parameters(fname=None) :
    print('%s.%s' % (__name__, sys._getframe().f_code.co_name))
    from expmon.SSConfigParameters import cp
    #from expmon.PSNameManager import nm
    if fname is not None : cp.readParametersFromFile(fname=fname)
    #nm.set_config_pars(cp)
    #print 'dataset %s' % nm.dsname()
    print('instr_name  %s' % cp.instr_name .value())
    print('exp_name    %s' % cp.exp_name   .value())
    print('str_runnum  %s' % cp.str_runnum .value())
    print('calib_dir   %s' % cp.calib_dir  .value())

#------------------------------

if __name__ == "__main__" :
    import sys

    MY_CONFIG_PARS_FILE_NAME = 'sourse-selector-confpars-my.txt'

    tname = sys.argv[1] if len(sys.argv) > 1 else '1'
    print(50*'_', '\nTest %s:' % tname)
    if   tname == '1': test_select_sources_on_flight()
    elif tname == '2': test_select_sources_from_config_file()
    elif tname == '3': test_access_to_other_config_parameters()
    elif tname == '4': test_select_sources_on_flight(fname=MY_CONFIG_PARS_FILE_NAME)
    elif tname == '5': test_select_sources_from_config_file(fname=MY_CONFIG_PARS_FILE_NAME)
    elif tname == '6': test_access_to_other_config_parameters(fname=MY_CONFIG_PARS_FILE_NAME)
    else : print('Not-recognized test name: %s' % tname)

#------------------------------


