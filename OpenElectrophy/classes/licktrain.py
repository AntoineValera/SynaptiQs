# -*- coding: utf-8 -*-
"""

"""

from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy

from base import OEBase



class LickTrain( OEBase):
    """
    Class to handle a lick train of an animal.
    
    """
    parents = [ 'segment' ]
    children = [ ]
    fields = [  ['name' , Text],
                    ['num' , Integer],
                    ['t_start' , Float],
                    ['t_stop' , Float],
                    ['lick_times' , numpy.ndarray],
                    ['lick_durations' , numpy.ndarray],
                ]
    tablename = 'licktrain'
    def __init__(self, *args , **kargs):
        """
        """
        for k,v in kargs.iteritems():
            if k in dict(self.fields):
                setattr(self, k, v)
        
        OEBase.__init__(self, *args, **kargs)
        
    plotAptitudes = [  
                            
                            ]
    

