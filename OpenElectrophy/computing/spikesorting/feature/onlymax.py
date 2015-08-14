# -*- coding: utf-8 -*-

"""
projection method for spike sorting : kepp only max


"""

from numpy import empty


class OnlyMax:
    """
    **Only max**
    
    This method extracts only the max of each waveform. This method mimics
    old habits in some lab.
    
    In case of mono-electrode the output dimension is 1. So you can't plot
    features in 3D space nor in N-D space.
    
    waveforms: matrix of waveforms with shape (N_spikes, trodness,
        len(waveform))
    
    Returns: feature matrix with shape (N_spikes, trodness)
    """    
    params = [ ]

    name = 'Only Max'
    
    
    def compute( self , waveforms , sampling_rate ) :
        
        maxs = empty( (waveforms.shape[0] , waveforms.shape[1] ) )
        for i in range(waveforms.shape[0]):
            for j in range(waveforms.shape[1]):
                maxs[i,j] = max( abs( waveforms[i,j,:] ) )
        
        
        return maxs



