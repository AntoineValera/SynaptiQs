# -*- coding: utf-8 -*-

"""
projection method for spike sorting : haar wavelet



"""

import mdp
import numpy
from numpy import empty, mean , std, concatenate, zeros, argsort, sum
from scipy import stats


class HaarWaveletProjection:
    """
    **Haar wavelet projection**
    
    This method use a harra wavelet for decomposition of the waveform and 
    perform a KS coefficient to select best feature.
    
    Introduced by Quiroga in 2004.
    
    This code is taken from 
    `wave_clus <http://www.vis.caltech.edu/~rodri/Wave_clus/Wave_clus_home.htm>`_ 
    matlab package release under GPL by Quiroga.
    
    You can have the original version in the file wave_features_wc.m
    
    
    """
    params = [
                    ( 'output_dim' , { 'value' : 6 , 'label' : 'n coefficient'} ),
                    ( 'level' , { 'value' : 4 , 'label' : 'decomposition level'} ),
                    ( 'std_restrict' , { 'value' : 3. , 'label' : 'std restriction'} ),
                    
                    ]
    
    name = 'Haar wavelet projection'

    def compute( self , waveforms , sampling_rate , 
                                output_dim =6,
                                level = 4,
                                std_restrict = 3.,
                                ) :
        import pywt

        #~ waveforms2 = empty( (waveforms.shape[0] , waveforms.shape[1]*waveforms.shape[2] ) )
        #~ for i in range(waveforms.shape[0]):
            #~ waveforms2[i,:] = waveforms[i].reshape( (waveforms.shape[1]*waveforms.shape[2]) )
        waveforms2 = waveforms.reshape(waveforms.shape[0], -1)

        coeffs = None
        for i in range(waveforms2.shape[0]):
            coeff = concatenate(pywt.wavedec(waveforms2[i,:] , 'haar' ,mode = 'sym', level = level))
            if i ==0:
                coeffs = empty((waveforms.shape[0] , coeff.shape[0]))
            coeffs[i,:] = coeff
        
        # find why ? eliminate zeros column
        keep = sum(coeffs==0. , axis=0) != waveforms2.shape[0]
        coeffs = coeffs[:,keep]
        #~ print 'sum', numpy.sum(coeffs , axis=0)
        
        # calcul tes ks for all coeff
        ks_score = zeros((coeffs.shape[1]))
        for j in range(coeffs.shape[1]):
            # keep only coeff inside m +- restrict std
            s = std(coeffs[:,j], axis=0)*3
            m = mean(coeffs[:,j], axis=0)
            ind_selected = (coeffs[:,j]>=m-s) & (coeffs[:,j]<=m+s)
            if sum(ind_selected) >= 10:
                x = coeffs[ind_selected, j]
                zscored = (x-mean(x))/std(x)
                D, pvalue = stats.kstest( zscored,'norm')
                ks_score[j] = D
                
        
        # keep only the best ones
        ind_sorted = argsort(ks_score)[::-1]
        ind_sorted = ind_sorted[:output_dim]
        print ind_sorted
        return coeffs[:, ind_sorted]
        

def test_ks():
    pass
