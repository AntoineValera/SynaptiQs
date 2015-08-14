# -*- coding: utf-8 -*-
"""


"""

from ..filter import fft_passband_filter

from numpy import where, argmin, argmax, unique, array, zeros, ones, median, nan
from scipy import signal


class SimpleRespirationCycleExtraction():
    params = [
                        ( 'inspiration_sign' , { 'value' : '-' , 'label' : 'Sign of inspiration', 'possible' : ['-', '+', ] } ),
                        ( 'high_pass_filter' , { 'value' : None , 'type' : float,  'label' : 'High pass filter to remove  deviation (Hz)'} ),
                        ( 'constrain_frequency' , { 'value' : None ,  'type' : float, 'label' : 'Constrain frequency band '} ),
                        ( 'median_windows_filter' , { 'value' : None ,  'type' : float, 'label' : 'Sliding window median filter (s)'} ),
                        
                        ( 'baseline_with_average' , { 'value' : True , 'label' : 'Baseline with average'} ),
                        ( 'manual_baseline' , { 'value' : 0. , 'label' : 'Otherwise manual baseline'} ),
                        
                        ( 'eliminate_time_shortest_ratio' , { 'value' : 3. , 'label' : 'ratio for eliminating shortest cycle in time'} ),
                        ( 'eliminate_amplitude_shortest_ratio' , { 'value' : 3. , 'label' : 'ratio for eliminating shortest cycle in amplitude'} ),
                        #~ ( 'eliminate_mode' , { 'value' : 'OR' , 'label' : 'condition for elimination', 'possible' : ['OR', 'AND', ] } ),
                        ]
    name = 'Simple cycle extraction'
    
    def compute(self, anaSig,
        
                                    # preprocessing
                                    inspiration_sign = '-',
                                    high_pass_filter = None,
                                    constrain_frequency = 1.,
                                    median_windows_filter = None,
                                    
                                    # baseline
                                    baseline_with_average = True,
                                    manual_baseline = 0.,
                                    
                                    # clean
                                    eliminate_time_shortest_ratio = 10,
                                    eliminate_amplitude_shortest_ratio = 10,
                                    eliminate_mode = 'OR', # 'AND'
                                    
                                    ):
        

        sig = anaSig.signal
        sr = anaSig.sampling_rate

        # STEP 1 : preprocessing
        sig = sig  - manual_baseline

        if inspiration_sign =='-' :
            sig = -sig
        
        original_sig = sig.copy()

        if median_windows_filter is not None:
            k = round(median_windows_filter*sr/2.)*2+1
            sig = signal.medfilt(sig, kernel_size = k)

        #baseline center
        if baseline_with_average:
            centered_sig = sig - sig.mean()
        else:
            centered_sig = sig

    
        if high_pass_filter is not None:
            sig =  fft_passband_filter(sig,high_pass_filter/(sr/2),1.)
        
        
        # hard filter to constrain frequency
        if constrain_frequency is not None:
            filtered_sig = fft_passband_filter(centered_sig,0.0,constrain_frequency/(sr/2))
        else :
            filtered_sig = centered_sig
        
        
        # STEP 2 : crossing zeros on filtered_sig
        ind1, = where( (filtered_sig[:-1] <=0) & (filtered_sig[1:] >0))
        ind2, = where( (filtered_sig[:-1] >=0) & (filtered_sig[1:] <0))
        ind2 = ind2[ (ind2>ind1[0]) & (ind2<ind1[-1]) ]

    
    

        # STEP 3 : crossing zeros on centered_sig
        ind_inspi_possible, = where( (centered_sig[:-1]<=0 ) &  (centered_sig[1:]>0 ) )
        list_inspi = [ ]
        for i in range(len(ind1)) :
            ind = argmin( abs(ind1[i] - ind_inspi_possible) )
            list_inspi.append( ind_inspi_possible[ind] )
        list_inspi = unique(list_inspi)

        ind_expi_possible, = where( (centered_sig[:-1]>0 ) &  (centered_sig[1:]<=0 ) )
        list_expi = [ ]
        for i in range(len(list_inspi)-1) :
            ind_possible = ind_expi_possible[ (ind_expi_possible>list_inspi[i]) & (ind_expi_possible<list_inspi[i+1]) ]
            
            ind_possible2 = ind2[ (ind2>list_inspi[i]) & (ind2<list_inspi[i+1]) ]
            ind_possible2.sort()
            if ind_possible2.size ==1 :
                ind = argmin( abs(ind_possible2 - ind_possible ) )
                list_expi.append( ind_possible[ind] )
            elif ind_possible2.size >=1 :
                ind = argmin( abs(ind_possible2[-1] - ind_possible ) )
                list_expi.append( ind_possible[ind]  )
            else :
                list_expi.append( max(ind_possible)  )
        
        list_inspi,list_expi =  array(list_inspi,dtype = 'i')+1, array(list_expi,dtype = 'i')+1
        
        
        # STEP 4 :  cleaning for small amplitude and duration
        nb_clean_loop = 20
        if eliminate_mode == 'OR':
            # eliminate cycle with too small duration or too small amplitude
        
            if eliminate_amplitude_shortest_ratio is not None :
                for b in range(nb_clean_loop) :
                    max_inspi = zeros((list_expi.size))
                    for i in range(list_expi.size) :
                        max_inspi[i] = max( abs(centered_sig[list_inspi[i]:list_expi[i]]) )
                    ind, = where( max_inspi < median(max_inspi)/eliminate_amplitude_shortest_ratio)
                    list_inspi[ind] = -1
                    list_expi[ind] = -1
                    list_inspi = list_inspi[list_inspi != -1]
                    list_expi = list_expi[list_expi != -1]
                    
                    max_expi = zeros((list_expi.size))
                    for i in range(list_expi.size) :
                        max_expi[i] = max( abs(centered_sig[list_expi[i]:list_inspi[i+1]]) )
                    ind, = where( max_expi < median(max_expi)/eliminate_amplitude_shortest_ratio)
                    list_inspi[ind+1] = -1
                    list_expi[ind] = -1
                    list_inspi = list_inspi[list_inspi != -1]
                    list_expi = list_expi[list_expi != -1]
                
            if eliminate_time_shortest_ratio is not None :
                for i in range(nb_clean_loop) :
                    l = list_expi - list_inspi[:-1]
                    ind, = where(l< median(l)/eliminate_time_shortest_ratio )
                    list_inspi[ind] = -1
                    list_expi[ind] = -1
                    list_inspi = list_inspi[list_inspi != -1]
                    list_expi = list_expi[list_expi != -1]
                    
                    l = list_inspi[1:] - list_expi
                    ind, = where(l< median(l)/eliminate_time_shortest_ratio )
                    list_inspi[ind+1] = -1
                    list_expi[ind] = -1
                    list_inspi = list_inspi[list_inspi != -1]
                    list_expi = list_expi[list_expi != -1]
        
        
        elif eliminate_mode == 'AND':
            # eliminate cycle with both too small duration and too small amplitude
            max_inspi = zeros((list_expi.size))
            for b in range(nb_clean_loop) :
                
                max_inspi = zeros((list_expi.size))
                for i in range(list_expi.size) :
                    max_inspi[i] = max( abs(centered_sig[list_inspi[i]:list_expi[i]]) )
                l = list_expi - list_inspi[:-1]
                cond = ( max_inspi < median(max_inspi)/eliminate_amplitude_shortest_ratio ) & (l< median(l)/eliminate_time_shortest_ratio)
                ind,  = where(cond)
                list_inspi[ind] = -1
                list_expi[ind] = -1
                list_inspi = list_inspi[list_inspi != -1]
                list_expi = list_expi[list_expi != -1]
                
                max_expi = zeros((list_expi.size))
                for i in range(list_expi.size) :
                    max_expi[i] = max( abs(centered_sig[list_expi[i]:list_inspi[i+1]]) )
                l = list_inspi[1:] - list_expi
                cond = ( max_expi < median(max_expi)/eliminate_amplitude_shortest_ratio) & (l< median(l)/eliminate_time_shortest_ratio )
                ind,  = where(cond)
                list_inspi[ind+1] = -1
                list_expi[ind] = -1
                list_inspi = list_inspi[list_inspi != -1]
                list_expi = list_expi[list_expi != -1]
        
        
        # STEP 5 : take crossing zeros on original_sig, last one before min for inspiration
        ind_inspi_possible, = where( (original_sig[:-1]<=0 ) &  (original_sig[1:]>0 ) )
        for i in range(len(list_inspi)-1) :
            ind_max = argmax(centered_sig[list_inspi[i]:list_expi[i]])
            ind = ind_inspi_possible[ (ind_inspi_possible>=list_inspi[i]) & (ind_inspi_possible<=list_inspi[i]+ind_max) ]
            if ind.size!=0:
                #~ print ind.max(), list_inspi[i] , list_expi[i]
                list_inspi[i] = ind.max()


        cycles = zeros( (list_inspi.size, 2),  dtype = 'f')*nan
        cycles[:,0] = anaSig.t()[list_inspi]
        cycles[:-1,1] = anaSig.t()[list_expi]
        
        return cycles
        
        #~ return list_inspi,list_expi



