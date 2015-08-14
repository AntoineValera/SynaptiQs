# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode, DateTime
import numpy

from base import OEBase

from matplotlib.pyplot import get_cmap

# for defitions list
__doc__ = neo.core.Segment.definition


class Segment(neo.core.Segment , OEBase):
    
    __doc__ = neo.core.Segment.__doc__ + \
    """This OpenElectrophy object inherits from `neo.core.Segment`.    
    
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
    
    
    parents = [ 'block' ]
    children = ['analogsignal' , 'spiketrain' , 'event' , 'epoch' , 
                            'imageserie' , 'licktrain', 'respirationsignal',
                            ]
    
    fields = [  ['name' , Text],
                    ['num' , Integer],
                    ['datetime' , DateTime],
                    ['info' , Text],
                    ['fileOrigin' , Text],
                ]
    tablename = 'segment'
    
    def __init__(self, *args , **kargs):
        """Creates a new Segment.
        
        In addition to the basic neo Segment initialization, (see
        OpenElectrophy.neo.core.Segment), the following fields in Block
        can be defined with sqlalchemy values:
            name : Text, name of the segment
            num : Integer
            info : Text, info about the segment
            fileOrigin : Text, origin of the data
            datetime : DateTime, beginning of the data segment
        """
        neo.core.Segment.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)


    plotAptitudes = [   [ 'allAnalogSignal' , {  
                                                        'name' : 'Plot all AnalogSignals',
                                                        'default_selected' :  True,
                                                        'ax_needed' : None,
                                                        'fig_needed' : 1,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [    [ 'colors' , {'value' : 'automatic' }],
                                                                                [ 'spread_and_norm' , {'value' : True }],
                                                                                [ 'withevent' , {'value' : True }],
                                                                                [ 'withepoch' , {'value' : True }],
                                                        
                                                                           ],
                                                    }
                                ],
                            ]
    def plot_allAnalogSignal(self ,colors = 'automatic',
                                                        spread_and_norm = True,
                                                        withevent = True,
                                                        withepoch = True,
                                                        
                                                        **kargs):
        if 'fig'in kargs:
            fig = kargs['fig']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
        
        ax = fig.add_subplot(1,1,1)
        
        cmap = get_cmap('jet', len(self._analogsignals))
        
        for i,ana in enumerate(self._analogsignals):
            if spread_and_norm:
                sig = ana.signal/max(abs(ana.signal))
                if ana.channel is not None:
                    offset = ana.channel
                else:
                    offset = i+1
                ax.plot(ana.t(), sig+offset, color = cmap(i))
            else:    
                ana.plot_natural( ax = ax, color = cmap(i) )
        
        if withevent:
            for i, ev in enumerate(self._events):
                ev.plot_vline(ax = ax )
            
        if withepoch:
            for i, ep in enumerate(self._epochs):
                ep.plot_vspan(ax = ax )
        
        return


