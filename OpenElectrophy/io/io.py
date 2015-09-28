# -*- coding: utf-8 -*- 
"""
Short module to wrap neo.io to OpenElectrophy.io

All IO are the same but they return OpenElecytrophy objects instead of neo objects.


"""

__all__ = [ 'all_format' , 'transform_all_spiketrain_mode']

from ..classes.neo import core as ncore
from  ..classes.neo import io as nio
from ..classes import allclasses, Block,Segment,RecordingPoint,Event,Epoch,Neuron,SpikeTrain,AnalogSignal, Oscillation
#~ from ..classes import *
from ..sqlmapper import NumpyField

import numpy

from sqlalchemy.orm.collections import InstrumentedList


def hierachicalNeoToOe(neoinstance):
    """
    transforme a neo instance to a OE instance and its children recursively
    """
    if type(neoinstance) in ncore.neotypes:
        
        if hasattr(neoinstance, 'oeinstance'):
            return neoinstance.oeinstance
        

        # create oe instance
        name = neoinstance.__class__.__name__.lower()
        oeinstance = allclasses[name]()
        #~ print name
        
        
        # copy neo attr to oe
        d = { }
        d.update( neoinstance.__dict__)
        for k in d.keys():
            for child in oeinstance.children :
                if '_'+child+'s' == k :
                    del d['_'+child+'s']
            if k in oeinstance.dict_field_types.keys():
                if oeinstance.dict_field_types[k] == numpy.ndarray:
                    del d[k]
                    setattr(oeinstance, k, getattr(neoinstance , k))
        oeinstance.__dict__.update(d)
        
        # copy 
        
        # do the same for children
        for child in oeinstance.children :
            #~ print ' ', child
            #~ print oeinstance
            #~ print oeinstance.tablename, ' has child', child
            if hasattr(neoinstance, '_'+child+'s' ):
                childinstances = getattr(neoinstance, '_'+child+'s' )
                #~ print 'childinstances', childinstances
                if childinstances is not None:
                    for i in range(len(childinstances)):
                        #~ childinstances[i] = hierachicalNeoToOe(childinstances[i])
                        #~ getattr(neoinstance, '_'+child+'s' )[i] = hierachicalNeoToOe(childinstances[i])
                        #~ print 'i', i, childinstances[i]
                        #~ hierachicalNeoToOe(childinstances[i])
                        getattr(oeinstance, '_'+child+'s').append(hierachicalNeoToOe(childinstances[i]))
            
    neoinstance.oeinstance = oeinstance
    
    return oeinstance
    



def __classinit__(self, *args, **kargs):
    self.neoinstance = self.neoclass(*args , **kargs)
    self.neoclass.__init__(self, *args , **kargs)

def read_block(self, *args, **kargs):
    #~ print 'inside OE read_bloc',self, self.neoinstance
    
    block = hierachicalNeoToOe( self.neoinstance.read_block(*args, **kargs) )
    
    # create a block with anaSig and Spiketrain with recordinpoint
    block2=Block()
    for fieldname, _ in Block.fields:
        if hasattr(block , fieldname):
            block2[fieldname] = block[fieldname]
    
    for rec in block._recordingpoints:
        block2._recordingpoints.append(rec)
    
    for seg in block._segments:
        block2.add_one_segment(seg)
    
    for neu in block._neurons:
        block2._neurons.append(neu)
    
    #~ block.name = 'old!!!'
    return block2
    

def read_segment(self,*args, **kargs):
    #~ print 'inside OE read_segment',self, self.neoinstance
    seg = hierachicalNeoToOe( self.neoinstance.read_segment(*args, **kargs) )
    return seg


#~ def write_block(self,*args, **kargs):
    #~ self.neoinstance.write_block(*args, **kargs) 


#~ def write_segment(self,*args, **kargs):
    #~ self.neoinstance.write_segmen(*args, **kargs) 


# wrapp all neo classes to OE classes
# with same names 
# overwritte read_block and read_segment


def transform_all_spiketrain_mode(ob , newmode):
    """
    tranform spiketrain mode ('container' or 'standalone')  for all spiketrain in  a segment or a block
    """
    
    if type(ob) == Block:
        for seg in ob._segments:
            for sptr in seg._spiketrains:
                sptr.change_mode( newmode )
    
    if type(ob) == Segment:
            for sptr in ob._spiketrains:
                sptr.change_mode( newmode )



class AnalogSignalList:
    pass

class SpikeTrainList:
    pass

translate = {
                    ncore.Block : Block,
                    ncore.Segment : Segment,
                    ncore.RecordingPoint : RecordingPoint,
                    ncore.Event : Event,
                    ncore.Epoch : Epoch,
                    ncore.Neuron : Neuron,
                    ncore.SpikeTrain : SpikeTrain,
                    ncore.AnalogSignal : AnalogSignal,
                    ncore.SpikeTrainList : SpikeTrainList,
                    ncore.AnalogSignalList : SpikeTrainList,
                    }


# Wrap all neo.io to OPenElectrophy.io
all_format = [ ]
for name, d in  nio.all_format :
    classname = d['class'].__name__
    newclass = type(classname,(d['class'],),{})
    newclass.neoclass = d['class']
    
    newclass.supported_objects = [ translate[o] for o in d['class'].supported_objects ]
    newclass.readable_objects = [ translate[o] for o in d['class'].readable_objects ]
    newclass.writeable_objects = [ translate[o] for o in d['class'].writeable_objects ]
    
    if d['class'].read_params is None:
        newclass.read_params = None
    else:
        newclass.read_params = { }
        for k,v in d['class'].read_params.iteritems():
            newclass.read_params[translate[k]] = v
    
    if d['class'].write_params is None:
        newclass.write_params = None
    else:
        newclass.write_params = { }
        for k,v in d['class'].write_params.iteritems():
            newclass.write_params[translate[k]] = v
    
    
    
    
    newclass.__init__ = __classinit__
    newclass.read_block = read_block
    newclass.read_segment = read_segment
    #~ newclass.write_block = write_block
    #~ newclass.write_segment = write_segment
    
    globals()[classname]= newclass
    __all__+=[classname]
    d['class'] = newclass
    all_format += [ [name, d] ]

