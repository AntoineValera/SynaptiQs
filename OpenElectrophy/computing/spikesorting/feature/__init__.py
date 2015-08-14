# -*- coding: utf-8 -*-
"""
feature module propose 4 methods for extracting features
of a waveform:

  * .. autoclass:: PCA

  * .. autoclass:: NoProjection
  
  * .. autoclass:: OnlyMax  
  
  * .. autoclass:: ICA
  
  * .. autoclass:: HaarWaveletProjection
  

"""


from pca import PCA
from noprojection import NoProjection
from ica import ICA
from onlymax import OnlyMax
from haar_wavelet import HaarWaveletProjection
from pca_plus_max import PCA_Plus_Max


list_method = [PCA , NoProjection , OnlyMax , ICA, HaarWaveletProjection,
    PCA_Plus_Max]

