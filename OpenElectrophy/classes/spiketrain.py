# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy
from numpy import newaxis, concatenate, arange, sort, random


from base import OEBase
from sqlalchemy import orm
from spike import Spike

# for defitions list
__doc__ = neo.core.SpikeTrain.definition


class SpikeTrain(neo.core.SpikeTrain , OEBase):
    __doc__ = neo.core.SpikeTrain.__doc__
    
    
    Spike = Spike
    
    parents = [ 'segment'  , 'recordingpoint' , 'neuron']
    children = [ 'spike' ]
    fields = [  ['name' , Text],
                    ['channel' , Integer],
                    ['t_start' , Float],
                    ['t_stop' , Float],
                    ['sampling_rate' , Float],
                    ['left_sweep' , Float],
                    ['right_sweep' , Float],
                    [ '_spike_times' , numpy.ndarray],
                    [ '_waveforms' , numpy.ndarray],
                    
                ]
    tablename = 'spiketrain'
    def __init__(self, *args , **kargs):
        """
        """
        neo.core.SpikeTrain.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
        
    @orm.reconstructor
    def init_on_load(self):       
        OEBase.init_on_load(self)
    
    
    plotAptitudes = [   [ 'raster' , {  
                                                        'name' : 'Raster plot',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [    [ 'y_offset' , {'value' : 0. }],
                                                                                [ 'color' , {'value' : 'g' }],
                                                        
                                                                           ],
                                                    }
                                ],
                                [ 'waveform' , {  
                                                        'name' : 'Superimposed waveform',
                                                        'default_selected' :  False,
                                                        'ax_needed' : None,
                                                        'fig_needed' : 1,
                                                        'widget_needed' : None,
                                                        'stackable' : False,
                                                        'params' :  [    [ 'color' , {'value' : 'g' }],
                                                                                [ 'max_spike' , {'value' : 200 }],
                                                                                [ 'average_mode' , {'value' : False }],
                                                                                
                                                                            ],
                                                    }
                                ],


                            ]
        

    def plot_raster(self , y_offset = 0.,
                                    color = 'g',
                                    **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig=pyplot.figure()
            ax=fig.add_subplot(111)
        ax.plot(self.spike_times, numpy.zeros(self.spike_times.size)+y_offset , color = color,
                                                                        linestyle = 'None',
                                                                        marker = '|',
                                                                        )



    def plot_waveform(self ,color = 'g',
                                    max_spike =  200,
                                    average_mode = False,
                                    **kargs):
        if 'fig'in kargs:
            fig = kargs['fig']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
        
        wf = self.waveforms
        if wf is None : return
        if wf.shape[0] <= 0: return
        
        tvect = arange(wf.shape[2], dtype = 'f')
        if self.sampling_rate is not None:
            tvect /= self.sampling_rate
        trodness = wf.shape[1]
        
        if average_mode:
            m = numpy.mean(wf, axis=0)
            s = numpy.std(wf , axis=0)
            trodness = m.shape[0]
            ax = None
            for i in range(trodness):
                ax = fig.add_subplot(1, trodness, i+1, sharex = ax, sharey = ax)
                ax.plot(tvect, m[i,:], color = color, linewidth = 2)
                ax.fill_between(tvect, m[i,:]+s[i,:], m[i,:]-s[i,:], color = color, alpha = .5)
        else:
            step = 1.*wf.shape[0]/max_spike
            if step<=1. :
                start, step = 0, 1
            else:
                start, step = int(random.rand()*step), int(step)
            ax = None
            for i in range(trodness):
                ax = fig.add_subplot(1, trodness, i+1, sharex = ax, sharey = ax)
                ax.plot( tvect , wf[start::step, i,:].transpose(), color = color)
            

