import pca
import onlymax
import numpy as np


class PCA_Plus_Max:
    """Simple combination of PCA feature and OnlyMax feature"""
    params = [
        ('n_pca_comp', {'value': 8 ,'label' : 'number of PCA components'} ),
        ('sign', {'value': '-', 'label': 'Positive or negative max?', 
            'possible': ['-', '+', 'either', 'abs(either)'] } )
        ]
    name = 'PCA Plus Max'
    
    def compute(self, waveforms, sampling_rate=None, n_pca_comp=8, sign='-'):
        """Return concatenation of PCA and OnlyMax features.
        
        OnlyMax is first component.
        """
        # shape (N_spikes, n_pca_comp)
        a1 = pca.PCA().compute(waveforms, sampling_rate, output_dim=n_pca_comp)
        
        # shape (N_spikes, trodness)
        #a2 = onlymax.OnlyMax().compute(waveforms, sampling_rate)
        print sign
        if sign == '-':
            a2 = np.min(waveforms, axis=2)
        elif sign == '+':
            a2 = np.max(waveforms, axis=2)
        elif sign == 'either':
            minny = np.min(waveforms, axis=2)
            maxxy = np.max(waveforms, axis=2)
            a2 = np.where(maxxy > np.abs(minny), maxxy, minny)
        elif sign == 'abs(either)':
            a2 = np.max(np.abs(waveforms), axis=2)
        
    
        return np.concatenate([a2, a1], axis=1)