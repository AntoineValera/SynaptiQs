# -*- coding: utf-8 -*-

"""
clusering method for spike sorting : one cell


"""

from numpy import zeros

class OneCell :
    """
    **One cell = no clustering**
    
    In case of intra cellular recordings no clustering is needed, so use this method.
    It groups all spikes in the same neuron.
    
    """    
    params = [ ]
    name = 'One cell (no clustering)'
    
    def compute(self , waveform, spike_times , ) :
        cluster = zeros(waveform.shape[0], dtype = 'i')
        return cluster
