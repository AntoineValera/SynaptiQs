# -*- coding: utf-8 -*-
"""
Old filtering methods based on fft.
To be rewrite soon...

"""

from scipy import *


#~ def fft_passband_filter(sig,
        #~ f_low =0,f_high=1 ) :
    #~ """
    #~ pass band filter using fft for real 1D signal.
    
    #~ sig : a numpy.array signal
    #~ f_low : low pass niquist frequency (1 = samplin_rate/2)
    #~ f_high : high  cut niquist frequency (1 = samplin_rate/2)
    #~ """
    #~ n = sig.size
    #~ N = 2**(ceil(log(n)/log(2)))
    #~ SIG = fft(sig,N)

    #~ n_low = floor((N-1)*f_low/2)+1;
    #~ fract_low = 1-((N-1)*f_low/2-floor((N-1)*f_low/2));
    #~ n_high = floor((N-1)*f_high/2)+1;
    #~ fract_high = 1-((N-1)*f_high/2-floor((N-1)*f_high/2));

    #~ if f_low >0 :
        #~ SIG[0] = 0
        
        #~ SIG[1:n_low ] = 0
        #~ SIG[n_low] *= fract_low
        
        #~ SIG[-n_low] *= fract_low
        #~ if n_low !=1 :
            #~ SIG[-n_low+1:] = 0

    #~ if f_high <1 :
        #~ SIG[n_high] *= fract_high
        #~ SIG[n_high+1:-n_high] = 0	
        #~ SIG[-n_high] *= fract_high


    #~ return real(ifft(SIG)[0:n])
    




def fft_passband_filter(sig,
        f_low =0,f_high=1,
        axis = 0,
        ) :
    """
    pass band filter using fft for real 1D signal.
    
    sig : a numpy.array signal
    f_low : low pass niquist frequency (1 = samplin_rate/2)
    f_high : high  cut niquist frequency (1 = samplin_rate/2)
    """
    
    n = sig.shape[axis]
    N = int(2**(ceil(log(n)/log(2))))
    SIG = fft(sig,n = N , axis = axis)

    n_low = floor((N-1)*f_low/2)+1;
    #~ print n_low
    fract_low = 1-((N-1)*f_low/2-floor((N-1)*f_low/2));
    n_high = floor((N-1)*f_high/2)+1;
    fract_high = 1-((N-1)*f_high/2-floor((N-1)*f_high/2));
    #~ print n_high

    s = [ slice(None) for i in range(sig.ndim) ]
    if f_low >0 :
        
        
        s[axis] = 0
        SIG[s] = 0
        
        s[axis] = slice(1,n_low)
        SIG[ s ] = 0
        
        s[axis] = n_low
        SIG[s] *= fract_low
        
        s[axis] = -n_low
        SIG[s] *= fract_low
        
        if n_low !=1 :
            s[axis] = slice(-n_low+1, None)
            SIG[s] = 0

    if f_high <1 :
        s[axis] = n_high
        SIG[s] *= fract_high
        
        s[axis] = slice(n_high+1,-n_high)
        SIG[ s ] = 0
        
        s[axis] = -n_high
        SIG[s] *= fract_high

    s[axis] = slice(0,n)
    
    return real(ifft(SIG , axis=axis)[s])

    
    
    
    
    






#~ def fft_bandstop_filter(sig,f_low =0,f_high=1 ) :
	#~ """
	#~ band stop filter using fft for real 1D signal
	#~ """
	#~ n = sig.size
	#~ N = 2**(ceil(log(n)/log(2)))
	#~ SIG = fft(sig,N)
	
	#~ n_low = floor((N-1)*f_low/2)+1;
	#~ fract_low = ((N-1)*f_low/2-floor((N-1)*f_low/2));
	#~ n_high = floor((N-1)*f_high/2)+1;
	#~ fract_high = ((N-1)*f_high/2-floor((N-1)*f_high/2));
	
	#~ if (f_low >0) and (f_high <1) :
		#~ SIG[n_low+1:n_high-1] = 0
		#~ SIG[n_low] *= fract_low
		#~ SIG[n_high] *= fract_high
		
		#~ SIG[-n_high+1:-n_low-1] = 0
		#~ SIG[-n_high] *= fract_high
		#~ SIG[-n_low] *= fract_low
	
	#~ return real(ifft(SIG)[0:n])