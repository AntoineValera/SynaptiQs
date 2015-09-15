# -*- coding: utf-8 -*-

"""



To use this you need sckit.learn

sudo easy_install scikit.learn


"""

#~ from scipy import *

#~ from scipy import cluster

import numpy as np


class AffinityPropagation :
    """
    **Affinity Propagation clustering**
    
    This method is introduce by Frey.
    A complete information here :
    http://www.psi.toronto.edu/index.php?q=affinity%20propagation
    
    Clustering by Passing Messages Between Data Points. [PDF] [BibTeX]
    Brendan J. Frey and Delbert Dueck, University of Toronto
    Science 315, 972-976, February 2007 

    A Binary Variable Model for Affinity Propagation  [PubMed]
    Inmar E. Givoni and Brendan J. Frey
    Neural Computation,Vol 21, issue 6, pp 1589-1600, June 2009
    
    This method has been implemented by the fantastic team of sckit.learn:
    http://scikit-learn.sourceforge.net/
    
    Many thanks to them.


    
    """
    params = [
                    #~ ( 'centers' , { 'value' : 16 , 'label' : 'Nb of cluster'} ),
                    #~ ( 'iter_base' , { 'value' : 10 , 'label' : 'iter number'} ),
                    #~ ( 'base_centers' , { 'value' : 30 , 'label' : 'initial clusters'} ),
                    #~ ( 'hclust_method' , { 'value' : 'single' , 'label' : 'hclust_method (metric)' , 'possible' : [ 'single' ,'ward' ,  'complete' , 'average' ,'mcquitty' ,  'median' ,  'centroid'] } ),
                    ]    

    name = 'Affinity Propagation'
    
    def compute(self , waveforms , spike_times ,  ) :
        
        import sklearn.cluster
        
        # Compute similarities
        X = waveforms
        X_norms = np.sum(X*X, axis=1)
        S = - X_norms[:,np.newaxis] - X_norms[np.newaxis,:] + 2 * np.dot(X, X.T)
        p = 10*np.median(S)
        
        # Compute Affinity Propagation
        af = sklearn.cluster.AffinityPropagation()
        af.fit(S, p)
        cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_
        
        
        return labels

