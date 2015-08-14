# -*- coding: utf-8 -*-
"""

"""

from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy
from scipy import signal
from scipy import digitize , nan

from base import OEBase



class Oscillation( OEBase):
    """
    Class to handle a transient oscillation.
    Can old the full line in time, frequency and complexe morlet value.
    
    """
    parents = [ 'analogsignal' ]
    children = [ ]
    fields = [  ['name' , Text],
    
                    ['time_start' , Float],
                    ['time_stop' , Float],
                    ['freq_start' , Float],
                    ['freq_stop' , Float],
                    ['time_max' , Float],
                    ['freq_max' , Float],
                    ['amplitude_max' , Float],
                    
                    ['time_line' , numpy.ndarray],
                    ['freq_line' , numpy.ndarray],
                    ['value_line' , numpy.ndarray],
                    
                ]
    tablename = 'oscillation'
    def __init__(self, *args , **kargs):
        """
        """
        for k,v in kargs.iteritems():
            if k in dict(self.fields):
                setattr(self, k, v)
        
        OEBase.__init__(self, *args, **kargs)
        
    plotAptitudes = [   [ 'line_on_signal' , {  
                                                        'name' : 'plot oscillation on signal',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [       [ 'color' , {'value' : 'm' }],
                                                                                    [ 'sampling_rate' , {'value' : None , 'type' : float }],
                                                        
                                                                           ],
                                                    }
                                ],
                            
                            ]
    
    def phase_of_times(self,  times , sampling_rate = 1000.):
        """
        Give the phases of the oscillation at the specific 'times'
        
        The under underlying precision of phase sampling is given by 'sampling_rate'
        
        Return 'nan' for timepoints outside the range where the oscillation phase is known (Oscillation.time_line)
        
        Note: an oscillation detected with a very small sampling rate compared to its frequency will have a drift in its reconstructed phase. 
        It is advised to have an original sampling rate of at least 4 times the oscillation frequency
        """
        if self.time_line.size>1:
            old_dt = self.time_line[1]-self.time_line[0]
            x = numpy.arange(self.time_start, self.time_stop+old_dt, 1./sampling_rate)
        else:
            x=self.time_line
        v = self.value_line
        
        # BAD
        #y = numpy.angle(v)
        #y = signal.resample( y, x.size)
        
        
        
        # bad 2
        #~ y = numpy.cos(numpy.angle(v))
        #~ y = signal.resample( y, x.size)
        #~ ind = numpy.diff(y)>0
        #~ ind = numpy.concatenate( (ind , [ind[-1]]))
        #~ y2 = numpy.arccos(y)
        #~ y2[ind] = -y2[ind]
        
        #ok
        # Before resampling, in order to avoid slow down due the use of ifft in scipy.resample
        # y is padded with 0 proportionnally to the distance from x.size to the next 2**N 
        # QUESTION: does it lead to some strange edge effects???
        N=numpy.ceil(numpy.log2(x.size))
        vv=numpy.r_[v,numpy.zeros(numpy.floor(v.size*(2**N-x.size)/x.size))]
        vv = signal.resample( vv, 2**N)
        v = vv[:x.size]

        #~ y = numpy.cos(numpy.angle(v))
        y2 = numpy.angle(v)



        d = digitize( times , x )
        d[d==len(v)] = 0 # points above the highest time value where the oscillation phase is known
        phases = y2[d]
        phases[ d==0 ] = nan # all points outside the range where the oscillation is known
        return phases



    
    def plot_line_on_signal(self,   color ='m',
                                                    sampling_rate = None,
                                                    **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        
        if sampling_rate is None:
            x = self.time_line
            v = self.value_line
            y = numpy.cos(numpy.angle(v))*numpy.abs(v)
        else :
            if self.time_line.size>1:
                old_dt = self.time_line[1]-self.time_line[0]
                x = numpy.arange(self.time_start, self.time_stop+old_dt, 1./sampling_rate)
            else:
                x=self.time_line
            v = self.value_line
            y = numpy.cos(numpy.angle(v))*numpy.abs(v)
            
            # Before resampling, in order to avoid slow down due the use of ifft in scipy.resample
            # y is padded with 0 proportionnally to the distance from x.size to the next 2**N 
            # QUESTION: does it lead to some strange edge effects???
            N=numpy.ceil(numpy.log2(x.size))
            yy=numpy.r_[y,numpy.zeros(numpy.floor(y.size*(2**N-x.size)/x.size))]
            yy = signal.resample( yy, 2**N)
            y = yy[:x.size]
        
        l = ax.plot(x,y  , linewidth = 1, color=color)
        return l

