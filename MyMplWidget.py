# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:53:57 2013

@author: pyvan187
"""

from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg,NavigationToolbar2QTAgg
#from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as 
from matplotlib import pyplot

class MyMplWidget(QtGui.QWidget,QtGui.QLayout):
    """
    Widget Container for every type of figure
    It allows easier Navigation than default one
    Use should be like IgorPro
    
    The Widget contains a MyMplCanvas Figure
    """
    def __init__(self, parent = None, subplots = 111 , sharex = None, sharey = None, title = 'No Title' , No_Toolbar = False):
        self.__name__="MyMplWidget"  

        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle(title) 
        self.canvas = MyMplCanvas(subplots=subplots,sharex=sharex,sharey=sharey)
        
        self.canvas.Object_Selection_Mode = None
        self.toolbar = NavigationToolbar2QTAgg(self.canvas, self.canvas)
        self.toolbar.setMinimumSize(300,30) #du coup la figure aura aussi cette taille minimum

        self.Status = QtGui.QLabel(self.canvas)
        self.Status.setMinimumSize(300,30) 
        
        if No_Toolbar == True:
            self.toolbar.hide()
        
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.toolbar)#pour que la toolbar soit en bas
        self.vbox.addWidget(self.Status)#pour que la toolbar soit en bas
        self.setLayout(self.vbox)
        

        ##########################
        self.hZoom = QtGui.QAction("Zoom",  self)
        self.hZoom.setShortcut("CTRL+Z")
        self.addAction(self.hZoom)
        QtCore.QObject.connect(self.hZoom,QtCore.SIGNAL("triggered()"), self.ZoomToggle)
        
        self.untag = QtGui.QAction("Untag",  self)
        self.untag.setShortcut("CTRL+Del")
        self.addAction(self.untag)
        QtCore.QObject.connect(self.untag,QtCore.SIGNAL("triggered()"), self.Untag_Selected_Sweep)   
         
        self.actionAutoScale = QtGui.QAction("AutoScale",  self)#self.MainWindow)
        self.actionAutoScale.setShortcut("Ctrl+A")
        self.addAction(self.actionAutoScale)
        QtCore.QObject.connect(self.actionAutoScale,QtCore.SIGNAL("triggered()"), self.autoscale_plot)
        
        self.canvas.mpl_connect('button_press_event', self.canvas.Clicked_Object) 
        
        self.print_button = QtGui.QPushButton()
        self.print_button.setText('Print Figure')
        self.print_button.setToolTip("Print the figure")
        self.toolbar.addWidget(self.print_button)
        self.connect(self.print_button, QtCore.SIGNAL('clicked()'), self.Print) 
        
        try:
            QtCore.QObject.connect(Main.Autoscale, QtCore.SIGNAL("stateChanged()"),self.canvas.Update_Figure)
        except:
            pass

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
    def Untag_Selected_Sweep(self):
        
        """
        When a trace is displayed, if my.Object_Selection_Mode == 'Trace', then you are allowed to Untag it 
        """
        
        if self.canvas.Object_Selection_Mode == 'Trace':
            
            Requete.tag["Selection"][Analysis.Wid.canvas.Current_Selected_Id]=0
            print "Sweep Number "+str(Analysis.Wid.canvas.Current_Selected_Id)+" was Untagged"
            
            
            #event.xdata=0
            #event.ydata=0
            #Analysis.Wid.canvas.Focus_on_Clicked_Sweep(event)
            
            self.canvas.Update_Superimpose()


    def ZoomToggle(self):
        self.canvas.Object_Selection_Mode = None
        Main.ModifySpikes.setCheckState(0)
        self.toolbar.zoom()
        
    def autoscale_plot(self):
        self.toolbar.home()

    def Print(self):
        
        
        printer = QtGui.QPrinter()
        printer.setFullPage(True)
        printer.Landscape
        printer.A4
        printer.HighResolution
        printer.Color
        
        anotherWidget = QtGui.QPrintDialog(printer,self)
        if(anotherWidget.exec_() != QtGui.QDialog.Accepted):
            return
            
        p = QtGui.QPixmap.grabWidget(self.canvas)
        #p = QtGui.QPixMapping.grabWidget(self.canvas)
        printLabel = QtGui.QLabel()
        printLabel.setPixmap(p)
        painter = QtGui.QPainter(printer)
        printLabel.render(painter)
        painter.end()

        pyplot.show()
        
        
