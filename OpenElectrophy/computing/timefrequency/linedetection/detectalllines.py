# -*- coding: utf-8 -*-
"""

"""
from numpy import where,in1d,array,c_,ediff1d,zeros,digitize,arange,unique
from ....classes import Oscillation

def simultaneous_ridge_detection(powermap,
            threshold,
            ind_start=0,
            ind_stop=None,
            only_inside_max = True
            ):
    """
    Detect all ridges of powermap above threshold (time is the first dimension)
    By defaults only ridges which contains a true local maxima are kept
    
    output:
    list of tuple (line_t array,line_f array) (all is index based)
    """
    if (powermap.shape[0]<=2)or(powermap.shape[1]<=2):
        return []
    else:
        if ind_stop==None:
            ind_stop=powermap.shape[0]
         
        # Following array are used to limit the "hill" top and "valley" down points
        # Detected lines will be composed of top points and separated by down points
        local_freq_max=((powermap[:,1:-1]-powermap[:,:-2])>=0)&((powermap[:,1:-1]-powermap[:,2:])>=0)
        local_freq_min=((powermap[:,1:-1]-powermap[:,:-2])<=0)&((powermap[:,1:-1]-powermap[:,2:])<=0) 
        # Add edges -> for now freq edges stop the lines
        #~ local_freq_max=c_[(powermap[:,0]-powermap[:,1])>=0,local_freq_max,(powermap[:,-1]-powermap[:,-2])>=0]
        #~ local_freq_min=c_[(powermap[:,0]-powermap[:,1])<=0,local_freq_min,(powermap[:,-1]-powermap[:,-2])>=0]
        null_vector=zeros(local_freq_max.shape[0],dtype='bool')
        local_freq_max=c_[null_vector,local_freq_max,null_vector]
        local_freq_min=c_[null_vector,local_freq_min,null_vector]
        
        # Take threshold into account
        local_freq_max=local_freq_max&(powermap>=threshold)


        basin_map=local_freq_min.cumsum(axis=1) # For a given timestep, it allows to know when "down" points have been crossed
        
        # Simultaneous construction of all lines by sweeping accross the powermap from left to right
        list_osc_final=[] # final oscillation list
        cur_f,=local_freq_max[ind_start,:].nonzero() # frequency list of ongoing oscillation detections
        osc_line_f=[[x] for x in cur_f] # line_f list of ongoing oscillation detections
        osc_line_t=[[ind_start] for x in xrange(cur_f.size)] # line_t list of ongoing oscillation detections

        for i in xrange(ind_start+1,ind_stop): # i is the next timestep
            next_f, =local_freq_max[i,:].nonzero() # tops of next timestep
            if cur_f.size>0:
                cur_basin=basin_map[i,cur_f] # gives the aera number of each line
                new_next_f=[]
                next_basin=basin_map[i,next_f] # area numbers of next tops 
                                    # (but taken from the same timestep since area nmbers can change at each step,
                                    # if a new area appear or another disappear)
                ind_osc=0 # exact list iterator
                for j in xrange(cur_f.size): # check the future of each line
                    try:
                        ind_next_f=where(next_basin==cur_basin[j])[0] # find next top index 
                    except:
                        print "Error :",j,cur_basin,i
                    if ind_next_f.size>0: # append new top to the line
                        osc_line_f[ind_osc].append(next_f[ind_next_f[0]])
                        new_next_f.append(next_f[ind_next_f[0]])
                        ind_osc+=1 # now check next line
                    else: # no more top, the line must be closed (with a "pop")
                        list_osc_final.append((array(osc_line_t.pop(ind_osc)),array(osc_line_f.pop(ind_osc))))
                if next_f.size>unique(new_next_f).size: # some tops may have no precursors => new lines !
                    new_osc_f=next_f[~in1d(next_f,array(new_next_f))] # find the tops not affected to any line
                    for f in new_osc_f:
                        osc_line_f.append([f])
                        osc_line_t.append([]) # the line_t are adjusted for all lines simultaneously later
                        new_next_f.append(f)
                for line_t in osc_line_t:
                    line_t.append(i) # increment line_t
                cur_f=array(new_next_f)
            else:
                if len(next_f)>0: # if there is ONLY new lines
                    cur_f=next_f.copy()
                    osc_line_f=[[x] for x in cur_f]
                    osc_line_t=[[i] for x in xrange(cur_f.size)]
                    cur_basin=basin_map[i,cur_f]

        for ind_osc in xrange(cur_f.size): # at stop, ongoing lines must be closed
            list_osc_final.append((array(osc_line_t[ind_osc]),array(osc_line_f[ind_osc])))

        if only_inside_max: # for all lines, check it contains a local max
            tmp_list=[]
            for indices in list_osc_final:
                power_line=powermap[indices]
                if any((ediff1d(power_line)[:-1]>0.)&(ediff1d(power_line)[1:]<0.)):
                    tmp_list.append(indices)
            list_osc_final = tmp_list

        return list_osc_final

def detect_oscillations(scalogram,
            t_start,
            sampling_rate,
            f_start,
            deltafreq,
            threshold,
            list_max = None,
            ):
    """
    Construct a list of :class:Oscillation which are detected on the scalogram
    
    Input:
    ``scalogram``
        complex scalogram array (its attributes t_start, sampling_rate, f_start and deltafreq must be given too)
        
    ``threshold``
        minimum power amplitude of :class:Oscillation line_val
        
    ``detection_start and detection_end``
        time limits of the detection in second
    
    Output:
    list of :class:Oscillation
    
   """ 
    if list_max==None:
        list_osc_indices=simultaneous_ridge_detection(abs(scalogram),threshold)
    else:
        if list_max.size>0:
            list_osc_indices=simultaneous_ridge_detection(abs(scalogram),threshold,only_inside_max=False)
            list_max_t=digitize(list_max.time,t_start+1.*arange(scalogram.shape[0])/sampling_rate)-1
            list_max_f=digitize(list_max.freq,f_start+1.*arange(scalogram.shape[1])*deltafreq)-1
            
            tmp_list=[]
            for indices in list_osc_indices:
                mask=in1d(indices[0],list_max_t)
                possible_ind=where(mask)[0]
                # Be careful, there may be two or more max at the same t (in list_max_t)
                for ind in possible_ind: 
                    if indices[1][ind] in list_max_f[list_max_t==indices[0][ind]]:
                        tmp_list.append(indices)
                        break
                        
            list_osc_indices=tmp_list
            
        else:
            list_osc_indices=[]
            
    list_osc=[]
    for line_t,line_f in list_osc_indices:
        osc=Oscillation()
        osc.time_line=t_start+1.*line_t/sampling_rate
        osc.freq_line=f_start+1.*line_f*deltafreq
        osc.value_line=scalogram[line_t,line_f]
        osc.amplitude_max=abs(osc.value_line).max()
        ind_max=abs(osc.value_line).argmax()
        osc.time_max=osc.time_line[ind_max]
        osc.freq_max=osc.freq_line[ind_max]
        osc.time_start=osc.time_line[0]
        osc.freq_start=osc.freq_line[0]
        osc.time_stop=osc.time_line[-1]
        osc.freq_stop=osc.freq_line[-1]
        list_osc.append(osc)
        
    return list_osc
