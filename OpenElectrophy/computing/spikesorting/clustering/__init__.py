# -*- coding: utf-8 -*-
"""
clustering module propose 4 methods:

  * .. autoclass:: KMean

  * .. autoclass:: OneCell
  
  * .. autoclass:: ParamMagnetic  
  
  * .. autoclass:: BaggedClustering  
  
  * .. autoclass:: GaussianMixtureMClust  
  

"""

from kmean_clustering import KMean
from onecell import OneCell
from paramagnetic import ParamMagnetic
#~ from superparamagnetic import SuperParamMagnetic

# needs R
from bagged_clustering import BaggedClustering
from gaussian_mixture_mclust import GaussianMixtureMClust


# need scikit.learn
from affinity_propagation import AffinityPropagation

#~ from sc import SC




list_method = [  KMean  , OneCell, ParamMagnetic ,BaggedClustering  , GaussianMixtureMClust , AffinityPropagation]



