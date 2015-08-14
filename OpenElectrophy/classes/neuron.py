# -*- coding: utf-8 -*-
"""

"""

import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy

from base import OEBase

from numpy import histogram, arange, diff, mean, concatenate

from matplotlib.pyplot import get_cmap


# for defitions list
__doc__ = neo.core.Neuron.definition


class Neuron(neo.core.Neuron , OEBase):
    __doc__ = neo.core.Neuron.__doc__
    
    parents = [ 'block'  ]
    children = [ 'spiketrain' ]
    fields = [  ['name' , Text],
                    ['sortingScore' , Text],
                    ['channel' , Integer],
                ]
    tablename = 'neuron'
    def __init__(self, *args , **kargs):
        """
        """
        neo.core.Neuron.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
        
        
    plotAptitudes = [   [ 'raster' , {  
                                                        'name' : 'Plot ratser of SpikeTrains',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [    [ 'color' , {'value' : 'g' }],
                                                                           ],
                                                    }
                                ],
                                
                             [ 'histogramISI' , {  
                                                        'name' : 'Histogram Inter Spike Interval',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [    [ 'spiketrain_pooled' , {'value' : True }],
                                                                                [ 'binsize' , {'value' :.001 }],
                                                                                [ 'plot_type' , {'value' : 'line' , 'possible' : ['line' ,  'bar']  }],
                                                                           ],
                                                    }
                                ],
                                
                             [ 'autocorrelogram' , {  
                                                        'name' : 'Autocorrelogram',
                                                        'default_selected' :  False,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [    [ 'spiketrain_pooled' , {'value' : True }],
                                                                                [ 'binsize' , {'value' :.001 }],
                                                                                [ 'winsize' , {'value' : .1 }],
                                                                           ],
                                                    }
                                ],                            
                            ]
    
    def plot_raster(self ,color = 'g',
                                                        **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        for i, sptr in enumerate( self._spiketrains):
            sptr.plot_raster(ax = ax, y_offset = i, color = color)
        ax.set_ylim(0, len(self._spiketrains)+1)


    def plot_histogramISI(self ,spiketrain_pooled = True,
                                                binsize = .001,
                                                plot_type = 'line',
                                                        **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        if spiketrain_pooled:
            all_isi = None
            for i, sptr in enumerate( self._spiketrains):
                if all_isi is None:
                    all_isi = sptr.isi()
                else:
                    all_isi = concatenate( (all_isi , sptr.isi() ) , axis=0)
            
            y,x = histogram( all_isi, bins = arange(0, all_isi.max(), binsize) )
            
            if plot_type == 'line':
                ax.plot(x[:-1]+binsize/2. , y , color = 'g')
            else:
                ax.bar(x[:-1] , y , width = binsize,  color = 'g')
                
        else:
            n = len( self._spiketrains )
            cmap = get_cmap('jet', n)
            for i, sptr in enumerate( self._spiketrains):
                all_isi = sptr.isi()
                y,x = histogram(all_isi , bins = arange(0, all_isi.max(), binsize) )
                
                if plot_type == 'line':
                    ax.plot(x[:-1]+binsize/2. , y , color = cmap(i))
                else:
                    ax.bar(x[:-1]+binsize*float(i)/n , y , width = binsize/n,  color = cmap(i))
                    
                    
                    
    def plot_autocorrelogram(self , spiketrain_pooled = True,
                                                            binsize = .001,
                                                           winsize = .1, 
                                                        **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        n = len( self._spiketrains )
        bins = arange( -winsize/2., winsize/2., binsize)
        if spiketrain_pooled:
            all = None
            for i, sptr in enumerate( self._spiketrains):
                if  all is None:
                    all = sptr.all_diff_combinate(sptr.spike_times)
                else:
                    all = concatenate( ( all, sptr.all_diff_combinate(sptr.spike_times)) )
            y,x = histogram( all ,  bins = bins )
            ax.plot(x[1:] , y, color = 'b' )
            
        else:
            cmap = get_cmap('jet', n)
            for i, sptr in enumerate( self._spiketrains):
                m  = sptr.all_diff_combinate(sptr.spike_times)
                y,x = histogram( m ,  bins = bins )
                ax.plot(x[1:] , y, color = cmap(i) )
                
        

