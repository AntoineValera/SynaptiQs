# -*- coding: utf-8 -*-

"""
clusering method for spike sorting : ParamMagnetic

based on spins at a fixed temperature


"""

from scipy import *

from scipy import cluster

class SuperParamMagnetic :
    params = [
                    ( 'n' , { 'value' : 3 , 'label' : 'output dimension (N cluster)'} ),
                    ]
    
    name = 'Super param magnetic'
    
    def compute(self , waveforms , spike_times , n=3 ) :
        codebook , distor =  cluster.vq.kmeans(waveforms , n)
        code, distor = cluster.vq.vq(waveforms , codebook)
        return code


