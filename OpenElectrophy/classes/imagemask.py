# -*- coding: utf-8 -*-
"""

"""




from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy
from scipy import signal
from scipy import interpolate , digitize , nan , arccos
from numpy import abs

from base import OEBase
from sqlalchemy import orm



class ImageMask( OEBase):
    """
    
    """
    parents = [ 'block' ]
    children = [ ]
    fields = [   ['name' , Text],
                    ['info' , Text],
                    ['mask' , numpy.ndarray],
                ]
    tablename = 'imagemask'
    def __init__(self, *args , **kargs):
        """
        """
        for k,v in kargs.iteritems():
            if k in dict(self.fields):
                setattr(self, k, v)
        
        OEBase.__init__(self, *args, **kargs)
        
        
    #~ @orm.reconstructor
    #~ def init_on_load(self):
