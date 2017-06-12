#------------------------------
"""Factory method to switch between EMQDet* objects, which support QWidget and data access methods.
   Created: 2017-05-18
   Author : Mikhail Dubrovin

Usage ::
    from expmon.EMQDetF import get_detector_widget
    src = 'SxrEndstation.0:Acqiris.1'
    w = get_detector_widget(None,src)
"""
#------------------------------

from expmon.EMQDetArea    import EMQDetArea
from expmon.EMQDetWF      import EMQDetWF
from expmon.EMQDetGMD     import EMQDetGMD
from expmon.EMQDetI       import EMQDetI

#------------------------------
#DETECTORS = ('OPAL', 'ANDOR', 'ACQIRIS', 'GMD')
# src_upper = src.upper()
#if not any([det in src_upper for det in DETECTORS]) :
#------------------------------

def get_detector_widget(parent=None, src=None) :
    """ Factory method for EMQDet* object
    """
    s_src = str(src)

    if   'Opal'      in s_src : return EMQDetArea(parent, s_src)
    elif 'Andor3d'   in s_src : return EMQDetArea(parent, s_src)
    elif 'Andor'     in s_src : return EMQDetArea(parent, s_src)
    elif 'Princeton' in s_src : return EMQDetArea(parent, s_src)
    elif 'pnCCD'     in s_src : return EMQDetArea(parent, s_src)
    elif 'Rayonix'   in s_src : return EMQDetArea(parent, s_src)
    elif 'Tm6740'    in s_src : return EMQDetArea(parent, s_src)
    elif 'Epix100a'  in s_src : return EMQDetArea(parent, s_src)
    elif 'Cspad2x2'  in s_src : return EMQDetArea(parent, s_src)
    elif 'Cspad'     in s_src : return EMQDetArea(parent, s_src)
    elif 'GMD'       in s_src : return EMQDetGMD (parent, s_src)
    elif 'Acqiris'   in s_src : return EMQDetWF  (parent, s_src)
    elif 'Imp'       in s_src : return EMQDetWF  (parent, s_src)
    else                      : return EMQDetI   (parent, s_src)

#------------------------------
