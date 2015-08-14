# -*- coding: utf-8 -*-

"""
clusering method for spike sorting : ParamMagnetic

based on spins at a fixed temperature


"""


from algomagnetic import paramagneticclustering


class ParamMagnetic :
    """
    **Param Magnetic**
    
    This method is a draft but usable of super-paramagnetic clustering (SPC)  by Blatt (1996)
    introduced in spike sorting world by Quian Quiroga (2004) 
    in the `wave_clus <http://www.vis.caltech.edu/~rodri/Wave_clus/Wave_clus_home.htm>`_ 
    matlab package.
    Unfortunatly the SPC part of wave_clus is closed source so this method is no completely
    equivalent but the concepts are the same.
    
    This code come from an old C code from Thomas Ott.
    
     :temperature: temperature
     :threshold: threshold
     
    
    """
    params = [
                    ( 'temperature' , { 'value' : 0.01 , 'label' : 'Temperature'} ),
                    ( 'threshold' , { 'value' : .3 , 'label' : 'Threshold'} ),
                    
                    ]    
    
    name = 'Param magnetic'
    
    def compute(self , waveforms , spike_times , temperature = 0.01, threshold = .3) :
        
        code = paramagneticclustering(waveforms,
                                                    T = temperature,
                                                    threshold=threshold,
                                                    knear=4 ,
                                                    radius=5.2,
                                                    Q = 20,
                                                    MCS=250 , #number of Monte Carlo steps 
                                                    
                                                    
                                                        )
        
        return code

