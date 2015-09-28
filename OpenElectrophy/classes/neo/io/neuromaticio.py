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


from numpy import *
try:
    from igor import binarywave,igorpy
except:
    print 'Error while loading a librairy. Did you register your Python PATH? '
import re,string,datetime,struct
 

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

        
    def __init__(self , filename = None, **kargs ) :
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
        #Valid up to 26 channels
        alph=list(string.ascii_uppercase)
                
        
        
        Array={} #each key corresponds to a wave
        Var={} #each key corresponds to a variable

        b=igorpy.load(self.filename)
        
        #Igor name channels RecordA, RecordB etc...
        #the first 7 characters are thus specific a a given channel
        ChannelNames=[]

        
        for i in b:
            if isinstance(i, igorpy.Wave):
                if 'Record' in str(i.name):
                    ChannelNames.append(str(i.name)[0:7])
                    Array[str(i.name)]=i.data
            elif isinstance(i, igorpy.Variables):
                Var=i.uservar    
        
        ChannelNames=list(set(ChannelNames))
        
       
        if Array == None and Var == None:
            return
            
        Filter=Filter
        templist1=[]
        templist2=[]
        AllWaveNames=[]
        for i in Array:
            AllWaveNames.append(i)
        
        
        AllWaveNames=sorted(AllWaveNames, key=self.splitgroups)
        
        #for i in Var:
        #    exec("Analysis."+i+"= Var[i]")

        Waves=[]
        # loop for record number
        counter=0
        for i in AllWaveNames:
            if Filter in i: 
                counter+=1
        
        #Identify date of creation from filename
        #TODO, use variable instead
        filename=self.filename.split('/')[-1]
        blck=Block()
        convertiontable=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        Day=int(filename[2:4])
        Month=int(convertiontable.index(filename[4:7]))
        Year=int(filename[7:11])
        date = datetime.date(Year,Month,Day)

        blck.datetime=date

        for i in AllWaveNames:
            seg = Segment()
            for k,j in enumerate(ChannelNames):
                seg.name=j
                if j in i:
                    anaSig = AnalogSignal()
                    #ADCMAX = header['ADCMAX']
                    #VMax = analysisHeader['VMax'][c]                  
                    #YG = float(header['YG%d'%c].replace(',','.'))
                    anaSig.signal = Array[i] #[alph[c],data[:,header['YO%d'%c]].astype('f4')*Var['VMax']/Var['ADCMAX']/YG]
                    #Waves.append(signal)
                    anaSig.sampling_rate = 1000./Var["SampleInterval"]
                    anaSig.t_start = 0.
                    anaSig.name = j
                    anaSig.channel = k
                    #anaSig.unit = header['YU%d'%c]
                    seg._analogsignals.append(anaSig)
            blck._segments.append(seg)
                

        return blck                

    def read(self , **kargs):
        """
        Read a fake file.
        Return a neo.Block
        See read_block for detail.
        """
        print 'in'
        return self.read_block( **kargs)
    

#AnalysisDescription = [
#('RecordStatus','8s'),
#('RecordType','4s'),
#('GroupNumber','f'),
#('TimeRecorded','f'),
#('SamplingInterval','f'),
#('VMax','8f'),
#]
#
#
#  

































