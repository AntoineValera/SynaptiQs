# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy

from numpy import arange

from base import OEBase

# for defitions list
__doc__ = neo.core.Spike.definition



class Spike(neo.core.Spike , OEBase):
    __doc__ = neo.core.Spike.__doc__
    
    parents = [ 'spiketrain']
    children = [  ]
    fields = [  ['time' , Text],
                    ['waveform' , numpy.ndarray],
                    ['sampling_rate' , Float],
                ]
    tablename = 'spike'
    def __init__(self, *args , **kargs):
        """
        """
        neo.core.Spike.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
        
        



    plotAptitudes = [   
                                [ 'waveform' , {  
                                                        'name' : 'Waveform',
                                                        'default_selected' :  True,
                                                        'ax_needed' : None,
                                                        'fig_needed' : 1,
                                                        'widget_needed' : None,
                                                        'stackable' : False,
                                                        'params' :  [    [ 'color' , {'value' : 'g' }],
                                                                            ],
                                                    }
                                ],


                            ]
        


    def plot_waveform(self ,color = 'g',
                                    max_spike =  200,
                                    average_mode = False,
                                    **kargs):
        if 'fig'in kargs:
            fig = kargs['fig']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
        
        if self.waveform is None :return
        
        trodness = self.waveform.shape[0]
        ax = None
        tvect = arange(self.waveform.shape[1], dtype = 'f')/self.sampling_rate
        for i in range(trodness):
            ax = fig.add_subplot(1, trodness, i+1, sharex = ax, sharey = ax)
            ax.plot(tvect, self.waveform[i,:], color = color)




