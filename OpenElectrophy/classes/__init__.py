
# neo classes
from block import Block
from segment import Segment

from analogsignal import AnalogSignal
from recordingpoint import RecordingPoint

from neuron import Neuron
from spiketrain import SpikeTrain
from spike import Spike

from epoch import Epoch
from event import Event


# specail classes
from oscillation import Oscillation
from imageserie import ImageSerie
from imagemask import ImageMask
from respirationsignal import RespirationSignal
from licktrain import LickTrain



cl = [Block, Segment, AnalogSignal , RecordingPoint , Neuron , SpikeTrain , Spike , Epoch , Event , 
                Oscillation , ImageSerie , ImageMask, RespirationSignal , LickTrain]

allclasses = { }
for c in cl :
    allclasses[c.tablename] = c

#~ __all__ = [ ]
#~ __all__ += cl
