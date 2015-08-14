# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:32:47 2013

@author: Antoine Valera
"""

from PyQt4 import QtCore, QtGui
from matplotlib import numpy,pyplot  
      
class Histogram(object):
    def __init__(self):
        self.__name__='Histogram'
 
        
    def Manager(self):
        
        try:
            self.Wid = QtGui.QWidget()
            self.Wid.setMinimumSize(900,500)
            self.Wid.setWindowTitle("Histogram Tools") 
            
            self.hbox=QtGui.QHBoxLayout()        
            
            self.Hist_Widget = QtGui.QWidget()
            self.hbox.addWidget(self.Hist_Widget)
            
            
            self.vbox=QtGui.QVBoxLayout()
        
            
            self.Source = QtGui.QComboBox(self.Hist_Widget)
            a,b,c,d=Infos.List_All_Globals(option="numericalonly")
            self.Source.addItems(a)
            self.Source.addItems(b)
            self.Source_Label = QtGui.QLabel(self.Hist_Widget)
            self.Source_Label.setText('Source')
            
            self.Min = QtGui.QLineEdit(self.Hist_Widget)
            self.Min.setText(str(min(eval(self.Source.currentText()))))        
            self.Min_Label = QtGui.QLabel(self.Hist_Widget)
            self.Min_Label.setText('Minimum')
            
            self.Max = QtGui.QLineEdit(self.Hist_Widget)
            self.Max.setText(str(max(eval(self.Source.currentText()))))          
            self.Max_Label = QtGui.QLabel(self.Hist_Widget)
            self.Max_Label.setText('Maximum')
            
            self.N = QtGui.QLineEdit(self.Hist_Widget)
            self.N.setText(str(min(eval((self.Source.currentText()))-min(eval(self.Source.currentText())))/10))          
            self.N_Label = QtGui.QLabel(self.Hist_Widget)
            self.N_Label.setText('Number of Bins')
            
            self.Size = QtGui.QLineEdit(self.Hist_Widget)
            self.Size.setText('10')         
            self.Size_Label = QtGui.QLabel(self.Hist_Widget)
            self.Size_Label.setText('Bin Size')
            
            self.Destination = QtGui.QLineEdit(self.Hist_Widget)
            self.Destination.setText('self.hist') 
            self.Destination_Label = QtGui.QLabel(self.Hist_Widget)
            self.Destination_Label.setText('Destination Wave')
            
            self.SendtoFit = QtGui.QPushButton(self.Hist_Widget)
            self.SendtoFit.setText('Send to Fitting Module') 
         
        
            self.vbox.addWidget(self.Source_Label)
            self.vbox.addWidget(self.Source)
            self.vbox.addWidget(self.Min_Label)
            self.vbox.addWidget(self.Min)
            self.vbox.addWidget(self.Max_Label)
            self.vbox.addWidget(self.Max)
            self.vbox.addWidget(self.N_Label)
            self.vbox.addWidget(self.N)
            self.vbox.addWidget(self.Size_Label)
            self.vbox.addWidget(self.Size)
            self.vbox.addWidget(self.Destination_Label)
            self.vbox.addWidget(self.Destination)
            self.vbox.addWidget(self.SendtoFit)
        
            self.hbox.addLayout(self.vbox)
            
            self.Show_Hist = MyMplWidget()
            self.Show_Hist.setMinimumSize(600,400)
            self.Show_Hist.setWindowTitle("Display")
        
            self.hbox.addWidget(self.Show_Hist)
            
            self.Wid.setLayout(self.hbox)
        
        
            QtCore.QObject.connect(self.Source, QtCore.SIGNAL('activated(int)'),self.AutoAdjust)
            QtCore.QObject.connect(self.Min, QtCore.SIGNAL('editingFinished()'),self.adjust)
            QtCore.QObject.connect(self.Max, QtCore.SIGNAL('editingFinished()'),self.adjust)
            QtCore.QObject.connect(self.N, QtCore.SIGNAL('editingFinished()'),self.adjust)
            QtCore.QObject.connect(self.Size, QtCore.SIGNAL('editingFinished()'),self.adjust)
            QtCore.QObject.connect(self.Destination, QtCore.SIGNAL('editingFinished()'),self.adjust)
            QtCore.QObject.connect(self.SendtoFit, QtCore.SIGNAL('clicked()'),Fitting.FittingWindowInput)
            
            self.Wid.show()
            
            self.adjust()
        except SyntaxError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>No numerical Array yet</b>
            <p>Load some numerical data first
            """)
            msgBox.exec_()



    def AutoAdjust(self):
        Min=min(eval(self.Source.currentText()))
        Max=max(eval(self.Source.currentText()))
        InitialN=10
        
        self.Min.setText(str(Min))        
        self.Max.setText(str(Max))          
        self.N.setText(str(InitialN))    
        self.AutoAdjust = True
        self.adjust()


    
    def adjust(self):

        Size=float(self.Size.text())
        N=float(self.N.text())
        Min=float(self.Min.text())
        Max=float(self.Max.text())
        
        
            
        
        if self.Wid.sender() == self.N:
            Size=(Max-Min)/N
            self.Size.setText(str(Size))
        elif self.Wid.sender() == self.Size:
            N=(Max-Min)/Size
            self.N.setText(str(N))
        elif self.AutoAdjust == True:
            Size=(Max-Min)/N
            self.Size.setText(str(Size))
            self.AutoAdjust=False
        
        if N > 10000:
            value,ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'Warning', 
            """The number of bin is very high and may slow down the computer. Please confirm the number of bins""")
            N=value
            Size=(Max-Min)/float(N)
            self.N.setText(str(N))
            self.Size.setText(str(Size))
           
            
            
        
        self.Process(Source=self.Source.currentText(),Min=Min,Max=Max,N=N,Size=Size,Destination='hist',Internal=True)

            
            
        
    
    def Process(self,Source,Min,Max,N,Size,Destination,Internal=False,Rendering=True):
        """
        display the histogram
        """

        #NaNs must be removed before histogram
        #Source = Source[~numpy.isnan(Source)]
   
        #Making the histogram
        if Internal == True:
            self.Show_Hist.canvas.axes.clear()
            self.n, self.bins, patches = self.Show_Hist.canvas.axes.hist(eval(str(Source)),bins=numpy.arange(Min,Max+Size,Size), facecolor='green', alpha=0.5)
            self.bin_centres = (self.bins[:-1] + self.bins[1:])/2
            figure=None
            self.Show_Hist.canvas.draw()
            
        else:
            figure=pyplot.figure()
            self.n, self.bins, patches = pyplot.hist(eval(str(Source)),bins=numpy.arange(Min,Max+Size,Size), facecolor='green', alpha=0.5)
            self.bin_centres = (self.bins[:-1] + self.bins[1:])/2      
            if Rendering == True:
                pyplot.show()

            Infos.Add_Array(Arrays=["Histogram.n",
                                   "Histogram.bin_centres"])
     
        #setattr(self,Destination,self.n)
        return self.n,self.bins,self.bin_centres,figure