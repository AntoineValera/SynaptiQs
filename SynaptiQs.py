# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:39:29 2011

@author: Antoine Valera

Version 2.1.0
"""


import sys,sip
from PyQt4 import QtCore, QtGui
from matplotlib import pyplot
from OpenElectrophy import *
from scipy import *


try:
    sip.setapi('QString', 2)
    Ipython=True
except ValueError:
    app = QtGui.QApplication(sys.argv)
    msgBox = QtGui.QMessageBox()
    msgBox.setText(
    """
    <b>API Error</b>
    <p>API 'QString' has already been set to version 1
    <p>Ipython will not work. You can change this option in 
    <b>Spyder->Tools-->Preference->External Module->PyQt->API #2</b>
    <p>SynaptiQs will now start without Ipython
    """)
    msgBox.exec_()   
    Ipython=False
    
    

import sys,os,atexit,glob,warnings
from matplotlib import *
#warnings.filterwarnings("ignore", category=DeprecationWarning) 




if __name__ == "__main__": #Executé si l'application est en StandAlone

    #with pyplot.xkcd():
        app = QtGui.QApplication(sys.argv) #Starts a new window application. First step to be done
    
        
        import __builtin__
        __all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]
        for i in __all__:
            setattr(sys.modules[__name__],i,__import__(i))
    
        Navigate = Navigate.Navigate() #Appel de la classe Navigate qui contient les fonctions de navigation et d'affichage
        Requete = Requete.Requete()
        Analysis = Analysis.Analysis() #Appel de la classe Analysis qui permet les mesures d'amplitude
        Main = Main.Main() #Appel de la classe Application_Main_Window qui creé tous les boutons et le menu
        MyMplCanvas = MyMplCanvas.MyMplCanvas
        MyMplWidget = MyMplWidget.MyMplWidget
        Infos = Infos.Infos()
        Fitting=Fitting.Fitting()
        Mapping = Mapping.Mapping()
        Histogram=Histogram.Histogram()
        SpreadSheet=SpreadSheet.SpreadSheet
        
        
        
        
        Infos.Class_List=[Navigate,Requete,Analysis,Main,MyMplCanvas,MyMplWidget,Infos,Mapping,Fitting,Histogram,SpreadSheet,Import] #Add all classes needed in the Script function
    
        #setattr(Infos,'Class_List',Class_List)
    
        for Class in Infos.Class_List:
            setattr(__builtin__,Class.__name__,Class)
        
        rcParams['figure.facecolor'] = 'white'
        rcParams['pdf.fonttype'] = 42
        rcParams['font.serif'] = 'Times New Roman'
        rcParams['savefig.dpi'] = 300
        rcParams['savefig.format'] = 'pdf'
        rcParams['ps.fonttype'] = 3
        rcParams['font.family'] = 'serif'
        rcParams['legend.fontsize'] = 8
    
        #if Ipython == True:
        #Main.ShellButton.setEnabled(1)
    
    
        Main.File_loading() #Chargement des parametres
        Main.Create_Window() #Execute l'initialisation de l'appli
        Plugins=Plugins.Plugins()
        Import=Import.MyWindow()
        
        setattr(__builtin__,'Plugins',Plugins)
        setattr(__builtin__,'Import',Plugins)
        Infos.List_All_Globals()  
        Main.MainWindow.show() #Affiche la fenetre
        sys.exit(app.exec_()) #Quitte lapplication si on "clique sur la croix" (=sys.exit)
        #It can raise a SytemExit Error in some python environnement. It's not relevant