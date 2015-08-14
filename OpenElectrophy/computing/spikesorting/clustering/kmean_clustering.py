# -*- coding: utf-8 -*-

"""
Clusering method for spike sorting : k-means


"""

from scipy import cluster

class KMean :
    """
    **K-Mean clustering**
    
    Classical K-mean algorithm for cluster separation. The algorithm comes
    from the scipy.cluster module.
    
     :n: number of clusters
     
    """
    params = [
                    ( 'n' , { 'value' : 4 , 'label' : 'output dimension (N cluster)'} ),
                    ]    

    name = 'K-means'
    
    def compute(self , waveforms , spike_times , n=3 ) :
        codebook , distor =  cluster.vq.kmeans(waveforms , n)
        code, distor = cluster.vq.vq(waveforms , codebook)
        return code

