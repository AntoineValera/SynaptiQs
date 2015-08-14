# -*- coding: utf-8 -*-


import neo.core
from sqlalchemy import Column, Integer, String, Float, Text, Unicode, DateTime
import numpy

from base import OEBase
from recordingpoint import RecordingPoint


# for defitions list
__doc__ = neo.core.Block.definition


class Block(neo.core.Block , OEBase):
    
    __doc__ = neo.core.Block.__doc__ + \
    """This OpenElectrophy object inherits from `neo.core.Block`.
    
    Usage
    -----
    To create a new block and add some segments to it, you
    must first have an open connection to the database, using
    `open_db`.
    
    # Initialize a Block and add a Segment
    block = Block(name='Data')
    seg = Segment(name='Trial 1')
    block._segments.append(seg)
    block.save()
    
    # Retrieve the segment
    seg = block.get_segments()[0]
    print seg.name
    
    See `Segment` for information on adding neural data to it.
    """
    
    
    parents = [ ]
    children = [ 'segment', 'recordingpoint', 'neuron'  , 'imagemask']
    fields = [  ['name' , Text],
                ['datetime' , DateTime],
                ['info' , Text],
                ['fileOrigin' , Text]
                ]
    tablename = 'block'
    def __init__(self, *args , **kargs):
        """Initialize a new Block.
        
        In addition to the basic neo Block initialization, (see
        OpenElectrophy.neo.core.Block), the following fields in Block
        can be defined with sqlalchemy values:
            name : Text, name of the block
            info : Text, info about the block
            fileOrigin : Text, origin of the data
            datetime : DateTime, beginning of the data block
        """
        neo.core.Block.__init__(self, *args, **kargs)
        OEBase.__init__(self, *args, **kargs)
    
    
    plotAptitudes = [ ]
    
    def add_one_segment(self, seg):
        """
        Add a segment in this block and verify recording alignment for analogsignals an spiketrains
        """
        
        self._segments.append(seg)
        
        recPoints = { }
        
        # dict
        for rec in self._recordingpoints:
            recPoints[rec.channel] = rec
            
        # analogsignals
        for ana in seg._analogsignals:
            channel = 0
            if hasattr(ana, 'num') :
                if ana.num is not None:
                    channel = ana.num
            if hasattr(ana, 'channel') :
                if ana.channel is not None:
                    channel = ana.channel
            if hasattr(ana, 'channelNum') :
                if ana.channelNum is not None:
                    channel = ana.channelNum
                    
            #~ print 'channel', channel, type(channel)
            
            if channel not in recPoints.keys():
                recPoints[channel] = RecordingPoint( name = 'Channel %d' %channel,
                                                                            group = None,
                                                                            channel = channel,
                                                                            trodness = 1,
                                                                            )
                self._recordingpoints.append( recPoints[channel] )
            recPoints[channel]._analogsignals.append( ana )
        
        # spiketrains
        for sptr in seg._spiketrains :
            channel = 0
            if hasattr(sptr, 'num') :
                if sptr.num is not None:
                    channel = sptr.num
            if hasattr(sptr, 'channel') :
                if sptr.channel is not None:
                    channel = sptr.channel
            if hasattr(sptr, 'channelNum') :
                if sptr.channelNum is not None:
                    channel = sptr.channelNum
            
            if channel not in recPoints.keys():
                recPoints[channel] = RecordingPoint( name = 'Channel %d' %channel,
                                                                            group = None,
                                                                            channel = channel,
                                                                            trodness = 1,
                                                                            )
                self._recordingpoints.append( recPoints[channel] )
            recPoints[channel]._spiketrains.append( sptr )
    
    def fix_recordingpoints(self):
        """
        When SpikeTrain or AnalogSIgnal are added to a segment and a block relative recordingpoint are
        not necessary valid. This function do this.
        
        It look for all SpikeTrain and AnalogSignal inside a block and group then in the good RecordingPoint according to there
        channel.
        
        Rules:
          * if recordingpoint do not exits it will be created
          * if 2 recordingpoints have the same *channel* one is removed.
        
        """
        
        recPoints = { }
        
        # dict
        for rec in self._recordingpoints:
            if rec.channel not in recPoints:
                recPoints[rec.channel] = rec
        
        for seg in self._segments:
            
            for ana in seg._analogsignals:
                if ana.channel is None: continue
                
                if ana.channel not in recPoints.keys():
                    rp = RecordingPoint( name = 'Channel %d' %ana.channel,
                                                                            group = None,
                                                                            channel = ana.channel,
                                                                            )
                    self._recordingpoints.append(rp)
                    recPoints[ana.channel] = rp
                
                if ana not in recPoints[ana.channel]._analogsignals:
                    recPoints[ana.channel]._analogsignals.append(ana)
            
            for sptr in seg._spiketrains:
                if sptr.channel is None: continue
                
                if sptr.channel not in recPoints.keys():
                    rp = RecordingPoint( name = 'Channel %d' %sptr.channel,
                                                                            group = None,
                                                                            channel = sptr.channel,
                                                                            )
                    self._recordingpoints.append(rp)
                    recPoints[sptr.channel] = rp
                
                if sptr not in recPoints[sptr.channel]._spiketrains:
                    recPoints[sptr.channel]._spiketrains.append(sptr)
        
