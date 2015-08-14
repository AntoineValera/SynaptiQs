# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:07:35 2013

@author: Antoine Valera
"""

import sys, os
from PyQt4 import QtGui, QtCore
from matplotlib import numpy
from sys import maxint
import re

class MyListWidget(QtGui.QListWidget,object):
    dropped = QtCore.pyqtSignal(list)

    def __init__(self, type, parent=None):
        super(MyListWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()

        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            filePaths = [
                str(url.toLocalFile())
                for url in event.mimeData().urls()
            ]

            self.dropped.emit(filePaths)

        else:
            event.ignore()
            


class MyWindow(QtGui.QWidget,object):
    
    
    def __init__(self, parent=None):
        self.__name__="Import"

        super(MyWindow, self).__init__(parent)

        self.listWidgetFiles = MyListWidget(self)
        self.listWidgetFiles.dropped.connect(self.on_listWidgetFiles_dropped)
        self.clear = QtGui.QPushButton()
        self.clear.setText('Clear')
        QtCore.QObject.connect(self.clear, QtCore.SIGNAL("clicked()"),self.ClearLocal)
        
        
        self.layoutVertical = QtGui.QVBoxLayout(self)
        self.layoutVertical.addWidget(self.listWidgetFiles)
        self.layoutVertical.addWidget(self.clear)

        self.setMinimumSize(300,175)


    def Rename(Prefix):
        Newlist=[]
        for i in range(int(Infos.YList.count())):
            if Prefix in Infos.YList.item(i).text():
                name=str(Infos.YList.item(i).text())
                shortname=name[name.index('dA')+2:]
                shortname=shortname.zfill(4)
                newname="Analysis."+Prefix+shortname
                Infos.YList.item(i).setText(newname)
    			

    def read_block(self,filename):
        """
        Return a Block.
        
        **Arguments**
            no arguments
        """
        from OpenElectrophy.classes.neo.io.winwcpio import HeaderReader
        AnalysisDescription = [
        ('RecordStatus','8s'),
        ('RecordType','4s'),
        ('GroupNumber','f'),
        ('TimeRecorded','f'),
        ('SamplingInterval','f'),
        ('VMax','8f'),
        ]
        fid = open(filename , 'rb')
        
        headertext = fid.read(1024)
        header = {}
        for line in headertext.split('\r\n'):
            if '=' not in line : continue
            #print '#' , line , '#'
            key,val = line.split('=')
            if key in ['NC', 'NR','NBH','NBA','NBD','ADCMAX','NP','NZ', ] :
                val = int(val)
            if key in ['AD', 'DT', ] :
                val = val.replace(',','.')
                val = float(val)
            header[key] = val
        
        print header

        Waves=[]
        Var={}
        SECTORSIZE = 512
        # loop for record number
        for i in range(header['NR']):
            #print 'record ',i
            offset = 1024 + i*(SECTORSIZE*header['NBD']+1024)
            
            # read analysis zone
            analysisHeader = HeaderReader(fid , AnalysisDescription ).read_f(offset = offset)
            #print analysisHeader
            
            # read data
            NP = (SECTORSIZE*header['NBD'])/2
            NP = NP - NP%header['NC']
            NP = NP/header['NC']
            data = numpy.core.memmap(filename , numpy.dtype('i2')  , 'r', 
                          #shape = (header['NC'], header['NP']) ,
                          shape = (NP,header['NC'], ) ,
                          offset = offset+header['NBA']*SECTORSIZE)
            
            alph=["A","B","C","D","E","F","G","H","I","J"]
            for c in range(header['NC']):
                Var['YG'] = float(header['YG%d'%c].replace(',','.'))
                Var['ADCMAX'] = header['ADCMAX']
                Var['VMax'] = analysisHeader['VMax'][c]
                signal = [alph[c],data[:,header['YO%d'%c]].astype('f4')*Var['VMax']/Var['ADCMAX']/Var['YG']]
                Waves.append(signal)
                Var['sampling_rate'] = 1./analysisHeader['SamplingInterval']
                Var['t_start'] = analysisHeader['TimeRecorded']
                Var['name'] = header['YN%d'%c]
                Var['unit'] = header['YU%d'%c]
                # TODO : Hack because letter are easier to read. Valid up to 10 channel
                Var['channel'] = alph[c]

        fid.close()
        return Waves,Var











    def IgorLoad(self,Source):
        from igor import binarywave,igorpy
        Waves={}
        Variables={}
        
        if Source[-3:] == 'ibw':
            Waves[binarywave.load(Source)['wave']['wave_header']['bname']]=binarywave.load(Source)['wave']['wData']
            Variables['SampleInterval']=1
        elif Source[-3:] == 'pxp':
            #tree=igorpy.load(Source).format()
            #print tree
            #print '#############'
            b=igorpy.load(Source)
            
            for i in b:
                if isinstance(i, igorpy.Wave):
                    Waves[str(i.name)]=i.data
                elif isinstance(i, igorpy.Variables):
                    Variables=i.uservar    
        elif Source[-3:] == 'txt':
            b=numpy.loadtxt(Source)
            Waves[Source.split("/")[-1].replace('.txt','').replace('.','_')]=b
            Variables=None 
        elif Source[-3:] == 'csv':
            b=numpy.loadtxt(Source)
            Waves[Source.split("/")[-1].replace('.txt','').replace('.','_')]=b
            Variables=None 
        elif Source[-3:] == 'wcp':
            print "not supported yet, but you can import an igor file" 
            b,c=self.read_block(Source)
            for i,j in enumerate(b):
                Waves[str(j[0])+str(i)]=numpy.array(j[1])
            for i in c:
                Variables[i]=c[i]  
        try:     
            return Waves,Variables
        except UnboundLocalError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Filtype not Supported</b>
            <p>Only txt, ibw and pxp files are supported
            """)
            msgBox.exec_()
            return None, None
            

    
    def splitgroups(self,s):
        groupre = re.compile(r'(\D*[^\d-])|(-?\d+)')
        return tuple(
            m.group(1) or int(m.group(2))
            for m in groupre.finditer(s)
        )    
            
            
    @QtCore.pyqtSlot(list)

   
    def on_listWidgetFiles_dropped(self, filePaths):
        self.FileType=None
        #TODO : Add wcp and igor SweepA
        #       Solve missing sweep bug. (counter will not increment)
        for filePath in filePaths:
            if os.path.exists(filePath):
                Array,Var=self.IgorLoad(filePath)
                if Array == None and Var == None:
                    return
                #if isinstance(Array, dict):
                Filter,ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'To filter names, add text here', 
                "",QtGui.QLineEdit.Normal,"RecordA")
                Filter=str(Filter) 
                templist1=[]
                templist2=[]
                tempkeys=[]
                for i in Array:
                    tempkeys.append(i)
                #tempkeys=self.SortComplicated(tempkeys)
                tempkeys=sorted(tempkeys, key=self.splitgroups)
                
                counter=0
                for i in tempkeys:
                    
                    if Filter in i:
                        i2=i
                        Main.LoadedList.append(i)
                        
                        if "RecordA" in i:
                            shortname=i[i.index('dA')+2:]
                            shortname=shortname.zfill(4)
                            i2="RecordA"+shortname
                            self.FileType="Neuromatic"
                            
                        if "RecordB" in i:
                            shortname=i[i.index('dB')+2:]
                            shortname=shortname.zfill(4)
                            i2="RecordA"+shortname    
                            self.FileType="Neuromatic"

                        if "sweepA" in i:
                            shortname=i[i.index('pA')+2:]
                            shortname=shortname.zfill(4)
                            self.FileType="Synaptics"
                            i2="sweepA"+shortname   

                        if "sweepB" in i:
                            shortname=i[i.index('pB')+2:]
                            shortname=shortname.zfill(4)
                            i2="sweepB"+shortname   
                            self.FileType="Synaptics"

                        if Filter == "A":
                            shortname=i[i.index('A')+1:]
                            shortname=shortname.zfill(4)
                            i2="A"+shortname
                            self.FileType="WinWCP"                            
                        if Filter == "B":
                            shortname=i[i.index('B')+1:]
                            shortname=shortname.zfill(4)
                            i2="B"+shortname
                            self.FileType="WinWCP"
                            
                        templist1.append(i)    
                        templist2.append(i2)
                        counter+=1    
                        exec("Analysis."+i2+"= Array[i]")
                        Navigate.ArrayList.append(eval("Analysis."+i2))
                
                
                
                if Var != None:
                    for i in Var:
                        exec("Analysis."+i+"= Var[i]")
                        Navigate.VarList[i]=eval("Analysis."+i)                      
                #else:
                   # exec("Analysis.Data = Array")
                Main.AnalysisWidget.setEnabled(True)
                Main.NavigationWidget.setEnabled(True)
                Main.MappingWidget.setEnabled(True)
                
                self.Update_Navigate()
                Requete.Add_Dictionnary_Arrays()
                Infos.Actualize()

                #QtGui.QListWidgetItem(filePath+" added as self."+filePath.split("/")[-1][:-4], self.listWidgetFiles)
                QtGui.QListWidgetItem(filePath+" opened", self.listWidgetFiles)
                 
                for i in range(len(templist1)):
                    QtGui.QListWidgetItem("         Igor Wave "+templist1[i]+" loaded as Analysis."+templist2[i], self.listWidgetFiles)

    def ClearLocal(self):
        for i in Main.LoadedList:
            try:
                exec("del Analysis."+i)
            except AttributeError:
                pass
        self.listWidgetFiles.clear()
        Infos.Actualize()
        self.Update_Navigate()
        del Navigate.ArrayList[0]
        del Requete.Current_Signal
        del Requete.timescale
        Requete.Current_Sweep_Number=0
        Requete.Block_ids=[None]
        Requete.Block_date=[None]
        Requete.Segment_ids=[None]
        Requete.Analogsignal_ids=[None]
        Requete.Analogsignal_name=[None]
        Requete.tag={}
        Requete.tag["Selection"]=[None]
        Requete.Analogsignal_channel=[None]
        Requete.Analogsignal_sampling_rate=[None]
        Requete.Block_fileOrigin=[None]
        Requete.Block_Info=[None]
        Requete.Analogsignal_signal_shape=[None]
        Requete.BypassedSamplingRate=[None]
        Requete.Shortest_Sweep_Length=1#Navigate.VarList["SamplesPerWave"]*Navigate.VarList["SampleInterval"]
        Main.slider.setRange(0, 0) #definit le range du slider sweepnb
        Requete.Spiketrain_ids=[None]
        Requete.Spiketrain_neuron_name=[None]
        Requete.Spiketrain_t_start=[None]
        Requete.Spiketrain_Neuid=[None]
        Main.To.setText('0')
        Main.LoadedList=[]
        try:
            del Navigate.VarList["SampleInterval"]
        except KeyError:
            pass
        try:
            del Navigate.VarList["sampling_rate"]
        except KeyError:
            pass    
        try:
            del Navigate.VarList["DT"]
        except KeyError:
            pass             
        Navigate.ArrayList=[]
        Main.MainFigure.canvas.Compute_Initial_Figure()
        Navigate.Check_From_To()
                
    def Update_Navigate(self):
        #Resetting Sequence
        try:
            RecordA0=Navigate.ArrayList[0]
        except IndexError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>No Data</b>
            <p>No data match your filter paramterers
            Caution, Filtering is case-sensitive
            """)
            msgBox.exec_()            
        Requete.url=None
        Requete.Current_Signal=RecordA0
        
        #if Navigate.VarList.has_key("sampling_rate") == True:
        #    Navigate.VarList["sampling_rate"]=Navigate.VarList["sampling_rate"]*1000.
        #    Navigate.VarList["SampleInterval"]=Navigate.VarList["sampling_rate"]
            
        if self.FileType == "Neuromatic":#Navigate.VarList.has_key("SampleInterval") == True:
            Requete.timescale=(Navigate.VarList["SampleInterval"])*numpy.array(range(len(RecordA0)))
            Requete.Analogsignal_sampling_rate=list([1000./Navigate.VarList["SampleInterval"]]*len(Navigate.ArrayList))
        elif self.FileType=="Synaptics":#Navigate.VarList.has_key("sampling_rate") == True:
            Requete.timescale=(1./Navigate.VarList["sampling_rate"])*numpy.array(range(len(RecordA0)))
            Requete.Analogsignal_sampling_rate=list([1000.*Navigate.VarList["sampling_rate"]]*len(Navigate.ArrayList))
        elif self.FileType=="WinWCP":#Navigate.VarList.has_key("sampling_rate") == True:
            Requete.timescale=(1000./Navigate.VarList["sampling_rate"])*numpy.array(range(len(RecordA0)))
            Requete.Analogsignal_sampling_rate=list([Navigate.VarList["sampling_rate"]]*len(Navigate.ArrayList))
        else:
            # TODO : Add manual SR input
            print "filtype not identified, Auto sampling rate ignored"
            Navigate.VarList["SampleInterval"] = 1.
            Requete.timescale = 1.*numpy.array(range(len(RecordA0)))
            Requete.Analogsignal_sampling_rate=list([len(Requete.Current_Signal)]*len(Navigate.ArrayList))

        
        Requete.Shortest_Sweep_Length=(Requete.timescale[-1]+(Requete.timescale[1]-Requete.timescale[0]))/1000. #in s
        if Navigate.VarList.has_key("sampling_rate") == True:
            Navigate.Points_by_ms = Navigate.VarList["sampling_rate"]
            Requete.BypassedSamplingRate=1000.*Navigate.VarList["sampling_rate"]
        else:
            Navigate.Points_by_ms = 1000./ Navigate.VarList["SampleInterval"]    
            Requete.BypassedSamplingRate=1000./Navigate.VarList["SampleInterval"]
        
        Requete.Current_Sweep_Number=0
        Requete.Block_ids=list([None]*len(Navigate.ArrayList))
        Requete.Block_date=list([None]*len(Navigate.ArrayList))
        Requete.Segment_ids=list([None]*len(Navigate.ArrayList))
        Requete.Analogsignal_ids=range(len(Navigate.ArrayList))#list([None]*len(Navigate.ArrayList))
        Requete.Analogsignal_name=list([None]*len(Navigate.ArrayList))
        Requete.tag={}
        Requete.tag["Selection"]=[0]*len(Requete.Analogsignal_ids)
        Requete.Analogsignal_channel=list([None]*len(Navigate.ArrayList))
        Requete.Block_fileOrigin=list([None]*len(Navigate.ArrayList))
        Requete.Block_Info=list([None]*len(Navigate.ArrayList))
        if Navigate.VarList.has_key("SamplesPerWave") == True:
            Requete.Analogsignal_signal_shape=list([int(Navigate.VarList["SamplesPerWave"])]*len(Navigate.ArrayList))
        else:
            Requete.Analogsignal_signal_shape=list([int(len(Requete.Current_Signal)*Requete.Shortest_Sweep_Length)]*len(Navigate.ArrayList))
        
        Main.slider.setRange(0, len(Requete.Analogsignal_ids)-1) #definit le range du slider sweepnb
        Requete.Spiketrain_ids=list([None]*len(Navigate.ArrayList))
        Requete.Spiketrain_neuron_name=list([None]*len(Navigate.ArrayList))
        Requete.Spiketrain_t_start=list([None]*len(Navigate.ArrayList))
        Requete.Spiketrain_Neuid=list([None]*len(Navigate.ArrayList))  

        
        Main.To.setText(str(len(Requete.Analogsignal_ids)-1))
        Navigate.Check_From_To()
        Navigate.Display_First_Trace()

                
