# -*- coding: utf-8 -*-
"""

"""


from scipy import *
from scipy.signal import resample
from scipy.fftpack import fft, ifft, fftshift

def generate_wavelet_fourier(len_wavelet,
            f_start,
            f_stop,
            deltafreq,
            sampling_rate,
            f0,
            normalisation,
            ):
    """
    Compute the wavelet coefficients at all scales and makes its Fourier transform.
    When different signal scalograms are computed with the exact same coefficients, 
        this function can be executed only once and its result passed directly to compute_morlet_scalogram
        
    Output:
        wf : Fourier transform of the wavelet coefficients (after weighting), Fourier frequencies are the first 
    """
    # compute final map scales
    scales = f0/arange(f_start,f_stop,deltafreq)*sampling_rate
    # compute wavelet coeffs at all scales
    xi=arange(-len_wavelet/2.,len_wavelet/2.)
    xsd = xi[:,newaxis] / scales
    wavelet_coefs=exp(complex(1j)*2.*pi*f0*xsd)*exp(-power(xsd,2)/2.)

    weighting_function = lambda x: x**(-(1.0+normalisation))
    wavelet_coefs = wavelet_coefs*weighting_function(scales[newaxis,:])

    # Transform the wavelet into the Fourier domain
    #~ wf=fft(wavelet_coefs.conj(),axis=0) <- FALSE
    wf=fft(wavelet_coefs,axis=0)
    wf=wf.conj() # at this point there was a mistake in the original script
    
    return wf

def compute_morlet_scalogram(ana,
            f_start=5.,
            f_stop=100.,
            deltafreq = 1.,
            sampling_rate = 200.,
            t_start = -inf, 
            t_stop = inf,
            f0=2.5, 
            normalisation = 0.,
            wf=None
            ):
    """

    Input:
    ana: AnalogSignal
    f_start, f_stop, deltafreq : Frequency start stop and step at which the scalogram is computed
    samplingrate : time samplingrate of the scalogram
    t_start, t_stop : optional time limit (in second)
    f0 : central frequency of the Morlet wavelet.  The Fourier spectrum of
        the Morlet wavelet appears as a Gaussian centered on f0. 
        It is also used as the wavelet characteristic frequency.
        Low f0 favors time precision of the scalogram while high f0 favors frequency precision
    normalisation : positive value favors low frequency components
    
    wf: if it is not None, it will ignore all other parameters and compute the map 
        assuming wf is the Fourier transform of the wavelet_coefs
    
    Output:
    wt: complex array with wavelet (time is the first dimension, frequency the second)
    
    Note : this code is a simplification and correction of the full wavelet package (cwt.py)
    orinally proposed by Sean Arms (http://github.com/lesserwhirls)
    
    """
    # Reduce signal to time limits
    sig=ana.signal[(ana.t()>=t_start)&(ana.t()<=t_stop)]
    
    if sig.size>0:
        if wf is None:
            if ana.sampling_rate != sampling_rate:
                sig=resample(sig,sig.size*sampling_rate/ana.sampling_rate)
            wf = generate_wavelet_fourier(sig.size,max(f_start,deltafreq),min(f_stop,ana.sampling_rate/2.),deltafreq,sampling_rate,f0,normalisation)
        else:
            if sig.size != wf.shape[0]:
                sig=resample(sig,wf.shape[0])

        # Transform the signal into the Fourier domain
        sigf=fft(sig)

        # Convolve (mult. in Fourier space)
        #~ wt_tmp=ifft(wf*sigf[newaxis,:],axis=1)
        wt_tmp=ifft(sigf[:,newaxis]*wf,axis=0)
 
        # shift output from ifft
        wt = fftshift(wt_tmp,axes=[0])
        
    else:
        scales = f0/arange(f_start,f_stop,deltafreq)*sampling_rate
        wt = empty((0,scales.size),dtype='complex')

    return wt
    
