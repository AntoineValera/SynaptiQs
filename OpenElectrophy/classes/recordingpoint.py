# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode, DateTime
import numpy

from base import OEBase

# for defitions list
__doc__ = neo.core.RecordingPoint.definition



class RecordingPoint(neo.core.RecordingPoint , OEBase):
    __doc__ = neo.core.RecordingPoint.__doc__
    
    """
    
    """
    parents = [ 'block' ]
    children = ['analogsignal' , 'spiketrain']
    fields = [  ['name' , Text],
                    ['channel' , Integer],
                    ['info' , Text],
                    ['group' , Integer],
                    ['trodness' , Integer],
                ]
    tablename = 'recordingpoint'
    def __init__(self, *args , **kargs):
        """
        """
        neo.core.RecordingPoint.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
