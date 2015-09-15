# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:50:11 2013

@author: Antoine Valera
"""


from PyQt4 import QtCore, QtGui
import numpy
import scipy
from OpenElectrophy import AnalogSignal,SpikeTrain,gui,sql
from matplotlib import pyplot,numpy

import warnings
warnings.filterwarnings("ignore")

#TODO :
#Remove_a_Leak still contains some manual parameters


class Analysis(object):

    """
    This Class Contains integrated SynaptiQs analyses function 
    """
    def __init__(self):
        self.__name__="Analysis"
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
    def Remove_a_Leak(self,Signal):#,Leak_Removing_Interval_Start=0,Leak_Removing_Interval_End=-1):
        #SealTestStart=2500
        #SealTestStop=3600
        SealTestStart=2500
        SealTestStop=2501    
        StimStart=self.Measurement_Interval[2]
    
    
        mask=numpy.zeros(len(Signal))
        mask[SealTestStart:SealTestStop]=1
        mask[StimStart:]=1
        mx = numpy.ma.masked_array(Signal, mask)
        if Mapping.Types_of_Events_to_Measure == 'Negative':
            self.Current_Leak=scipy.stats.scoreatpercentile(mx, 85)
        elif Mapping.Types_of_Events_to_Measure == 'Positive':
            self.Current_Leak=scipy.stats.scoreatpercentile(mx, 15)            
            
        #self.Current_Leak=numpy.median(Signal[Leak_Removing_Interval_Start:Leak_Removing_Interval_End]) Median Filtering
        #self.Current_Leak=scipy.stats.scoreatpercentile(Signal, 75)
        #self.Current_Leak=scipy.stats.scoreatpercentile(scipy.signal.decimate(Navigate.si,10), 75) #Even faster
        Signal=Signal-self.Current_Leak
        return Signal

    
    def Measure_on_Average(self,List_of_Ids=None,Measure_All_from_Baseline1=False,Display_Superimposed_Traces=False,Rendering=True,Position=(None,None),Origin=None,All_from_Zero=False,ProgressDisplay=True,NumberofChannels=1):
        
        """
        This function measure the average trace of a given list of Analogsignal ids (default is Requete.Analogsignal_ids tagged traces)
        It calculates mean amplitude 1, 2 and 3 and mean charge 1, 2 and 3 from SynaptiQs settings. These values are also returned (in this order)
        The function creates an Analysis.mean trace (which is also returned)
        
        If Measure_All_from_Baseline1 is True, mean amplitude 1, 2 and 3 and mean charge 1, 2 and 3 are calculated from baseline 1 value
        If All_from_Zero is True, mean amplitude 1, 2 and 3 and mean charge 1, 2 and 3 are calculated from 0 after leak substraction
        
        """   
        
        ##scipy.signal.decimate could accelerate the display
      
            
        if List_of_Ids == None:
            List_of_Ids = Requete.Analogsignal_ids
            NumberofChannels=Requete.NumberofChannels

        self.Currently_Used_Sweep_nb_for_Local_Average=[]#[[numpy.NaN]*Requete.NumberofChannels]*len(List_of_Ids)
                
        for n in range(NumberofChannels):
            self.Check_Measuring_Parameters_Validity()
            
    #        if Main.SQLTabWidget.currentIndex() == 0 or Main.SQLTabWidget.currentIndex() == 1:
    #            sig = AnalogSignal().load(List_of_Ids[0],session=Requete.Global_Session)
    #        elif Main.SQLTabWidget.currentIndex() == 2:
    #            sig = eval("Analysis.RecordA"+str(Requete.Current_Sweep_Number))
            
            
            
            self.mean = Navigate.si[n]-Navigate.si[n]
    
            counter=0
            
    
            self.List_of_Averaged_Sweeps=[]
            for i in range(len(List_of_Ids)):
                if ProgressDisplay==True:
                    Main.progress.setMinimum(0)
                    Main.progress.setMaximum(len(List_of_Ids)-1)
                    Main.progress.setValue(i)
                if Main.SQLTabWidget.currentIndex() == 2: # if Local file only
                    Requete.Current_Sweep_Number=i
                if ((List_of_Ids is Requete.Analogsignal_ids) and (i >= int(Main.From.text())) and (i <= int(Main.To.text())) and (Requete.tag["Selection"][i*Requete.NumberofChannels+n] == 1)) or (List_of_Ids is not Requete.Analogsignal_ids):
                    counter+=1
                    self.List_of_Averaged_Sweeps.append(i)
    
                    if Main.Analyze_Filtered_Traces_Button.checkState() == 0:
                        Navigate.Load_This_Trace(List_of_Ids[i])
                        self.mean = self.mean+Navigate.si[n]
                    elif Main.Analyze_Filtered_Traces_Button.checkState() == 2:
                        Navigate.Load_This_Trace(List_of_Ids[i])
                        self.mean = self.mean+Navigate.Filtered_Signal[n]                      
    
                      
            Info_Message="It's an average of "+str(counter)+" Sweeps"
            Main.status_text.setText(Info_Message) 
            
            self.mean/=counter
    
            if Main.Measure_From_Zero_Button.checkState() == 2:
                All_from_Zero == True
    
            if All_from_Zero == True:
                Main.Remove_Leak_Button.setCheckState(2) 
                Measure_All_from_Baseline1 = False
            if Main.Remove_Leak_Button.checkState() == 2:
                if All_from_Zero == False:
                    Main.Remove_Leak_Button.setCheckState(0)
                leaktemporaryremoved=True
            else:
                leaktemporaryremoved=False  
    
    
            self.Ampvalues = range(6)
            self.Surfacevalues = range(6)
            self.Measurement_Interval = range(6)
            self.left = range(6)
            
    
            listofmeth=["Baseline1_meth","Peak1_meth",
                             "Baseline2_meth","Peak2_meth",
                             "Baseline3_meth","Peak3_meth"]
            
            compteur=0
     
            for loc in Main.listofcoord:
            
                bgn=str("Main."+str(loc[0])+".text()")
                end=str("Main."+str(loc[1])+".text()")
                size=str("Main."+str(loc[2])+".text()")
                meth=str("Main."+str(listofmeth[compteur])+".currentText()")
                                    
    
                if  eval(meth) == 'Max':
                            #if there is a bug here, it's because the preset parameters you used ware aclculated on a different samplig rate, and not corrected                
                    try:
                        aloc = numpy.argmax(self.mean[int(float(eval(bgn))*Navigate.Points_by_ms):int(float(eval(end))*Navigate.Points_by_ms)])
                    except ValueError:
                        aloc = 0            
                elif eval(meth) == 'Min':
                            #if there is a bug here, it's because the preset parameters you used ware aclculated on a different samplig rate, and not corrected                
                    try:
                        aloc = numpy.argmin(self.mean[int(float(eval(bgn))*Navigate.Points_by_ms):int(float(eval(end))*Navigate.Points_by_ms)])
                    except ValueError:
                        aloc = 0
                        
                leftpnt = int(aloc-float(eval(size))*Navigate.Points_by_ms/2+float(eval(bgn))*Navigate.Points_by_ms)
    
                if leftpnt<0:
                    leftpnt=0
                if leftpnt<float(eval(bgn))*Navigate.Points_by_ms:
                    leftpnt=int(float(eval(bgn))*Navigate.Points_by_ms)
                rightpnt = int(aloc+float(eval(size))*Navigate.Points_by_ms/2+float(eval(bgn))*Navigate.Points_by_ms)
                
                if rightpnt>len(self.mean):
                    rightpnt=len(self.mean)
                if rightpnt>float(eval(end))*Navigate.Points_by_ms:
                    rightpnt=int(float(eval(end))*Navigate.Points_by_ms)
                    
                avalue = numpy.mean(self.mean[leftpnt:rightpnt])
                self.Ampvalues[compteur]=avalue
                
                self.Measurement_Interval[compteur]=rightpnt-leftpnt
                self.left[compteur]=leftpnt
                compteur+=1
                       
        
            if Main.Measure_From_Baseline1_Button.checkState() == 0 :
                
                self.Mean_Amplitude_1=(self.Ampvalues[1]-self.Ampvalues[0])
                self.Mean_Amplitude_2=(self.Ampvalues[3]-self.Ampvalues[2])
                self.Mean_Amplitude_3=(self.Ampvalues[5]-self.Ampvalues[4])
                
                self.Mean_Charge_1=sum(self.mean[int(float(Main.Peak1_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak1_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-self.Ampvalues[0]*float(len(self.mean[int(float(Main.Peak1_begin.text())):int(float(Main.Peak1_end.text()))]))/1000
                self.Mean_Charge_2=sum(self.mean[int(float(Main.Peak2_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak2_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-self.Ampvalues[2]*float(len(self.mean[int(float(Main.Peak2_begin.text())):int(float(Main.Peak2_end.text()))]))/1000
                self.Mean_Charge_3=sum(self.mean[int(float(Main.Peak3_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak3_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-self.Ampvalues[4]*float(len(self.mean[int(float(Main.Peak3_begin.text())):int(float(Main.Peak3_end.text()))]))/1000     
    
            elif Main.Measure_From_Baseline1_Button.checkState() == 2 or Measure_All_from_Baseline1 == True:
    
                self.Mean_Amplitude_1=(self.Ampvalues[1]-self.Ampvalues[0])
                self.Mean_Amplitude_2=(self.Ampvalues[3]-self.Ampvalues[0])
                self.Mean_Amplitude_3=(self.Ampvalues[5]-self.Ampvalues[0])
                
                self.Mean_Charge_1=sum(self.mean[float(Main.Peak1_begin.text())*Navigate.Points_by_ms:float(Main.Peak1_end.text())*Navigate.Points_by_ms])/(Navigate.Points_by_ms*1000)-self.Ampvalues[0]*float(len(self.mean[float(Main.Peak1_begin.text()):float(Main.Peak1_end.text())]))/1000
                self.Mean_Charge_2=sum(self.mean[float(Main.Peak2_begin.text())*Navigate.Points_by_ms:float(Main.Peak2_end.text())*Navigate.Points_by_ms])/(Navigate.Points_by_ms*1000)-self.Ampvalues[0]*float(len(self.mean[float(Main.Peak2_begin.text()):float(Main.Peak2_end.text())]))/1000
                self.Mean_Charge_3=sum(self.mean[float(Main.Peak3_begin.text())*Navigate.Points_by_ms:float(Main.Peak3_end.text())*Navigate.Points_by_ms])/(Navigate.Points_by_ms*1000)-self.Ampvalues[0]*float(len(self.mean[float(Main.Peak3_begin.text()):float(Main.Peak3_end.text())]))/1000 
            
            elif All_from_Zero == True:
                self.Mean_Amplitude_1=self.Ampvalues[1]
                self.Mean_Amplitude_2=self.Ampvalues[3]
                self.Mean_Amplitude_3=self.Ampvalues[5]
                
                self.baseline=numpy.zeros(int(len(self.Amplitudes_1)+2))
                self.Mean_Charge_1=sum(self.mean[float(Main.Peak1_begin.text())*Navigate.Points_by_ms:float(Main.Peak1_end.text())*Navigate.Points_by_ms])/(Navigate.Points_by_ms*1000)
                self.Mean_Charge_2=sum(self.mean[float(Main.Peak2_begin.text())*Navigate.Points_by_ms:float(Main.Peak2_end.text())*Navigate.Points_by_ms])/(Navigate.Points_by_ms*1000)
                self.Mean_Charge_3=sum(self.mean[float(Main.Peak3_begin.text())*Navigate.Points_by_ms:float(Main.Peak3_end.text())*Navigate.Points_by_ms])/(Navigate.Points_by_ms*1000) 
    
    
            
            if leaktemporaryremoved == True and All_from_Zero == False:
                Main.Remove_Leak_Button.setCheckState(2)
    
    
    
            if Rendering == True: #Still some pb if called from outside
                'rendering of average'
    
                Info_Message="Amp1 = "+str(self.Mean_Amplitude_1)+"    Amp2 = "+str(self.Mean_Amplitude_2)+"    Amp3 = "+str(self.Mean_Amplitude_3)
                Main.status_text.setText(Info_Message)
        
                #Creating measurements labels
                self.Base1 = numpy.ones(self.Measurement_Interval[0])*self.Ampvalues[0]
                self.Base1_coord = numpy.array(range(len(self.Base1)))+self.left[0]
                self.Peak1 = numpy.ones(self.Measurement_Interval[1])*self.Ampvalues[1]
                self.Peak1_coord = numpy.array(range(len(self.Peak1)))+self.left[1]
                self.Base2 = numpy.ones(self.Measurement_Interval[2])*self.Ampvalues[2]
                self.Base2_coord = numpy.array(range(len(self.Base2)))+self.left[2]
                self.Peak2 = numpy.ones(self.Measurement_Interval[3])*self.Ampvalues[3]
                self.Peak2_coord = numpy.array(range(len(self.Peak2)))+self.left[3]
                self.Base3 = numpy.ones(self.Measurement_Interval[4])*self.Ampvalues[4]
                self.Base3_coord = numpy.array(range(len(self.Base3)))+self.left[4]
                self.Peak3 = numpy.ones(self.Measurement_Interval[5])*self.Ampvalues[5]
                self.Peak3_coord = numpy.array(range(len(self.Peak3)))+self.left[5]
          
    #            if Main.Measure_From_Baseline1_Button.checkState() == 2 or Measure_All_from_Baseline1 == True:
    #                self.Base1-=self.Ampvalues[0]
    #                self.Peak1-=self.Ampvalues[0]
    #                self.Base2-=self.Ampvalues[0]
    #                self.Peak2-=self.Ampvalues[0]
    #                self.Base3-=self.Ampvalues[0]
    #                self.Peak3-=self.Ampvalues[0]
    
                #Only Once
                if QtCore.QObject().sender().__class__.__name__ == 'QCheckBox':
                    if n == 0:
                        self.Wid.canvas.axes.clear()    
                else:
                    if n == 0:
                        #For the first trace, we create the widget
                        self.Wid = MyMplWidget(title = 'Averaged Trace',subplots=[NumberofChannels,1,n+1])
                    
                        
                        self.Wid.canvas.Superimpose_Used_Traces_Button = QtGui.QCheckBox()
                        self.Wid.canvas.Superimpose_Used_Traces_Button.setText("Superimpose")
                    
                        if Main.Superimpose_Used_Traces == False or Display_Superimposed_Traces == False:
                            self.Wid.canvas.Superimpose_Used_Traces_Button.setCheckState(0) 
                        if Main.Superimpose_Used_Traces == True or Display_Superimposed_Traces == True :
                            self.Wid.canvas.Superimpose_Used_Traces_Button.setCheckState(2)
                          
                        self.Wid.toolbar.addWidget(self.Wid.canvas.Superimpose_Used_Traces_Button)
                        QtCore.QObject.connect(self.Wid.canvas.Superimpose_Used_Traces_Button,QtCore.SIGNAL('stateChanged(int)'),self.Wid.canvas.Update_Superimpose)            
                    else:
                        
                        #For the next ones we do just add subplots
                        self.Wid.canvas.axes = self.Wid.canvas.fig.add_subplot(NumberofChannels,1,n+1)

    
                #This can be optimized
                if Main.Superimpose_Used_Traces == True or Display_Superimposed_Traces == True :
                    
                    self.Wid.canvas.Object_Selection_Mode = 'Trace'
                    for i,j in enumerate(List_of_Ids):
                        if ((List_of_Ids is Requete.Analogsignal_ids) and (i >= int(Main.From.text())) and (i <= int(Main.To.text())) and (Requete.tag["Selection"][i] == 1)) or (List_of_Ids is not Requete.Analogsignal_ids):
                            if Main.SQLTabWidget.currentIndex() == 2:
                                Requete.Current_Sweep_Number=i
                                Navigate.Load_This_Trace(i)
                            else:
                                Navigate.Load_This_Trace(j)
                            
                            if Main.Analyze_Filtered_Traces_Button.checkState() == 0:
                                locals()["Displayed_"+str(i)]=Navigate.si[n]
                            elif Main.Analyze_Filtered_Traces_Button.checkState() == 2:
                                locals()["Displayed_"+str(i)]=Navigate.Filtered_Signal[n]
                            
                            if List_of_Ids is Requete.Analogsignal_ids:
                                #i is the sweepnumber
                                #print i,self.Currently_Used_Sweep_nb_for_Local_Average[i]
                                self.Currently_Used_Sweep_nb_for_Local_Average.append(i+n)#[i][n]=i
                            else:
                                #j is the analogsignal id
                                self.Currently_Used_Sweep_nb_for_Local_Average.append(j)#[i][n]=j
                            
                            self.Wid.canvas.axes.plot(Requete.timescale,eval("Displayed_"+str(i)),'k',alpha=0.3,picker=1)
                            self.Wid.Status.setText("It's an average of "+str(counter)+" Sweeps"+" at position "+str(Position)+
                                                    "<p>"+"Average A1 = "+str(self.Mean_Amplitude_1)+"\t Average C1 = "+str(self.Mean_Charge_1)+
                                                    "<p>"+"Average A2 = "+str(self.Mean_Amplitude_2)+"\t Average C2 = "+str(self.Mean_Charge_2)+
                                                    "<p>"+"Average A3 = "+str(self.Mean_Amplitude_3)+"\t Average C3 = "+str(self.Mean_Charge_3)+
                                                    "<p>"+"Sweep "+str(self.Currently_Used_Sweep_nb_for_Local_Average)+" were used")
                else:
                    self.Wid.Status.setText("It's an average of "+str(counter)+" Sweeps"+
                                                            "<p>"+"Average A1 = "+str(self.Mean_Amplitude_1)+"\t Average C1 = "+str(self.Mean_Charge_1)+
                                                            "<p>"+"Average A2 = "+str(self.Mean_Amplitude_2)+"\t Average C2 = "+str(self.Mean_Charge_2)+
                                                            "<p>"+"Average A3 = "+str(self.Mean_Amplitude_3)+"\t Average C3 = "+str(self.Mean_Charge_3)+
                                                            "<p>"+"Sweep "+str(self.List_of_Averaged_Sweeps)+" were used") 
                 
                
                print self.Currently_Used_Sweep_nb_for_Local_Average
                self.Wid.canvas.axes.plot(Requete.timescale,self.mean,picker=1)
                self.Wid.canvas.axes.plot(self.Base1_coord/Navigate.Points_by_ms,self.Base1,'r',linewidth=3)
                self.Wid.canvas.axes.plot(self.Peak1_coord/Navigate.Points_by_ms,self.Peak1,'r',linewidth=3)
                self.Wid.canvas.axes.plot(self.Base2_coord/Navigate.Points_by_ms,self.Base2,'r',linewidth=3)
                self.Wid.canvas.axes.plot(self.Peak2_coord/Navigate.Points_by_ms,self.Peak2,'r',linewidth=3)
                self.Wid.canvas.axes.plot(self.Base3_coord/Navigate.Points_by_ms,self.Base3,'r',linewidth=3)
                self.Wid.canvas.axes.plot(self.Peak3_coord/Navigate.Points_by_ms,self.Peak3,'r',linewidth=3)
                self.Wid.canvas.axes.set_xlabel("Time (ms)")
                self.Wid.canvas.axes.set_ylabel("Amplitude")
                
        if Rendering == True:     
            if QtCore.QObject().sender().__class__.__name__ == 'QCheckBox':
                self.Wid.canvas.draw()
            else:
                self.Wid.show()
                    
    
            Requete.Current_Sweep_Number=int(Main.Sweep_Number_Input_Field.text())  
        return self.Mean_Amplitude_1,self.Mean_Amplitude_2,self.Mean_Amplitude_3,self.Mean_Charge_1,self.Mean_Charge_2,self.Mean_Charge_3, self.mean, List_of_Ids

    def PeakDetection(self,v, delta, x = None):
        
        maxtab = []
        mintab = []

        if x is None:
            x = numpy.arange(len(v))
        
        v = numpy.asarray(v)
        
    
        mn, mx = numpy.Inf, numpy.Inf*-1
        mnpos, mxpos = numpy.NaN, numpy.NaN
        
        lookformax = True
        
        for i in numpy.arange(len(v)):
            this = v[i]
            if this > mx:
                mx = this
                mxpos = x[i]
            if this < mn:
                mn = this
                mnpos = x[i]
            
            if lookformax:
                if this < mx-delta:
                    maxtab.append((mxpos, mx))
                    mn = this
                    mnpos = x[i]
                    lookformax = False
            else:
                if this > mn+delta:
                    mintab.append((mnpos, mn))
                    mx = this
                    mxpos = x[i]
                    lookformax = True
    
        return numpy.array(maxtab), numpy.array(mintab)  

    def DetectSpikesOnLocalFile(self,Thr):

        Source = Requete.Analogsignal_ids
        Requete.Spiketrain_ids=numpy.copy(Requete.Analogsignal_ids)
        Requete.SpikeTrainfromLocal={}
        Requete.AmpSpikeTrainfromLocal={}
        
        counter=0
        for i in range(len(Source)):
            Main.progress.setMinimum(0)
            Main.progress.setMaximum(len(Source)-1)
            Main.progress.setValue(i)
            Requete.Current_Sweep_Number=i            
            Navigate.Load_This_Trace(i)     
            
            
            if i >= int(Main.From.text()) and i <= int(Main.To.text()) and Requete.tag["Selection"][i] == 1:

                Max,Min=self.PeakDetection(Navigate.si, Thr, x = Navigate.timescale) 
                Current_Spike_Times=[]
                Amplitude_At_Spike_Time=[]
                for event in Min:
                    Current_Spike_Times.append(event[0])
                    Amplitude_At_Spike_Time.append(event[1])
                    
                Requete.SpikeTrainfromLocal[str(i)]=Current_Spike_Times
                Requete.AmpSpikeTrainfromLocal[str(i)]=Amplitude_At_Spike_Time
                counter+=1
        return        
        

                

    def Count_All_Events(self):#,Rendering=True,Range=None,Silent=False):
        



        Source = Requete.Spiketrain_ids
        
        self.Events=[numpy.NaN]*len(Requete.Spiketrain_ids)
        self.Maximale_Frequency=[numpy.NaN]*len(Requete.Spiketrain_ids)

        
        counter=0

        for i in range(len(Source)):
            Main.progress.setMinimum(0)
            Main.progress.setMaximum(len(Source)-1)
            Main.progress.setValue(i)
            if Main.SQLTabWidget.currentIndex() == 2: # if Local file only
                Requete.Current_Sweep_Number=i            
            
            if i >= int(Main.From.text()) and i <= int(Main.To.text()) and Requete.tag["Selection"][i] == 1:
                
                sptr=SpikeTrain.load(Source[i],session=Requete.Global_Session)
                
                self.Events[i]=len(sptr._spike_times)
                temp=[]
                if len(sptr._spike_times)>1:
                    for i in range(len(sptr._spike_times)-1):
                        if sptr._spike_times[i+1]-sptr._spike_times[i]!=0: #Usually due to a bug with duplicate point
                            temp.append(sptr._spike_times[i+1]-sptr._spike_times[i])
                    self.Maximale_Frequency[i]=1/numpy.min(temp)
                elif len(sptr._spike_times) == 1:
                    self.Maximale_Frequency[i]=0
                elif len(sptr._spike_times) == 0:
                    self.Maximale_Frequency[i]=numpy.NaN

                    
                counter+=1
        return self.Events,self.Events,self.Events,self.Maximale_Frequency,self.Maximale_Frequency,self.Maximale_Frequency       
        
    def Count_Events(self):#,Rendering=True,Range=None,Silent=False):

        Bsl_bgn=float(Main.Baseline1_begin.text())/1000
        Bsl_end=float(Main.Baseline1_end.text())/1000
        Mes_bgn=float(Main.Peak1_begin.text())/1000
        Mes_end=float(Main.Peak1_end.text())/1000                              


        Source = Requete.Spiketrain_ids
        
        self.Events=[numpy.NaN]*len(Requete.Spiketrain_ids)
        self.Maximale_Frequency=[numpy.NaN]*len(Requete.Spiketrain_ids)

        
        counter=0

        for i in range(len(Source)):
            Main.progress.setMinimum(0)
            Main.progress.setMaximum(len(Source)-1)
            Main.progress.setValue(i)
            if Main.SQLTabWidget.currentIndex() == 2: # if Local file only
                Requete.Current_Sweep_Number=i            
            
            if i >= int(Main.From.text()) and i <= int(Main.To.text()) and Requete.tag["Selection"][i] == 1:
                
                if Main.SQLTabWidget.currentIndex() != 2:
                    sptr=SpikeTrain.load(Source[i],session=Requete.Global_Session)
                    #first we could calculate the baseline number of events, not done
                    subspikes=[]
                    #Second, we count the evnts in measurement range
                    for j in sptr._spike_times-sptr.t_start:
                        if j >Mes_bgn and j <Mes_end:
                            subspikes.append(j) 
                elif Main.SQLTabWidget.currentIndex() == 2:
                    sptr=Requete.SpikeTrainfromLocal[str(i)]
                    #first we could calculate the baseline number of events, not done
                    subspikes=[]
                    #Second, we count the evnts in measurement range
                    for j in sptr:
                        if j/1000. >Mes_bgn and j/1000. <Mes_end:
                            subspikes.append(j)                     
                self.Events[i]=len(subspikes)

                temp=[]
                if len(subspikes)>1:
                    for i in range(len(subspikes)-1):
                        if subspikes[i+1]-subspikes[i]!=0: #Usually due to a bug with duplicate point
                            temp.append(subspikes[i+1]-subspikes[i])
                    self.Maximale_Frequency[i]=1/numpy.min(temp)
                elif len(subspikes) == 1:
                    self.Maximale_Frequency[i]=0
                elif len(subspikes) == 0:
                    self.Maximale_Frequency[i]=numpy.NaN

                    
                counter+=1
        return self.Events,self.Events,self.Events,self.Maximale_Frequency,self.Maximale_Frequency,self.Maximale_Frequency   
        
        
    def Measure(self,Rendering=True,Measure_Filtered=False,Measure_All_from_Baseline1=False,Silent=False,All_from_Zero=False):
        
        """
        Mesure les amplitudes et la charge entre 
        -Baseline1 et Peak1
        -Baseline2 et Peak2
        -Baseline3 et Peak3
        
        Sachant que 
            Baseline1 = moyenne entre Analysis.Baseline1_begin et Analysis.Baseline1_end sur Analysis.Baseline1_size(en ms)*Navigate.Points_by_ms
        et que
            Baseline1_meth definit si c'est un maximum ou un minimum que l'on cherche (courant + ou -)
        enfin, selon si Main.Analyze_Filtered_Traces_Button est coché ou non, on analyse sur la trace brute ou sur la trace filtrée
        
        La fonction retourne 3 Listes pour les amplitudes:
        Analysis.Amplitudes_1, Analysis.Amplitudes_2, Analysis.Amplitudes_3 qui sont les liste des amplitudes 1,2 et 3 respectivement

        La fonction retourne 3 Listes pour les charges:
        Analysis.Charges_1, Analysis.Charges_2, Analysis.Charges_3 qui sont les liste des amplitudes 1,2 et 3 respectivement
        
        La fonction sort aussi 2*3 tables de valeurs et fait 2*3 plots
        Les points non tagguées sont des Nan
        
        if Rendering=False, theanalysis doesn't show the final figure and value tables

        """
        if Main.Measure_From_Zero_Button.checkState() == 2:
            All_from_Zero == True
        if All_from_Zero == True:
            Main.Remove_Leak_Button.setCheckState(2)   
            Measure_All_from_Baseline1 = False
        if Main.Remove_Leak_Button.checkState() == 2:
            if All_from_Zero == False:
                Main.Remove_Leak_Button.setCheckState(0)
            leaktemporaryremoved=True
        else:
            leaktemporaryremoved=False 


        if Main.Analyze_Filtered_Traces_Button.checkState() == 0:
            si = Navigate.si
        elif Main.Analyze_Filtered_Traces_Button.checkState() == 2 or Measure_Filtered == True:
            si = Navigate.Filtered_Signal  
            
       
        for n in range(Requete.NumberofChannels):    
            #On importe le signal
            self.Check_Measuring_Parameters_Validity()
            Ampvalues = range(6)
            Chargevalues = range(6)
            self.Amplitudes_1=range(len(Requete.Analogsignal_ids))
            self.Amplitudes_2=range(len(Requete.Analogsignal_ids))
            self.Amplitudes_3=range(len(Requete.Analogsignal_ids))
            self.Charges_1=range(len(Requete.Analogsignal_ids))
            self.Charges_2=range(len(Requete.Analogsignal_ids))
            self.Charges_3=range(len(Requete.Analogsignal_ids))
            compteur2=0
    
            listofmeth=     ["Baseline1_meth","Peak1_meth",
                             "Baseline2_meth","Peak2_meth",
                             "Baseline3_meth","Peak3_meth"]
            
            
            for i,j in enumerate(Requete.Analogsignal_ids):
                Main.progress.setMinimum(0)
                Main.progress.setMaximum(len(Requete.Analogsignal_ids)-1)
                Main.progress.setValue(compteur2)
                
                print compteur2*Requete.NumberofChannels+n
                if Requete.tag["Selection"][compteur2*Requete.NumberofChannels+n] == 1 and compteur2 >= int(Main.From.text()) and compteur2 <= int(Main.To.text()): #On n'analyse que les amplitudes sur les sweeps taggués
                    if Main.SQLTabWidget.currentIndex() == 2:
                        Requete.Current_Sweep_Number=i
                        Navigate.Load_This_Trace(i)
                    else:
                        Navigate.Load_This_Trace(j)
                    if Main.Analyze_Filtered_Traces_Button.checkState() == 0:
                        si = Navigate.si[n]
                    elif Main.Analyze_Filtered_Traces_Button.checkState() == 2:
                        si = Navigate.Filtered_Signal[n]                        
                    
                    compteur=0
                    
                    for loc in Main.listofcoord:
                        #loc[0] est le début du range
                        #loc[1] est la fin du range
                        #loc[2] est la taille du range qui sera utilisé pour le calcul de la moyenne
                        #aloc est la position du minimum
                        
                        bgn=str("Main."+str(loc[0])+".text()")
                        end=str("Main."+str(loc[1])+".text()")
                        size=str("Main."+str(loc[2])+".text()")
                        meth=str("Main."+str(listofmeth[compteur])+".currentText()")
                        
                        try:
                            if  eval(meth) == 'Max':
                                #if there is a bug here, it's because the preset parameters you used ware aclculated on a different samplig rate, and not corrected                        
                                aloc = numpy.argmax(si[int(float(eval(bgn))*Navigate.Points_by_ms):int(float(eval(end))*Navigate.Points_by_ms)])
                            elif eval(meth) == 'Min':
                                #if there is a bug here, it's because the preset parameters you used ware aclculated on a different samplig rate, and not corrected
                                aloc = numpy.argmin(si[int(float(eval(bgn))*Navigate.Points_by_ms):int(float(eval(end))*Navigate.Points_by_ms)])
                        except ValueError:
                            msgBox = QtGui.QMessageBox()
                            msgBox.setText(
                            """
                            <b>Range Error</b>
                            <p>You used measure parameters that are out of range, or
                            <p>You used measure parameters with a smaller timescale than the signal itself
                            """) 
                            msgBox.exec_() 
                            return                        
                        leftpnt = int(aloc-float(eval(size))*Navigate.Points_by_ms/2+float(eval(bgn))*Navigate.Points_by_ms)
                        
                        if leftpnt<0:
                            leftpnt=0
                            
                        if leftpnt<float(eval(bgn))*Navigate.Points_by_ms:
                            leftpnt=int(float(eval(bgn))*Navigate.Points_by_ms)
                            
                        rightpnt = int(aloc+float(eval(size))*Navigate.Points_by_ms/2+float(eval(bgn))*Navigate.Points_by_ms)
                        
                        if rightpnt>len(si):
                            rightpnt=len(si)
                            
                        if rightpnt>float(eval(end))*Navigate.Points_by_ms:
                            rightpnt=int(float(eval(end))*Navigate.Points_by_ms)
       
                        avalue = numpy.mean(si[leftpnt:rightpnt]) #a value est l'amplitude
                        Ampvalues[compteur]=avalue
                        compteur+=1
                                
                else:
                    for a in range(6):
                        Ampvalues[a]=numpy.NaN
                        Chargevalues[a]=numpy.NaN   
    
                     
                if Main.Measure_From_Baseline1_Button.checkState() == 0:
                    self.Amplitudes_1[compteur2]=(Ampvalues[1]-Ampvalues[0])
                    self.Amplitudes_2[compteur2]=(Ampvalues[3]-Ampvalues[2])
                    self.Amplitudes_3[compteur2]=(Ampvalues[5]-Ampvalues[4])
                    
    
                    self.baseline=numpy.zeros(int(len(self.Amplitudes_1)+2))
                    self.Charges_1[compteur2]=sum(si[int(float(Main.Peak1_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak1_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-Ampvalues[0]*float(len(si[int(float(Main.Peak1_begin.text())):int(float(Main.Peak1_end.text()))]))/1000
                    self.Charges_2[compteur2]=sum(si[int(float(Main.Peak2_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak2_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-Ampvalues[2]*float(len(si[int(float(Main.Peak2_begin.text())):int(float(Main.Peak2_end.text()))]))/1000
                    self.Charges_3[compteur2]=sum(si[int(float(Main.Peak3_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak3_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-Ampvalues[4]*float(len(si[int(float(Main.Peak3_begin.text())):int(float(Main.Peak3_end.text()))]))/1000                   
                    
                    
                elif Main.Measure_From_Baseline1_Button.checkState() == 2 or Measure_All_from_Baseline1 == True:
                    self.Amplitudes_1[compteur2]=(Ampvalues[1]-Ampvalues[0])
                    self.Amplitudes_2[compteur2]=(Ampvalues[3]-Ampvalues[0])
                    self.Amplitudes_3[compteur2]=(Ampvalues[5]-Ampvalues[0]) 
                    
                    self.baseline=numpy.zeros(int(len(self.Amplitudes_1)+2))
                    self.Charges_1[compteur2]=sum(si[int(float(Main.Peak1_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak1_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-Ampvalues[0]*float(len(si[int(float(Main.Peak1_begin.text())):int(float(Main.Peak1_end.text()))]))/1000
                    self.Charges_2[compteur2]=sum(si[int(float(Main.Peak2_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak2_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-Ampvalues[0]*float(len(si[int(float(Main.Peak2_begin.text())):int(float(Main.Peak2_end.text()))]))/1000
                    self.Charges_3[compteur2]=sum(si[int(float(Main.Peak3_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak3_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)-Ampvalues[0]*float(len(si[int(float(Main.Peak3_begin.text())):int(float(Main.Peak3_end.text()))]))/1000   
    
                elif All_from_Zero == True:
                    self.Amplitudes_1[compteur2]=Ampvalues[1]
                    self.Amplitudes_2[compteur2]=Ampvalues[3]
                    self.Amplitudes_3[compteur2]=Ampvalues[5]
                    
                    self.baseline=numpy.zeros(int(len(self.Amplitudes_1)+2))
                    self.Charges_1[compteur2]=sum(si[int(float(Main.Peak1_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak1_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)
                    self.Charges_2[compteur2]=sum(si[int(float(Main.Peak2_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak2_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000)
                    self.Charges_3[compteur2]=sum(si[int(float(Main.Peak3_begin.text())*Navigate.Points_by_ms):int(float(Main.Peak3_end.text())*Navigate.Points_by_ms)])/(Navigate.Points_by_ms*1000) 
        
    
                compteur2+=1
    
    
            if Rendering==True:
                
                #TODO: only show the 2nd round
                self.popupWidget = QtGui.QWidget()
                self.popupWidget.setMinimumSize(600,600) #definit la taille minimale du Widget (largeur, hauteur)          

                vbox = QtGui.QVBoxLayout()
                hbox = QtGui.QHBoxLayout()
       
                    #1 : Création des onglet; valeurs chiffrées
                self.ValueTab = QtGui.QTabWidget(self.popupWidget)
                self.ValueTab.setMaximumSize(400,1024)
    
                self.Amplitude_table = SpreadSheet(parent=self.ValueTab,Source=[self.Amplitudes_1,self.Amplitudes_2,self.Amplitudes_3],Labels=["Amp1","Amp2","Amp3"])
                self.Charge_table = SpreadSheet(parent=self.ValueTab,Source=[self.Charges_1,self.Charges_2,self.Charges_3],Labels=["Char1","Char2","Char3"])
                vbox.addWidget(self.ValueTab)
                hbox.addLayout(vbox)
                vbox = QtGui.QVBoxLayout()
                
                self.ValueTab.addTab(self.Amplitude_table,"Amplitudes")
                self.ValueTab.addTab(self.Charge_table,"Charges")
                
                    #2 : Création des onglet; Graphiques
                self.Graphtab = QtGui.QTabWidget(self.popupWidget)
                self.Wid=MyMplWidget()#self.Amplitude_graph)
                self.Wid2=MyMplWidget()#self.Charge_graph)
                self.Graphtab.addTab(self.Wid,"Amplitudes")
                self.Graphtab.addTab(self.Wid2,"Charges")
                
                vbox.addWidget(self.Graphtab)
                hbox.addStrut(50)
                hbox.addLayout(vbox)
                self.popupWidget.setLayout(hbox)
       
                self.Wid.canvas.axes.plot(self.baseline,'k--',)
                A1, = self.Wid.canvas.axes.plot(self.Amplitudes_1,'bo-',alpha=0.7)
                A2, = self.Wid.canvas.axes.plot(self.Amplitudes_2,'ro-',alpha=0.7)
                A3, = self.Wid.canvas.axes.plot(self.Amplitudes_3,'go-',alpha=0.7)
                l=self.Wid.canvas.axes.legend([A1, A2, A3], ["Amplitude 1", "Amplitude 2", "Amplitude 3"], loc='best',fancybox=True)
                l.get_frame().set_alpha(0.5)
                self.Wid.canvas.axes.set_xlabel("Sweep #")
                self.Wid.canvas.axes.set_ylabel("Amplitude (pA)")    
                
                self.Wid2.canvas.axes.plot(self.baseline,'k--',)
                C1, = self.Wid2.canvas.axes.plot(self.Charges_1,'bo-',alpha=0.7)
                C2, = self.Wid2.canvas.axes.plot(self.Charges_2,'ro-',alpha=0.7)
                C3, = self.Wid2.canvas.axes.plot(self.Charges_3,'go-',alpha=0.7)
                l=self.Wid2.canvas.axes.legend([C1, C2, C3], ["Charge 1", "Charge 2", "Charge 3"], loc='best',fancybox=True)
                l.get_frame().set_alpha(0.5)
                self.Wid2.canvas.axes.set_xlabel("Sweep #")
                self.Wid2.canvas.axes.set_ylabel("Charge (pC)")  
              
              
            self.popupWidget.show()       
            Infos.Add_Array(Arrays=[ "Analysis.Amplitudes_1",
                        "Analysis.Amplitudes_2",
                        "Analysis.Amplitudes_3",
                        "Analysis.Charges_1",
                        "Analysis.Charges_2",
                        "Analysis.Charges_3"])
     
    
    
    
            if leaktemporaryremoved == True and All_from_Zero == False:
                Main.Remove_Leak_Button.setCheckState(2) 
                
        return self.Amplitudes_1,self.Amplitudes_2,self.Amplitudes_3,self.Charges_1,self.Charges_2,self.Charges_3
        
        
        
    def Set_User_Parameters(self,name):
        
        #Index is the position corresponding to the wanted name
        index=Main.User_Defined_Measurement_Parameters.findText(name)
        
        if index != -1 :
            Main.User_Defined_Measurement_Parameters.setCurrentIndex(index)
            self.Load_User_Defined_Parameters(index,True)
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b> %s doesn't exist in Main.User_Defined_Measurement_Parameters
            """ % (name)) 
            msgBox.exec_() 
                     
        
        
        
    def Set_User_Defined_Measurement_Parameters_to_Zero(self):
        
        for i in range(12):
            Main.param_inf[i+10]=float(0.0)
        for i in range(6):
            Main.param_inf[i+22]=float(1.0)            
        Main.Create_Measure_Variables()  
        
        for a in Main.listofmeasurecoord:
            exec('Main.'+str(a)+'.setText("0.0")')
       
        for a in ["Baseline1_size","Peak1_size","Baseline2_size","Peak2_size","Baseline3_size","Peak3_size"]:
            exec('Main.'+a+'.setText("1.0")')
            
        for a in ["Baseline1_meth","Peak1_meth","Baseline2_meth","Peak2_meth","Baseline3_meth","Peak3_meth"]:
            exec('index=Main.'+a+'.findText("Min")') 
            exec('Main.'+a+'.setCurrentIndex(index)')                
            

        self.Load_User_Defined_Parameters(0)

    def Add_User_Defined_Measurement_Parameters(self):
        
        Wid=MyMplWidget()
        
        savename, ok = QtGui.QInputDialog.getText(Wid,'Input Dialog', 
            'Please enter parameters name')
        savename=str(savename)
        
        if ok:
            a=int(Main.User_Defined_Measurement_Parameters.count())
            Main.User_Defined_Measurement_Parameters.insertItem(a,savename)
            Main.User_Defined_Measurement_Parameters.setCurrentIndex(a)
            
            templist=[savename]
            for a in Main.listofmeasurecoord:
                exec('temp = Main.'+str(a)+'.text()')
                templist.append(str(temp))
            for a in ["Baseline1_size","Peak1_size","Baseline2_size","Peak2_size","Baseline3_size","Peak3_size"]:
                exec('temp = Main.'+str(a)+'.text()')                
                templist.append(str(temp))
            for a in ["Baseline1_meth","Peak1_meth","Baseline2_meth","Peak2_meth","Baseline3_meth","Peak3_meth"]:
                exec('temp =Main.'+a+'.currentText()') 
                templist.append(str(temp)) 
                

        Main.Analysis_Preferences.append(templist)
                
        self.Load_User_Defined_Parameters(0)
        
        
    def Remove_User_Defined_Measurement_Parameters(self):
        
        a=int(Main.User_Defined_Measurement_Parameters.count())
        Main.Analysis_Preferences.pop(int(Main.User_Defined_Measurement_Parameters.currentIndex()))
        Main.User_Defined_Measurement_Parameters.removeItem(Main.User_Defined_Measurement_Parameters.currentIndex())
        
        Main.User_Defined_Measurement_Parameters.setCurrentIndex(a-2)
        
        self.Load_User_Defined_Parameters(0)

    def Load_User_Defined_Parameters(self,index,External=False):

        #name of the loaded list: Main.Analysis_Preferences[int(Main.sender().currentIndex())][0]
        if External == False:
            for i in range(23):
                Main.param_inf[i+10]=Main.Analysis_Preferences[int(Main.User_Defined_Measurement_Parameters.currentIndex())][i+1]
                if i < 18:
                    Main.param_inf[i+10]=float(Main.param_inf[i+10])    
            Main.Create_Measure_Variables()
            
            compteur=0
            for a in Main.listofmeasurecoord:
                setnew = 'Main.'+str(a)+'.setText("'+str(Main.param_inf[compteur+10])+'")'
                exec(setnew)
                compteur+=1
            compteur=0    
            for a in ["Baseline1_size","Peak1_size","Baseline2_size","Peak2_size","Baseline3_size","Peak3_size"]:
                setnew = 'Main.'+str(a)+'.setText("'+str(Main.param_inf[compteur+22])+'")'
                exec(setnew)
                compteur+=1
            compteur=0    
            for a in ["Baseline1_meth","Peak1_meth","Baseline2_meth","Peak2_meth","Baseline3_meth","Peak3_meth"]:
                exec('index=Main.'+a+'.findText(str(Main.param_inf[compteur+28]))')
                #print 'internal',index,str(Main.param_inf[compteur+28])
                exec('Main.'+a+'.setCurrentIndex(index)')                 
                compteur+=1

                
        elif External == True:
            for i in range(23):
                Main.param_inf[i+10]=Main.Analysis_Preferences[int(Main.User_Defined_Measurement_Parameters.currentIndex())][i+1]
                #Main.param_inf[i+10]=Main.Analysis_Preferences[int(Main.User_Defined_Measurement_Parameters.count()-1)][i+1]
                if i < 18:
                    Main.param_inf[i+10]=float(Main.param_inf[i+10])                  
            Main.Create_Measure_Variables()
            
            compteur=0
            for a in Main.listofmeasurecoord:
                setnew = 'Main.'+str(a)+'.setText("'+str(Main.param_inf[compteur+10])+'")'
                exec(setnew)
                compteur+=1 
            compteur=0      
            for a in ["Baseline1_size","Peak1_size","Baseline2_size","Peak2_size","Baseline3_size","Peak3_size"]:
                setnew = 'Main.'+str(a)+'.setText("'+str(Main.param_inf[compteur+22])+'")'
                exec(setnew)
                compteur+=1 
            compteur=0    
            for a in ["Baseline1_meth","Peak1_meth","Baseline2_meth","Peak2_meth","Baseline3_meth","Peak3_meth"]:
                exec('index=Main.'+a+'.findText(str(Main.param_inf[compteur+28]))') 
                #print 'external',index,str(Main.param_inf[compteur+28])
                exec('Main.'+a+'.setCurrentIndex(index)')                 
                compteur+=1  
        
            

            
        self.Check_Measuring_Parameters_Validity()
        self.Save_User_Defined_Parameters()
        
    def Save_User_Defined_Parameters(self):
        
        print "-----------> user parameters valid and saved"
        parameters = open(Main.Analysis_Preferences_Path,'w')
        saving =''
        for i in Main.Analysis_Preferences:
            saving=saving+str(i)+"\n"
        parameters.write(saving)       
        parameters.close()
        
    
    def Check_Measuring_Parameters_Validity(self):
        
        """
        This function check that the point n+1 in measure paramteres is AFTER the point n.
        """
        
        previous_value=0 #c'est la position du point précédent dans le systeme de mesur, +1 point
        
        #le premier point doit être positif ou nul
        if Main.measurecoord["Baseline1_begin"] < 0:
            Main.measurecoord["Baseline1_begin"]=0
            Main.Baseline1_begin.setText("0")

        for a in Main.listofmeasurecoord:
            name = 'Main.measurecoord["'+str(a)+'"]' #c'est le nom de la variable Main.measurecoord["champs"]. eval(name) est sa valeur en ms
            cond="float(Main."+str(a)+".text())*Navigate.Points_by_ms" #c'est la valeur du pnt d'interet en points
            namevalue=eval(cond) #la coordonnée demandée est convertie en points

          
    
            if namevalue <= previous_value: #Le point n+1 doit etre >au point n, sinon on corrige
                print "cursor position correction!"
                namevalue=previous_value+1 #on corrige la valeur
                previous_value = namevalue #on redefinit previous value pour la boucle suivante
                convert=round(100*namevalue/Navigate.Points_by_ms)/100 #arrondi à 10µs près la valeur du point, pour la lisibilité
                setnew = 'Main.'+str(a)+'.setText("'+str(convert)+'")'
                setnew2='Main.measurecoord["'+str(a)+'"]=round(100*namevalue/Navigate.Points_by_ms)/100'
                exec(setnew)
                exec(setnew2)
    
            else:
                setnew2='Main.measurecoord["'+str(a)+'"]=round(100*namevalue/Navigate.Points_by_ms)/100'
                exec(setnew2)             
                previous_value = namevalue #on redefinit previous value pour la boucle suivante

        #same loop, + the "size" parameters
        liste=["Baseline1_begin","Baseline1_end","Peak1_begin","Peak1_end","Baseline2_begin","Baseline2_end","Peak2_begin","Peak2_end","Baseline3_begin","Baseline3_end","Peak3_begin","Peak3_end"]
        for i in range(len(liste)):
            #print Main.measurecoord[liste[i]]
            Main.param_inf[i+10]=Main.measurecoord[liste[i]]


    def Measure_On_Off_Activated(self):
        """
        Affiche les mesures sans changer de sweep
        """
        try:
            Navigate.Load_This_Trace(Requete.Analogsignal_ids[Requete.Current_Sweep_Number])
            Main.MainFigure.canvas.Update_Figure()
        except AttributeError: # if no Analogsignal_ids usually. for example if you haven't loaded anything yet
            pass
        


    def Measure_On_Off(self,channel=0):
        """
        Cette Fonction permet l'affichage des curseurs et de la charge sur la trace
        """
   
        if Main.Display_Measures_Button.checkState() == 2:
            if Main.Filtered_Display.checkState() == 0:
                si = Navigate.si[channel] 
            elif Main.Filtered_Display.checkState() == 2:
                si = Navigate.Filtered_Signal[channel]               

            self.Check_Measuring_Parameters_Validity()
            
            if Main.Display_Charge_Button.checkState() == 2:
                self.Charge_trace = numpy.array(si)
                self.Charge_trace[0:int(float(Main.Peak1_begin.text())*float(Navigate.Points_by_ms))]=numpy.NaN
                self.Charge_trace[int(float(Main.Peak1_end.text())*float(Navigate.Points_by_ms)):len(self.Charge_trace)]=numpy.NaN
           
            
            
            Ampvalues = range(6)
            self.Measurement_Interval = range(6)
            self.left = range(6)

            
            listofmeth=["Baseline1_meth","Peak1_meth",
                             "Baseline2_meth","Peak2_meth",
                             "Baseline3_meth","Peak3_meth"]

            compteur=0
            
            for loc in Main.listofcoord:

                
                #loc[0] est le début du range
                #loc[1] est la fin du range
                #loc[2] est la taille du range qui sera utilisé pour le calcul de la moyenne
                #aloc est la position du minimum
                
                bgn=str("Main."+str(loc[0])+".text()")
                end=str("Main."+str(loc[1])+".text()")
                size=str("Main."+str(loc[2])+".text()")
                meth=str("Main."+str(listofmeth[compteur])+".currentText()")
                                

                if  eval(meth) == 'Max':
                    try:
                        aloc = numpy.argmax(si[int(float(eval(bgn))*Navigate.Points_by_ms):int(float(eval(end))*Navigate.Points_by_ms)])
                    except ValueError:
                        msgBox = QtGui.QMessageBox()
                        msgBox.setText(
                        """
                        <b>Measure range is wrong</b>
                        <p>You can not have null intervall
                        """) 
                        msgBox.exec_()  
                        return
  
                        
                elif eval(meth) == 'Min':
                    try:
                        aloc = numpy.argmin(si[int(float(eval(bgn))*Navigate.Points_by_ms):int(float(eval(end))*Navigate.Points_by_ms)])
                    except ValueError:
                        msgBox = QtGui.QMessageBox()
                        msgBox.setText(
                        """
                        <b>Measure range is wrong</b>
                        <p>You can not have null intervall
                        """)      
                        msgBox.exec_()  
                        return
                            
                leftpnt = int(aloc-float(eval(size))*Navigate.Points_by_ms/2+float(eval(bgn))*Navigate.Points_by_ms)

                if leftpnt<0:
                    leftpnt=0
                if leftpnt<float(eval(bgn))*Navigate.Points_by_ms:
                    leftpnt=int(float(eval(bgn))*Navigate.Points_by_ms)                  

                rightpnt = int(aloc+float(eval(size))*Navigate.Points_by_ms/2+float(eval(bgn))*Navigate.Points_by_ms)
                if rightpnt>len(si):
                    rightpnt=len(si)
                if rightpnt>float(eval(end))*Navigate.Points_by_ms:
                    rightpnt=int(float(eval(end))*Navigate.Points_by_ms)

                avalue = numpy.mean(si[leftpnt:rightpnt])
                Ampvalues[compteur]=avalue
                self.Measurement_Interval[compteur]=rightpnt-leftpnt
                self.left[compteur]=leftpnt

                compteur+=1
                       
            if Main.Measure_From_Zero_Button.checkState() == 2:
                self.Amplitude_1=Ampvalues[1]
                self.Amplitude_2=Ampvalues[3]
                self.Amplitude_3=Ampvalues[5]
            elif Main.Measure_From_Baseline1_Button.checkState() == 2:  
                self.Amplitude_1=(Ampvalues[1]-Ampvalues[0])
                self.Amplitude_2=(Ampvalues[3]-Ampvalues[0])
                self.Amplitude_3=(Ampvalues[5]-Ampvalues[0])                
            else:    
                self.Amplitude_1=(Ampvalues[1]-Ampvalues[0])
                self.Amplitude_2=(Ampvalues[3]-Ampvalues[2])
                self.Amplitude_3=(Ampvalues[5]-Ampvalues[4])
                
            #Les listes des amplitudes 
            #print self.Amplitude_1
            #print self.Amplitude_2
            #print self.Amplitude_3
            #print self.Measurement_Interval  

            Info_Message="Amp1 = "+str(self.Amplitude_1)+"    Amp2 = "+str(self.Amplitude_2)+"    Amp3 = "+str(self.Amplitude_3)
            Main.status_text.setText(Info_Message)                    
    
            
            self.Base1 = numpy.ones(self.Measurement_Interval[0])*Ampvalues[0]
            self.Base1_coord = numpy.array(range(len(self.Base1)))+self.left[0]
            self.Peak1 = numpy.ones(self.Measurement_Interval[1])*Ampvalues[1]
            self.Peak1_coord = numpy.array(range(len(self.Peak1)))+self.left[1]
            self.Base2 = numpy.ones(self.Measurement_Interval[2])*Ampvalues[2]
            self.Base2_coord = numpy.array(range(len(self.Base2)))+self.left[2]
            self.Peak2 = numpy.ones(self.Measurement_Interval[3])*Ampvalues[3]
            self.Peak2_coord = numpy.array(range(len(self.Peak2)))+self.left[3]
            self.Base3 = numpy.ones(self.Measurement_Interval[4])*Ampvalues[4]
            self.Base3_coord = numpy.array(range(len(self.Base3)))+self.left[4]
            self.Peak3 = numpy.ones(self.Measurement_Interval[5])*Ampvalues[5]
            self.Peak3_coord = numpy.array(range(len(self.Peak3)))+self.left[5]
            
    def Raster_Plot(self,Bar_time=0.2,Bar_Width=0.1,Rendering=True,Source=None): 
        """
        This function display a Raster plot of all the spike times using "Source" list of spiketrain ids.
        Source must be a list. If None, Source is Requete.Spiketrain_ids
        The function returns the figure
        """
        if Source == None:
            Source = Requete.Spiketrain_ids
    
        if QtCore.QObject().sender() == Main.Rasterplot:
            Bar_time=float(Main.Raster_Start.text())
            Bar_Width=float(Main.Raster_Duration.text())

        self.Wid = MyMplWidget(title = 'Raster Plot')#, width=6, height=4)
        concatenatedEvents=[]
        
        if Main.SQLTabWidget.currentIndex() == 0 or Main.SQLTabWidget.currentIndex() == 1:
            sptr=SpikeTrain.load(Source[0],session=Requete.Global_Session)
            try:
                h=[0,sptr.t_stop-sptr.t_start,-1,len(Source)+1]
            except AttributeError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Raster Plot Error</b>
                <p>No Spiketrains in the selection
                """)                 
                msgBox.exec_()
                return
                h=[0,0,-1,len(Source)]
            self.Wid.canvas.axes.axis(h)
            counter=0
    
            if Source is Requete.Spiketrain_ids:        
                for i in range(len(Source)):
                    Main.progress.setMinimum(0)
                    Main.progress.setMaximum(len(Source)-1)
                    Main.progress.setValue(i)
                    
                    
                    if i >= int(Main.From.text()) and i <= int(Main.To.text()) and Requete.tag["Selection"][i] == 1:
                        
                        sptr=SpikeTrain.load(Source[i],session=Requete.Global_Session)
                        try:
                            for j in range(len(sptr._spike_times)):
                                sptr._spike_times[j]-=sptr.t_start
                                #print sptr.t_start, sptr._spike_times 
                                y=i*numpy.ones(len(sptr._spike_times))   
                                self.Wid.canvas.axes.plot(sptr._spike_times,y, 'k|')
                        
                        except ValueError:
                            print "ID ",Source[i]," passed"
                        counter+=1    
    
            else:
                for i in range(len(Source)):
                    sptr=SpikeTrain.load(Source[i],session=Requete.Global_Session)
         
                    for j in range(len(sptr._spike_times)):
                        sptr._spike_times[j]-=sptr.t_start
                        
                    y=i*numpy.ones(len(sptr._spike_times))   
                    self.Wid.canvas.axes.plot(sptr._spike_times,y, 'k|')
                    counter+=1   
                    
        elif Main.SQLTabWidget.currentIndex() == 2:
            h=[0,0,-1,len(Source)]
            self.Wid.canvas.axes.axis(h)
            counter=0
            
            for i in range(len(Source)):
                Main.progress.setMinimum(0)
                Main.progress.setMaximum(len(Source)-1)
                Main.progress.setValue(i)
                
                if i >= int(Main.From.text()) and i <= int(Main.To.text()) and Requete.tag["Selection"][i] == 1:
                    try:
                        sptr=Requete.SpikeTrainfromLocal[str(i)]
                        #for j in range(len(sptr)):
                        y=i*numpy.ones(len(sptr)) 
                        self.Wid.canvas.axes.plot(sptr,y, 'k|')
                        concatenatedEvents.extend(sptr)
                    except (ValueError,KeyError):
                        print "ID ",Source[i]," passed"
                    counter+=1              
                
            self.Wid.canvas.axes.set_xlabel("Time")
            self.Wid.canvas.axes.set_ylabel("Sweep Number")
            self.Wid.canvas.axes.invert_yaxis()
            self.Wid.canvas.axes.axvspan(Bar_time,Bar_time+Bar_Width,facecolor='b', alpha=0.3)
            self.Wid.canvas.axes.set_xbound(0.,1000.)
            self.Wid.canvas.axes.set_ybound(-1.,len(Source)+2.)
            self.Wid.canvas.axes.hist(concatenatedEvents, bins=100, range=(0.,1000.),histtype="stepfilled",alpha=0.6, normed=False)

            
        if Rendering == True:
            self.Wid.show()        

            Info_Message="It's a superposition of "+str(counter)+" sweeps"
            Main.status_text.setText(Info_Message)  

        return self.Wid  

    def Display_Events(self,leftsweep=5.,rightsweep=5.,Source=None,Baseline=None,Range=None,Rendering=True):
    	"""
    	This function is able to display at the same time 	-a raster plot and
    														-a superposition of all detected events
    	if Source is None (or Requete.Spiketrain_ids) all the tagging/Intervall system of SynaptiQs is used
    	leftsweep/rightsweep is the intervall used for display around _spiketime
    	Baseline is the time BEFORE the event used for offset substraction. if None, the whole AnalogSignal_id corresponding signal is used
    	Range is the range in second where the events are selected
    	to be solved : sometimes, some events are missed. their position is printed.
    	"""
    	from OpenElectrophy import AnalogSignal,SpikeTrain
    	from matplotlib import numpy
    
    
    	if Source== None:
    		Source=Requete.Spiketrain_ids
    
    	if Rendering == True:
    		self.Widget=QtGui.QWidget()
    		vbox=QtGui.QVBoxLayout()
    		Raster=self.Raster_Plot(Source=Source,Rendering=False,Bar_time=0.2,Bar_Width=0.2)
    		self.Wid = MyMplWidget(subplots=None)
    		self.Wid.canvas.axes = self.Wid.canvas.fig.add_subplot(111)
    
    	As=AnalogSignal.load(Requete.SpikeTrain_id_and_Corresponding_AnalogSignal_id_Dictionnary[Source[0]])
    	pnts_by_s=As.sampling_rate
    	counter=0
    
    	L=int(leftsweep*pnts_by_s)
    	H=int(rightsweep*pnts_by_s)
    	average_trace=numpy.zeros(L+H)
    	croped_axe=numpy.arange(float(leftsweep*-1),float(rightsweep),float(1/pnts_by_s))
    
    	if Range == None:
    		Range = [0.,len(As.signal)/pnts_by_s]
    	else:
    		if Rendering == True:
    			Raster.canvas.axes.axvspan(Range[0],Range[1],facecolor='r', alpha=0.3)
    
    
    
    	for j,i in enumerate(Source):
    		if (Source is Requete.Spiketrain_ids) and (j < int(Main.From.text())) or (j > int(Main.To.text())) or (Requete.tag["Selection"][j] == 0):
    			pass
    		else:
    			st=SpikeTrain.load(i)
    			As=AnalogSignal.load(Requete.SpikeTrain_id_and_Corresponding_AnalogSignal_id_Dictionnary[i])
    			pnts_by_s=As.sampling_rate
    
    			if Baseline == None:
    				baseline=numpy.mean(As.signal)
    			else: baseline=Baseline
    			
    			try:
    				for k in st._spike_times:
    					if (k-st.t_start > Range[0]) and (k-st.t_start < Range[1]):
    						lower=int((k-st.t_start)*pnts_by_s)-L
    						higher=int((k-st.t_start)*pnts_by_s)+H
    						event = As.signal[lower:higher]
    						
    						event=event-numpy.mean(event[(leftsweep-baseline)*pnts_by_s:leftsweep*pnts_by_s])
    
    						try:
    							average_trace+=event
    							counter+=1
    						except ValueError:
    							print 'error in spiketrain id %s, at %s ms' % (i,(k-st.t_start)*pnts_by_s/1000)
    
    						#print len(croped_axe), len(event)
    
    						if len(list(croped_axe))>len(list(event)):
    							croped_axe=list(croped_axe)
    							#print len(croped_axe), len(event)
    							#croped_axe.pop()
    						if Rendering == True :
    							if len(list(croped_axe)) != len(list(event)):
    								print j,i, 'passed'
    								pass
    							else:
    								self.Wid.canvas.axes.plot(croped_axe,event,color='k',alpha=0.15)
    			except ValueError:
    				pass
    						
    
    	average_trace/=counter
    	#HACK
    	Min=min([len(croped_axe),len(average_trace)])
    	croped_axe=croped_axe[:Min]
    	average_trace=average_trace[:Min]
    	print croped_axe,average_trace
    	if Rendering == True:
    		self.Wid.canvas.axes.plot(croped_axe,average_trace,color='red',alpha=1)
    		vbox.addWidget(Raster)
    		vbox.addWidget(self.Wid)
    		self.Widget.setLayout(vbox)
    		self.Widget.show()
    
    	return croped_axe,average_trace

    def Load_Tags(self):
        
        """
        This function allow you to load an alternative tag list directly from a file
        """

        path = QtGui.QFileDialog()
        path.setNameFilter("Tags Files (*.txt)")
        path.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        path.setFileMode(QtGui.QFileDialog.ExistingFiles)
        
        if (path.exec_()) :
            parameters = open(path.selectedFiles()[0])
            a=parameters.readlines()
            
            for i in range(len(a)):
                a[i].replace('\n','')
                Requete.tag["Selection"][i]=float(a[i])
            parameters.close()
            print "///////////////Tags Loaded from selected file"

    def Manip_Check_up(self,window=10,Leakbegin=0,Leakend=None):
        """
        This function allows a quick measurement of the signal, based on one point, on Tagged traces
        Filtering is ignored
        Leak is measured between Leakbegin (defaut is 0) and Leakend (defaut is sealtest time -1ms)
        Sealtest is the minimal value (on 1 point) between time and time +window (defaut is 10ms)
       
        """

        self.Seal_test=[numpy.NaN]*len(Requete.Analogsignal_ids)
        self.Leak=[numpy.NaN]*len(Requete.Analogsignal_ids)
        self.Noise_Level=[numpy.NaN]*len(Requete.Analogsignal_ids)
        self.Leak_Drop=[numpy.NaN]*len(Requete.Analogsignal_ids)
        
        self.Manip_Diagnosis_Widget = MyMplWidget(subplots=None,sharex=True, title = 'Manip Diagnosis')
        
        
        
        value, ok = QtGui.QInputDialog.getInt(Main.FilteringWidget, 'Input Dialog', 
            'Please Enter Seal Test time:')
        value=int(value)
        
       
        if Leakend==None:
            Leakend=value-1
            
        for i in range(len(Requete.Analogsignal_ids)):

            Main.progress.setMinimum(0)
            Main.progress.setMaximum(len(Requete.Analogsignal_ids)-1)
            Main.progress.setValue(i)  

            if Requete.tag["Selection"][i] == 1:
                sig = AnalogSignal().load(Requete.Analogsignal_ids[i],session=Requete.Global_Session)
                si = sig.signal
                self.Leak[i] = numpy.mean(si[float(Leakbegin)*Navigate.Points_by_ms:float(Leakend)*Navigate.Points_by_ms])
                self.Seal_test[i] = min(si[float(value)*Navigate.Points_by_ms:float(value+window)*Navigate.Points_by_ms])-self.Leak[i]
                self.Noise_Level[i] = numpy.std(si[float(Leakbegin)*Navigate.Points_by_ms:float(Leakend)*Navigate.Points_by_ms])
                self.Leak_Drop[i] = numpy.mean(si[float(Leakbegin)*Navigate.Points_by_ms:float(Leakend)*Navigate.Points_by_ms])-numpy.mean(si[((Leakbegin)*Navigate.Points_by_ms)*-1:-1])
                
        self.Seal_test=numpy.array(self.Seal_test)        
                
        self.Manip_Diagnosis_Widget.canvas.axes = self.Manip_Diagnosis_Widget.canvas.fig.add_subplot(511)
        self.Manip_Diagnosis_Widget.canvas.axes.plot(self.Seal_test,'ro-')
        self.Manip_Diagnosis_Widget.canvas.axes.set_ylabel("Seal Test (pA)")

        self.Manip_Diagnosis_Widget.canvas.axes = self.Manip_Diagnosis_Widget.canvas.fig.add_subplot(512)
        self.Manip_Diagnosis_Widget.canvas.axes.plot(-0.01/(self.Seal_test*0.000000000001),'go-')
        self.Manip_Diagnosis_Widget.canvas.axes.set_ylabel("Serie Resistance (MOhm)")

        self.Manip_Diagnosis_Widget.canvas.axes = self.Manip_Diagnosis_Widget.canvas.fig.add_subplot(513)
        self.Manip_Diagnosis_Widget.canvas.axes.plot(self.Leak,'bo-')
        self.Manip_Diagnosis_Widget.canvas.axes.set_ylabel("Leak (pA)")

        self.Manip_Diagnosis_Widget.canvas.axes = self.Manip_Diagnosis_Widget.canvas.fig.add_subplot(514)
        self.Manip_Diagnosis_Widget.canvas.axes.plot(self.Noise_Level,'ko-')
        self.Manip_Diagnosis_Widget.canvas.axes.set_ylabel("Noise_Level")

        self.Manip_Diagnosis_Widget.canvas.axes = self.Manip_Diagnosis_Widget.canvas.fig.add_subplot(515)
        self.Manip_Diagnosis_Widget.canvas.axes.plot(self.Leak_Drop,'co-')
        self.Manip_Diagnosis_Widget.canvas.axes.set_ylabel("Leak_Drop")

        self.Manip_Diagnosis_Widget.show()


    
    def fft_passband_filter(sig,
            f_low =0,f_high=1,
            axis = 0,
            ) :
        """
        pass band filter using fft for real 1D signal.
        sig : a numpy.array signal
        f_low : low pass niquist frequency (1 = samplin_rate/2)
        f_high : high  cut niquist frequency (1 = samplin_rate/2)
        """
        n = sig.shape[axis]
        N = int(2**(numpy.ceil(numpy.log(n)/numpy.log(2))))
        SIG = numpy.fft(sig,n = N , axis = axis)
        
        n_low = numpy.floor((N-1)*f_low/2)+1;
    
        fract_low = 1-((N-1)*f_low/2-numpy.floor((N-1)*f_low/2));
        n_high = numpy.floor((N-1)*f_high/2)+1;
        fract_high = 1-((N-1)*f_high/2-numpy.floor((N-1)*f_high/2));

        s = [ slice(None) for i in range(sig.ndim) ]
        if f_low >0 :
            s[axis] = 0
            SIG[s] = 0
            
            s[axis] = slice(1,n_low)
            SIG[ s ] = 0
            
            s[axis] = n_low
            SIG[s] *= fract_low
            
            s[axis] = -n_low
            SIG[s] *= fract_low
            
            if n_low !=1 :
                s[axis] = slice(-n_low+1, None)
                SIG[s] = 0
    
        if f_high <1 :
            s[axis] = n_high
            SIG[s] *= fract_high
            
            s[axis] = slice(n_high+1,-n_high)
            SIG[ s ] = 0
            
            s[axis] = -n_high
            SIG[s] *= fract_high
    
        s[axis] = slice(0,n)
        
        return numpy.real(numpy.ifft(SIG , axis=axis)[s])

        
    def Display_Infos(self):
        a='None'
        self.Tagged_Sweeps=0
        for i in range(len(Requete.Analogsignal_ids)):
            if Requete.tag["Selection"][i]==1:
                self.Tagged_Sweeps+=1
        msgBox = QtGui.QMessageBox()
        msgBox.setText(
        """
        <b>SQL Request</b>"""+
        "<p>"+str(Requete.query)+
        """<p><b>General Infos</b>"""+
        """<p>Number of Loaded Blocks : """+str(len(set(Requete.Block_ids)))+
        """<p>Number of Loaded Sweeps : """+str(len(Requete.Analogsignal_ids))+
        """<p>Number of Tagged Sweeps : """+str(self.Tagged_Sweeps)+
        """<p>Type of experiment : """+str(a)+
        """<p>Sampling rate : """+str(Navigate.Points_by_ms)+ """ points by ms (""" +str(Navigate.Points_by_ms)+"""kHz) , or 1 point = """+str(1/Navigate.Points_by_ms)+ """ ms"""+
        """<p><b>Mapping Infos (saved in the tag field)</b>"""
        """<p>Have a nice analysis...""")      
        msgBox.exec_()

