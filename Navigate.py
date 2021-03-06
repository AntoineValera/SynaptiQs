# -*- coding: utf-8 -*-
"""
Created on Tue May 21 22:27:27 2013

@author: Antoine.Valera
"""

from OpenElectrophy import AnalogSignal,computing,SpikeTrain
from matplotlib import *
from PyQt4 import QtGui,QtCore
import scipy


class Navigate(object):
    """
    The Navigate class contains all the function used to display traces in SynaptiQs
    """
    
    def __init__(self):
        self.__name__="Navigate"
        self.lowvalue=0
        self.highvalue=5000
        self.Color_of_Standard_Trace='g'
        self.SpikeTrainEdited = False
        self.Color_of_Filtered_Traces = 'r'
        #self.Weired=False #testing... for a second filtering if needed
    
    def _all(self,All=False):
        List=[]
        i=self.__name__
        for j in dir(eval(i)):
            if All==False and j[:2] == '__':
                pass
            else:
                List.append(i+'.'+j)
        for i in List:
            print i
    def Load_This_Sweep_Number(self,Current_Displayed_Sweep_Number=None,SkipUpdate=False):
        """
        This function use the Main.Sweep_Number_Input_Field Value to set a Sweep Number
        or any INT value, within the len(Request.Analogsignal_ids) range
        if Current_Displayed_Sweep_Number is None, the sweep is reloaded
        """
        
        if SkipUpdate == False:
               
            if Current_Displayed_Sweep_Number == None:
                Current_Displayed_Sweep_Number=Main.Sweep_Number_Input_Field.text()
            
            try:
                Main.Sweep_Number_Input_Field.setStyleSheet("QLineEdit{background:white;}")
                Current_Displayed_Sweep_Number=int(Current_Displayed_Sweep_Number)
            except ValueError:
                Main.Sweep_Number_Input_Field.setStyleSheet("QLineEdit{background:red;}")
                return
            
            
            if Current_Displayed_Sweep_Number >= (len(Requete.Analogsignal_ids)-1):
                if Current_Displayed_Sweep_Number == (len(Requete.Analogsignal_ids)-1):
                    print "It's the Last sweep"            
                Current_Displayed_Sweep_Number = (len(Requete.Analogsignal_ids)-1)
                Main.Sweep_Number_Input_Field.setText(str(len(Requete.Analogsignal_ids)-1))
    
    
                
            if Current_Displayed_Sweep_Number <= 0:
                if Current_Displayed_Sweep_Number == 0:
                    print "It's the First sweep"            
                Current_Displayed_Sweep_Number = 0 
                Main.Sweep_Number_Input_Field.setText(str(0))
    
    
            Requete.Current_Sweep_Number=Current_Displayed_Sweep_Number
            
            
            
            try:
                self.Load_This_Trace(Requete.Analogsignal_ids[Requete.Current_Sweep_Number])
            except IndexError:
                
                msg="""
                <b>Loading Error</b>
                <p>This Sweep Number doesn't Exist
                <p> (or doesn't exist anymore if you changed your SQL mode)
                <p>Check your SweepNumber, or your Filtering Parameters
                """                 
                Infos.Error(msg)

       
            #This displays some ids information in the bottom bar of SynaptiQs
            try:
                Info_Message="Sweep # = "+str(Requete.Current_Sweep_Number)+" current AnalogSignal.id is "+str(Requete.Analogsignal_ids[Requete.Current_Sweep_Number])+" ,current segment.id is "+str(Requete.Segment_ids[Requete.Current_Sweep_Number])+" and spiketrain.id is "+str(Requete.Spiketrain_ids[Requete.Current_Sweep_Number])+ " with t_start at "+str(Requete.Spiketrain_t_start[Requete.Current_Sweep_Number])
            except:        
                Info_Message="Sweep # = "+str(Requete.Current_Sweep_Number)+" current AnalogSignal.id is "+str(Requete.Analogsignal_ids[Requete.Current_Sweep_Number])+" ,current segment.id is "+str(Requete.Segment_ids[Requete.Current_Sweep_Number])
            Main.status_text.setText(Info_Message)
            
            for n in range(Requete.NumberofChannels):
                if Requete.tag["Selection"][Requete.Current_Sweep_Number][n] == None: #Au cas où le champs Tag est de type None, on met 0
                    Requete.tag["Selection"][Requete.Current_Sweep_Number][n]=int(0)
                    Requete.sig.save()
    
            if Main.Display_Spikes_Button.checkState() == 2:
                if Main.SQLTabWidget.currentIndex() == 2:
                    print "Only one channel displayed at the time for now. Change the channel in Menu>MappingOption>CurrentChannel"
                    pass
                else:
                    Requete.Call_Spikes()            
            Main.MainFigure.canvas.Update_Figure()  
            
            #Lecture du Tag
            for n in range(Requete.NumberofChannels):
                
                if Requete.tag["Selection"][Requete.Current_Sweep_Number][n] == 1:
                    Main.Tagging_Button.setChecked(True)
                elif Requete.tag["Selection"][Requete.Current_Sweep_Number][n] == 0:
                    Main.Tagging_Button.setChecked(False) 

                
            Main.slider.setValue(Requete.Current_Sweep_Number)



    def Load_This_Trace(self,Analogisgnal_id_to_Load,Color_of_Standard_Trace='g',Color_of_Filtered_Traces='r'):
        """
        This function loads the signal to be displayed.
        Thus, it is called every time the trace has to change 
        However, it doesn't display the trace. If you want a display, just call Navigate.Load_This_Sweep_Number(sweepnumber)
        
        Important arrays/Variable are :    Navigate.sig : The whole analogsignal class of the current id
                                           Navigate.si : the current signal
                                           Navigate.Signal_Length_in_Points : the signal length in points...
                                           Navigate.signal_length_in_ms : the signal length in ms...
                                           Navigate.Points_by_ms : The sampling rate
        """

        def running_median_insort(seq,win=801):
            import cProfile
            from collections import deque
            from bisect import insort, bisect_left
            from itertools import islice
        
            seq = iter(seq)
            d = deque()
            s = []
            result = []
            for item in islice(seq, win):
                d.append(item)
                insort(s, item)
                result.append(s[len(d)//2])
            m = win // 2
            c=0
            e=0
            for item in seq:
                if c>win/2:
                    old = d.popleft()
                    d.append(item)
                    del s[bisect_left(s, old)]
                    insort(s, item)
                    result.append(s[m])
                else:
                    e+=1
                c+=1
            for i in range(e):
                result.append(s[m])
            return result
        
        #Loading the signal
        # TODO : Check that filtered signal is implemented everywhere it should
        if Main.SQLTabWidget.currentIndex() == 0 or Main.SQLTabWidget.currentIndex() == 1:
            Analogisgnal_id_to_Load=list(Analogisgnal_id_to_Load)
            self.si=[]
            self.Filtered_Signal=[]
            for i in Analogisgnal_id_to_Load:
                self.sig = AnalogSignal().load(i,session=Requete.Global_Session)
                #Resampling to the lowest sampling rate in the selection. It doesn't change anything if there is only one sampling rate
                self.si.append(scipy.signal.resample(self.sig.signal,(Requete.BypassedSamplingRate)*(len(self.sig.signal)/self.sig.sampling_rate)))
                self.Filtered_Signal.append(scipy.signal.resample(self.sig.signal,(Requete.BypassedSamplingRate)*(len(self.sig.signal)/self.sig.sampling_rate)))            
              
                  
        elif Main.SQLTabWidget.currentIndex() == 2:#For local Files
            #TODO:Implement multichannel on spikes
            self.si = self.ArrayList[Requete.Current_Sweep_Number]
            self.Filtered_Signal = self.ArrayList[Requete.Current_Sweep_Number]
            n=Mapping.CurrentChannel
            try:
                Requete.Current_Spike_Times=Requete.SpikeTrainfromLocal[str(Requete.Current_Sweep_Number)+'_'+str(n)]
                Requete.Amplitude_At_Spike_Time=Requete.AmpSpikeTrainfromLocal[str(Requete.Current_Sweep_Number)+'_'+str(n)]
            except :
                Requete.Current_Spike_Times=[]
                Requete.Amplitude_At_Spike_Time=[]
                
        #Cropping of the signal to the shortest duration of the selection. It doesn't change anything if there is only one sampling rate
        for i,j in enumerate(self.si):
            self.si[i] = self.si[i][0:int(Requete.BypassedSamplingRate*Requete.Shortest_Sweep_Length)] #+1
        for i,j in enumerate(self.Filtered_Signal):   
            self.Filtered_Signal[i] = self.Filtered_Signal[i][0:int(Requete.BypassedSamplingRate*Requete.Shortest_Sweep_Length)] #+1

        
        Analysis.Measure_On_Off()
        

        
        #Leak Removal for RAW signal
        if Main.Remove_Leak_Button.checkState() == 2:
            for i,j in enumerate(self.si):
                self.si[i]=Analysis.Remove_a_Leak(self.si[i])
        else:
            Analysis.Current_Leak=0
        #Leak Removal for filtered signal
        #If Analyze_Filtered_Traces_Button is checked, then we apply Leak Removal and Filtering on self.Filtered_Signal
        if Main.Analyze_Filtered_Traces_Button.checkState () == 2 or Main.Filtered_Display.checkState() == 2:
            Main.Filtered_Display.setCheckState(2)
            if Main.Remove_Leak_Button.checkState() == 2:
                for i,j in enumerate(self.Filtered_Signal):
                    self.Filtered_Signal[i]=Analysis.Remove_a_Leak(self.Filtered_Signal[i])                

        #Filtering. 
        #Both FFT AND/OR median Filtering can be used, on RAW AND/OR Filtered signal
        if Main.Filtered_Display.checkState() == 2:
            nq = self.Points_by_ms*1000/2
            for i,j in enumerate(self.Filtered_Signal):
                self.Filtered_Signal[i] = computing.filter.fft_passband_filter(self.si[i], f_low = int(Main.low_freq.text())/nq , f_high = int(Main.high_freq.text())/nq)
                if Main.Median_Filtered_Display.checkState() == 2: 
                    c=running_median_insort(self.Filtered_Signal[i],win=int(Main.median_filt.text()))
                    b=running_median_insort(c,win=int(Main.median_filt.text()))
                    a=running_median_insort(b,win=int(Main.median_filt.text()))
                    self.Filtered_Signal[i]=self.Filtered_Signal[i]-a            
        else:
            if Main.Median_Filtered_Display.checkState() == 2: 
                for i,j in enumerate(self.Filtered_Signal):
                    c=running_median_insort(self.Filtered_Signal[i],win=int(Main.median_filt.text()))
                    b=running_median_insort(c,win=int(Main.median_filt.text()))
                    a=running_median_insort(b,win=int(Main.median_filt.text()))
                    self.Filtered_Signal[i]=self.Filtered_Signal[i]-a         


        #Je sais plus pourquoi c'est la
#         
        #or Main.Measure_From_Zero_Button.checkState() == 2 
            #if Main.Remove_Leak_Button.checkState() == 0:
               # Main.Remove_Leak_Button.setCheckState(2)         
         
        #self.Filtered_Signal=Analysis.Remove_a_Leak(self.Filtered_Signal,Leak_Removing_Interval_Start=0*self.Points_by_ms,Leak_Removing_Interval_End=200*self.Points_by_ms)                    
  
        #TODO : OBSOLETE, A corriger  
        self.Signal_Length_in_Points=len(self.si[0]) #durée du signal en pnts
        self.signal_length_in_ms=len(self.si[0])/(Requete.Analogsignal_sampling_rate[Requete.Current_Sweep_Number]) #durée du signal en ms
        
        #print "Pb to be solved : I'm loaded 2 times",Requete.Current_Sweep_Number
        self.Points_by_ms=Requete.Analogsignal_sampling_rate[Requete.Current_Sweep_Number]/1000
        self.timescale=numpy.array(range(len(self.si[0])))/self.Points_by_ms                

        self.Color_of_Standard_Trace=Color_of_Standard_Trace
        self.Color_of_Filtered_Traces=Color_of_Filtered_Traces

        #if Requete.NumberofChannels == 1:
        #    self.si=self.si[0]
        #    self.Filtered_Signal=self.Filtered_Signal[0]

        
    def Update_SweepNumber_Slider(self):
        Slider_Value=int(Main.slider.value())
        Main.Sweep_Number_Input_Field.setText(str(Slider_Value))
        try:        
            self.Load_This_Sweep_Number(Slider_Value,SkipUpdate=False)
        except IndexError:
            Requete.Analogsignal_ids=[]
            Requete.Current_Sweep_Number=None
            Main.slider.setValue(0)
            Requete.Resetfields()
            Mapping.Reset_Mapping_Variables()
            Main.Show_Main_Figure()
            
            
        #if SkipUpdate == False:
            # if Main.FastMode == False:
           #      print Slider_Value
                 #self.Load_This_Sweep_Number(Slider_Value) #Double load problem is here
      #  else:         
        #    Main.slider.setValue(Requete.Current_Sweep_Number)

       
    def Display_Next_Trace(self):
        if Requete.Current_Sweep_Number < (len(Requete.Analogsignal_ids)-1):
            Requete.Current_Sweep_Number+=1
        Main.slider.setValue(Requete.Current_Sweep_Number)
        self.Load_This_Sweep_Number(Requete.Current_Sweep_Number,SkipUpdate=True)

    def Display_Previous_Trace(self):
        if Requete.Current_Sweep_Number > 0:
            Requete.Current_Sweep_Number-=1
        Main.slider.setValue(Requete.Current_Sweep_Number)
        self.Load_This_Sweep_Number(Requete.Current_Sweep_Number,SkipUpdate=True)
    
    def Display_Trace_plus_Step(self):
        if Requete.Current_Sweep_Number < (len(Requete.Analogsignal_ids)-1):
            Requete.Current_Sweep_Number+=self.Step
        Main.slider.setValue(Requete.Current_Sweep_Number)
        self.Load_This_Sweep_Number(Requete.Current_Sweep_Number,SkipUpdate=True)        


    def Display_Trace_minus_Step(self):
        if Requete.Current_Sweep_Number > 0:
            Requete.Current_Sweep_Number-=self.Step
        Main.slider.setValue(Requete.Current_Sweep_Number)
        self.Load_This_Sweep_Number(Requete.Current_Sweep_Number,SkipUpdate=True)        

    def Modify_Step_Range(self,item):
        """
        This function is called to add a Step Value in the
        self.Menu_with_List_of_Positive_Steps AND self.Menu_with_List_of_Negative_Steps
        Just call Navigate.Modify_Step_Range('value') to change both buttons
        """
        item.replace("-","")
        item.replace("+","")
        self.Step=abs(int(item))
        Main.Minus_Step.setText("- "+str(self.Step)) 
        Main.Plus_Step.setText("+ "+str(self.Step)) 
    
    def Display_First_Trace(self):
        self.Load_This_Sweep_Number(0)
        Main.slider.setValue(0)

    def Display_Last_Trace(self):
        self.Load_This_Sweep_Number(len(Requete.Analogsignal_ids)-1,SkipUpdate=True)
        Main.slider.setValue(len(Requete.Analogsignal_ids)-1)

        
    def Change_Tag_Checkbox_State(self):
        """
        This function change the Requete.tag["Selection"][Requete.Current_Sweep_Number] for all channels
        depending on the Main.Tagging_Button.checkState()
        """
        new=Requete.tag["Selection"]
        for n in range(Requete.NumberofChannels):
            if Main.Tagging_Button.isChecked():
                new[Requete.Current_Sweep_Number][n]=1
            else:
                new[Requete.Current_Sweep_Number][n]=0
        Requete.tag["Selection"]=new  
    def Tag_All_Traces(self,ProgressDisplay=True):
        
        for i in range(len(Requete.Analogsignal_ids)):
            if ProgressDisplay == True:
                Main.progress.setMinimum(0)
                Main.progress.setMaximum(len(Requete.Analogsignal_ids)-1)
                Main.progress.setValue(i)
         
            if i >= int(Main.From.text()) and i <= int(Main.To.text()):
                for n in range(Requete.NumberofChannels):
                    Requete.tag["Selection"][i][n]=int(1)
                    
        if ProgressDisplay == True:            
            Info_Message="Everything is Tagged"
            Main.status_text.setText(Info_Message) 
        
    def UnTag_All_Traces(self,ProgressDisplay=True):

        for i in range(len(Requete.Analogsignal_ids)):
            if ProgressDisplay == True:
                Main.progress.setMinimum(0)
                Main.progress.setMaximum(len(Requete.Analogsignal_ids)-1)
                Main.progress.setValue(i)
         
            if i >= int(Main.From.text()) and i <= int(Main.To.text()):
                for n in range(Requete.NumberofChannels):
                    Requete.tag["Selection"][i][n]=int(0)
                
        if ProgressDisplay == True:           
            Info_Message="Everything is UnTagged"
            Main.status_text.setText(Info_Message) 
        
    def Invert_All_Tag_Values(self,ProgressDisplay=True):
        
        for i in range(len(Requete.Analogsignal_ids)):
            if ProgressDisplay == True:
                Main.progress.setMinimum(0)
                Main.progress.setMaximum(len(Requete.Analogsignal_ids)-1)
                Main.progress.setValue(i)
            
            if i >= int(Main.From.text()) and i <= int(Main.To.text()):
                for n in range(Requete.NumberofChannels):
                    if Requete.tag["Selection"][i][n]==1:
                        Requete.tag["Selection"][i][n]=int(0)
                    elif Requete.tag["Selection"][i][n]==0:
                        Requete.tag["Selection"][i][n]=int(1)
                    
        if ProgressDisplay == True:
            Info_Message="All Tags are Inverted"
            Main.status_text.setText(Info_Message) 

           
        
    def Check_From_To(self):
        try:
            if int(Main.From.text())<0:
                Main.From.setText(str(0))
            if int(Main.From.text())>(len(Requete.Analogsignal_ids)-1):
                Main.From.setText(str(len(Requete.Analogsignal_ids)-2))            
            if int(Main.To.text())>(len(Requete.Analogsignal_ids)-1):
                Main.To.setText(str(len(Requete.Analogsignal_ids)-1))
            if int(Main.To.text())<int(Main.From.text()):
                Main.To.setText(str(int(Main.From.text())+1))
        except:# ValueError:
            Main.From.setText(str(0))
            Main.To.setText(str(len(Requete.Analogsignal_ids)-1))

    def Concatenate(self,Source=None,Mode='Ids',Start=None,Stop=None,Channels=None,Rendering=False):
        '''
        Source is a list of analogisnal ids (Default is Requete.Analogsignal_ids) OR a list of arrays.
        if Source is a list of Ids, Mode == 'Ids', else Mode == 'RAW'
        Source Structure must be [[a1,b1],[a2,b2],[a3,b3]] letters being channels and numbers beeing sweep numbers

        Concatenate all traces from Source  and save them as
            Navigate.Concatenated
        Start and Stop define the range of interest (default to None concatenate all traces)
        Channel define the Channel to concatenate. Default behavior concatenate all channels
        Rendering shows the result. Default to False
        '''
        #If No Defined Source, we used the analogsignal ids
        if Source == None:
            Source = Requete.Analogsignal_ids
        
        
        #If No Defined Source, we used the analogsignal ids
        try:
            if type(Source[0]) not in [list,numpy.ndarray]:
                #if input is [a1,a2,a3,a4]
                Source=[[x] for x in Source]
                print 'Corrected input', Source
        except IndexError:
                msg="""
                <b>No DATA</b>
                <p>Did you tag any trace?
                """                 
                Infos.Error(msg)            

        if Channels==None:
            self.Concatenated=[[] for x in [None]*Requete.NumberofChannels]
            Channels=range(Requete.NumberofChannels)
        else:
            if type(Channels) is int or type(Channels) is float:
                Channels=[int(Channels)]
            self.Concatenated=[[] for x in Channels]
            #self.Concatenated=[[None]*len(Channels)]

        if Start == None or Stop <0:
            Start=0
        if Stop == None or Stop > len(Source): 
            Stop = len(Source)

        if Mode == 'RAW': #correction for improper user input with single channel
            #if the user enter [array,array,array] it becomes [[array],[array],[array]]
            if type(Source[0][0]) not in [list,numpy.ndarray]:
                Source=[[x] for x in Source]

        for n,m in enumerate(Channels):
            for j,i in enumerate(Source):
                if j>= Start and j<=Stop:
                    if Mode == 'Ids':
                        try:
                            a=AnalogSignal.load(i[m]).signal
                        except TypeError:#when it's a local file
                            a=self.ArrayList[j][n]
                    elif Mode == 'RAW':
                        a=Source[j][n]
                    else:
                        print 'Mode', Mode, 'not recognized'
                        return
                    self.Concatenated[n].extend(a)
            if Rendering == True:
                pyplot.plot(self.Concatenated[n])
        
        if Rendering == True:
            pyplot.show()
        
        
                
        
            

           
            
            
            
            
            
            
            