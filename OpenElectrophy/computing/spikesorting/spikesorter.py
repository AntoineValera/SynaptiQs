# -*- coding: utf-8 -*-


"""This implements a high level object for spike sorting, which is
useful in a script to wrap low level functions.

The GUI also creates and uses SpikeSorter.
"""
from numpy import *
from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter


from ...classes import *

import filtering
import detection
import extraction
import feature
import clustering


steps = [ 
                        ['Filtering' , filtering, ],
                        ['Detection' , detection,],
                        ['Extraction' , extraction,],
                        ['Features' , feature,],
                        ['Clustering' , clustering,],
                   ]

mode_steps = {
                'from_full_band_signal' : ['Filtering' ,  'Detection' , 'Extraction' , 'Features' , 'Clustering'],
                'from_filtered_signal' :  [ 'Detection' , 'Extraction' , 'Features' , 'Clustering'],
                'from_detected_spike' : [ 'Features' , 'Clustering'],
                }


class SpikeSorter():
    """A convenience class encapsulating all spike sorting functionality.
    
    DATAFLOW
    Each method requires some inputs and produces some outputs, which
    are all stored as attributes in the object. You specify
    the actual implementation method (eg, you can specify a PCA computing
    method for computeFeatures).
    
    Method: __init__
    Parameters: mode, session, recordingPointList, spikeSign, left_sweep,   
        right_sweep
    Outputs: anaSigList, anaSigFilteredList, recordingPoint, trodness, block,
        id_segments, spikeTimes (if present), spike_id_segments (if present)
    
    Method: computeFiltering
    Inputs: anaSigList
    Outputs: anaSigFilteredList    
    
    Method: computeDetection
    Inputs: anaSigFilteredList, spikeSign, left_sweep, right_sweep
    Outputs: spikeTimes, spikePosistionList, spikeLabels, waveforms, features
    
    Method: computeDetectionEnhanced (replaces above)
    Parameters: consistent_across_segments, consistent_across_channels, 
        correct_times
    Inputs: anaSigFilteredList, spikeSign, left_sweep, right_sweep
    Outputs: spikeTimes, spikePosistionList, spikeLabels, waveforms, features
    
    Method: computeExtraction
    Usage: spikesorter.computeExtraction(OE.extraction.WaveformExtractor)
    Inputs: anaSigFilteredList, spikePosistionList, spikeSign, left_sweep,
        right_sweep
    Outputs: waveforms
    
    Method: computeFeatures
    Usage: spikesorter.computeFeatures(feature.PCA, output_dim=8)
    Inputs: waveforms, sampling_rate
    Outputs: features
    
    Method: computeClustering
    Usage: spikesorter.computeClustering(clustering.KMean, n=4)
    Inputs: features, spikeTimes
    Outputs: spikeLabels, names, sortingScores
    
    Method: save_to_db
    Usage: spikesorter.save_to_db()
    Parameters: save_waveform, spiketrain_mode, save_trash, create_empty
    Inputs: mode, waveforms, spikeTimes (if mode == 'from_detected_spike') or
        spikePosistionList, spikeLabels
    Outputs to database: one Neuron per cluster, containing waveforms
        and spike_times
    
    
    ATTRIBUTES (CONCATENATED ACROSS SEGMENTS, ONE ROW PER SPIKE)
    spikeTimes : an array of all spike times concatenated. The
        spike times are relative to the same zero point at the beginning
        of the first segment. Time between segments is not included.    
        (With computeDetectionEnhanced, the times are corrected.)
    spikeLabels : an array of cluster id for each spike
    waveforms : concatenations of waveforms from each SpikeTrain
        Shape is (N_spikes, trodness, len(waveform))
    spikeLabels : array of same length as spike_times containing the
        id_neuron from which each spike came.
        Shape is (N_spikes,)
    spike_id_segments : array of same length as spike_times containing
        the id_segment from which each spike came.    
        Shape is (N_spikes,).
    
    
    ATTRIBUTES (LISTED BY SEGMENT)
    anaSigList : a list of lists, each containing AnalogSignal objects
        from the corresponding Segment in self.id_segments. For example,
        self.anaSigList[3] is a list of the Segment objects in 
        Segment().load(self.id_segments[3])
    anaSigFilteredList : if mode == 'from_filtered_signal', then this
        is the same as self.anaSigList. If mode == 'from_full_band_signal',
        then this is None.        
    spikePosistionList : a list of arrays. The nth entry is the
        spike times from the nth segment in self.anaSigFilteredList.    
    
    
    ATTRIBUTES (DICT BY CLUSTER)
    names : dict mapping cluster ids to cluster names
    sortingScores : dict mapping cluster ids to sorting scores
    
    
    OTHER ATTRIBUTES
    recordingPointList : a list of recording points.
        Each must contain the same number of Segment and each Segment
        must contain the same number of AnalogSignal. Length of this
        variable defines the trodness. Thus you would have 4 signals per
        segment for tetrodes). Also, each signal should have the same sampling
        rate and be from the same block.
    
    TODO
    Remove dependence on spikePosistionList outside of detection methods
    by converting to spikeTimes, thus simplifying data model and allowing
    re-extraction from detected spikes.
    
    Ensure that input analog signals have consistent t_start and sampling_rate
    """
    def __init__(self,
                        
                        
                        
                        mode = None,
                        session = None,
                        
                        recordingPointList=None,
                        # 'from_full_band_signal'
                        # 'from_filtered_signal'
                        # 'from_detected_spike'
                        
                        
                        
                        ):
        """Instantiates a new SpikeSorter to sort spikes from a channel group.
        
        Given a mode of operation, a database, and a list of recording points
        to sort on, this object initializes itself in preparation for sorting
        spikes on the group. It is assumed that the recording points are
        measuring at least some of the same spikes (for example, they are 
        a tetrode).
        
        Parameters
        ----------
        mode : string, one of the following:
            'from_full_band_signal' : we need to filter first
            'from_filtered_signal' : the signals are already filtered
            'from_detected_spike' : spikes have previously been extracted
        
        session : the SQL session that links to the data. The global session
            may be obtained by calling OpenElectrophy.Session()
        
        recordingPointList : a list of RecordingPoint objects. The length of
            this list is the trodness. For example, it could be a list of
            RecordingPoint on the same tetrode.
        
        The AnalogSignal in recordingPointList must all have the same
        sampling rate and come from the same block. The first
        RecordingPoint is privileged: sorted Neuron will be assigned to it,
        and the :trodness: and :block: will be taken from it.
        
        After initialization, the following attributes will be set:
        mode, session, recordingPointList : from arguments
        recordingPoint : the first entry in recordingPointList
        trodness : length of recordingPointList
        block : the block of recordingPoint. Note that all signals should be
            from the same block.
        
        In modes other than 'from_detected_spike', analog data is loaded
        into the following attributes.
        id_segments : a list of id of all Segment in self.block
        anaSigList : a list of lists, each containing AnalogSignal objects
            from the corresponding Segment in self.id_segments. For example,
            self.anaSigList[3] is a list of the Segment objects in 
            Segment().load(self.id_segments[3])
        sampling_rate : sampling rate of self.anaSigList[0][0]. Note that
            this should be the same for all of the signals provided.
        anaSigFilteredList : if mode == 'from_filtered_signal', then this
            is the same as self.anaSigList. If mode == 'from_full_band_signal',
            then this is None.
        
        Finally we have concatenations of spike data, each of the same
        length which is the total number of spikes. If spikes exist in the
        database, they will be loaded, regardless of mode.
        spikeTimes : concatenations of spike_times from each SpikeTrain
        waveforms : concatenations of waveforms from each SpikeTrain
        spikeLabels : array of same length as spike_times containing the
            id_neuron from which each spike came.
        spike_id_segments : array of same length as spike_times containing
            the id_segment from which each spike came.
        
        If mode == 'from_detected_spike', a refreshColors() call occurs.
        """        
        # Save provided parameters
        self.mode = mode
        self.session = session        
        self.recordingPointList = recordingPointList
        self.recordingPoint =  recordingPointList[0]
#        try:
        self.block = recordingPointList[0].block
#        except AttributeError:
#            a=RecordingPoint().load(1)
#            self.block = recordingPointList[1]
        
        # The trodness is the number of recording points to analyze.
        self.trodness = len(self.recordingPointList)            

        self.colors = { }
        self.allLabels = [ ]
        self.shuffledSpikeSubset = None
        self._max_size_by_cluster = 100 # Not util normally
        self.names = { -1 : 'Trash'}
        self.sortingScores = { -1 : ''}

        # These attributes will be set with raw data (in raw data modes).
        self.id_segments = None
        self.anaSigFilteredList = None
        self.anaSigList = None
        self.spikePosistionList = None # list
        
        # These attributes will be loaded from the database if possible.
        # Otherwise, they will be set after detection, extraction, etc.
        self.spikeSign = None
        self.left_sweep = None
        self.right_sweep = None        
        self.spikeTimes = None
        self.waveforms = None
        self.features = None
        self.spikeLabels = None
        self.spike_id_segments = None
        
        # Get Session if necessary
        if self.session is None:
            self.session = globalvars.globalSession()

        # Create links to analog data (in raw data modes)
        if self.mode =='from_full_band_signal' or self.mode =='from_filtered_signal':
            self.id_segments = [seg.id for seg in self.block._segments]
            
            # Get the ids of the recording points
            rp_id_list = [rp.id for rp in self.recordingPointList]
            
            # Define a query for AnalogSignal from the relevant recording
            # points (sorted by id). Later we will unsort back into the 
            # original recording point ordering.
            q = self.session.query(AnalogSignal)
            q = q.order_by(AnalogSignal.id_recordingpoint)           
            q = q.filter(AnalogSignal.id_recordingpoint.in_(rp_id_list))    
            
            # Error check. We should have one analog signal for each
            # recording point and each segment.
            assert q.count() == len(self.recordingPointList) * len(self.id_segments), \
                (("There are %d recording points and %d segments but only " +
                "%d analog signals matched to them!") % (
                len(self.recordingPointList), len(self.id_segments),
                q.count()))
            
            # This will be a list of the same length as self.id_segments. Each
            # entry is itself a list of signals from the specified recording
            # points in each segment.
            self.anaSigList = [q.filter(AnalogSignal.id_segment==id_seg).all() \
                for id_seg in self.id_segments]
            
            # Now unsort into the original recording point ordering
            unsort_idxs = [rp_id_list.index(id) for id in sorted(rp_id_list)]
            self.anaSigList = [list(take(sl, unsort_idxs)) \
                for sl in self.anaSigList]
            
            # Load data now to prevent expungement, and also to speed up
            # future data accesses.
            all_signals = [[s.signal for s in ss] for ss in self.anaSigList]
            del all_signals

            self.sampling_rate = self.anaSigList[0][0].sampling_rate
            
        # If we are using a filtered signal, alias `anaSigList`
        if self.mode =='from_filtered_signal':
            self.anaSigFilteredList = self.anaSigList
        
        # Load spike data from this group if it exists
        q = self.session.query(SpikeTrain)
        q = q.filter(SpikeTrain.id_recordingpoint == self.recordingPoint.id)
        if q.count() > 0:
            # Get all spike trains from this recording point
            stl = q.all()
            
            # Each is a concatenated array with spike number along dim 0
            wf_list = [st.waveforms for st in stl]
            
            # Load waveforms.
            # There are three possible cases.
            # 1) Every spiketrain has waveforms saved -> concatenate wf_list.
            # 2) Some spiketrains had no spikes, so wf_list[n] is None.
            #    In this case we replace the None with 0d array and concatenate.
            # 3) No waveforms were saved and all entries in wf_list are None.
            #    In this case we set self.waveforms to None.
            #    This is a problematic case because we have spike_times
            #    but not spikePosistionList, so the user cannot extract
            #    waveforms even if he wants to. A better solution would be
            #    to regenerate spikePosistionList here (or in Extraction).

            # Get length of waveform if they were saved
            len_waveform = None
            for wf in wf_list:
                if wf is not None: len_waveform = wf.shape[2]
            
            if len_waveform is not None:
                # Waveforms were saved
                for n, wf in enumerate(wf_list):
                    # Wherever waveforms are missing, replace with 0d array.
                    if wf is None:
                        wf_list[n] = zeros((0, len(self.recordingPointList), 
                            len_waveform), dtype=float)
                # Concatenate
                self.waveforms = concatenate(wf_list)
            else:
                # No waveforms were saved in any spiketrain     
                self.waveforms = None
            
            # Concatenate spike times and spike segments.
            self.spikeTimes = concatenate([st.spike_times for st in stl])
            self.spike_id_segments = concatenate([\
                st.id_segment * \
                ones(len(st.spike_times), dtype='i') for st in stl])
            
            # The label of each spike is SpikeTrain.id_neuron if it exists,
            # otherwise it's SpikeTrain.id
            self.spikeLabels = concatenate([\
                (st.id_neuron if st.id_neuron is not None else st.id) * \
                ones(len(st.spike_times), dtype='i') for st in stl])
        
        # If user specified to load from detected spikes, load some additional
        # data from the SpikeTrain, and also set the raw data attributes to None
        if self.mode == 'from_detected_spike':
            assert q.count() > 0, \
                'you requested detected spikes, but no SpikeTrain exist'
            self.sampling_rate = st.sampling_rate
            self.left_sweep = st.left_sweep
            self.right_sweep = st.right_sweep 
            self.refreshColors()
            self.allLabels = unique(self.spikeLabels)
            
            # load names and sorting scores
            self.sortingScores = dict()
            self.names = dict()
            #~ for lbl in self.allLabels:
                #~ q_neuron = self.session.query(Neuron).filter(
                    #~ Neuron.id == lbl).all()
                #~ if len(q_neuron) == 1:
                    #~ self.names[lbl] = q_neuron[0].name
                    #~ self.sortingScores[lbl] = q_neuron[0].sortingScore
        
        
        
        self.session.expunge_all()
        
        
        self.used_methods = { }
        self.used_params = { }
    
    def refreshPlotUtilities(self):
        self.refreshColors()
        self.refreshShuffle(self._max_size_by_cluster)

    def refreshColors(self):
        self.colors = { }
        if self.spikeLabels is None:
            self.allLabels = [ ]
        else:
            self.allLabels = unique(self.spikeLabels)
            cmap = get_cmap('jet' , len(self.allLabels)+3)
            for i , c in enumerate(self.allLabels):
                self.colors[c] = ColorConverter().to_rgb( cmap(i+2) )
        
        self.colors[-1] = ColorConverter().to_rgb( 'k' ) #trash
        
    def refreshShuffle(self, max_size_by_cluster = 100):
        self._max_size_by_cluster = max_size_by_cluster
        if self.spikeLabels is None: return
        
        self.shuffledSpikeSubset = { }
        for i , c in enumerate(self.allLabels):
            ind, = where( self.spikeLabels ==c )
            random.shuffle(ind)
            if max_size_by_cluster < ind.size:
                ind = ind[:max_size_by_cluster]
            self.shuffledSpikeSubset[c]  = ind


    def computeFiltering(self, method_class, **kargs) :
        """
        
        """
        assert 'Filtering' in mode_steps[self.mode], 'Impossible in mode'+ self.mode
        
        self.anaSigFilteredList = [ ]
        for i in range( len(self.anaSigList) ):
            l = [ ]
            for j in range(self.trodness):
                l.append( method_class().compute( self.anaSigList[i][j] , **kargs) )
            self.anaSigFilteredList.append( l )
            
        self.used_methods['Filtering'] = method_class
        self.used_params['Filtering'] = kargs

    

    def computeDetection(self, method_class, **kargs) :
        """Detect spikes in the data and store their times and positions.
        
        The data sources is `self.anaSigFilteredList`, which must be defined.
        
        Parameters
        ----------
        method_class : the class that will do the actual detection. It should
            be defined in the `detection` module and provide a `compute`
            method that accepts a list of filtered AnalogSignal from a
            single segment.
        sign, left_sweep, right_sweep : passed to `method_class.compute` 
        
        The data are passed to `method_class` and the results are stored.
        The results are stored in two objects:
        self.spikePosistionList : a list of arrays. The nth entry is the
            spike times from the nth segment in self.anaSigFilteredList.
        self.spikeTimes : an array of all spike times concatenated. The
            spike times are relative to the same zero point at the beginning
            of the first segment. Time between segments is not included.
        
        To finish up, :spikeLabels: is assigned to all zeros,
        and :waveforms: and :features: are defined but left empty.
        """
        
        assert 'Detection' in mode_steps[self.mode], 'Impossible in mode'+ self.mode
        assert self.anaSigFilteredList is not None, 'not yet filtered'
        
        # Store the provided parameters
        self.spikeSign = kargs['sign']
        self.left_sweep = kargs['left_sweep']
        self.right_sweep = kargs['right_sweep']
        
        # The first place to store results, a list of lists.
        self.spikePosistionList = [ ]
        
        # Keep track of elapsed time.
        t_start = 0.
        
        # Use the sampling rate of the first signal
        sr = self.anaSigList[0][0].sampling_rate
        
        # The second place to store results, all concatenated.
        self.spikeTimes = zeros((0), dtype='f')
        
        # For each segment that we have collected after initialization,
        # extract spike times and append to the growing lists.
        for i in range( len(self.anaSigList) ):
            # Actually call the detection method on the signals from
            # one of the segments.
            spikePosition = method_class().compute(self.anaSigFilteredList[i], **kargs)
            
            # Store the calculated times in two formats.
            self.spikePosistionList.append(  spikePosition  )
            self.spikeTimes = concatenate( (self.spikeTimes , spikePosition/sr + t_start) , axis = 0)
            
            # Add the length of the processed signal to the elapsed time.
            t_start += self.anaSigList[i][0].signal.size/sr
        
        # Define objects that will be assigned by later stages of sorting.
        self.spikeLabels = zeros(self.spikeTimes.size, dtype = 'i')
        self.waveforms = None
        self.features = None
        
        self.refreshColors()

        self.used_methods['Detection'] = method_class
        self.used_params['Detection'] = kargs

    def computeDetectionEnhanced(self, method_class,
        consistent_across_segments=True, consistent_across_channels=False,
        correct_times=True, **kargs) :
        """Replacement for computeDetection (under development). See
        docstring for computeDetection for basic functionality.
        
        This method is designed to be a drop-in replacement for
        computeDetection. It should be backwards compatible.
        
        When used with a new detection :method_class:, such as
        EnhancedMedianThreshold, accepts three new optional arguments:
        consistent_across_segments : same threshold for all segments
        consistent_across_channels : same threshold for all channels
        correct_times : self.spikeTimes will be stored in correct time
            relative to AnalogSignal time, rather than the old method
            which used only elapsed time.
        
        Backwards Compatibility
        -----------------------
        The defaults will produce different behavior than the old 
        detection methods did. To recapitulate old behavior, set:
        consistent_across_segments = False
        consistent_across_channels = True
        correct_times = False
        
        Unless there is a reason to keep the old behavior with 
        correct_times == False, this will be removed soon. One possible
        reason to keep it is if the user wants to assume that segments
        are always contiguous and does not assign t_start. But in that case
        we should assign t_start for him.
        """
        assert 'Detection' in mode_steps[self.mode], 'Impossible in mode'+ self.mode
        assert self.anaSigFilteredList is not None, 'not yet filtered'
               
        # Store the provided parameters
        self.spikeSign = kargs['sign']
        self.left_sweep = kargs['left_sweep']
        self.right_sweep = kargs['right_sweep']
        
        # Check whether method_class support global processing
        m = method_class()
        global_processing = \
            any([p[0] is 'consistent_across_segments' for p in m.params])        
        
        # Get the spike times in one of two methods. If :method_class:
        # supports global processing, then it needs the entire list by
        # segment, and (optionally) the spike times are corrected.
        # Otherwise, :method_class: takes one segment at a time.
        if global_processing:
            # The method should accept these keywords
            kargs['consistent_across_segments'] = consistent_across_segments
            kargs['consistent_across_channels'] = consistent_across_channels
            
            # Get sampling rate
            sr = self.anaSigFilteredList[0][0].sampling_rate
            
            # TODO: error check consistent sampling rate and t_start here            
            
            # The first place to store results, a list of lists.
            m = method_class()
            self.spikePosistionList = m.compute(self.anaSigFilteredList, **kargs)
            
            # Store the threshold that the method used
            self.thresholdsBySegment = m.thresholdsBySegment
            
            # Determine when each segment started
            if correct_times:
                t_starts = [sig_list[0].t_start \
                    for sig_list in self.anaSigFilteredList]
            else:
                # Backwards compatibility: used elapsed time, which is
                # essentially assuming all signals are contiguous.
                t_starts = [len(sig_list[0].signal) / sr \
                    for sig_list in self.anaSigFilteredList]
                t_starts = concatenate([[0.], cumsum(t_starts)[:-1]])
            
            # Concatenate spike times corrected for segment start time
            self.spikeTimes = concatenate([spl / sr + t_start \
                for spl, t_start in zip(self.spikePosistionList, t_starts)])
            
            
            # Define objects that will be assigned by later stages of sorting.
            self.spikeLabels = zeros(self.spikeTimes.size, dtype = 'i')
            self.waveforms = None
            self.features = None
            
            self.refreshColors()

            # Log the parameters that were used
            self.used_methods['Detection'] = method_class
            self.used_params['Detection'] = kargs
            
        else:
            # Fall back on local detection code
            self.computeDetection(method_class, **kargs)


    
    def computeExtraction(self, method_class, **kargs) :
        """Extract waveforms using detected spike times.
        
        method_class : class that actually does extraction, such as
            extraction.WaveformExtractor.
            It will receive the following arguments for each segment:
                self.anaSigFilteredList[i] (from a single segment)
                self.spikePosistionList[i] (from a single segment)
                self.spikeSign, self.left_sweep, self.right_sweep
                and all other keyword arguments in `kargs`

        Usage: spikesorter.computeExtraction(OE.extraction.WaveformExtractor)

        The results are concatenated and stored in self.waveforms.
        """
        assert 'Extraction' in mode_steps[self.mode], 'Impossible in mode'+ self.mode
        assert self.spikePosistionList is not None, 'not yet detected'
        
        # Run extraction on each segment and concatenate the results
        self.waveforms = None
        wf_list = []
        for i in range( len(self.anaSigList) ):
            wf = method_class().compute(self.anaSigFilteredList[i], self.spikePosistionList[i],self.spikeSign, left_sweep = self.left_sweep , right_sweep = self.right_sweep, **kargs)
            wf_list.append(wf)

        self.waveforms = concatenate(wf_list)

        self.used_methods['Extraction'] = method_class
        self.used_params['Extraction'] = kargs


    def computeFeatures(self, method_class, **kargs) :
        """Compute features from detected spike waveforms.
        
        method_class : class that actually does the feature calculations,
            such as feature.PCA.
            It will receive the following arguments:
                self.waveforms (N_spikes, N_recordingpoints, len(waveform))
                self.sampling_rate
               any other keyword arguments you provide.
        
        Usage: spikesorter.computeFeatures(feature.PCA, output_dim=8)
        
        The results are stored in self.features, an array of shape
        (N_spikes, N_features).
        """
        assert 'Features' in mode_steps[self.mode], 'Impossible in mode'+ self.mode
        assert self.waveforms is not None, 'not yet extracted'
        
        self.features = method_class().compute( self.waveforms, self.sampling_rate, **kargs)

        self.used_methods['Features'] = method_class
        self.used_params['Features'] = kargs


    def computeClustering(self, method_class, **kargs) :
        """Cluster spikes based on their features.
        
        method_class : class that actually does the clustering, such as
            clustering.KMean
            It will receive the following arguments:
            self.features : ndarray of shape (N_spikes, N_features)
                containing calculated features.
            self.spikeTimes : ndarray of spike times in seconds, combined
                across all segments.
            and any other keyword arguments you specify.
        
        Usage: spikesorter.computeClustering(clustering.KMean, n=4)
        
        The results are stored in self.spikeLabels, an array that is the
        same shape as self.spikeTimes but contains an integer flag for
        the cluster id of each spike.
        
        The following variables are also created:
            self.names : dict, mapping cluster ids to cluster names
            self.sortingScores : dict, mapping cluster ids to sorting scores
        """
        assert 'Clustering' in mode_steps[self.mode], 'Impossible in mode'+ self.mode
        assert self.features is not None, 'features have not yet been calculated'
        
        self.spikeLabels = method_class().compute(self.features, 
            self.spikeTimes, **kargs)
        
        # Redraw the spikes with colors assigned from clusters
        self.refreshColors()

        self.used_methods['Clustering'] = method_class
        self.used_params['Clustering'] = kargs

        # Create dicts for cluster names and scores, mostly useful for GUI
        self.names = { -1 : 'Trash'}
        self.sortingScores = { -1 : ''}

    def subComputeCluster(self, labelToSubCluster, method_class, **kargs):
        ind, = where( self.spikeLabels ==labelToSubCluster )            
        m = method_class()
        new_sorted = m.compute( self.features[ind] , self.spikeTimes[ind] , **kargs )
        new_sorted += max(self.allLabels)+1
        self.spikeLabels[ind] = new_sorted.astype('i')
        for c in unique(new_sorted):
            if c in self.names: self.names.pop(c)
            if c in self.sortingScores: self.sortingScores.pop(c)
        self.refreshColors()
        
        
    def deleteOneNeuron(self, num):
        #FIXME if not features
        
        self.block = self.session.merge(self.block)
        ind = self.spikeLabels != num
        if self.mode =='from_full_band_signal' or self.mode =='from_filtered_signal':
            p = 0 # position in spikeLabels
            for i,seg in enumerate(self.block._segments) :
                pos = self.spikePosistionList[i]
                ind2 = ind[p:p+pos.size]
                self.spikePosistionList[i] = self.spikePosistionList[i][ind2]
                p += pos.size
        elif self.mode == 'from_detected_spike':
            self.spike_id_segments= self.spike_id_segments[ind]
        
        self.features= self.features[ind]
        self.waveforms= self.waveforms[ind]
        self.spikeTimes= self.spikeTimes[ind]
        self.spikeLabels= self.spikeLabels[ind]
        
        self.refreshColors()
        self.session.expunge_all()
    
    def regroupSmallUnits(self, size = 10):
        
        n = max(self.allLabels) +1
        for c in self.allLabels:
            ind = self.spikeLabels == c
            if sum(ind) <size:
                self.spikeLabels[ ind ] = n
        self.refreshColors()
        
    
    
    
    def save_to_db(self,    save_waveform = 'save filtered waveform', # 'do not save' ,  'save natural waveform'
                                        spiketrain_mode = 'standalone',   #'container'
                                        save_trash = False,
                                        create_empty = True,
                                    ):
        """Write sorted spikes to database.
                
        This method takes the results of spike sorting, which are stored
        as internal variables in this object, and creates Neuron and 
        SpikeTrain objects suitable for the database. One Neuron is created
        for each label in :allLabels:. One SpikeTrain is created for each
        Neuron and Segment in :block._segments:.
        
        The attribute :self.mode: affects how the data is stored. If it is
        'from_detected_spike' then the spike times are taken from
        :self.spikeTimes: (which is probably incorrect for non-contiguous
        Segment). Otherwise the spike times are taken from the :t(): method
        of the AnalogSignal from which they came.
        
        Parameters
        ----------
        save_waveform : a string taking one of the following values
            'save filtered waveform' : SpikeTrain will contain the waveform
                of each spike from the filtered signal which was used to
                find spikes in the first place.
            'save natural waveform' : If
                :self.mode: is 'from_filtered_signal', then the unfiltered
                signal is not available, and this parameter has no effect.
                If :self.mode: is 'from_full_band_signal', then this
                parameter means that SpikeTrain will contain the original,
                unfiltered waveform. This is actually implemented by
                re-running the last-used 'Extraction' method on the
                original signal using the detected spike times. These waveforms
                are then stored in SpikeTrain, though the 'waveforms'
                attribute of this object is unchanged.
            'do not save' : waveforms will not be saved to database
        
        spiketrain_mode : a string taking one of the following values
            'standalone' : waveforms and spike times are written to the
                'waveforms' and 'spike_times' attributes of SpikeTrain
                as arrays.
            'container' : the 'waveforms' and 'spike_times' attributes of
                SpikeTrain will be None. Instead, a Spike object is created
                for each spike and linked to SpikeTrain.
        
        save_trash : if True, the spikes with label -1 (Trash) will be
            written to the database. Otherwise they will not.
        
        create_empty : if True and no spikes were detected 
            (meaning :allLabels: has length 0)
            a special Neuron with name 'Empty' will be stored in the database.
            if False, nothing will be written to the database in this case.        
        """
        # Delete all SpikeTrain and Neuron objects associated with
        # :self.recordingPointList: in the database.
        id_neurons = [ ]
        for rp in self.recordingPointList:
            # Delete SpikeTrain from this RecordingPoint
            for sptr in self.session.query( SpikeTrain ).filter_by( id_recordingpoint = rp.id ).all():
                id_neurons.append( sptr.id_neuron )
                self.session.delete(sptr)
        for id_neuron in unique(id_neurons):
            # Delete all Neuron associated with those SpikeTrain
            if id_neuron is None : continue
            neu = self.session.query( Neuron ).filter_by(id = int(id_neuron) ).one( )
            self.session.delete(neu)
        self.session.commit()
        
        #  Update the stored handle to :block:
        self.block = self.session.merge(self.block)
        
        # If necessary, re-run the Extraction method on the unfiltered data
        # and save the results in a temporary variable :waveformsNatural:
        if self.mode=='from_full_band_signal' and save_waveform=='save natural waveform':
            # re-extract waveform on non filtered AnalogSignal
            m = self.used_methods['Extraction']()
            wfn_list = [ ]
            for i in range( len(self.anaSigList) ):
                wf = m.compute(self.anaSigList[i], self.spikePosistionList[i],
                    self.spikeSign, left_sweep = self.left_sweep , 
                    right_sweep = self.right_sweep ,
                    **self.used_params['Extraction'])
                wfn_list.append(wf)
            waveformsNatural = concatenate(wfn_list)

        # Get the labels of each spike. After detection, these are set to
        # zero. If no spikes have been detected, flag this case with a -2.
        alllabels = self.allLabels        
        if len(alllabels) == 0 and create_empty:
            alllabels = [ -2 ]
        
        # Save each label (neuron)
        for c in alllabels:
            # The trash is marked with label -1
            if c==-1 and not(save_trash) : continue
            
            # Name the unit with user-specified name or default
            if c in self.names and (self.names[c] != ''): name = self.names[c]
            elif c== -2: name = 'Empty'
            else: name='Neuron %d of recPoint %d' % (c, self.recordingPoint.channel)
            
            # Get sorting score of this neuron
            if c in self.sortingScores: sortingScore =self.sortingScores[c]
            else: sortingScore = None
            
            # Create a Neuron object and link it to the session
            neu = Neuron(  id_block = self.block.id,
                                    name = name,
                                    sortingScore = sortingScore,
                                    channel = self.recordingPoint.channel
                                    )
            self.session.add( neu )
            self.session.commit()

            # Save SpikeTrain, one for each pair of (Neuron, Segment)
            p = 0 # position in waveform.shape[0] and spikeLabels
            for i,seg in enumerate(self.block._segments) :
                # Get spike times and waveforms from this segment and put
                # in :_spike_times: and :_waveforms:
                if self.mode == 'from_full_band_signal' or self.mode =='from_filtered_signal':
                    # Get an array of spike times in this segment
                    pos = self.spikePosistionList[i]
                    
                    # Index into the labels of the spikes and find label :c:
                    labels2 = self.spikeLabels[p:p+pos.size]
                    ind, = where(labels2 == c)
                    
                    # Find the spike times by indexing into the time array
                    # of the first AnalogSignal from this segment
                    _spike_times = self.anaSigList[i][0].t()[pos[ind]]
                    
                    # Get waveforms of these spikes, filtered or natural
                    _waveforms = None
                    if save_waveform=='save filtered waveform':
                        if ind.size != 0:
                            _waveforms = self.waveforms[p+ind,:,:]
                    elif save_waveform =='do not save':
                        _waveforms = None
                    elif save_waveform =='save natural waveform':
                        if ind.size != 0:
                            if self.mode =='from_full_band_signal':
                                _waveforms = waveformsNatural[p+ind,:,:]
                            else:
                                _waveforms = self.waveforms[p+ind,:,:]
                    
                    # Increase :p:, the index into all spike times from
                    # all segments, by the number of spikes in this Segment.
                    p += pos.size
                    
                    # Find start and stop times of this Segment
                    t_start = float(self.anaSigList[i][0].t_start)
                    t_stop = float(self.anaSigList[i][0].t()[-1])
                    
                elif self.mode == 'from_detected_spike':
                    # TODO
                    # In this case we use :spikeLabels: and :spike_id_segments:
                    # which are formatted "one entry per spike" instead
                    # of iterating through the list of segments.
                    # Find indices of spikes with label :c: in Segment :seg:
                    ind, = where( (self.spikeLabels == c) & ( seg.id == self.spike_id_segments) )
                    
                    # Take the spike times from :spikeTimes: which does
                    # not account for non-contiguous Segment.
                    _spike_times = self.spikeTimes[ind]

                    if save_waveform =='save filtered waveform':
                        _waveforms = self.waveforms[ind,:,:]
                    elif save_waveform =='do not save':
                        _waveforms = None
                    elif save_waveform =='save natural waveform':
                        _waveforms = waveformsNatural[ind,:,:]
                    
                    t_start = 0.
                    t_stop = None
                    
                
                # Only store the results if spiketrain_mode is 'standalone'
                if spiketrain_mode == 'standalone':
                    spike_times = _spike_times
                    waveforms = _waveforms
                elif spiketrain_mode == 'container':
                    spike_times = None
                    waveforms = None
                
                if self.left_sweep is not None:
                    self.left_sweep = float(self.left_sweep)
                if self.right_sweep is not None:
                    self.right_sweep = float(self.right_sweep)
                
                # Create a new SpikeTrain linked to the Neuron, the
                # RecordingPoint, and the Segment with the spike times and
                # waveforms from label :c:
                sptr = SpikeTrain( id_neuron = neu.id,
                                            id_recordingpoint = self.recordingPoint.id,
                                            id_segment = seg.id, 
                                            name = name,
                                            t_start = t_start,
                                            t_stop = t_stop,
                                            sampling_rate =  float(self.sampling_rate),
                                            left_sweep = self.left_sweep,
                                            right_sweep = self.right_sweep,
                                            channel = self.recordingPoint.channel,
                                            _spike_times = spike_times,
                                            _waveforms = waveforms,
                                            )
                
                # Store in session
                self.session.add( sptr )
                # More efficient to commit fewer times, after each neuron
                #self.session.commit()
                
                # Special container mode
                if spiketrain_mode== 'container':
                    for j in range(_spike_times.size):
                        if _waveforms is None:
                            waveform = None
                        else:
                            waveform = _waveforms[j]
                        spike = Spike( id_spiketrain = sptr.id,
                                                time = float(_spike_times[j]),
                                                waveform = waveform,
                                                sampling_rate =  float(self.sampling_rate),
                                            )
                        self.session.add( spike )
                    self.session.commit()
            
            # More efficient to commit fewer times, after each neuron
            self.session.commit()
        
        self.session.expunge_all()

    
    
