# -*- coding: utf-8 -*-
"""
Higher level object for computing, ploting and manipulating morlet scalogram.

"""

from morletscalo.convolution_freq import generate_wavelet_fourier, compute_morlet_scalogram
#~ from ...classes import *
from ...classes import AnalogSignal

from scipy.signal import resample
import numpy
from numpy import inf

# global for caching wf
global cache_for_wf
cache_for_wf = None
global signature_for_wf
signature_for_wf = ''


class TimeFreq():
    doc2="""
    *TimeFreq*
    
    """
    docparam = """
    
    Params:
     :f_start: lkjlkj
    
    """
    
    __doc__ = doc2+docparam
    
    def __init__(self,
                        anaSig,
                        method = 'convolution_freq',
                        f_start=5.,
                        f_stop=100.,
                        deltafreq = 1.,
                        sampling_rate = 200.,
                        t_start = -inf, 
                        t_stop = inf,
                        f0=2.5, 
                        normalisation = 0.,
                        **kargs
                        ):
                        
        self.anaSig = anaSig
        self.method = method
        self.f_start=f_start
        self.f_stop=f_stop
        self.deltafreq = deltafreq
        self.sampling_rate = sampling_rate
        self.t_start = t_start
        self.t_stop = t_stop
        self.f0=f0
        self.normalisation = normalisation
        
        self.t_start = max(self.t_start , self.anaSig.t_start)
        self.t_stop = min(self.t_stop , self.anaSig.t()[-1]+1./self.anaSig.sampling_rate )
        
        self._map = None
        self._t = None
        self._f = None
        
        if self.method == 'convolution_freq':
            self._wf = None
            self.subAnaSig = None


    def compute_time_vector(self) :
        return numpy.arange(len(self.subAnaSig.signal), dtype = 'f8')/self.sampling_rate + self.t_start

    def compute_freq_vector(self) :
        return numpy.arange(self.f_start,self.f_stop,self.deltafreq, dtype = 'f8')

    def t(self):
        if self._t==None:
            self._t=self.compute_time_vector()
        return self._t
    
    def f(self):
        if self._f==None:
            self._f=self.compute_freq_vector()
        return self._f
    
        
    @property
    def map(self):
        if self._map is None:
            self.recomputeMap()
        return self._map


    def recomputeMap(self):
        """
        Compute or recompute a map
        """
        if self.subAnaSig is None:
        #~ if True:
            sig=self.anaSig.signal[(self.anaSig.t()>=self.t_start)&(self.anaSig.t()<self.t_stop)]
            if self.sampling_rate != self.anaSig.sampling_rate :
                sig=resample(sig,sig.size*self.sampling_rate/self.anaSig.sampling_rate)
            self.subAnaSig = AnalogSignal( signal = sig,
                                                            sampling_rate = self.sampling_rate,
                                                            t_start = self.t_start,
                                                        )
        
        if self.method == 'convolution_freq':
            if self._wf is None :
                global signature_for_wf
                global cache_for_wf
                signature = '%d %f %f %f %f %f %f' % (self.subAnaSig.signal.size,
                                                                                self.f_start,
                                                                                self.f_stop,
                                                                                self.deltafreq,
                                                                                self.sampling_rate,
                                                                                self.f0,
                                                                                self.normalisation,
                                                                                )
                if signature != signature_for_wf:
                    cache_for_wf= generate_wavelet_fourier(len_wavelet=self.subAnaSig.signal.size,
                                                                                f_start=self.f_start,
                                                                                f_stop=self.f_stop,
                                                                                deltafreq=self.deltafreq,
                                                                                sampling_rate=self.sampling_rate,
                                                                                f0=self.f0,
                                                                                normalisation = self.normalisation,
                                                                                )
                    signature_for_wf = signature
                
                self._wf = cache_for_wf
            
            
            self._map = compute_morlet_scalogram(self.subAnaSig,wf = self._wf )
            
        
    def plotMap(self, ax,
                                    colorbar = True,
                                    cax =None,
                                    orientation='horizontal',
                                    **kargs):
        """
        
        ax : a matplotlib axes
        
        """
        im = ax.imshow(abs(self.map).transpose(),
                                    interpolation='nearest', 
                                    extent=(self.t_start, self.t_stop, self.f_start-self.deltafreq/2., self.f_stop-self.deltafreq/2.),
                                    origin ='lower' ,
                                    aspect = 'normal')

        if colorbar:
            if cax is None:
                ax.figure.colorbar(im)
            else:
                ax.figure.colorbar(im,ax = ax, cax = cax ,orientation=orientation)
            
                
        return im
        

    