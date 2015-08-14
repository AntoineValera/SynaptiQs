# -*- coding: utf-8 -*-

"""
The spikesorting.detection module offers 4 methods for detection. Note
that all methods work both for mono-electrode and tetrodes except the
last one:

 * .. autoclass:: CrossingThreshold

 * .. autoclass:: StdThreshold
 
 * .. autoclass:: MedianThreshold

 * .. autoclass:: DiffBaselinePeak

"""

from numpy import inf, nan, where, any, array, mean, median , ones, sum, empty, argsort, std, tile, all, concatenate, ones_like
#~ from scipy import any
from scipy import convolve, diff
from scipy import signal

class CrossingThreshold:
    """
    **Crossing threshold method**
    
    Classical detection method: when a peak is above (or below) the threshold
    a spike is detected. Note that the detected spike windows do not overlap since you give 
    the left and right sweep of the windows.
    
    Note the current version of MedianThreshold passes a negative value. It
    looks like if sign == '-', then threshold should be negative.
    
     :sign: positive or negative spikes
     :thresh: absolute value of threshold
     :left_sweep: left sweep of the window in second
     :right_sweep: right sweep of the window in second
    
    """
    params = [
                        ( 'sign' , { 'value' : '-' , 'label' : 'Sign of front', 'possible' : ['-', '+', ] } ),
                        ( 'thresh' , { 'value' : 1. , 'label' : 'Asbolut threshold'} ),
                        ( 'left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
                        ( 'right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),
                        ]
    name = 'Abs threshold detection'
    
    def compute(self, anaSigList, sign = '-', left_sweep = 0.001 , right_sweep = 0.002, thresh = 1.):
        """Return indices of threshold crossings, combined across signals.
        
        Description
        -----------
        Given a threshold and a list of signals, this function returns
        the indices of threshold crossings (putative spikes), subject to
        the following constraints:
        1)  The peak must be below :thresh: if :sign: is '-', and above
            :thresh: otherwise.
        2)  The crossing must not occur within :left_sweep: of the beginning
            of the signals, or within :right_sweep: of the end of the signal.
        3)  There must not be another peak in any of the AnalogSignal within
            [:-left_sweep:, :right_sweep:] that is more extreme than the
            returned spike. "Extreme" means negative if :sign: is '-'.
        This guarantees that windows of size [:-left_sweep:, :right_sweep]
        taken around any returned spike times will not overlap.        
        
        Parameters
        ----------
        anaSigList : a list of AnalogSignal in which to detect spikes. These
            should have the same time course and be from the same spike
            sorting group (for example, a single channel, or 4 channels
            from the same tetrode).
        sign : if '-', return negative peaks, otherwise return positive peaks.
        left_sweep : float, in seconds, see Description
        right_sweep : float, in seconds, see Description
        thresh : in same units as AnalogSignal, the minimum height of a peak.
            This should be negative if :sign: is '-'.
        
        Returns
        -------
        An array of putative spike times subject to contraints in Description.
        """
        # A list of lists of spike times (in samples), relative to beginning
        # of each AnalogSignal.
        pos_spikes = [ ]
        
        # Convert threshold to positive value. You should be passing a
        # negative value for threshold if you want negative spikes.
        if sign == '-' :
            thresh = - thresh
        elif sign =='+' :
                pass

        # For each AnalogSignal, put threshold crossings into pos_spikes.
        # Strictly speaking: iff :idx: is in pos_spikes[n], then 
        # anaSigList[n][idx] <= thresh  &&  anaSigList[n+1][idx] > thresh
        for i,anaSig in enumerate(anaSigList):
            sr = anaSig.sampling_rate
            sig_size = anaSig.signal.size
            swL = int(left_sweep*sr)
            swR = int(right_sweep*sr)
            sig = anaSig.signal
            
            # Reduce both cases to the case of finding positive crossings.
            if sign == '-' :
                sig = -sig
            elif sign =='+' :
                pass
                #~ sig = sig
            
            # Classical threshold detection for positive crossings.
            # Threshold crossings occur (ie, n is in pos_spike) when
            # sig[n]<=thresh && sig[n+1]>thresh. Note the last index of the
            # segment can never be a spike according to this definition.
            pos_spike, = where( (sig[:-1] <= thresh) & ( sig[1:]>thresh) )
            
            # Remove spikes within left (right) sweep from beginning (end)
            # of segment, with some additional padding.
            pos_spike = pos_spike[ pos_spike > (swL+1) ]
            pos_spike = pos_spike[ pos_spike < (sig_size-swR-3) ]
            pos_spikes.append(pos_spike)
        
        
        # Concatenate spikes from each AnalogSignal into one array and
        # also keep track of the index into :anaSigList: with :on_signal:
        n_total = sum([ pos_spike.size for pos_spike in pos_spikes ])
        all_pos_spike = empty( (n_total), 'i')
        on_signal = empty( (n_total), 'i')
        p = 0
        for i,pos_spike in enumerate(pos_spikes):
            all_pos_spike[p:p+pos_spike.size] = pos_spike
            on_signal[p:p+pos_spike.size] = i
            p += pos_spike.size
        
        # merge overlapping sweeps inter and intra signals
        # Sort the spikes from all AnalogSignal together.
        ind_sort = argsort(all_pos_spike)
        all_pos_spike = all_pos_spike[ind_sort]
        on_signal = on_signal[ind_sort]
        l1=0
        l2 = 0
        to_remove = [ ]
        
        # Iterate through all threshold crossings :p:. Compare all other
        # threshold crossings :l: within the window from :p:. Discard :p:
        # if the extrema within the window occur at the window edges. Discard
        # either :p: or :l:, keeping the one which has a greater peak within
        # its window.        
        for p in xrange(all_pos_spike.size):
            # Take the p-th spike time
            pos = all_pos_spike[p]
            
            # Find the index of the last spike which occurs <= (pos - swL),
            # or if None, then use l1 == all_pos_spike.size
            while (all_pos_spike[l1] + swL) <= pos and (l1<all_pos_spike.size-1): l1+=1
            
            # Find the index of the last spike which occurs <= (pos + swR),
            # or if None, then use l2 == all_pos_spike.size
            while (all_pos_spike[l2] - swR) <= pos  and (l2<all_pos_spike.size-1) : l2+=1
            
            # Iterate through the spikes in this time range from all signals.
            # Identify the highest peak from any signal in this time range and
            # append all others to :to_remove:.
            # Once we know that spike :p: is not the highest, break out of
            # this loop since :p: will be removed anyway.
            for l in range(l1,l2):
                if l == p :continue
                #compare all_pos_spike[p] vs all_pos_spike[l]
                # where is the best amplitude of the first following peak ?
                # s1 is the signal from which :pos: was detected,
                # from one sample before p to swR samples after p
                s1 = anaSigList[on_signal[p]].signal[all_pos_spike[p]-1:all_pos_spike[p]+swR]
                
                # Invert signal for sign == '-', so we can just detect
                # positive peaks.
                if sign == '-' : s1 = -s1
                
                # Find indices where s1[n+1] >= s1[n]
                # and also s1[n+1] >= s1[n+2] (ie relative maxima)
                # Note the s1[0] (p-1) and s1[-1] (p+swR-1) are not eligible.
                peaks, =where((s1[1:-1] >= s1[:-2]) & (s1[1:-1] >= s1[2:]))
                if len(peaks)==0:
                    # No peaks, the maxima are at the extremes, remove :p:
                    # and break out of this loop
                    to_remove.append(p)
                    break
                
                # Store the value at the peak, accounting for the shift of 1
                # We keep only the first peak, which should be :p+1: since :p+1:
                # is a peak and we began checking at :p-1:.
                peak1 = peaks[0]+1
                
                # Do the same trick with spike :l: from signal :on_signal[l]:
                s2 = anaSigList[on_signal[l]].signal[all_pos_spike[l]-1:all_pos_spike[l]+swR]
                if sign == '-' : s2 = -s2
                peaks, =where((s2[1:-1] >= s2[:-2]) & (s2[1:-1] >= s2[2:]))
                if len(peaks)==0:
                    to_remove.append(l)
                    continue
                peak2 = peaks[0]+1
                
                # Compare the height of the peaks for p and l and keep
                # the higher one. If :p: is not the highest, break out of this
                # loop completely
                if s1[peak1] >= s2[peak2]:
                    to_remove.append(l)
                else:
                    to_remove.append(p)
                    break
        
        # Remove all spikes in :to_remove:
        to_remove = array(to_remove, 'i')
        all_pos_spike[to_remove] = -1
        all_pos_spike = all_pos_spike[all_pos_spike!=-1]
        
        # Now return the indices of the threshold crossings. Add one so
        # that the returned index is the first to exceed threshold.
        return all_pos_spike+1



class EnhancedCrossingThreshold:
    """Replacement for CrossingThreshold (under development).
    
    Methods
    -------
    compute : Requires all segments at once. Accepts some new optional
        arguments.
    compute_single_segment : Calculates crossings on just one segment
    """
    # These params are used in the GUI I think.
    # Also, computeDetectionEnhanced looks for the presence of
    # 'consistent_across_segments' in order to know that this is a global
    # detection method. Once all detection methods are
    # global, it will not be necessary to keep these flags here.
    # Actually this method does not even use the consistent_across_channels
    # or consistent_across_segments flags. 
    params = [
        ( 'sign' , { 'value' : '-' , 'label' : 'Sign of threshold', 'possible' : ['-', '+', ] } ),
        ( 'thresh' , { 'value' : 1. , 'label' : 'Absolute threshold'} ),
        ( 'left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
        ( 'right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),
        ('consistent_across_channels', 
            {'value' : True, 'label' : 'Consistent across channels'}),
        ('consistent_across_segments',
            {'value' : True, 'label' : 'Consistent across segments'}),        
        ]
    name = 'Multi-segment absolute threshold detection'
    
    def compute(self, anaSigBySegment, sign='-', left_sweep=0.001, 
        right_sweep=0.002, thresh=1., consistent_across_segments=True,
        consistent_across_channels=True):
        """Replacement for CrossingThreshold (under development)       
        
        New Arguments
        -------------
        :anaSigBySegment: A list with one entry for each Segment.
            Each entry is itself a list of AnalogSignal from that Segment. 
            The AnalogSignal should be consistently ordered in each entry. 
            
            Generally the signals come from physically grouped channels, 
            such as a tetrode, because one list of crossing times will be
            calculated using all of the signals.
        
        :thresh: 
            If 2d array of thresholds: thresh[r, c] is the threshold
                for segment r and channel c. Generally this is produced by
                EnhancedMedianThreshold.
            If scalar: the threshold to be used for all cases.
        
        :consistent_across_channels: does nothing here, will be removed
        :consistent_across_segments: does nothing here, will be removed
        """
        # Check for a common error
        if sign is '-' and any(thresh > 0):
            # We should probably just silently make the sign of `thresh`
            # correct unless somebody is using this functionality on purpose.
            print "warning, some seg_threshs > 0 but sign is '-'"        
        
        # If thresh is a scalar, make a 2d array
        try:
            thresh.shape
        except:
            thresh = thresh * ones((len(anaSigBySegment), 
                len(anaSigBySegment[0])))
        
        # Store
        self.thresholdsBySegment = thresh
        self.left_sweep = left_sweep
        self.right_sweep = right_sweep
        self.sign = sign
        self.sr = anaSigBySegment[0][0].sampling_rate
        self.swL = int(self.left_sweep*self.sr)
        self.swR = int(self.right_sweep*self.sr)           
        
        # Get threshold crossings from each segment independently and
        # append to a growing list.
        spikes_by_segment = []
        for rownum, anaSigList in enumerate(anaSigBySegment):
            # Use the correct row of `thresh` for this segment
            crossings = self.compute_single_segment(anaSigList, 
                thresh_this_segment=thresh[rownum, :])
            spikes_by_segment.append(crossings)
        
        # TODO deal with Segment boundaries here
        
        return spikes_by_segment
    
    def compute_single_segment(self, anaSigList, thresh_this_segment):
        """Computes threshold crossings from single segment
        
        Currently this code is pretty much the same as CrossingThreshold
        but I plan to optimize and test it here before eventually replacing
        CrossingThreshold.
        """        
        # Find threshold crossings from each signal
        all_pos_spike, on_signal = self._get_all_threshold_crossings(anaSigList, 
            thresh_this_segment)    
    
        # Iterate through all threshold crossings :p:. Compare all other
        # threshold crossings :l: within the window from :p:. Discard :p:
        # if the extrema within the window occur at the window edges. Discard
        # either :p: or :l:, keeping the one which has a greater peak within
        # its window.        
        l1=0
        l2 = 0
        to_remove = [ ]
        for p in xrange(all_pos_spike.size):
            # Take the p-th spike time
            pos = all_pos_spike[p]
            
            # Find the index of the last spike which occurs <= (pos - swL),
            # or if None, then use l1 == all_pos_spike.size
            while (all_pos_spike[l1] + self.swL) <= pos and (l1<all_pos_spike.size-1): l1+=1
            
            # Find the index of the last spike which occurs <= (pos + swR),
            # or if None, then use l2 == all_pos_spike.size
            while (all_pos_spike[l2] - self.swR) <= pos  and (l2<all_pos_spike.size-1) : l2+=1
            
            # Iterate through the spikes in this time range from all signals.
            # Identify the highest peak from any signal in this time range and
            # append all others to :to_remove:.
            # Once we know that spike :p: is not the highest, break out of
            # this loop since :p: will be removed anyway.
            for l in range(l1,l2):
                if l == p :continue
                #compare all_pos_spike[p] vs all_pos_spike[l]
                # where is the best amplitude of the first following peak ?
                # s1 is the signal from which :pos: was detected,
                # from one sample before p to swR samples after p
                s1 = anaSigList[on_signal[p]].signal[all_pos_spike[p]-1:all_pos_spike[p]+self.swR]
                
                # Invert signal for sign == '-', so we can just detect
                # positive peaks.
                if self.sign == '-' : s1 = -s1
                
                # Find indices where s1[n+1] >= s1[n]
                # and also s1[n+1] >= s1[n+2] (ie relative maxima)
                # Note the s1[0] (p-1) and s1[-1] (p+swR-1) are not eligible.
                peaks, =where((s1[1:-1] >= s1[:-2]) & (s1[1:-1] >= s1[2:]))
                if len(peaks)==0:
                    # No peaks, the maxima are at the extremes, remove :p:
                    # and break out of this loop
                    to_remove.append(p)
                    break
                
                # Store the value at the peak, accounting for the shift of 1
                # We keep only the first peak, which should be :p+1: since :p+1:
                # is a peak and we began checking at :p-1:.
                peak1 = peaks[0]+1
                
                # Do the same trick with spike :l: from signal :on_signal[l]:
                s2 = anaSigList[on_signal[l]].signal[all_pos_spike[l]-1:all_pos_spike[l]+self.swR]
                if self.sign is '-' : s2 = -s2
                peaks, =where((s2[1:-1] >= s2[:-2]) & (s2[1:-1] >= s2[2:]))
                if len(peaks)==0:
                    to_remove.append(l)
                    continue
                peak2 = peaks[0]+1
                
                # Compare the height of the peaks for p and l and keep
                # the higher one. If :p: is not the highest, break out of this
                # loop completely
                if s1[peak1] >= s2[peak2]:
                    to_remove.append(l)
                else:
                    to_remove.append(p)
                    break
        
        # Remove all spikes in :to_remove:
        to_remove = array(to_remove, 'i')
        all_pos_spike[to_remove] = -1
        all_pos_spike = all_pos_spike[all_pos_spike!=-1]
        
        # Now return the indices of the threshold crossings. Add one so
        # that the returned index is the first to exceed threshold.
        return all_pos_spike+1        

    def _get_all_threshold_crossings(self, anaSigList, thresh_this_segment):
        pos_spikes = list()
        # For each AnalogSignal, put threshold crossings into pos_spikes.
        # Strictly speaking: iff :idx: is in pos_spikes[n], then 
        # anaSigList[n][idx] <= thresh  &&  anaSigList[n+1][idx] > thresh
        for anaSig, thresh in zip(anaSigList, thresh_this_segment):
            sig_size = anaSig.signal.size
            sig = anaSig.signal
            
            # Reduce both cases to the case of finding positive crossings.
            if self.sign is '-' :
                sig = -sig
                thresh = -thresh
            
            # Classical threshold detection for positive crossings.
            # Threshold crossings occur (ie, n is in pos_spike) when
            # sig[n]<=thresh && sig[n+1]>thresh. Note the last index of the
            # segment can never be a spike according to this definition.
            pos_spike, = where( (sig[:-1] <= thresh) & ( sig[1:]>thresh) )
            
            # Remove spikes within left (right) sweep from beginning (end)
            # of segment, with some additional padding.
            pos_spike = pos_spike[ pos_spike > (self.swL+1) ]
            pos_spike = pos_spike[ pos_spike < (sig_size-self.swR-3) ]
            pos_spikes.append(pos_spike)
        
        # Concatenate spikes from each AnalogSignal into one array and
        # also keep track of the index into :anaSigList: with :on_signal:
        all_pos_spike = concatenate(pos_spikes)
        on_signal = concatenate([i*ones_like(pos_spike) \
            for i, pos_spike in enumerate(pos_spikes)])
        
        # Sort the spikes from all AnalogSignal together.
        ind_sort = argsort(all_pos_spike)
        all_pos_spike = all_pos_spike[ind_sort]
        on_signal = on_signal[ind_sort]
        
        return (all_pos_spike, on_signal)


class StdThreshold :
    """
    **Standard deviation threshold method**
    
    Very similar to the **Crossing threshold method** except that the threshold is given
    with a multiple of Std of the signal.
    
    thresh = mean(signal) + std_thresh * std(signal)
    
    
     :sign: positive or negative spikes
     :std_thresh: factor of std threshold
     :left_sweep: left sweep of the window in ms
     :right_sweep: rigth sweep of the window in ms
    
    """    
    params = [
                        ( 'sign' , { 'value' : '-' , 'label' : 'Sign of peak', 'possible' : ['-', '+', ] } ),
                        ( 'std_thresh' , { 'value' : 5. , 'label' : 'Std threshold'} ),
                        ( 'left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
                        ( 'right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),
                        
                        ]
    name = 'Std threshold detection'
    
    def compute(self, anaSigList, sign = '-', left_sweep = 0.001 , right_sweep = 0.002, std_thresh = 5.):
        s = {'+' : 1. , '-' : -1.}[sign]
        threshs = [ ]
        for anaSig in anaSigList :
                threshs.append(  s*abs(std_thresh)*std(anaSig.signal) )
        thresh = mean(threshs)
        #~ print 'thresh' , thresh
        m = CrossingThreshold()
        return m.compute( anaSigList, sign = sign, left_sweep = left_sweep , right_sweep = right_sweep, thresh = thresh)
        


class EnhancedMedianThreshold:
    """Replacement for MedianThreshold (under development).
    
    Usually, the user provides this class to a SpikeSorter :object:, which
    instantiates me and calls my `compute` method on its data.
    
    Methods
    -------
    compute : Requires all segments at once. Accepts new optional parameters
    calculate_threshold : sets the threshold according to parameters, which
        is the first step in detection.
    """
    # These params are used in the GUI I think.
    # Also, computeDetectionEnhanced looks for the presence of
    # 'consistent_across_segments' in order to know that this is a global
    # detection method.
    params = [
        ('sign', {'value': '-', 'label': 'Sign of peak', 'possible': ['-', '+']}),
        ('median_thresh' , { 'value' : 5. , 'label' : 'Median threshold'} ),
        ('left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
        ('right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),
        ('consistent_across_channels', 
            {'value' : False, 'label' : 'Consistent across channels'}),
        ('consistent_across_segments',
            {'value' : True, 'label' : 'Consistent across segments'}),
        ]
    name = 'Multi-segment median threshold detection'

    def compute(self, anaSigBySegment, sign='-', left_sweep=.001,
        right_sweep=.002, median_thresh=5., consistent_across_channels=False,
        consistent_across_segments=True):
        """Computes the threshold on the provided data.
        
        Given a list of lists of AnalogSignal from each Segment, a threshold
        is calculated using the median deviation method:
            median_thresh * median(abs(signal) / .6745)
        
        The thresholds may be:
            * consistent across channels, and/or 
            * consistent across segments.
        
        As usual, the data are then piped to :class: CrossingThreshold to
        actually calculate the crossings of the computed threshold.                
        
        
        Parameters
        ----------
        :anaSigBySegment: A list with one entry for each Segment.
            Each entry is itself a list of AnalogSignal from that Segment. 
            The AnalogSignal should be consistently ordered in each entry. 
            
            Generally the signals come from physically grouped channels, 
            such as a tetrode, because one list of crossing times will be
            calculated using all of the signals.
        
        :sign: string. 
            If '-', negative threshold crossings are returned.
            If '+', positive threshold crossings are returned.        
        :left_sweep: left sweep of the window in ms. See CrossingThreshold
        :right_sweep: right sweep of the window in ms. See CrossingThreshold.
        :median_thresh: float. Desired multiple of the median deviation.
        :consistent_across_channels:
            If True, then the same threshold will be used for all channels.
            If False, then each channel's threshold will be calculated
            independently.
        :consistent_across_segments:
            If True, then the same threshold will be used for all segments.
            If False, the threshold is independently calculated for each
            segment.        
        """
        # TODO: error check here that sampling rate and channel ordering
        # is consistent across all AnalogSignal in anaSigBySegment        
        
        # Use 'sign' to set sign of threshold
        median_thresh = abs(median_thresh)        
        
        # Calculate thresholds. They will be negative if sign is '-'
        seg_threshs = self.calculate_threshold(anaSigBySegment, sign,
            left_sweep, right_sweep, median_thresh, 
            consistent_across_channels, consistent_across_segments)
        
        # Store
        self.thresholdsBySegment = seg_threshs
        
        # Instantiate a crossing threshold detector using these calculated
        # thresholds and return the results.
        m = EnhancedCrossingThreshold()
        return m.compute(anaSigBySegment, sign=sign, left_sweep=left_sweep,
            right_sweep=right_sweep, thresh=seg_threshs)

    def calculate_threshold(self, anaSigBySegment, sign='-', left_sweep=.001,
        right_sweep=.002, median_thresh=5., consistent_across_channels=True,
        consistent_across_segments=False):
        """A separate method in case of future modularization. See `compute`"""
        
        # Use 'sign' to set sign of threshold
        median_thresh = abs(median_thresh)
        
        # `seg_threshs` is a list of lists with one entry per segment. 
        # Each entry is a list with one entry per channel.
        # Later we will average over segments (and/or over channels).        
        seg_threshs = list()
        
        # Iterate over each segment
        for anaSigList in anaSigBySegment:
            # Actually calculate the threshold on each signal individually.
            thresh_by_signal = list()
            for anaSig in anaSigList:
                thresh = median_thresh * median(abs(anaSig.signal)) / .6745
                thresh_by_signal.append(thresh)            
            seg_threshs.append(thresh_by_signal)
        
        # Convert to a 2d array, which uses the assumption that each
        # segment contains the same recording points in the same order
        # seg_threshs will have len(anaSigList) rows and len(anaSigList[0])
        # columns, even if those numbers are one.
        seg_threshs = array(seg_threshs)
        
        # Average across segments and/or channels.
        # Because these are linear operations, we may cascade them.
        if consistent_across_segments:
            temp = seg_threshs.mean(axis=0)
            seg_threshs = tile(temp, (seg_threshs.shape[0], 1))
        if consistent_across_channels:
            temp = seg_threshs.mean(axis=1)
            seg_threshs = tile(temp, (seg_threshs.shape[1], 1)).transpose()
        
        # Adjust for sign
        if sign is '-':
            seg_threshs = -abs(seg_threshs)
        
        return seg_threshs
    


class MedianThreshold :
    """
    **Median deviation threshold method**
   
    Given a list of AnalogSignal (all from the same Segment), a threshold is
    calculated based on Median Deviation Threshold method. Then the data
    are piped to `CrossingThreshold` with this threshold.
    
    Parameters
    ----------
    :sign: positive or negative spikes
    :median_thresh: factor of median threshold
    :left_sweep: left sweep of the window in ms
    :right_sweep: right sweep of the window in ms
    
    The threshold is calculated as
        median_thresh * median(abs(signal)/.6745) 
    for each AnalogSignal individually, and then these results are averaged.    
    """        
    params = [
                        ( 'sign' , { 'value' : '-' , 'label' : 'Sign of peak', 'possible' : ['-', '+', ] } ),
                        ( 'median_thresh' , { 'value' : 5. , 'label' : 'Median threshold'} ),
                        ( 'left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
                        ( 'right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),
                        
                        ]
    name = 'Median threshold detection'
    
    def compute(self, anaSigList, sign = '-', left_sweep = 0.001 , right_sweep = 0.002, median_thresh = 5.):
        # Calculate a threshold
        s = {'+' : 1. , '-' : -1.}[sign]
        threshs = [ ]
        for anaSig in anaSigList :
                threshs.append(  s*abs(median_thresh)*median(abs(anaSig.signal)/.6745) )
        thresh = mean(threshs)
        
        #~ print 'thresh' , thresh
        
        # Pipe data to `CrossingThreshold` and return the results
        m = CrossingThreshold()
        return m.compute( anaSigList, sign = sign, left_sweep = left_sweep , right_sweep = right_sweep, thresh = thresh)
    



class DiffBaselinePeak :
    """
    **Difference between baseline and peak**
    
    This is an experimental detection.
    This a fast transcription of Guillaume Spacan routine
    for detection of synaptic events.
    
    Note that this method works only on mono-electrode.
    
     :sign: positive or negative
     :baseline_time: 
     :rise_time: 
     :peak_time: 
     :window: 
     :threshold: 
     :left_sweep: left sweep of the window in second
     :right_sweep: rigth sweep of the window in second    
    
    """
    params = [
                        ( 'sign' , { 'value' : '-' , 'label' : 'Sign of peak', 'possible' : ['-', '+', ] } ),
                        ( 'baseline_time' , { 'value' : .05 , 'label' : 'Baseline time (s)'} ),
                        ( 'rise_time' , { 'value' : .001 , 'label' : 'Rise time (s)'} ),
                        ( 'peak_time' , { 'value' : .001 , 'label' : 'Peak time (s)'} ),
                        ( 'window' , { 'value' : .00001 , 'label' : 'Windows (s)'} ),
                        ( 'threshold' , { 'value' : 20. , 'label' : 'Threshold'} ),
                        
                        ( 'left_sweep' , { 'value' : 0.001 , 'label' : 'Left sweep'} ),
                        ( 'right_sweep' , { 'value' : 0.002 , 'label' : 'Right sweep'} ),                        
                        ]
    name = 'SpAcAn diff(peak - baseline)'
    
    def compute(self, anaSigList, sign = '-', left_sweep = 0.001 , right_sweep = 0.002, 
                                                                        baseline_time = .05,
                                                                        rise_time = .001,
                                                                        peak_time = .001,
                                                                        threshold =20.,
                                                                        window = .0001,

                                                ):
        anaSig = anaSigList[0]
        sr = anaSig.sampling_rate
        
        nb = int(baseline_time*sr)
        nb = int(nb/2.)*2+1
        nr = int(rise_time*sr)
        np = int(peak_time*sr)
        print peak_time, np, sr
        nw =  int(window*sr)
        
        sigBase = convolve(anaSig.signal , ones(nb, dtype='f')/nb , 'same')
        #~ sigBase = signal.medfilt(anaSig.signal , kernel_size = nb)
        
        sigPeak = convolve(anaSig.signal , ones(np, dtype='f')/np , 'same')
        
        if sign=='-':
            aboves=  sigBase[:-(nr+nb/2+np/2)]  - sigPeak[nr+nb/2+np/2:] >  threshold 
        elif sign=='+':
            aboves =    sigPeak[nr+nb/2+np/2:] - sigBase[:-(nr+nb/2+np/2)] >  threshold 
        
        
        print aboves
        # detection when n point consecutive more than window
        aboves = aboves.astype('f')
        aboves[0]=0
        aboves[-1]=0
        indup, = where( diff(aboves)>.5)
        
        return indup+nr+nb/2+np/2
        
        #~ inddown, = where( diff(aboves)<-.5)
        #~ print indup
        print inddown
        #~ ind,  = where( inddown - indup > nw)
        

        #~ return indup[ind]+nr+nb/2+np/2
        






list_method = [ MedianThreshold, StdThreshold,   CrossingThreshold , DiffBaselinePeak]

