# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy

from base import OEBase

# for defitions list
__doc__ = neo.core.Event.definition



class Event(neo.core.Event , OEBase):
    
    __doc__ = neo.core.Event.__doc__ + \
    """This OpenElectrophy object inherits `from neo.core.Event`."""
    
    parents = [ 'segment'  ]
    children = [  ]
    fields = [  ['name' , Text],
                    ['label' , Text],
                    ['time' , Float],
                    ['num', Integer],
                ]
    tablename = 'event'
    def __init__(self, *args , **kargs):
        """Creates a new Event.
        
        In addition to neo.core.Event initialization, the following SQL
        fields are set:
            name: Text
            label: Text
            time: Float
            num: Integer
        """
        neo.core.Event.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
        
        


    plotAptitudes = [   [ 'vline' , {  
                                                        'name' : 'vertival line',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [   [ 'color' , {'value' : 'r' }],
                                                                           ],
                                                    }
                                    ],
                                ]


    def plot_vline(self , color = 'r', **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        return ax.axvline( self.time, color = color)




    
    