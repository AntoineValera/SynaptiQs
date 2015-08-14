# -*- coding: utf-8 -*-

"""
projection method for spike sorting : pca



"""

import mdp
from numpy import empty

class PCA:
    """
    **Principal Component Analysis**
    
    This methods computes a principal component decomposition, and
    keep the N highest eigenvalues. 
    
    This algorithm comes from the excellent MDP  toolkit : 
        http://mdp-toolkit.sourceforge.net/
    """
    params = [
        ('output_dim', 
            {'value': 8, 'label': 'output dimension (n component)'}),
        ('start_sample', 
            {'value': 0, 'label': '1st sample to use (0 means beginning)'}),
        ('num_samples', 
            {'value': 0, 
            'label': '# of samples to use (0 means all)'})
        ]
    
    name = 'Principal Component Analysis'

    def compute(self, waveforms, sampling_rate=None, output_dim=2,
        start_sample=0, num_samples=0):
        """Computes PCA of waveforms concatenated across recording points.
        
        waveforms : ndarray of waveforms, of shape
            (N_spikes, N_recordingpoints, len(waveform))        
        sampling_rate : not used
        output_dim : Number of features (eigenvalues) to return per waveform
        start_sample : Index of first sample in each waveform to slice out
            to use for PCA
        num_samples : Number of samples of each waveform to use for PCA.
            The default is '0', which means to use all samples, regardless
            of the value of `start sample`.
        
        Returns : pca_mat, a matrix of components. shape: (N_spikes, N_features)
        """
        lenwf = waveforms.shape[2]
        
        if num_samples > 0:
            # We're not using all samples
            if start_sample < 0 or start_sample >= lenwf: 
                # garbage input, use all samples
                print "warning: start_sample must be in [0, %d)" % lenwf
                start_sample = 0
            
            # slice
            waveforms = waveforms[:, :, start_sample:(start_sample+num_samples)]
        
        # reshape into the format PCA expects. Each row is now a concatenation
        # of waveforms from each channel in the group.
        waveforms2 = waveforms.reshape(waveforms.shape[0], 
            waveforms.shape[1]*waveforms.shape[2])
        
        # do PCA and return results in (N_spikes, N_features) shape
        pca_mat = mdp.pca(waveforms2, output_dim=output_dim)
        return pca_mat

