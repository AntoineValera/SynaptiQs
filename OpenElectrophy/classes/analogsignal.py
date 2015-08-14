# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy
from scipy import signal

from base import OEBase
from sqlalchemy import orm




# for defitions list
__doc__ = neo.core.AnalogSignal.definition

class AnalogSignal(neo.core.AnalogSignal , OEBase):
    __doc__ = neo.core.AnalogSignal.__doc__ + \
    """This OpenElectrophy object inherits from `neo.core.AnalogSignal`.
    
    Usage
    -----
    You must first have opened a connection to an OpenElectrophy database.
    Let's say you have two channel traces in a numpy array called `data` that
    you want to add to the database.
    
    # Create a Segment and an AnalogSignal
    seg = Segment(name='Trial 1')    
    anasig0 = AnalogSignal(signal=data[0], channel=0, t_start=3.4,
        sampling_rate=1000.0)
    anasig1 = AnalogSignal(signal=data[1], channel=1, t_start=3.4,
        sampling_rate=1000.0)
    
    # Add signals to segment
    seg._analogsignals.append(anasig0)
    seg._analogsignals.append(anasig1)
    seg.save()

    # Retrieve data
    plot(seg._analogsignals[0].signal)
    """    
    
    
    parents = [ 'segment'  , 'recordingpoint',]
    children = ['oscillation' ]
    fields = [  ['name' , Text],
                    ['channel' , Integer],
                    ['t_start' , Float],
                    ['sampling_rate' , Float],
                    ['signal' , numpy.ndarray],
                ]
    tablename = 'analogsignal'
    def __init__(self, *args , **kargs):        
        neo.core.AnalogSignal.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
    
    # Doc string for __init__ including neo __init__
    __init__.__doc__ = neo.core.AnalogSignal.__init__.__doc__ + \
    """
    Additional information for OpenElectrophy object:

    The following SQL fields will be stored in the database:
        name : Text, name of the signal
        channel : Integer
        t_start : Float
        sampling_rate : Float
        signal : numpy.ndarray
        id_segment : id of Segment containing this analog signal
        id_recordingpoint : id of RecordingPoint containing this
    
    Since this object inherits from OEBase, `metadata` can also
    be specified.
    """

    @orm.reconstructor
    def init_on_load(self):
        OEBase.init_on_load(self)
        self._t = None

        
    plotAptitudes = [   [ 'natural' , {  
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
                                [ 'filtered' , {  
                                                        'name' : 'Band pass filtered',
                                                        'default_selected' :  False,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [    [ 'color' , {'value' : 'g' }],
                                                                                [ 'f1' , {'value' : 300. }],
                                                                                [ 'f2' , {'value' : numpy.inf }],
                                                                                
                                                                            ],
                                                    }
                                ],                                
                                [ 'scalogram' , {  
                                                        'name' : 'Morlet scalogram',
                                                        'default_selected' :  False,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : False,
                                                        'params' :  [    [ 'f_start' , {'value' : 5. }],
                                                                                [ 'f_stop' , {'value' : 100. }],
                                                                                [ 't_start' , {'value' : -numpy.inf }],
                                                                                [ 't_stop' , {'value' : numpy.inf }],
                                                                                [ 'sampling_rate' , {'value' : 200. }],
                                                                                [ 'deltafreq' , {'value' : 1. }],
                                                                                [ 'f0' , {'value' : 2.5 }],
                                                                                [ 'normalisation' , {'value' : 0. }],
                                                                                [ 'colorbar' , {'value' : True }],
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


    def plot_filtered(self , color = 'g',
                                        f1 = 300.,
                                        f2 = numpy.inf,
                                        **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)

        from ..computing.filter import fft_passband_filter
        nq = self.sampling_rate/2.
        sigF = fft_passband_filter(self.signal, f_low = f1/nq , f_high = f2/nq)
        return ax.plot(self.t(), sigF , color = color)



    def plot_scalogram(self, colorbar = True, **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        from ..computing.timefrequency  import TimeFreq
        tf = TimeFreq(self, **kargs)
        return tf.plotMap(ax, colorbar = colorbar)
        


