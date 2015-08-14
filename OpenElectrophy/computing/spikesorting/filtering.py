# -*- coding: utf-8 -*-

"""

spikesorting.filtering module offer actually 5 methods:


 * .. autoclass:: MethodFFT

 * .. autoclass:: NoFiltering

 * .. autoclass:: MedianFilter

 * .. autoclass:: ButterworthFiltering

 * .. autoclass:: BesselFiltering
"""


from numpy import inf, isinf
import scipy
from scipy import signal

from ..filter import fft_passband_filter


class MethodFFT :
    """
    **FFT Filter based.**
    
    Method based on the FFT transform and zero filling on cut bands.
     
     :f_low: low frequency in Hz
     :f_high: high frequency in Hz
    
    """
    params = [
                        ( 'f_low' , { 'value' : 300. , 'label' : 'Low cut frequency'} ),
                        ( 'f_high' , { 'value' : inf , 'label' : 'High cut frequency'} ),
                    ]
    name = 'Filtering with FFT'
    
    def compute(self , anaSig , f_low = 0. , f_high = inf ) :
        anaSig_filtered = anaSig.copy()
        nq = anaSig.sampling_rate/2.
        anaSig_filtered.signal = fft_passband_filter(anaSig.signal, f_low = f_low/nq , f_high = f_high/nq)
        return anaSig_filtered

class NoFiltering :
    """
    **No filtering**
    This apply no filter and simply copy the signal for the next step.
    Useful when the signal imported is already filtered inline by the acquisition system.
    
    """    
    params = [ ]
    name = 'No filtering'

    def compute(self , anaSig ) :
        anaSig_filtered = anaSig.copy()
        return anaSig_filtered



class MedianFilter :
    """
    **Median sliding window Filter**
    This method apply a median filter on a sliding window to compute the baseline.
    
    The high pass signal is the substraction of the signal itself and this baseline.
    
    This method is really slow and can't be used on big signal (>60s at 10kHz). But it is useful and
    there are only few edge effects.
    
     :win_size: size in second of the filtering kernel
    
    """
    params = [
                        ( 'win_size' , { 'value' : .05 , 'label' : 'Windows size (s.)'} ),
                    ]
    name = 'Median Subtraction Filter'
    
    def compute(self , anaSig , win_size = None ) :
        sr = anaSig.sampling_rate
        anaSig_filtered = anaSig.copy()
        anaSig_filtered.signal = anaSig.signal - signal.medfilt(anaSig.signal , kernel_size = int(win_size/2.*sr)*2+1)
        return anaSig_filtered








class ButterworthFiltering :
    """
    **Butterworth filter**
    
     :f_low: low frequency
     :N: order
    
    """    
    params = [
                        ( 'f_low' , { 'value' : 300. , 'label' : 'Low cut frequency'} ),
                        ( 'N' , { 'value' : 5 , 'label' : 'Order N'} ),
                        ]
    name = 'Nth order Butterworth Filter'
    
    def compute(self , anaSig , f_low = 0. , N = 5 ) :
        anaSig_filtered = anaSig.copy()
        sr = anaSig.sampling_rate
        
        #~ if isinf(f_high):
            #~ f_high = .95*sr/2.
        #Wn = [f_low/(sr/2.) , f_high/(sr/2.)]
        #b,a = signal.iirfilter(N, Wn, btype = 'band', analog = 0, ftype = 'butter', output = 'ba')
        
        Wn = f_low/(sr/2.)
        b,a = signal.iirfilter(N, Wn, btype = 'high', analog = 0, ftype = 'butter', output = 'ba')
        anaSig_filtered.signal = signal.lfilter(b, a, anaSig.signal, zi = None)
        return anaSig_filtered


class BesselFiltering :
    """
    **Bessel filter**
    
     :f_low: low frequency
     :N: order    
    """
    params = [
                        ( 'f_low' , { 'value' : 300. , 'label' : 'Low cut frequency'} ),
                        ( 'N' , { 'value' : 5 , 'label' : 'Order N'} ),
                        ]
    name = 'Nth order Bessel Filter'
    
    def compute(self , anaSig , f_low = 300. ,  N = 5 ) :
        anaSig_filtered = anaSig.copy()
        sr = anaSig.sampling_rate
        
        #~ if isinf(f_high):
            #~ f_high = .95*sr/2.
        #Wn = [f_low/(sr/2.) , f_high/(sr/2.)]
        #b,a = signal.iirfilter(N, Wn, btype = 'band', analog = 0, ftype = 'bessel', output = 'ba')
        
        Wn = f_low/(sr/2.)
        b,a = signal.iirfilter(N, Wn, btype = 'high', analog = 0, ftype = 'bessel', output = 'ba')
        anaSig_filtered.signal = signal.lfilter(b, a, anaSig.signal, zi = None)
        
        return anaSig_filtered



list_method = [ MethodFFT  , MedianFilter, NoFiltering, ButterworthFiltering, BesselFiltering ]

