# -*- coding: utf-8 -*-

"""
projection method for spike sorting : no projetcion



"""

from numpy import empty

class NoProjection:
    """
    **No projection**
    
    This method does not extract any component but keep the original waveform to later compute
    the clustering.
    In case of tetrode, it concatenate all original waveforms in one dimension.
    
    """

    params = [ ]

    name = 'No projection'

    def compute( self , waveforms , sampling_rate ) :
        
        #~ waveforms2 = empty( (waveforms.shape[0] , waveforms.shape[1]*waveforms.shape[2] ) )
        #~ for i in range(waveforms.shape[0]):
            #~ waveforms2[i,:] = waveforms[i].reshape( (waveforms.shape[1]*waveforms.shape[2]) )
        
        waveforms2 = waveforms.reshape(waveforms.shape[0], -1)
        
        return waveforms2



