# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy

from base import OEBase


# for defitions list
__doc__ = neo.core.Epoch.definition

class Epoch(neo.core.Epoch , OEBase):
    __doc__ = neo.core.Epoch.__doc__ + \
    """This OpenElectrophy object inherits from neo.core.Epoch.
    
    An object representing a period of time.
    """
    
    parents = [ 'segment'  ]
    children = [  ]
    fields = [  ['name' , Text],
                    ['label' , Text],
                    ['time' , Float],
                    ['duration' , Float],
                    ['num', Integer],
                ]
    tablename = 'epoch'
    def __init__(self, *args , **kargs):
        """In addition to neo initialization (see neo.core.Epoch),
        we set the following SQL fields:
            name, Text
            label, Text
            time, Float
            duration, Float
            num, Integer
        """
        neo.core.Epoch.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
        
        

    plotAptitudes = [   [ 'vspan' , {  
                                                        'name' : 'vertival line',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [     [ 'facecolor' , {'value' : 'g' }],
                                                                                [ 'alpha' , {'value' : .3 }],
                                                                           ],
                                                    }
                                    ] ,
                                ]

    def plot_vspan(self , facecolor = 'g', alpha=.3, **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        return ax.axvspan(self.time, self.time+self.duration, facecolor=facecolor, alpha=0.5)



