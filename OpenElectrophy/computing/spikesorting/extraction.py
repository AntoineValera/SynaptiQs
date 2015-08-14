# -*- coding: utf-8 -*-


"""
Extraction of the waveforms from the signal and spike positions 

The extracted waveform array has 3 dimensions:
  0.: spike index
  1.: recording index (in a group of recording points, size=1 for monoelectrode)
  2.: individual spike trace waveform

spikesorting.extraction offers only 1 method:

 * .. autoclass:: WaveformExtractor



"""
from numpy import zeros, nan, where, inf

class WaveformExtractor:
    """
    **Waveform extractor**
    
    This method is really straightforward. The only subtility
    is the temporal spike alignment. 
    
     :alignment: **on threshold** or **on peak**
     
     
     
    """
    params = [
                        #~ ( 'left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
                        #~ ( 'right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),
                        ( 'alignment' , { 'value' : 'on peak' , 'label' : 'Waveform alignment', 'possible' : ['on peak', 'on threshold', ] } ),
                        
                        
                        ]
    name = 'Waveform extraction'    
    
    
    def compute(self, anaSigList, pos_spike,sign,  left_sweep = 0.001 , right_sweep = 0.002, alignment = 'on peak' ):
        
        # assuming same sampling_rate
        sr = anaSigList[0].sampling_rate
        swL = int(left_sweep*sr)
        swR = int(right_sweep*sr)
        wsize = swL + swR + 1
        trodness = len( anaSigList )
        
        waveforms = zeros( (pos_spike.size,  trodness, wsize) )
        for i,pos in enumerate(pos_spike) :
            if  alignment == 'on peak':
                if sign == '-' : max_peak = inf
                elif sign == '+' : max_peak = -inf
                
                shift = 0
                for j,anaSig in enumerate(anaSigList):
                    sig = anaSig.signal
                    s1 = sig[pos-1:pos+swR]
                    if sign == '-' :
                        peaks, =where((s1[1:-1] <= s1[:-2]) & (s1[1:-1] <= s1[2:]))
                    elif sign == '+' :
                        peaks, =where((s1[1:-1] >= s1[:-2]) & (s1[1:-1] >= s1[2:]))
                    if len(peaks)!=0:
                        peak1 = peaks[0]+1
                        if sign == '-' :
                            if s1[peak1]<max_peak :
                                max_peak = s1[peak1]
                                shift = peak1-1
                        elif sign == '+' :
                            if s1[peak1]>max_peak :
                                max_peak = s1[peak1]
                                shift = peak1-1
                pos += shift
            
            for j,anaSig in enumerate(anaSigList):
                sig = anaSig.signal
                if (pos-swL > 0) and (pos+swR+1 < sig.size):
                    waveforms[i, j, :] = anaSig.signal[pos-swL : pos+swR+1]
           
        return waveforms





list_method = [ WaveformExtractor ]


