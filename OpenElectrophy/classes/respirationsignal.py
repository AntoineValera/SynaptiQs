# -*- coding: utf-8 -*-
"""

"""

from sqlalchemy import Column, Integer, String, Float, Text, Unicode
from sqlalchemy import orm

import numpy
from scipy import signal
from scipy import interpolate , digitize , nan , arccos
from numpy import abs

from base import OEBase



class RespirationSignal( OEBase):
    parents = [ 'segment'  ,]
    children = [ ]
    fields = [  ['name' , Text],
                    ['channel' , Integer],
                    ['t_start' , Float],
                    ['sampling_rate' , Float],
                    ['signal' , numpy.ndarray],
                    ['cycle_times' , numpy.ndarray],
                ]
    tablename = 'respirationsignal'
    def __init__(self, *args , **kargs):
        """
        """
        OEBase.__init__(self, *args, **kargs)
        for k,v in self.fields:
            if k in kargs:
                self[k] = kargs[k]
        self._t = None
        

    @orm.reconstructor
    def init_on_load(self):
        OEBase.init_on_load(self)
        self._t = None


    def compute_time_vector(self) :
        return numpy.arange(len(self.signal), dtype = 'f8')/self.sampling_rate + self.t_start

    def t(self):
        if self._t==None:
            self._t=self.compute_time_vector()
        return self._t



    plotAptitudes =    [   [ 'natural' , {  
                                                        'name' : 'natural bandwith plot',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [   [ 'color' , {'value' : 'g' }],
                                                        
                                                                           ],
                                                    }
                                    ],
                                ]


    def plot_natural(self , color = 'g', t_start = None, **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        t  = self.t()
        if t_start  is not  None:
            t = t - t[0] + t_start
        
        return ax.plot(t, self.signal , color = color)


