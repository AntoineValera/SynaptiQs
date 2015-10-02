# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:56:10 2013

@author: pyvan187
"""

import sys
from matplotlib import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import time
from PyQt4 import QtCore, QtGui
from OpenElectrophy import SpikeTrain





class MyMplCanvas(FigureCanvasQTAgg): 
    """
    Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).
    Ce widget permet d'afficher n'importe quelle Figure.
    Il est parametrable, et vient avec une barre
    
    """
    def __init__(self, parent=None, width = 5, height = 5, dpi = 100, sharex = None, sharey = None, parameters=None,subplots=None ):
        self.__name__="MyMplCanvas"
        self.fig = Figure(figsize = (width, height), dpi=dpi, facecolor ='white')
        
        if subplots != None:
            self.axes = self.fig.add_subplot(subplots, sharex = sharex, sharey = sharey)
            #self.fig.subplots_adjust(left=0.15, bottom=0.15, right=0.85, top=0.85)
            self.xtitle="x-Axis"
            self.ytitle="y-Axis"
            self.PlotTitle = "Plot"
            self.grid_status = True
            self.xaxis_style = 'linear'
            self.yaxis_style = 'linear'
            #self.fig.tight_layout()
            self.format_labels()
        
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(self,
                    QtGui.QSizePolicy.Expanding,
                    QtGui.QSizePolicy.Expanding)
        
        FigureCanvasQTAgg.updateGeometry(self)
                
        QtCore.QObject.connect(Main.ModifySpikes, QtCore.SIGNAL("stateChanged(int)"), self.Add_or_Remove_Spikes)
   

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
                    
            
    def format_labels(self):

        self.axes.set_title(self.PlotTitle)
        self.axes.title.set_fontsize(10)
        self.axes.set_xlabel(self.xtitle, fontsize = 10)
        self.axes.set_ylabel(self.ytitle, fontsize = 10)
        labels_x = self.axes.get_xticklabels()
        labels_y = self.axes.get_yticklabels()

        for xlabel in labels_x:
                xlabel.set_fontsize(8)
        for ylabel in labels_y:
                ylabel.set_fontsize(8)
                ylabel.set_color('k')



#    def resizeEvent( self, event ):
#        if DEBUG: print 'resize (%d x %d)' % (event.size().width(), event.size().height())
#        w = event.size().width()
#        h = event.size().height()
#        if DEBUG: print "FigureCanvasQtAgg.resizeEvent(", w, ",", h, ")"
#        dpival = self.figure.dpi
#        winch = w/dpival
#        hinch = h/dpival
#        self.figure.set_size_inches( winch, hinch )
#        self.draw()
#        self.update()
#        QtGui.QWidget.resizeEvent(self, event)
#  
#    def sizeHint( self ):
#        w, h = self.get_width_height()
#        return QtCore.QSize( w, h )
#  
#    def minumumSizeHint( self ):
#        return QtCore.QSize( 10, 10 )
##    def minimumSizeHint(self):
##            return QtCore.QSize(10, 10)
            
    def Clicked_Object(self,event):
        
        if self.Object_Selection_Mode == 'Coordinates': 
            self.already_displayed = False
            self.mpl_connect('button_press_event', self.Return_Coordinates)
        elif self.Object_Selection_Mode == 'Time':
            self.cid = self.mpl_connect('button_press_event', self.Return_Time_of_Click)  
        elif self.Object_Selection_Mode == 'Trace':
            self.already_clicked = False
            self.mpl_connect('button_press_event', self.Focus_on_Clicked_Sweep)

#            pass
        
    def Return_Coordinates(self,event):
        #print event,event.xdata,event.ydata
        
        if self.already_displayed == False:
        
            #correction=1./float(Mapping.Current_Map.Stim_Resolution.text())  #so the clicked coordinate, in microns, select the coordinate in pixels
            correction = 1./float(Mapping.CM.Scaling_Factor)
            x = (event.xdata*correction, event.ydata*correction)
            sys.stdout.flush()
            try:
                q = Mapping.CM.Sorted_X_and_Y_Coordinates #The list of avaible coordinates
            except IOError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Mapping Error</b>
                <p>Mapping returned no Data, Please re-process
                """)      
                msgBox.exec_()     
                
            #Here we find the closest point
            t = []
            for item in q:
                a = abs(item[0]-x[0])
                b = abs(item[1]-x[1])
                avg = (a + b)/2.0
                t.append((avg, item))
             
            #print min(t)     # (17.5, (200, 500))
            a=min(t)[1]  # (200, 500)
            
            self.already_displayed = True
            
            Mapping.One_Stim_Average(X=a[0],Y=a[1])
        
        else:
            print 'This point was Already displayed'
            
            
    def Add_or_Remove_Spikes(self): 
        
        if Main.ModifySpikes.checkState() == 2:
            print 'Modify SpikeTimes ON'
            Main.MainFigure.canvas.Object_Selection_Mode = 'Time'
        elif Main.ModifySpikes.checkState() == 0:
            print 'Modify SpikeTimes OFF'
            Main.MainFigure.canvas.Object_Selection_Mode = 'Trace'
            
    def Return_Time_of_Click(self,event):
        """
        x[0] est la position exacte du clic
        closest est le spike le plus proche
        """
        #TODO : Put Analysis.Use_t_Start in a menu somewhere
        Analysis.Use_t_Start=False
        
        def find_nearest_index(array,value):
            return (numpy.abs(array-value)).argmin()
        def find_nearest_value(array,value):
            return numpy.abs(array-value).min() 


        if Main.ModifySpikes.checkState() == 2:
            xclick = event.xdata
            
            #self.flush_events()
            q=list(Requete.Current_Spike_Times)
            tstart=Requete.Spiketrain_t_start[0]
            f = SpikeTrain().load(Requete.Spiketrain_ids[Requete.Current_Sweep_Number])
            if event.button==1:
                if Analysis.Use_t_Start == True:
                    if xclick+tstart not in q:
                        q.append(xclick+tstart)
                        q.sort()
                        f._spike_times = numpy.array(q)/1000.+f.t_start
                        f.save()
                else:
                    if xclick not in q:
                        q.append(xclick)
                        q.sort()
                        f._spike_times = numpy.array(q)/1000.
                        f.save()     
            
            if event.button==3:
                if Analysis.Use_t_Start == True:
                    if len(q) == 0:
                        print "can't remove spike, the list is empty"
                        return
                    ind=find_nearest_index(q,xclick)
    
                    q.pop(ind)
                    f._spike_times = numpy.array(q)/1000.+f.t_start
                    f.save()  
                    
                else:
                    if len(q) == 0:
                        print "can't remove spike, the list is empty"
                        return
                    ind=find_nearest_index(q,xclick)
    
                    q.pop(ind)
                    f._spike_times = numpy.array(q)/1000.
                    f.save() 
            
            if Analysis.Use_t_Start == True: 
                Requete.Current_Spike_Times=(f._spike_times-f.t_start)*1000
            else:
                Requete.Current_Spike_Times=(f._spike_times)*1000.
            Requete.Amplitude_At_Spike_Time=numpy.ones(len(Requete.Current_Spike_Times))
            for i in range(len(Requete.Current_Spike_Times)):
                Requete.Amplitude_At_Spike_Time[i]=Navigate.si[Requete.Current_Spike_Times[i]/1000.*Requete.Analogsignal_sampling_rate[Requete.Current_Sweep_Number]]    
            self.Update_Figure()

        self.mpl_disconnect(self.cid)
          

        
    def Focus_on_Clicked_Sweep(self,event):
        
        if self.already_clicked == False:     
    
            x = (event.xdata, event.ydata)
            #print 'clicked point', (event.xdata, event.ydata)
            
            try:
                self.LowX=Analysis.Wid.canvas.axes.get_xbound()[0]
                self.HighX=Analysis.Wid.canvas.axes.get_xbound()[1]
                self.LowY=Analysis.Wid.canvas.axes.get_ybound()[0]
                self.HighY=Analysis.Wid.canvas.axes.get_ybound()[1]                
                
                
                
                
                q = Analysis.Currently_Used_Sweep_nb_for_Local_Average
                t = []
                
                Analysis.Wid.canvas.axes.clear()
                
                #this is very slow if there are a lot of superimposed traces
                for i in q:
    
                    Navigate.Load_This_Trace(Requete.Analogsignal_ids[i])
#                    if Main.Analyze_Filtered_Traces_Button.checkState() == 0:
                    si = Navigate.si
#                    elif Main.Analyze_Filtered_Traces_Button.checkState() == 2:
#                        si = Navigate.Filtered_Signal                 
                    Analysis.Wid.canvas.axes.plot(Requete.timescale,si,'grey',alpha=0.3,picker=1)
                    MinimalY = abs(si[event.xdata*Navigate.Points_by_ms]-x[1])
                    t.append((MinimalY,i))
                    
                
                Navigate.Load_This_Trace(Requete.Analogsignal_ids[min(t)[1]])
                
                if Main.Analyze_Filtered_Traces_Button.checkState() == 0:
                    si = Navigate.si
                elif Main.Analyze_Filtered_Traces_Button.checkState() == 2:
                    si = Navigate.Filtered_Signal   
                    
                self.Current_Selected_Id = min(t)[1]
                
                print "Selected Sweep is Sweep number ",self.Current_Selected_Id
                
                Navigate.Load_This_Sweep_Number(self.Current_Selected_Id)
                
                Analysis.Wid.canvas.axes.plot(Requete.timescale,si,'r',picker=1)            
                Analysis.Wid.canvas.axes.plot(Requete.timescale,Analysis.mean,'b',picker=1)
                Analysis.Wid.canvas.axes.set_xbound(self.LowX,self.HighX)
                Analysis.Wid.canvas.axes.set_ybound(self.LowY,self.HighY)            
                
                self.draw()
                self.already_clicked = True
              
            except AttributeError:
                print "You must superpose data to select a trace"

        else:
            print "already clicked"

    def Update_Superimpose(self):
        """
        If you click on the "superimpose" button in the Widget
        """
        
        if self.Superimpose_Used_Traces_Button.checkState()==0:
            
            self.Object_Selection_Mode = None
            Main.Superimpose_Used_Traces=False
            Analysis.Measure_on_Average(Display_Superimposed_Traces = False , List_of_Ids = None)
            
        elif self.Superimpose_Used_Traces_Button.checkState()==2:
            
            self.Object_Selection_Mode = 'Trace'
            Main.Superimpose_Used_Traces=True
            Analysis.Measure_on_Average(Display_Superimposed_Traces = True, List_of_Ids = None)
        

       
    def Compute_Initial_Figure(self):
        """
        This only display an initial figure
        """
        #self.axes.addsubplot(112)
        self.axes = self.fig.add_subplot(1,1,1)
        self.axes.plot(range(1000), range(1000),  'r')
        self.axes.plot(range(1000), numpy.arange(1000)*-1+1000,  'r')
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Amplitude")
        
        #self.show()

    def Update_Figure(self):
        """
        This function Update the displayed figure
        """
        
        Color_of_Standard_Trace=Navigate.Color_of_Standard_Trace
        Color_of_Filtered_Traces=Navigate.Color_of_Filtered_Traces
        Main.MainFigure.canvas.Object_Selection_Mode = None #just in case there is a bug somewhere
        
        tot=len(list(set(Requete.Analogsignal_name)))
        
        self.axes = Main.MainFigure.canvas.fig.add_subplot(tot,1,1)
       
       
       
        self.LowX=self.axes.get_xbound()[0]
        self.HighX=self.axes.get_xbound()[1]
        self.LowY=self.axes.get_ybound()[0]
        self.HighY=self.axes.get_ybound()[1]
            
          
        if Main.Superimposetraces.checkState() == 0:
            self.axes.clear()
            
        if Main.Measure_From_Zero_Button.checkState() == 2:
            Main.Remove_Leak_Button.setCheckState(2) 
            
        if Main.Remove_Leak_Button.checkState() == 2: #it's a line at 0
            self.axes.plot(Requete.timescale,numpy.zeros(int(len(Requete.timescale))),'r--',picker=0)
            
        if Main.RAW_Display.checkState() == 2:
            try:
                self.axes.plot(Requete.timescale,Navigate.si,Color_of_Standard_Trace,picker=1)
            except ValueError:
                print len(Requete.timescale),len(Navigate.si)
                print "Requete.timescale and Navigate.si do not have the same number of points, loading skipped"
                return
            
        if Main.Filtered_Display.checkState() == 2 or Main.Median_Filtered_Display.checkState() == 2:
            self.axes.plot(Requete.timescale,Navigate.Filtered_Signal,Color_of_Filtered_Traces,picker=1)
        else:
            Main.RAW_Display.setCheckState(2)
            try:
                self.axes.plot(Requete.timescale,Navigate.si,Color_of_Standard_Trace,picker=1)
            except ValueError:
                print len(Requete.timescale),len(Navigate.si)
                print "Caution, the timescale is causing some issues..."
            except AttributeError:
                pass

        self.axes.set_xlabel("Time (ms)")
        self.axes.set_ylabel("Amplitude (pA)")

        if Main.Display_Charge_Button.checkState() == 2 and Main.Display_Measures_Button.checkState() == 0:
           Main.Display_Measures_Button.setCheckState(2)
           
        if Main.Display_Measures_Button.checkState() == 2:
            Analysis.Measure_On_Off()
            self.axes.plot(Analysis.Base1_coord/Navigate.Points_by_ms,Analysis.Base1,'r',linewidth=3)
            self.axes.plot(Analysis.Peak1_coord/Navigate.Points_by_ms,Analysis.Peak1,'r',linewidth=3)
            self.axes.plot(Analysis.Base2_coord/Navigate.Points_by_ms,Analysis.Base2,'r',linewidth=3)
            self.axes.plot(Analysis.Peak2_coord/Navigate.Points_by_ms,Analysis.Peak2,'r',linewidth=3)
            self.axes.plot(Analysis.Base3_coord/Navigate.Points_by_ms,Analysis.Base3,'r',linewidth=3)
            self.axes.plot(Analysis.Peak3_coord/Navigate.Points_by_ms,Analysis.Peak3,'r',linewidth=3)
       
        if Main.Display_Charge_Button.checkState() == 2:
            if Main.Measure_From_Zero_Button.checkState() == 2:
                if Mapping.CM.Types_of_Events_to_Measure == 'Negative':
                    self.axes.fill_between(Requete.timescale,Analysis.Charge_trace,0.,where=0.>Analysis.Charge_trace,alpha=0.3)
                elif Mapping.CM.Types_of_Events_to_Measure == 'Positive':
                    self.axes.fill_between(Requete.timescale,Analysis.Charge_trace,0.,where=0.<Analysis.Charge_trace,alpha=0.3)                    
            else:
                if Mapping.CM.Types_of_Events_to_Measure == 'Negative':
                    self.axes.fill_between(Requete.timescale,Analysis.Charge_trace,Analysis.Base1[0],where=Analysis.Base1[0]>Analysis.Charge_trace,alpha=0.3)
                elif Mapping.CM.Types_of_Events_to_Measure == 'Positive':
                    self.axes.fill_between(Requete.timescale,Analysis.Charge_trace,Analysis.Base1[0],where=Analysis.Base1[0]<Analysis.Charge_trace,alpha=0.3)

        if Main.Display_Spikes_Button.checkState() == 2:
            try:
                #print Requete.Current_Spike_Times
                #print Requete.Amplitude_At_Spike_Time
                self.axes.plot(Requete.Current_Spike_Times,Requete.Amplitude_At_Spike_Time,'ro',linewidth=10)
            except:
                Requete.Current_Spike_Times=[]
                print "No spikes to plot here"
        elif Main.Display_Spikes_Button.checkState() == 0:
            Requete.Current_Spike_Times=[]
        else:
            pass
            
        if Main.Autoscale.checkState() == 0:            
            self.axes.set_xbound(self.LowX,self.HighX)
            self.axes.set_ybound(self.LowY,self.HighY)
        elif Main.Autoscale.checkState() == 2:
            self.axes.set_autoscale_on(True)  

        self.draw() 