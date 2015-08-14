# -*- coding: utf-8 -*-

"""




sudo apt-get install python-rpy
sudo R
install.packages('e1071')
q()


"""

#~ from scipy import *

#~ from scipy import cluster

import numpy

try:
    from rpy import r 
    R_available = True
except:
    R_available = False


class BaggedClustering :
    """
    **Bagged clustering**

    This the R e1071 clustering library. or R language.

    Friedrich Meisch introduced this merthod in 1998.

    Used Christophe Pouzat for spikesorting in SpikeOMatic

    
     :n: number of clusters
     
    """
    params = [
                    ( 'centers' , { 'value' : 16 , 'label' : 'Nb of cluster'} ),
                    ( 'iter_base' , { 'value' : 10 , 'label' : 'iter number'} ),
                    ( 'base_centers' , { 'value' : 30 , 'label' : 'initial clusters'} ),
                    ( 'hclust_method' , { 'value' : 'single' , 'label' : 'hclust_method (metric)' , 'possible' : [ 'single' ,'ward' ,  'complete' , 'average' ,'mcquitty' ,  'median' ,  'centroid'] } ),
                    ]    

    name = 'bagged clustering'
    
    def compute(self , waveforms , spike_times ,  centers = 16 , iter_base = 10,
                                                                    base_centers = 30,  hclust_method = "ward") :
        
        
        if not R_available: return None
        
        r.library('e1071')
        
        ret = r.bclust(waveforms , centers = centers , iter_base = iter_base , 
                                                                    base_centers = base_centers, hclust_method = hclust_method)
        #~ print ret
        
        code = numpy.array(ret['cluster'] , dtype = 'i')
        #~ print type(code)

        
        
        return code

