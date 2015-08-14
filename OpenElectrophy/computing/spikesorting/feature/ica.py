# -*- coding: utf-8 -*-

"""
projection method for spike sorting : ica

"""




import mdp
from numpy import empty

class ICA:
    """
    **Independant Component Analysis**
    
    This method compute an indepedent component decomposition, and
    keep the N higher eigenvalues. 
    
    This algorithm comes from the excellent MDP  toolkit : http://mdp-toolkit.sourceforge.net/
    
     :N: N higher components
    
    """    
    params = [
                    ( 'output_dim' , { 'value' : 8 , 'label' : 'output dimension (n component)'} ),
                    ]
    
    name ='Independant Component Analysis'

    def compute( self , waveforms , sampling_rate , output_dim =2) :
        
        #~ waveforms2 = empty( (waveforms.shape[0] , waveforms.shape[1]*waveforms.shape[2] ) )
        #~ for i in range(waveforms.shape[0]):
            #~ waveforms2[i,:] = waveforms[i].reshape( (waveforms.shape[1]*waveforms.shape[2]) )
        
        waveforms2 = waveforms.reshape(waveforms.shape[0], -1)
        
        ica_mat = mdp.fastica(waveforms2 , whitened = 0,
                        white_comp = output_dim,
                        g = 'tanh' ,
                        approach= 'symm'  )
        return ica_mat
        
        
