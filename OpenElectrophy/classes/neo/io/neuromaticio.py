# -*- coding: utf-8 -*-
"""

Class for fake reading/writing data from WinWCP, a software tool written by
John Dempster.

WinWCP is free:
http://spider.science.strath.ac.uk/sipbs/software.htm


Supported : Read

@author : sgarcia

"""


from baseio import BaseIO
#from neo.core import *
from ..core import *


import struct
from numpy import *
from igor import binarywave,igorpy
import re
class NeuromaticIO(BaseIO):
    """
    Class for reading/writing from a WinWCP file.
    
    **Example**
        #read a file
        io = WinWcpIO(filename = 'myfile.wcp')
        blck = io.read() # read the entire file    
    """
    
    is_readable        = True
    is_writable        = False

    supported_objects  = [Block, Segment , AnalogSignal]
    readable_objects   = [Block, Segment]
    writeable_objects  = []  

    has_header         = False
    is_streameable     = False
    
    read_params        = {  Block : [    
                                        ('Filter' , { 'Filter' : 'RecordA' } )
                                    ]
                         }
    
    write_params       = None

    name               = 'Neuromatic'
    extensions          = [ 'pxp' ]
    
    
    mode = 'file'
    
    
    def __init__(self , filename = None) :
        """
        This class read a Neuromatic pxp file.
        
        **Arguments**
            filename : the filename to read
        
        """
        BaseIO.__init__(self)
        self.filename = filename
        
    def splitgroups(self,s):
        groupre = re.compile(r'(\D*[^\d-])|(-?\d+)')
        return tuple(
            m.group(1) or int(m.group(2))
            for m in groupre.finditer(s)
        )  
    
    def read_block(self,Filter= 'RecordA'):
          
        """
        Return a Block.
        
        **Arguments**
            no arguments
        """

        blck=Block()
        
        Array={} #each key corresponds to a wave
        Var={} #each key corresponds to a variable

        b=igorpy.load(self.filename)
        for i in b:
            if isinstance(i, igorpy.Wave):
                Array[str(i.name)]=i.data
            elif isinstance(i, igorpy.Variables):
                Var=i.uservar    

        if Array == None and Var == None:
            return
        Filter=Filter
        templist1=[]
        templist2=[]
        tempkeys=[]
        for i in Array:
            tempkeys.append(i)
            
        tempkeys=sorted(tempkeys, key=self.splitgroups)

        #for i in Var:
        #    exec("Analysis."+i+"= Var[i]")

        Waves=[]
        # loop for record number
        counter=0
        for i in tempkeys:
            if Filter in i: 
                counter+=1
        
        for i in tempkeys:
            if Filter in i:
                print i

                data = Array[i]
                
                alph=["A","B","C","D","E","F","G","H","I","J"]
                seg = Segment()
                blck._segments.append(seg)            
                
                #for c in range(counter):
                anaSig = AnalogSignal()
                seg._analogsignals.append(anaSig)
                #ADCMAX = header['ADCMAX']
                #VMax = analysisHeader['VMax'][c]                  
                #YG = float(header['YG%d'%c].replace(',','.'))

                anaSig.signal = data #[alph[c],data[:,header['YO%d'%c]].astype('f4')*Var['VMax']/Var['ADCMAX']/YG]
                #Waves.append(signal)
                anaSig.sampling_rate = 1000./Var["SampleInterval"]
                anaSig.t_start = 0.
                anaSig.name = Filter
                #anaSig.unit = header['YU%d'%c]
    
                # TODO : Hack because letter are easier to read. Valid up to 10 channel
                #Var['channel'] = alph[c]
                #anaSig.channel = c
                

        
        return blck                

    def read(self , **kargs):
        """
        Read a fake file.
        Return a neo.Block
        See read_block for detail.
        """
        return self.read_block( **kargs)
    
    




AnalysisDescription = [
('RecordStatus','8s'),
('RecordType','4s'),
('GroupNumber','f'),
('TimeRecorded','f'),
('SamplingInterval','f'),
('VMax','8f'),
]

class HeaderReader():
    def __init__(self,fid ,description ):
        self.fid = fid
        self.description = description
    def read_f(self, offset =0):
        self.fid.seek(offset)
        d = { }
        for key, format in self.description :
            val = struct.unpack(format , self.fid.read(struct.calcsize(format)))
            if len(val) == 1:
                val = val[0]
            else :
                val = list(val)
            d[key] = val
        return d



    
    def splitgroups(self,s):
        groupre = re.compile(r'(\D*[^\d-])|(-?\d+)')
        return tuple(
            m.group(1) or int(m.group(2))
            for m in groupre.finditer(s)
        )    
            
            
  

































