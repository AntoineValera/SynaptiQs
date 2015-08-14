# -*- coding: utf-8 -*-

"""



sudo apt-get install python-rpy
sudo R
install.packages('mclust')
q()


"""

#~ from scipy import *
from numpy import array
#~ from scipy import cluster

try:
    from rpy import r 
    R_available = True
except:
    R_available = False

class GaussianMixtureMClust :
    """
    **Gaussian Mixture Clustering from mclust**

    Gaussian Mixture based on the mclust R library dev by Chis Fraley and Adrian Raftery.

    Used Christophe Pouzat for spikesorting in SpikeOMatic.


    
     :n: number of clusters
     
    """
    params = [
                    ( 'minG' , { 'value' : 1 , 'label' : 'min component'} ),
                    ( 'maxG' , { 'value' : 32 , 'label' : 'max component'} ),
                    
                    ]    

    name = 'gaussian mixture mclust R'
    
    def compute(self , waveforms , spike_times ,  minG = 1 , maxG = 32,):
        
        #~ from rpy import r 
        
        if not R_available: return None
        
        r.library('mclust')
        
        ret = r.Mclust( waveforms , minG = minG , maxG =maxG)
        
        code = array(ret['classification'] , dtype = 'i')
        
        return code

