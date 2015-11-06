# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:32:05 2013

@author: Antoine Valera
"""


import os,time
from PyQt4 import QtCore, QtGui
from matplotlib import pyplot,numpy,image
from scipy import stats
from math import pow
from math import sqrt
import scipy
from OpenElectrophy import Block
import Map
from copy import deepcopy
from OpenElectrophy import sqlalchemy
#import Requete,Infos,Main,MyMplWidget,SpreadSheet,Navigate,Analysis

#TODO : Add a tool to pool some coordinates together when they are close
#       Add a way to gray the mapping areas where no stim was made (!= No response)
#       Add a way to see both inhibition and excitation
#       Find a way to define the number of repeat with user defined coordinates

class Mapping(object):
    """
    C'est l'ensemble des fonctions qui concernent le mapping
    """
    def __init__(self):
        self.__name__="Mapping" 
        self.Current_Picture_Directory=os.getenv("HOME")
        self.Reset_Mapping_Variables()
        self.Display_Red=True
        self.Display_Green=True
        self.Display_Blue=True
        self.Vertical_Lines_Button = None
        self.Horizontal_Lines_Button = None
        self.CM.Types_of_Events_to_Measure = 'Negative'
        self.DB_Picture=False
        self.XPositions=numpy.array([None]*10)
        self.YPositions=numpy.array([None]*10)
        self.Max_Valid_Dist=250
        self.Use_Number_of_Turns=True
        self.Image_ColorMap='Greys'
        self.NormalizeMappingMode='Charge' #controls the measurement type you can use for map normalization
        self.CurrentChannel = 0
        self.Mapping_ID = 0
        self.StoredMaps=[]
        self.AllowToAddaMapping=False
        self.NumberOfLevels = 20
        
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

    def Reset_Mapping_Variables(self):
        #TODO : verify that all variables are here        
        for variable_to_delete in ['self.CM.Sorted_X_and_Y_Coordinates',
                                   'self.CM.Sorted_Mean_Amplitudes_1',
                                   'self.CM.Sorted_Mean_Charges_1',
                                   'self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary',
                                   'self.CM.Coordinates_and_Corresponding_Amplitudes1_Dictionnary',
                                   'self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary',
                                   'self.CM.Coordinates_and_Corresponding_Charges1_Dictionnary',
                                   'self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary',
                                   'self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary',
                                   'self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary',
                                   'self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary',
                                   'self.CM.Initially_Excluded_AnalogSignal_Ids',
                                   'self.CM.Success_list',
                                   'self.CM.Success_rate',
                                   'self.CM.Local_Amplitude',
                                   'self.CM.Local_Amplitude_sd',
                                   'self.CM.Local_Surface',
                                   'self.CM.Local_Surface_sd',
                                   'self.CM.Local_Success',
                                   'self.Current_Picture_for_the_Map']:
                      
            try:
                exec ('del '+variable_to_delete)
                print '     ',variable_to_delete, ' deleted'
            except:
                print '     ',variable_to_delete, ' not found, not deleted'
          

        try:
            self.CM = Map.Map()
            self.X_Neuron.setText("0")
            self.Y_Neuron.setText("0")
            self.X_Start_Field.setText("")   
            self.X_End_Field.setText("")         
            self.X_Step_Field.setText("")   
            self.Y_Start_Field.setText("")    
            self.Y_End_Field.setText("")          
            self.Y_Step_Field.setText("")
            self.Number_of_Turns.setText("")         
            self.Thresholding_Mode_Input_Field.setText("0")   
            self.Stim_Resolution.setText("1") 
            self.Transparency.setText("0.4") 
            self.X_Offset.setText("0") 
            self.Y_Offset.setText("0")                 
            self.Activate_Map.setEnabled(False)
            self.AllowToAddaMapping=False
            self.Use_Number_of_Turns=True
            if len(Requete.Spiketrain_ids) > 0 or Main.SQLTabWidget.currentIndex() == 2:
                if numpy.isnan(Requete.Spiketrain_ids[0]) == True:
                    self.Thresholding_Mode.clear()
                    self.Thresholding_Mode.addItems(["None","pA","pC","% of Max","% of success","Combo","Variance"])
                else:
                    self.Thresholding_Mode.clear()
                    self.Thresholding_Mode.addItems(["None","pA","pC","% of Max","% of success","Combo","Variance","Events"])                
        except AttributeError: #First launch error
            pass

        
        self.CM.Scanning_Direction_Mode=None
        self.SuccessRate_Ready=False
        self.DB_Picture=False
        
           
    def Tools(self):
  
        """
        Definit les Champs et Variables de base du menu mapping
        X_Offset et Y_Offset permettent de recentrer l'image CCD par rapport au champ du PM
        """
        
        #We open the Mapping_Pref.txt file, which contains user defined parameters for Mappings 
        try:

            print "/////////////// Mapping_Pref.txt Loaded correctly"
            parameters = open(Main.Mapping_Preferences_Path)
            Mapping_Preferences=parameters.readlines() #on lit
            self.Mapping_Preferences=['']*len(Mapping_Preferences)
            for i in range(len(Mapping_Preferences)):
                Mapping_Preferences[i]=Mapping_Preferences[i].replace('\n','')
                self.Mapping_Preferences[i] = eval(Mapping_Preferences[i])
            self.List_of_User_Defined_Mapping_Parameters=[]
            
            for i in range(len(self.Mapping_Preferences)):
                self.List_of_User_Defined_Mapping_Parameters.append(self.Mapping_Preferences[i][0])
            parameters.close() #on ferme le fichier
            
        except : #Si le fichier de parametres n'existe pas, on le crée, mais il faut les droits d'ecriture dans le dossier
            print "error, Mapping_Pref.txt does not exist, file created"
            parameters = open(Main.Mapping_Preferences_Path,'w')
            self.Mapping_Preferences=[]
            self.List_of_User_Defined_Mapping_Parameters=[""]
            self.Mapping_Preferences.append(["Default",-100,100,200,-100,100,200,1,"Lines"])
            self.List_of_User_Defined_Mapping_Parameters[0] = "Default"
            self.Save_User_Defined_Parameters()
            parameters.close()
            
        GlobalVBox=QtGui.QVBoxLayout(Main.MappingWidget)


   
        self.X_Start_Label = QtGui.QLabel()
        self.X_Start_Label.setGeometry(10, 10, 40, 20)
        self.X_Start_Label.setText("X Start")   
        self.X_Start_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.X_Start_Field.setGeometry(50,10,40,20)
        self.X_Start_Field.setText("") 

        self.X_End_Label = QtGui.QLabel()
        self.X_End_Label.setGeometry(110, 10, 40, 20)
        self.X_End_Label.setText("X End")   
        self.X_End_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.X_End_Field.setGeometry(150,10,40,20)
        self.X_End_Field.setText("")         
        
        self.X_Step_Label = QtGui.QLabel()
        self.X_Step_Label.setGeometry(210, 10, 40, 20)
        self.X_Step_Label.setText("X Step")   
        self.X_Step_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.X_Step_Field.setGeometry(250,10,40,20)
        self.X_Step_Field.setText("")   

        self.X_Number_Label = QtGui.QLabel()
        self.X_Number_Label.setGeometry(210, 10, 40, 20)
        self.X_Number_Label.setText("Step#")   
        self.X_Number_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.X_Number_Field.setGeometry(250,10,40,20)
        self.X_Number_Field.setText("")  

        self.Y_Start_Label = QtGui.QLabel()
        self.Y_Start_Label.setGeometry(10, 30, 40, 20)
        self.Y_Start_Label.setText( "Y Start")   
        self.Y_Start_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Y_Start_Field.setGeometry(50,30,40,20)
        self.Y_Start_Field.setText("")    
        
        self.Y_End_Label = QtGui.QLabel()
        self.Y_End_Label.setGeometry(110, 30, 40, 20)
        self.Y_End_Label.setText( "Y End")   
        self.Y_End_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Y_End_Field.setGeometry(150,30,40,20)
        self.Y_End_Field.setText("")          

        self.Y_Step_Label = QtGui.QLabel()
        self.Y_Step_Label.setGeometry(210, 30, 40, 20)
        self.Y_Step_Label.setText( "Y Step")   
        self.Y_Step_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Y_Step_Field.setGeometry(250,30,40,20)
        self.Y_Step_Field.setText("")

        self.Y_Number_Label = QtGui.QLabel()
        self.Y_Number_Label.setGeometry(210, 10, 40, 20)
        self.Y_Number_Label.setText("Step#")   
        self.Y_Number_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Y_Number_Field.setGeometry(250,10,40,20)
        self.Y_Number_Field.setText("") 

        self.Number_of_Turns_Label = QtGui.QLabel()
        self.Number_of_Turns_Label.setGeometry(150, 50, 120, 20)
        self.Number_of_Turns_Label.setText( "Number of Turns")   
        self.Number_of_Turns = QtGui.QLineEdit() #Lines, columns, Parent
        self.Number_of_Turns.setGeometry(250,50,40,20)
        self.Number_of_Turns.setText("")

        self.MappingID = QtGui.QComboBox()
        self.MappingID.setGeometry(150, 80, 120, 20)
        QtCore.QObject.connect(self.MappingID, QtCore.SIGNAL("activated(int)"),self.ImportMapping)

        self.CurrentMapFocus = QtGui.QComboBox()
        self.CurrentMapFocus.setGeometry(250, 80, 120, 20)
        QtCore.QObject.connect(self.CurrentMapFocus, QtCore.SIGNAL("currentIndexChanged(int)"),self.ChangeCurrentChannel)



        self.ClearMappings = QtGui.QPushButton()
        self.ClearMappings.setGeometry(150, 80, 120, 20) #taille et position (X,Y,Xsize,Ysize)
        self.ClearMappings.setText( "Clear Maps")  
        QtCore.QObject.connect(self.ClearMappings, QtCore.SIGNAL("clicked()"),self.Clear_Mappings)
                
        
        self.Define_Coordinates_Button = QtGui.QPushButton() #creation du bouton
        self.Define_Coordinates_Button.setGeometry(300, 10, 80, 32) #taille et position (X,Y,Xsize,Ysize)
        self.Define_Coordinates_Button.setText( "Define\nCoordinates")  
        QtCore.QObject.connect(self.Define_Coordinates_Button, QtCore.SIGNAL("clicked()"),self.Define_Coordinates)
        
        self.User_Defined_Measurement_Parameters = QtGui.QComboBox()
        self.User_Defined_Measurement_Parameters.setGeometry(300, 40, 80, 20)
        self.User_Defined_Measurement_Parameters.addItems(self.List_of_User_Defined_Mapping_Parameters)

        self.Add_User_Defined_Measurement_Parameters_Button = QtGui.QPushButton() #creation du bouton
        self.Add_User_Defined_Measurement_Parameters_Button.setGeometry(300, 60, 15, 14) #taille et position (X,Y,Xsize,Ysize)
        self.Add_User_Defined_Measurement_Parameters_Button.setText("+")  
        
        self.Remove_User_Defined_Measurement_Parameters_Button = QtGui.QPushButton() #creation du bouton
        self.Remove_User_Defined_Measurement_Parameters_Button.setGeometry(330, 60, 15, 14) #taille et position (X,Y,Xsize,Ysize)
        self.Remove_User_Defined_Measurement_Parameters_Button.setText("-")          

        self.Set_User_Defined_Measurement_Parameters_to_Zero_Button = QtGui.QPushButton() #creation du bouton
        self.Set_User_Defined_Measurement_Parameters_to_Zero_Button.setGeometry(365, 60, 15, 14) #taille et position (X,Y,Xsize,Ysize)
        self.Set_User_Defined_Measurement_Parameters_to_Zero_Button.setText("0")  

 
        inputhbox=QtGui.QHBoxLayout()
        
        Grid=QtGui.QGridLayout()
        Grid.addWidget(self.X_Start_Label,1,0)
        Grid.addWidget(self.X_Start_Field,1,1)
        Grid.addWidget(self.X_End_Label,1,2)
        Grid.addWidget(self.X_End_Field,1,3)
        Grid.addWidget(self.X_Step_Label,1,4)
        Grid.addWidget(self.X_Step_Field,1,5)        
        Grid.addWidget(self.X_Number_Label,1,6)
        Grid.addWidget(self.X_Number_Field,1,7) 
        Grid.addWidget(self.Y_Start_Label,2,0)
        Grid.addWidget(self.Y_Start_Field,2,1)
        Grid.addWidget(self.Y_End_Label,2,2)
        Grid.addWidget(self.Y_End_Field,2,3)
        Grid.addWidget(self.Y_Step_Label,2,4)
        Grid.addWidget(self.Y_Step_Field,2,5)        
        Grid.addWidget(self.Y_Number_Label,2,6)
        Grid.addWidget(self.Y_Number_Field,2,7)
        Grid.addWidget(self.Number_of_Turns_Label,3,0)
        Grid.addWidget(self.Number_of_Turns,3,1)   
        Grid.addWidget(self.MappingID,3,2)
        Grid.addWidget(self.ClearMappings,3,3)
        Grid.addWidget(self.CurrentMapFocus,3,4)
        Grid.addWidget(self.Define_Coordinates_Button,1,8,1,3)
        Grid.addWidget(self.User_Defined_Measurement_Parameters,2,8,1,3)
        Grid.addWidget(self.Add_User_Defined_Measurement_Parameters_Button,3,8)
        Grid.addWidget(self.Remove_User_Defined_Measurement_Parameters_Button,3,9)
        Grid.addWidget(self.Set_User_Defined_Measurement_Parameters_to_Zero_Button,3,10)
        inputhbox.addLayout(Grid)
        
        GlobalVBox.addLayout(inputhbox)
        
        QtCore.QObject.connect(self.User_Defined_Measurement_Parameters, QtCore.SIGNAL('activated(int)'),self.Load_User_Defined_Parameters)
        QtCore.QObject.connect(self.Add_User_Defined_Measurement_Parameters_Button, QtCore.SIGNAL("clicked()"),self.Add_User_Defined_Measurement_Parameters)
        QtCore.QObject.connect(self.Remove_User_Defined_Measurement_Parameters_Button, QtCore.SIGNAL("clicked()"),self.Remove_User_Defined_Measurement_Parameters)
        QtCore.QObject.connect(self.Set_User_Defined_Measurement_Parameters_to_Zero_Button, QtCore.SIGNAL("clicked()"),self.Set_User_Defined_Measurement_Parameters_to_Zero)




        self.averagebyposition = QtGui.QPushButton() #creation du bouton
        self.averagebyposition.setGeometry(120,70,100,25) #taille et position (X,Y,Xsize,Ysize)
        self.averagebyposition.setText( "Mapping Average")        
        QtCore.QObject.connect(self.averagebyposition, QtCore.SIGNAL("clicked()"),self.Average_Traces_By_Position)
             
        self.measurebyposition = QtGui.QPushButton() #creation du bouton
        self.measurebyposition.setGeometry(10,70,100,25) #taille et position (X,Y,Xsize,Ysize)
        self.measurebyposition.setText( "Mapping Measure")        
        QtCore.QObject.connect(self.measurebyposition, QtCore.SIGNAL("clicked()"),self.Measure_Traces_By_Position)
       
        self.mappingprogress = QtGui.QProgressBar()
        self.mappingprogress.setGeometry(230, 73, 100, 20)
        
        hbox4=QtGui.QHBoxLayout()
        hbox4.addWidget(self.averagebyposition)
        hbox4.addWidget(self.measurebyposition)
        hbox4.addWidget(self.mappingprogress)
        GlobalVBox.addLayout(hbox4)

#        hbox4bis=QtGui.QHBoxLayout()
#        hbox4bis.addWidget(self.mappingprogress)
#        GlobalVBox.addLayout(hbox4bis)
        
        self.Thresholding_Mode_Label = QtGui.QLabel()
        self.Thresholding_Mode_Label.setGeometry(5, 125, 55, 20)
        self.Thresholding_Mode_Label.setText( "Threshold :")
        self.Thresholding_Mode = QtGui.QComboBox()
        self.Thresholding_Mode.setGeometry(60, 125, 80, 20)
        self.Thresholding_Mode.addItems(["None","pA","pC","% of Max","% of success","Combo","Variance","Events"])
        self.Thresholding_Mode_Input_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Thresholding_Mode_Input_Field.setGeometry(145, 125, 50, 20)
        self.Thresholding_Mode_Input_Field.setText("0")   
        
        hbox5=QtGui.QHBoxLayout()
        hbox5.addWidget(self.Thresholding_Mode_Label)
        hbox5.addWidget(self.Thresholding_Mode)
        hbox5.addWidget(self.Thresholding_Mode_Input_Field)        
        GlobalVBox.addLayout(hbox5)


        self.X_Neuron_Label = QtGui.QLabel()
        self.X_Neuron_Label.setGeometry(100, 95, 8, 20)
        self.X_Neuron_Label.setText( "X:")         
        self.X_Neuron = QtGui.QLineEdit() #Lines, columns, Parent
        self.X_Neuron.setGeometry(110,95,40,20)
        self.X_Neuron.setText("0")


        self.Y_Neuron_Label = QtGui.QLabel()
        self.Y_Neuron_Label.setGeometry(160, 95, 8, 20)
        self.Y_Neuron_Label.setText( "Y:")   
        self.Y_Neuron = QtGui.QLineEdit() #Lines, columns, Parent
        self.Y_Neuron.setGeometry(170,95,40,20)
        self.Y_Neuron.setText("0")
        
        
        self.SweepPosition_Label = QtGui.QLabel()
        self.SweepPosition_Label.setGeometry(5, 95, 80, 20)
        self.SweepPosition_Label.setText( "Sweep #")   
        self.SweepPosition = QtGui.QLineEdit() #Lines, columns, Parent
        self.SweepPosition.setGeometry(50, 95, 45, 20)
        #self.SweepPosition.setText("")
        self.SweepPosition.setValidator(QtGui.QIntValidator(0, 100,self.SweepPosition))

        QtCore.QObject.connect(self.SweepPosition, QtCore.SIGNAL("editingFinished()"),self.Find_Corresponding_Coordinates)        

        self.onepositionaverage = QtGui.QPushButton() #creation du bouton
        self.onepositionaverage.setGeometry(210,95,100,25) #taille et position (X,Y,Xsize,Ysize)
        self.onepositionaverage.setText( "Local Average")        
        QtCore.QObject.connect(self.onepositionaverage, QtCore.SIGNAL("clicked()"),self.One_Stim_Average)   


        hbox5bis=QtGui.QHBoxLayout()
        hbox5bis.addWidget(self.X_Neuron_Label)
        hbox5bis.addWidget(self.X_Neuron)
        hbox5bis.addWidget(self.Y_Neuron_Label)
        hbox5bis.addWidget(self.Y_Neuron)
        hbox5bis.addWidget(self.SweepPosition_Label)
        hbox5bis.addWidget(self.SweepPosition)
        hbox5bis.addWidget(self.onepositionaverage)
        GlobalVBox.addLayout(hbox5bis)



        self.Objective = QtGui.QComboBox()
        self.Objective.setGeometry(5, 145, 50, 25)
        self.Objective.addItems(["PM","CCD","UCL"])
        
        self.Select_Experiment_Picture_Button = QtGui.QPushButton()
        self.Select_Experiment_Picture_Button.setGeometry(55, 145, 25, 25)
        self.Select_Experiment_Picture_Button.setText( "...")
        QtCore.QObject.connect(self.Select_Experiment_Picture_Button, QtCore.SIGNAL("clicked()"),self.Change_Experiment_Picture)

        self.Stim_Resolution_Label = QtGui.QLabel()
        self.Stim_Resolution_Label.setGeometry(85, 135, 60, 40)
        self.Stim_Resolution_Label.setText( "Pixel Size")   
        self.Stim_Resolution = QtGui.QLineEdit() #Lines, columns, Parent
        self.Stim_Resolution.setGeometry(140,145,30,20)
        self.Stim_Resolution.setText("1") 

        self.Transparency_Label = QtGui.QLabel()
        self.Transparency_Label.setGeometry(170, 145, 50, 20)
        self.Transparency_Label.setText( "Opacity")   
        self.Transparency = QtGui.QLineEdit() #Lines, columns, Parent
        self.Transparency.setGeometry(210,145,30,20)
        self.Transparency.setText("0.75") 
        QtCore.QObject.connect(self.Transparency, QtCore.SIGNAL('editingFinished ()'),self.Correction_of_Abnormal_Parameters_for_Mapping)

        self.Activate_Map = QtGui.QPushButton() #creation du bouton
        self.Activate_Map.setGeometry(240, 145, 60, 25) #taille et position (X,Y,Xsize,Ysize)
        self.Activate_Map.setText( "Do Map")
        self.Activate_Map.setEnabled(False)
        QtCore.QObject.connect(self.Activate_Map, QtCore.SIGNAL("clicked()"),self.Display_Mapping_Results)

        self.ColorMap = QtGui.QComboBox()
        self.ColorMap.setGeometry(300, 145, 120, 25)
        self.ColorMap.addItems(['hot',
                                "bwr",
                                'autumn',
                                'spectral',
                                'gist_heat',
                                'afmhot',
                                'gnuplot',
                                'seismic',
                                'Greens',
                                'Blues',
                                'Reds',
                                'Grays',
                                'Oranges_r',
                                'Greens_r',
                                'Blues_r',
                                'Reds_r',
                                'Grays_r',
                                'Oranges_r']) #others at http://www.loria.fr/~rougier/teaching/matplotlib/
        
        hbox6=QtGui.QHBoxLayout()
        hbox6.addWidget(self.Objective)
        hbox6.addWidget(self.Select_Experiment_Picture_Button)
        hbox6.addWidget(self.Stim_Resolution_Label)
        hbox6.addWidget(self.Stim_Resolution)
        hbox6.addWidget(self.Transparency_Label)
        
        hbox6.addWidget(self.Transparency)
        hbox6.addWidget(self.Activate_Map)           
        hbox6.addWidget(self.ColorMap)          
        GlobalVBox.addLayout(hbox6)



        self.CM.Charge='None'
        self.CM.Amplitude='Color'
       

        self.Amplitudes_Display_Mode_Label = QtGui.QLabel()
        self.Amplitudes_Display_Mode_Label.setGeometry(5, 170, 100, 25)
        self.Amplitudes_Display_Mode_Label.setText( "Show Amplitude as")
        self.Amplitudes_Display_Mode = QtGui.QComboBox()
        self.Amplitudes_Display_Mode.setGeometry(100, 170, 60, 25)
        self.Amplitudes_Display_Mode.addItems(["Color","Surface","None"])           
        self.Charges_Display_Mode_Label = QtGui.QLabel()
        self.Charges_Display_Mode_Label.setGeometry(165, 170, 100, 25)
        self.Charges_Display_Mode_Label.setText( "and Charge as")   
        self.Charges_Display_Mode = QtGui.QComboBox()
        self.Charges_Display_Mode.setGeometry(240, 170, 60, 25)
        self.Charges_Display_Mode.addItems(["Color","Surface","None"])
        self.Charges_Display_Mode.setCurrentIndex(1)

        hbox7=QtGui.QHBoxLayout()
        hbox7.addWidget(self.Amplitudes_Display_Mode_Label)
        hbox7.addWidget(self.Amplitudes_Display_Mode)
        hbox7.addWidget(self.Charges_Display_Mode_Label)  
        hbox7.addWidget(self.Charges_Display_Mode)  
        GlobalVBox.addLayout(hbox7)

        self.Manual_Min_Label = QtGui.QLabel()
        self.Manual_Min_Label.setGeometry(10, 200, 80, 20)
        self.Manual_Min_Label.setText( "Manual Min")   
        self.Manual_Min_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Manual_Min_Field.setGeometry(100,200,80,20)
        self.Manual_Min_Field.setText("")   

        self.Manual_Max_Label = QtGui.QLabel()
        self.Manual_Max_Label.setGeometry(210, 200, 80, 20)
        self.Manual_Max_Label.setText( "Manual Max")   
        self.Manual_Max_Field = QtGui.QLineEdit() #Lines, columns, Parent
        self.Manual_Max_Field.setGeometry(300,200,80,20)
        self.Manual_Max_Field.setText("")  
        
        hbox8=QtGui.QHBoxLayout()
        hbox8.addWidget(self.Manual_Min_Label)
        hbox8.addWidget(self.Manual_Min_Field)
        hbox8.addWidget(self.Manual_Max_Label)  
        hbox8.addWidget(self.Manual_Max_Field)  
        GlobalVBox.addLayout(hbox8)
        
#        self.X_Offset_Label = QtGui.QLabel()
#        self.X_Offset_Label.setGeometry(5, 250, 50, 20)
#        self.X_Offset_Label.setText( "X Offset")   
#        self.X_Offset = QtGui.QLineEdit() #Lines, columns, Parent
#        self.X_Offset.setGeometry(50,250,50,20)
#        self.X_Offset.setText("0") 
#        
#        self.Y_Offset_Label = QtGui.QLabel()
#        self.Y_Offset_Label.setGeometry(105, 250, 50, 20)
#        self.Y_Offset_Label.setText( "Y Offset")   
#        self.Y_Offset = QtGui.QLineEdit() #Lines, columns, Parent
#        self.Y_Offset.setGeometry(150,250,50,20)
#        self.Y_Offset.setText("0")         
#
#        hbox9=QtGui.QHBoxLayout()
#        hbox9.addWidget(self.X_Offset_Label)
#        hbox9.addWidget(self.X_Offset)
#        hbox9.addWidget(self.Y_Offset_Label)  
#        hbox9.addWidget(self.Y_Offset)  
#        GlobalVBox.addLayout(hbox9)

        #TODO : Fix Image saving or remove in MySQL before activating
        #hbox10=QtGui.QHBoxLayout()

        #self.Save_Image = QtGui.QPushButton(Main.MappingWidget) #creation du bouton
        #self.Save_Image.setGeometry(300,250,100,20) #taille et position (X,Y,Xsize,Ysize)
        #self.Save_Image.setText( "Save Picture in db")        
        #QtCore.QObject.connect(self.Save_Image, QtCore.SIGNAL("clicked()"),self.Save_Associated_Image)
             
        #self.Load_Image = QtGui.QPushButton(Main.MappingWidget) #creation du bouton
        #self.Load_Image.setGeometry(200,250,100,20) #taille et position (X,Y,Xsize,Ysize)
        #self.Load_Image.setText( "Load db Picture")        
        #QtCore.QObject.connect(self.Load_Image, QtCore.SIGNAL("clicked()"),self.Load_Associated_Image)
        
        #hbox10.addWidget(self.Save_Image)
        #hbox10.addWidget(self.Load_Image)
        #GlobalVBox.addLayout(hbox10)

        
        QtCore.QObject.connect(self.Amplitudes_Display_Mode, QtCore.SIGNAL('currentIndexChanged(int)'),self.Update_Display_Parameters)        
        QtCore.QObject.connect(self.Charges_Display_Mode, QtCore.SIGNAL('currentIndexChanged(int)'),self.Update_Display_Parameters)        
        QtCore.QObject.connect(self.Thresholding_Mode, QtCore.SIGNAL('currentIndexChanged(int)'),self.Update_Display_Parameters)        



        #if "Analysis.Amplitudes_1", analyse sur les amplitudes, si "Analysis.Charges_1", analyse sur les charges
        self.Analysis_mode="Analysis.Amplitudes_1"
        self.Update_Display_Parameters()
        

        
    def More_Options(self):
        
        self.OptionWid=QtGui.QWidget()            
        hbox=QtGui.QVBoxLayout()

        ListofVar=[self.__name__+'.Max_Valid_Dist',
                   self.__name__+'.Use_Number_of_Turns',
                   self.__name__+'.CurrentChannel',
                   self.__name__+'.Image_ColorMap',
                   self.__name__+'.Analysis_mode',
                   self.__name__+'.Transparency',
                   self.__name__+'.NumberOfLevels']
        for i in ListofVar:
            Option_Label=QtGui.QLabel(i)
            Option=QtGui.QLineEdit()
            Option.setObjectName(i)
            i=i.replace(self.__name__,'self')
            Option.setText(str(eval(i)))
            hbox.addWidget(Option_Label)
            hbox.addWidget(Option) 
            QtCore.QObject.connect(Option, QtCore.SIGNAL('editingFinished()'),Infos.LineEdited)
        self.OptionWid.setLayout(hbox)
        
                
        self.OptionWid.show()
        
    def ChangeCurrentChannel(self):
        print self.CurrentMapFocus.currentIndex()
        self.CurrentChannel = int(self.CurrentMapFocus.currentIndex()) 
        
    def EnableDisableOptions(self,Amplitude,Charge,Average,Measure,ThresholdInput,ChangeDisplay=False):
        self.CM.Amplitude=str(self.Amplitudes_Display_Mode.currentText())
        self.CM.Charge=str(self.Charges_Display_Mode.currentText())
        
        self.Amplitudes_Display_Mode.setEnabled(Amplitude)
        self.Charges_Display_Mode.setEnabled(Charge)  
        self.averagebyposition.setEnabled(Average)
        self.measurebyposition.setEnabled(Measure)
        self.Thresholding_Mode_Input_Field.setEnabled(ThresholdInput)
        
        if ChangeDisplay == True:
            self.Amplitudes_Display_Mode.setCurrentIndex(0)  
            self.Charges_Display_Mode.setCurrentIndex(2)          
        
 
    def Update_Display_Parameters(self):

        if self.Thresholding_Mode.currentIndex()==0:
            self.EnableDisableOptions(True,True,True,False,False)
        elif self.Thresholding_Mode.currentIndex()==1:
            self.EnableDisableOptions(True,True,True,True,True)
        elif self.Thresholding_Mode.currentIndex()==2:
            self.EnableDisableOptions(True,True,True,True,True)
        elif self.Thresholding_Mode.currentIndex()==3:
            self.EnableDisableOptions(True,True,True,False,True)
            #self.EnableDisableOptions(True,True,True,True,True)
        elif self.Thresholding_Mode.currentIndex()==4:
            self.EnableDisableOptions(False,True,False,False,True,ChangeDisplay=True)
        elif self.Thresholding_Mode.currentIndex()==5:
            self.EnableDisableOptions(False,True,False,True,True,ChangeDisplay=True)
        elif self.Thresholding_Mode.currentIndex()==6:
            self.EnableDisableOptions(True,True,True,True,True)
        elif self.Thresholding_Mode.currentIndex()==7: #for spikes
            self.EnableDisableOptions(True,True,False,True,False,ChangeDisplay=True)
        
        #TODO : explain what that is
        if self.CM.Charge==self.CM.Amplitude:
            if self.CM.Charge!='None':
                self.Charges_Display_Mode.setCurrentIndex(2)
                self.CM.Charge='None'
            else:
                self.Charges_Display_Mode.setCurrentIndex(1)
                self.CM.Charge='Surface'

    def Set_User_Parameters(self,name):
        #TODO : The 4 followinf function are like their source in Analysis. Those function should be pooled together
        #Index is the position corresponding to the wanted name
        index=self.User_Defined_Measurement_Parameters.findText(name)
        if index != -1 :
            print "index", index
            self.User_Defined_Measurement_Parameters.setCurrentIndex(index)
            self.Load_User_Defined_Parameters(index,True)
        else:
            msg="""
            <b> %s doesn't exist in self.User_Defined_Measurement_Parameters
            """ % (name) 
            Infos.Error(msg)
                     
        
    def Set_User_Defined_Measurement_Parameters_to_Zero(self):

        for a in ["X_Start_Field","X_End_Field","X_Step_Field","Y_Start_Field","Y_End_Field","Y_Step_Field","Number_of_Turns"]:
            exec('self.'+a+'.setText("1")')
        self.Load_User_Defined_Parameters(0)

    def Add_User_Defined_Measurement_Parameters(self):
        
        Wid=MyMplWidget()
        
        savename, ok = QtGui.QInputDialog.getText(Wid,'Input Dialog', 
            'Please enter parameters name')
        savename=str(savename)
        
        if ok:
            a=int(self.User_Defined_Measurement_Parameters.count())
            self.User_Defined_Measurement_Parameters.insertItem(a,savename)
            self.User_Defined_Measurement_Parameters.setCurrentIndex(a)
            templist=[savename]

            for a in ["X_Start_Field","X_End_Field","X_Step_Field","Y_Start_Field","Y_End_Field","Y_Step_Field","Number_of_Turns"]:
                exec('temp = self.'+str(a)+'.text()')                
                templist.append(str(temp))

        self.Mapping_Preferences.append(templist)
        self.Load_User_Defined_Parameters(len(self.User_Defined_Measurement_Parameters)-1)
        
        
    def Remove_User_Defined_Measurement_Parameters(self):
        
        a=int(self.User_Defined_Measurement_Parameters.count())
        self.Mapping_Preferences.pop(int(self.User_Defined_Measurement_Parameters.currentIndex()))
        self.User_Defined_Measurement_Parameters.removeItem(self.User_Defined_Measurement_Parameters.currentIndex())
        self.User_Defined_Measurement_Parameters.setCurrentIndex(a-2)
        self.Load_User_Defined_Parameters(0)

    def Load_User_Defined_Parameters(self,index,External=False):

        #name of the loaded list: self.Mapping_Preferences[int(Main.sender().currentIndex())][0]
        if External == True:
            compteur=0    
            for a in ["X_Start_Field","X_End_Field","X_Step_Field","Y_Start_Field","Y_End_Field","Y_Step_Field","Number_of_Turns"]:
                setnew = 'self.'+str(a)+'.setText("1")'
                exec(setnew)
                compteur+=1
                
        elif External == False:
            param_inf=list(numpy.copy(self.Mapping_Preferences[index]))
            param_inf.pop(0)
            compteur=0    
            for a in ["X_Start_Field","X_End_Field","X_Step_Field","Y_Start_Field","Y_End_Field","Y_Step_Field","Number_of_Turns"]:
                setnew = 'self.'+str(a)+'.setText(str(param_inf[compteur]))'#"'str(Main.param_inf[compteur+22])+'")'
                exec(setnew)
                compteur+=1            
            
        self.Save_User_Defined_Parameters()
        
    def Save_User_Defined_Parameters(self):
        
        print "-----------> Mapping parameters valid and saved"
        parameters = open(Main.Mapping_Preferences_Path,'w')
        saving =''
        for i in self.Mapping_Preferences:
            saving=saving+str(i)+"\n"
        parameters.write(saving)       
        parameters.close()        


    def UpdateUsableArrayList(self):
        FilteredList=[]
        for i in Main.ExistingSweeps:
            i=i.replace('Mapping.','self.')
            if len(eval(i)) == len(Requete.Analogsignal_ids):
                #if eval(i)
                FilteredList.append(i) 
                
        return FilteredList
        
    def Load_Coordinates(self):
       
        #self.List1=range(180)
        #self.List2=range(180)
        
        Infos.Actualize()
        self.Load_Coordinate_Widget = QtGui.QWidget()#self.popupDialog)
        #Load_Coordinate_Widget.setFixedSize(400,120) #definit la taille minimale du Widget (largeur, hauteur)          

        MapWidget = QtGui.QGridLayout(self.Load_Coordinate_Widget)
        MapWidget.addWidget(QtGui.QLabel('X Coordinates'),0,0)
        MapWidget.addWidget(QtGui.QLabel('Y Coordinates'),1,0)
        self.XArrayInputField=QtGui.QLineEdit('')
        self.YArrayInputField=QtGui.QLineEdit('')
        self.XArrayInputField.setObjectName("self.CM.Sorted_X_Coordinates")
        self.YArrayInputField.setObjectName("self.CM.Sorted_Y_Coordinates")
        MapWidget.addWidget(self.XArrayInputField,0,1)        
        MapWidget.addWidget(self.YArrayInputField,1,1)
        x=QtGui.QPushButton('...')
        y=QtGui.QPushButton('...')
        x.setObjectName("self.CM.Sorted_X_Coordinates")
        y.setObjectName("self.CM.Sorted_Y_Coordinates")
        
        FilteredList=self.UpdateUsableArrayList()
         
        self.ListOfXArrays=QtGui.QComboBox()
        self.ListOfXArrays.setObjectName("self.CM.Sorted_X_Coordinates")
        self.ListOfXArrays.addItems(FilteredList)
        self.ListOfYArrays=QtGui.QComboBox()
        self.ListOfYArrays.addItems(FilteredList)
        self.ListOfYArrays.setObjectName("self.CM.Sorted_Y_Coordinates")
        MapWidget.addWidget(self.ListOfXArrays,0,2)        
        MapWidget.addWidget(self.ListOfYArrays,1,2)         
        MapWidget.addWidget(x,0,3)        
        MapWidget.addWidget(y,1,3)  
        
        QtCore.QObject.connect(x, QtCore.SIGNAL("clicked()"),self.Load_File)
        QtCore.QObject.connect(y, QtCore.SIGNAL("clicked()"),self.Load_File)
        #QtCore.QObject.connect(self.ListOfXArrays, QtCore.SIGNAL("currentIndexChanged(int)"),self.UpdateCurrent)
        #QtCore.QObject.connect(self.ListOfYArrays, QtCore.SIGNAL("currentIndexChanged(int)"),self.UpdateCurrent)
        QtCore.QObject.connect(self.XArrayInputField, QtCore.SIGNAL("editingFinished()"),self.UpdateCurrent)
        QtCore.QObject.connect(self.YArrayInputField, QtCore.SIGNAL("editingFinished()"),self.UpdateCurrent)
        
        self.Load_Coordinate_Widget.show()
        

    def Load_File(self):        
        path = QtGui.QFileDialog()
        path.setNameFilter("*.txt")
        path.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        path.setFileMode(QtGui.QFileDialog.ExistingFiles)
        
        if (path.exec_()) :
            File=str(path.selectedFiles()[0])
            val=list(numpy.loadtxt(File))
            name=str(QtCore.QObject().sender().objectName())
            name=name.replace('self.','')
            setattr(Mapping,name,val)
            self.UpdateCurrent()
            #print str(QtCore.QObject().sender().objectName())
            
            #if str(QtCore.QObject().sender().objectName()) == 'self.CM.Sorted_X_Coordinates':
            #    idx=self.ListOfXArrays.findText('Mapping.'+name)
            #    self.ListOfXArrays.setCurrentIndex(idx)
            #elif str(QtCore.QObject().sender().objectName()) == 'self.CM.Sorted_Y_Coordinates':
            #    idx=self.ListOfXArrays.findText('Mapping.'+name)
            #    self.ListOfYArrays.setCurrentIndex(idx)
                    
        
    def UpdateCurrent(self):
        
        FilteredList=self.UpdateUsableArrayList()
        self.ListOfXArrays.clear()
        self.ListOfXArrays.addItems(FilteredList)
        self.ListOfYArrays.clear()
        self.ListOfYArrays.addItems(FilteredList)        
        
        try:
            obj=str(QtCore.QObject().sender().objectName())
        except AttributeError: # when the file doesn't exist yet
            exec(str(QtCore.QObject().sender().objectName())+'=[]')
            obj=str(QtCore.QObject().sender().objectName())
        if QtCore.QObject().sender().sender().__class__.__name__ == 'QFrame':
            val=str(QtCore.QObject().sender().currentText())
            val=val.replace('Mapping','self')
            obj=obj.replace('self.','')
            setattr(Mapping,obj,eval(val)) 
        elif QtCore.QObject().sender().__class__.__name__ == 'QLineEdit':
            val=str(QtCore.QObject().sender().text())
            val=val.replace('Mapping','self')
            obj=obj.replace('self.','')
            if val =='': #should be replaced by a if exist
                return
            else:
                setattr(Mapping,obj,eval(val))
        else:
            return
        
    def Autofill_Coordinates_Values_from_Tag_Field(self):
        
        """
        Trouve tout seul à partir des tags les paramètres de mapping.
        Fonctionne uniquement si les tags ont été enregistrés au préalable
        Si l'étape fonctionne, les champs sont remplis, ###et la variable Bypass passe en True,
        sinon elle reste en False
        """
        try:
            #Reading of the Coordinates Values
            
            #For each point, X & Y coordinates are converted into INT
            for i in range(len(Requete.tag['X_coord'])):

                Requete.tag['X_coord'][i]=int(Requete.tag['X_coord'][i])
                Requete.tag['Y_coord'][i]=int(Requete.tag['Y_coord'][i])  


            #Unsorted list of X & Y coordinates used for Mapping                  
            List_of_X_Coordinates=list(set(Requete.tag['X_coord'])) 
            List_of_Y_Coordinates=list(set(Requete.tag['Y_coord']))            
               
            List_of_X_Coordinates.sort()  
            List_of_Y_Coordinates.sort()  
               
            #Reading of the Step Values
            self.X_Step_Field.setText(str(Requete.tag['XSteps'][0]))   
            self.Y_Step_Field.setText(str(Requete.tag['YSteps'][0]))
            
            if int(self.X_Step_Field.text()) > 0:
                self.X_Start_Field.setText(str(min(List_of_X_Coordinates)))   
                self.X_End_Field.setText(str(max(List_of_X_Coordinates)))
            elif int(self.X_Step_Field.text()) < 0:
                self.X_Start_Field.setText(str(max(List_of_X_Coordinates)))   
                self.X_End_Field.setText(str(min(List_of_X_Coordinates)))

            if int(self.Y_Step_Field.text()) > 0:
                self.Y_Start_Field.setText(str(min(List_of_Y_Coordinates)))               
                self.Y_End_Field.setText(str(max(List_of_Y_Coordinates)))
            elif int(self.Y_Step_Field.text()) < 0:
                self.Y_Start_Field.setText(str(max(List_of_Y_Coordinates)))               
                self.Y_End_Field.setText(str(min(List_of_Y_Coordinates)))
            
            #Reading of the Number of Turns Value
            self.Number_of_Turns.setText(str(Requete.tag['NumberofTurns'][0]))
            #Reading of the Scanning direction Value
            self.CM.Scanning_Direction_Mode=str(Requete.tag["ScanWay"][0])
            
            #self.Bypass=True 

        except:
            print "/////////////// No Mapping parameters detected in this Experiment, you have to define it///////////////"
            #self.Bypass=False

    def Correction_of_Abnormal_Parameters_for_Mapping(self):
        """
        Mapping.Transparency is the alpha value for the scatter plot.
        Mapping.{X/Y}_{Start/End]_Field are the bounds of the mapping system. Value can be changed if setup evolves
        """
        #TODO : COrrect this script which is specific to my analysis
        #Corrections for transparency values
        if float(self.Transparency.text()) > 1:
            self.Transparency.setText("1")    
        if float(self.Transparency.text()) < 0:
            self.Transparency.setText("0")

        if float(self.Stim_Resolution.text()) <= 0:
            self.Stim_Resolution.setText("1")   

        #Corrections for step direction
        Xstart=int(self.X_Start_Field.text())
        Xend=int(self.X_End_Field.text())
        Xstep=int(self.X_Step_Field.text())
        Ystart=int(self.Y_Start_Field.text())
        Yend=int(self.Y_End_Field.text())
        Ystep=int(self.Y_Step_Field.text())
        if Xstart < Xend and Xstep <= 0:
            self.X_Step_Field.setText(str(Xstep*-1)) 
        elif Xstart > Xend and Xstep >= 0:
            self.X_Step_Field.setText(str(Xstep*-1))            
        if Ystart < Yend and Ystep <= 0:
            self.Y_Step_Field.setText(str(Ystep*-1)) 
        elif Ystart > Yend and Ystep >= 0:
            self.Y_Step_Field.setText(str(Ystep*-1)) 
            
        #Corrections for "average by Sweep Number"
        try:
            self.SweepPosition.setText(str(int(self.SweepPosition.text()))) 
            if int(self.SweepPosition.text())<0:
                self.SweepPosition.setText("0")
            if int(self.SweepPosition.text()) > len(Requete.Analogsignal_ids)-1:
                self.SweepPosition.setText(str(len(Requete.Analogsignal_ids)-1)) 
        except ValueError:
            self.SweepPosition.setText('') 
        
    
    
    def Change_Experiment_Picture(self,Picture=None):        

        """
        Popup Window to select the experimental picture
        """
        if Picture == None:
            path = QtGui.QFileDialog()
            path.setDirectory(self.Current_Picture_Directory)
            path.setNameFilter("Image files (*.png *.xpm *.jpg *.bmp *.tif)")
            path.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            path.setFileMode(QtGui.QFileDialog.ExistingFiles)
            
            if (path.exec_()) :
                self.Current_Picture_for_the_Map=str(path.selectedFiles()[0])
                self.Current_Picture_Directory=path.directory()
                self.DB_Picture=False
        else:
            self.Current_Picture_for_the_Map = Picture

        return self.Current_Picture_for_the_Map
        
    def Define_Non_Grid_Positions(self):

        self.CM.Scanning_Direction_Mode = 'UserDefined'   
        self.Set_Auto_Coordinates_Visible()        
        try:
            #Wid=QtGui.QWidget()
            #self.repeats, ok = QtGui.QInputDialog.getInt(Wid,'Number of pattern repeats', 
            #    'Enter the number of time your coordinates are repeated',value=1)
            #self.repeats=int(self.repeats)
            
            #if ok:
            self.Window=SpreadSheet(Source=[self.CM.Sorted_X_Coordinates,self.CM.Sorted_Y_Coordinates],Rendering=True,MustBeClosed=True)
            QtCore.QObject.connect(self.Window, QtCore.SIGNAL('destroyed()'),self.UpdateDictafterWidgetClosure)        
        except AttributeError:
            self.Load_Coordinates()


    def UpdateDictafterWidgetClosure(self):
        """
        This function edit the coordiantes list if you manually changed some values
        """
        if self.Use_Number_of_Turns == False:
            Number_of_Turns = 1
        else:
            Number_of_Turns=int(self.Number_of_Turns.text())
            
        self.CM.Sorted_Y_Coordinates_Full=self.CM.Sorted_Y_Coordinates*Number_of_Turns
        self.CM.Sorted_X_Coordinates_Full=self.CM.Sorted_X_Coordinates*Number_of_Turns
        self.CM.Sorted_X_and_Y_Coordinates=[None]*len(self.CM.Sorted_X_Coordinates)
        for i,j in enumerate(self.CM.Sorted_Y_Coordinates):
            self.CM.Sorted_X_and_Y_Coordinates[i]=(self.CM.Sorted_X_Coordinates[i],j)    
            
        self.CM.Sorted_X_and_Y_Coordinates_Full=self.CM.Sorted_X_and_Y_Coordinates*Number_of_Turns
        self.Set_Coordinates_in_Tag_Variable()
        
       

    def Define_Coordinates(self,Available=[1,2,3,4]):
        
        """
        C'est le popup qui permet de selectionner si le scan est par ligne ou par colonne
        Il appelle donc Mapping.setXlines ou Mapping.setYlines
        La fonction est appelée automatiquement si on lance le Mapping
        Elle peut aussi etre appelée séparement, dans le but de sauver les coordonnées.
        Une fois excuté, les infos sont stockées dans Requete.tag
        Dans les 2 cas, une fois passée, self.Bypass devient True
        """
        
        self.Map_tools_Widget = QtGui.QWidget()#self.popupDialog)
        self.Map_tools_Widget.setFixedSize(400,120) #definit la taille minimale du Widget (largeur, hauteur)          

        MapWidget = QtGui.QWidget(self.Map_tools_Widget)
        MapWidget.setGeometry(0,0,400,120)
        
        if 1 in Available:
            self.Vertical_Lines_Button = QtGui.QPushButton(MapWidget) #creation du bouton
            self.Vertical_Lines_Button.setGeometry(10,10,80,80) #taille et position (X,Y,Xsize,Ysize)
            self.Vertical_Lines_Button.setIcon(QtGui.QIcon(Main.Script_Path+"/Columns.png"))
            self.Vertical_Lines_Button.setIconSize(QtCore.QSize(70, 70))
            QtCore.QObject.connect(self.Vertical_Lines_Button, QtCore.SIGNAL("clicked()"),self.Create_Mapping_Pathway)
        
        if 2 in Available:
            self.Horizontal_Lines_Button = QtGui.QPushButton(MapWidget) #creation du bouton
            self.Horizontal_Lines_Button.setGeometry(110,10,80,80) #taille et position (X,Y,Xsize,Ysize)
            self.Horizontal_Lines_Button.setIcon(QtGui.QIcon(Main.Script_Path+"/Lines.png"))
            self.Horizontal_Lines_Button.setIconSize(QtCore.QSize(70, 70))
            QtCore.QObject.connect(self.Horizontal_Lines_Button, QtCore.SIGNAL("clicked()"),self.Create_Mapping_Pathway)

        if 3 in Available:
            self.UserDefined_Button = QtGui.QPushButton(MapWidget) #creation du bouton
            self.UserDefined_Button.setGeometry(210,10,80,80) #taille et position (X,Y,Xsize,Ysize)
            self.UserDefined_Button.setText("User Defined")
            QtCore.QObject.connect(self.UserDefined_Button, QtCore.SIGNAL("clicked()"),self.Define_Non_Grid_Positions)
        
        if 4 in Available:
            self.GridGenerator_Button = QtGui.QPushButton(MapWidget) #creation du bouton
            self.GridGenerator_Button.setGeometry(310,10,80,80) #taille et position (X,Y,Xsize,Ysize)
            self.GridGenerator_Button.setText("AutoFill Grid")
            QtCore.QObject.connect(self.GridGenerator_Button, QtCore.SIGNAL("clicked()"),self.AutoFill_Grid)
  
        self.CM = Map.Map() 
        self.Map_tools_Widget.show()  
        
     
    def Set_Auto_Coordinates_Visible(self):        
        #TODO : Add Number of Steps
        for i in [self.X_Start_Field,
                  self.X_End_Field,
                  self.X_Step_Field,
                  self.Y_Start_Field,
                  self.Y_End_Field,
                  self.Y_Step_Field]:
            if self.CM.Scanning_Direction_Mode == 'UserDefined':
                i.setEnabled(False)
            else:
                i.setEnabled(True)
                
                


                
    def Create_Mapping_Pathway(self):
        
        """
        Permet de creer les dictionnaires de coordonnées
        Un scan en X est un scan par ligne successives
        La fonction est appelée automatiquement si on lance le Mapping
        Elle peut aussi etre appelée séparement, dans le but de sauver les coordonnées.
        Dans les 2 cas, une fois passée, self.Bypass devient True
        
        self.CM.Sorted_Y_Coordinates : An array of the Y coordinates of the experiment, in one turn
        self.CM.Sorted_X_Coordinates : An array of the X coordinates of the experiment, in one turn
        self.CM.Sorted_X_and_Y_Coordinates : An array of the (X,Y) coordinates of the experiment, in one turn
        
        self.CM.Sorted_X_and_Y_Coordinates_Full : An array of the (X,Y) coordinates of the experiment, in all the experiment
        self.CM.Sorted_Y_Coordinates : An array of the Y coordinates of the experiment, in all the experiment
        self.CM.Sorted_X_Coordinates : An array of the X coordinates of the experiment, in all the experiment     
        
        int(self.Number_of_Turns.text()) is the number of turns
        """
        

        self.Correction_of_Abnormal_Parameters_for_Mapping()
        
        if QtCore.QObject().sender() ==  self.Vertical_Lines_Button or QtCore.QObject().sender() ==  self.Horizontal_Lines_Button:
            self.CM.Scanning_Direction_Mode = None   

        try:
            List_of_X_Points = range(int(self.X_Start_Field.text()),int(self.X_End_Field.text())+int(self.X_Step_Field.text()),int(self.X_Step_Field.text()))        #liste les coordonnées en X
            self.Number_of_X_Points=len(List_of_X_Points) #Number of X-axis points
            List_of_Y_Points = range(int(self.Y_Start_Field.text()),int(self.Y_End_Field.text())+int(self.Y_Step_Field.text()),int(self.Y_Step_Field.text()))         #liste les coordonnées en Y
            self.Number_of_Y_Points=len(List_of_Y_Points) #Number of Y-axis points   
        except ValueError:
            msg="""
            <b>Error</b>
            
            <p>Was each mapping complete, or was your mapping interrupted?
            The total number of sweeps must be EXACTLY #points in a grid X #turns
            If the mapping is irregular you might consider a user defined mapping
            
            """  
            Infos.Error(msg)
            return
            
        if QtCore.QObject().sender() ==  self.Vertical_Lines_Button or self.CM.Scanning_Direction_Mode == "X":
            self.CM.GenerateGridCoordinates("X",List_of_X_Points, List_of_Y_Points)
        elif QtCore.QObject().sender() ==  self.Horizontal_Lines_Button or self.CM.Scanning_Direction_Mode == "Y":
            self.CM.GenerateGridCoordinates("Y",List_of_X_Points, List_of_Y_Points)

        try:
            self.Correction_of_Abnormal_Parameters_for_Mapping()
            self.Set_Auto_Coordinates_Visible() 
            self.Set_Coordinates_in_Tag_Variable()
            self.AutoComplete_Missing_Fields()
            
        except ValueError:
            msg="""
            <b>Error</b>
            <p>Please indicate the number of turns, and re-set coordinates
            """
            Infos.Error(msg)
            return()
            
            
        if QtCore.QObject().sender() ==  self.Vertical_Lines_Button or QtCore.QObject().sender() ==  self.Horizontal_Lines_Button:   
            self.Mapping_Pattern = MyMplWidget(title='Mapping Pattern')
            self.Mapping_Pattern.canvas.axes.plot(self.CM.Sorted_X_Coordinates,self.CM.Sorted_Y_Coordinates,'o-',-400,-400,400,400)

            self.Mapping_Pattern.canvas.axes.arrow(self.CM.Sorted_X_Coordinates[-2],self.CM.Sorted_Y_Coordinates[-2],(self.CM.Sorted_X_Coordinates[-1]-self.CM.Sorted_X_Coordinates[-2]),(self.CM.Sorted_Y_Coordinates[-1]-self.CM.Sorted_Y_Coordinates[-2]),length_includes_head=True,width=1, head_width=int(self.X_Step_Field.text()),head_length=int(self.X_Step_Field.text()),fc='r')
            self.Mapping_Pattern.canvas.axes.annotate("expected Nb of Sweeps : "+str(len(self.CM.Sorted_Y_Coordinates_Full)),(-380,350),backgroundcolor='white',alpha=0.4)
            self.Map_tools_Widget.close()
            self.Mapping_Pattern.show()
    

    def AutoFill_Grid(self):
        
        #TODO : detect modulo, so that when the step doesn't exactly match we can correct if
        #TODO : also, coordinates should be set with float, only int a working now
        if self.X_Start_Field.text() == '' or self.X_End_Field.text() == '':
            self.X_Start_Field.setText('-100')
            self.X_End_Field.setText('100')
        if self.Y_Start_Field.text() == '' or self.Y_End_Field.text() == '':
            self.Y_Start_Field.setText('-100')
            self.Y_End_Field.setText('100')
        if self.Number_of_Turns.text() == '':    
            self.Number_of_Turns.setText('1') 
            
        Xe=int(self.X_End_Field.text())
        Xs=int(self.X_Start_Field.text())
        Xn=int(self.X_Number_Field.text())-1 #because if there are 6 points on a line, there are 5 intervals
        N=int(self.Number_of_Turns.text())
        Ye=int(self.Y_End_Field.text())
        Ys=int(self.Y_Start_Field.text())
        Yn=int(self.Y_Number_Field.text())-1 #because if there are 6 points on a line, there are 5 intervals

        self.X_Step_Field.setText(str((Xe-Xs)/abs(Xn)))#(Xn*N*Yn)))
        self.Y_Step_Field.setText(str((Ye-Ys)/abs(Yn)))#(Yn*N*Xn)))
        
        L=(Yn+1)*(Xn+1)*N
        print 'expected number of sweep is ', L
        print 'actual number is', len(Requete.Analogsignal_ids)
        
        if L != len(Requete.Analogsignal_ids):
            raise IOError('The number of recordings do not match your mapping plan')
        else:
            self.Define_Coordinates(Available=[1,2])
            
            
    def AutoComplete_Missing_Fields(self):
        
        Xe=int(self.X_End_Field.text())
        Xs=int(self.X_Start_Field.text())
        Xst=int(self.X_Step_Field.text())
        Ye=int(self.Y_End_Field.text())
        Ys=int(self.Y_Start_Field.text())
        Yst=int(self.Y_Step_Field.text())    
        PreviousX=self.X_Number_Field.text() #Can be ''
        PreviousY=self.Y_Number_Field.text() #Can be ''
        NewX=(Xe-Xs)/(Xst)+1
        NewY=(Ye-Ys)/(Yst)+1
        
        if PreviousX == '':
            self.X_Number_Field.setText(str(NewX))
        elif PreviousX != NewX:
            print 'Warning, number of X steps was adjusted using X_Step Value'
            self.X_Number_Field.setText(str(NewX))
        if PreviousY == '':
            self.Y_Number_Field.setText(str(NewY))
        elif PreviousY != NewY:
            print 'Warning, number of Y steps was adjusted using Y_Step Value'
            self.Y_Number_Field.setText(str(NewY))            

    def Set_Coordinates_in_Tag_Variable(self):
        
        """
        This function fills the Requete.tag field, so you can save coordinates

        """
        warning_displayed = False
        for i in range(len(Requete.Analogsignal_ids)):
            try:                
                Requete.tag["X_coord"][i]=self.CM.Sorted_X_Coordinates_Full[i]
                Requete.tag["Y_coord"][i]=self.CM.Sorted_Y_Coordinates_Full[i]
            except IndexError: 
                #TODO :
                #Add an autocorrection for number of turns
                if warning_displayed == False:
                    msg="""
                    <b>Error</b>
                    <p>Did you set the grid boundaries correctly?
                    is the number of turns right?
                    Was each mapping complete, or was your mapping interrupted?
                    The total number of sweeps must be EXACTLY #points in a grid X #turns
                    If the mapping is irregular you might consider a user defined mapping
                    """
                    Infos.Error(msg)
                    warning_displayed = True

                print "Index error for sweep ", i
                Requete.tag["X_coord"][i]=None
                Requete.tag["Y_coord"][i]=None


        Requete.tag["XSteps"]=['']*len(Requete.Analogsignal_ids)
        Requete.tag["YSteps"]=['']*len(Requete.Analogsignal_ids)
        Requete.tag["NumberofTurns"]=['']*len(Requete.Analogsignal_ids)
        Requete.tag["ScanWay"]=['']*len(Requete.Analogsignal_ids)
        
        for i in range(len(Requete.Analogsignal_ids)):
            Requete.tag["XSteps"][i]=str(self.X_Step_Field.text())
            Requete.tag["YSteps"][i]=str(self.Y_Step_Field.text())
            Requete.tag["NumberofTurns"][i]=str(self.Number_of_Turns.text())
            Requete.tag["ScanWay"][i]=self.CM.Scanning_Direction_Mode

        #self.Bypass=True

    def Create_Dictionnaries(self):
        """
        Base Mapping dictionnaries are created here
            self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary : {id:(X,Y)}
            self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary : {(X,Y):[id1,id2,id3...]}
            self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary : {id:sweep#}
            self.CM.Initially_Excluded_AnalogSignal_Ids : {sweep#:id} #It's a blacklist of initially unchecked sweeps
        """                

        self.CM.Initially_Excluded_AnalogSignal_Ids={}
#        try:
        for i,j in enumerate(Requete.Analogsignal_ids):
            if Requete.tag["Selection"][i][self.CurrentChannel]==0:
                self.CM.Initially_Excluded_AnalogSignal_Ids[i] = j[self.CurrentChannel]
       
        #Creation des liste de coordonnées
        self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary={} #Keys = ids , Values = (X,Y)
        self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary={} #Keys = ids , Values = Sweep #
        for i,j in enumerate(Requete.Analogsignal_ids):
            self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary[j[self.CurrentChannel]]=i
            if Requete.tag["Selection"][i][self.CurrentChannel] != 0:
                try:
                    self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[j[self.CurrentChannel]]=(int(Requete.tag["X_coord"][i]),int(Requete.tag["Y_coord"][i]))
                except TypeError:
                    msg="""
                    <b>Error</b>
                    <p>Coordinates or number of turns are wrong
                    please correct and re-Define Coordinates
                    """
                    Infos.Error(msg)    
                    return
            else:
                self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[j[self.CurrentChannel]]=None
        
        #On inverse le dictionaire
        self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary={}  #Keys = (X,Y)coordinates , Values = array of corresponding ids
        for i,j in self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary.iteritems():
            self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[j] = self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary.get(j, [])
            self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[j].append(i)
            if self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary.has_key(None) == True: #None coordinates are deleted
                del self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[None]         
        
#        except TypeError:
#            msg="""
#            <b>Error</b>
#            <p>Did you set the grid boundaries correctly?
#            Was each mapping complete, or was your mapping interrupted?
#            The total number of sweeps must be EXACTLY #points in a grid X #turns
#            If the mapping is irregular you might consider a user defined mapping
#            """
#            Infos.Error(msg)
#            return True             

        self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary={}
        self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary={}
        self.CM.Coordinates_and_Corresponding_Amplitudes1_Dictionnary={}
        self.CM.Coordinates_and_Corresponding_Charges1_Dictionnary={}        
        self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary={}
        self.Coordinates_and_Corresponding_Mean_Variance1_Dictionnary={}

    def Find_Corresponding_Coordinates(self):
        
        """
        Permet de trouver les coordonnées correspondant à un sweep donnée
        N'est activé que si des coordonnées existent (find coordinates a été lancé, ou sauvé depuis une analyse précédente)
        """

        if self.CM.Scanning_Direction_Mode == "X" or self.CM.Scanning_Direction_Mode == "Y":
            try: #write the value
                self.X_Neuron.setText(str(self.CM.Sorted_X_and_Y_Coordinates_Full[int(self.SweepPosition.text())][0]))
                self.Y_Neuron.setText(str(self.CM.Sorted_X_and_Y_Coordinates_Full[int(self.SweepPosition.text())][1]))
            except AttributeError:
                self.Define_Coordinates()
                self.X_Neuron.setText('retry!')
                self.Y_Neuron.setText('retry!')
        else:
            self.Define_Coordinates()
            
    def Average_Traces_By_Position(self):

        """
        Cette fonction permet de faire la moyenne des traces points par points.
        Les parametres utilisés sont ceux du menu Measure  .
        On y créé des dictionnaires utiles:
            self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary : {id:(X,Y)}
            self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary : {(X,Y):[id1,id2,id3...]}
            self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary : {id:sweep#}
            self.CM.Initially_Excluded_AnalogSignal_Ids : {sweep#:id} #It's a blacklist
        """        

        abort=self.Create_Dictionnaries()        
        AllC1values=[]
        AllA1values=[]
        if abort == True:
            return

        counter=0
        #On fait une moyenne par position
        #TODO : only channel 1 can be mapped now
        for keys in self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary:
            Navigate.UnTag_All_Traces(ProgressDisplay=False)
            for i in self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[keys]:
                Requete.tag["Selection"][self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary[i]][self.CurrentChannel]=1 #Keys = ids , Values = Sweepnumber

            self.mappingprogress.setMinimum(0)
            self.mappingprogress.setMaximum(len(self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary)-1)
            self.mappingprogress.setValue(counter)
            MA1,MA2,MA3,MC1,MC2,MC3,current_averaged_trace,current_List_of_Ids = Analysis.Measure_on_Average(Rendering=False,ProgressDisplay=False,Channel=[self.CurrentChannel])
            try:
                self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary[keys]=MA1 #one point array
                self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary[keys]=MC1 #one point array
                #self.Coordinates_and_Corresponding_Mean_Variance1_Dictionnary[keys]=0
                self.CM.Coordinates_and_Corresponding_Amplitudes1_Dictionnary=None
                self.CM.Coordinates_and_Corresponding_Charges1_Dictionnary=None
                self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary[keys]=None
                AllC1values.append(MC1)
                AllA1values.append(MA1)
                counter+=1
            except TypeError:
                msg="""
                <b>Tag Error</b>
                <p>Error at position %s, You must set the Coordinates!
                """ %str(keys)
                Infos.Error(msg)
                counter+=1

        
        Navigate.Tag_All_Traces(ProgressDisplay=False)
        #print self.CM.Initially_Excluded_AnalogSignal_Ids 
        for i in self.CM.Initially_Excluded_AnalogSignal_Ids: #pour chaque key de la Initially_Excluded_AnalogSignal_Ids (= les sweepnumber)
            Requete.tag["Selection"][i][self.CurrentChannel]=0

        
        # TODO: if the mapping contains more theoretical points than real point, ther eis a value error here
        # this should be raised somewhere to warn the user
#        if self.Analysis_mode=="Analysis.Amplitudes_1":
#            self.Manual_Min_Field.setText(str(numpy.nanmin(AllA1values)))
#            self.Manual_Max_Field.setText(str(numpy.nanmax(AllA1values)))
#        elif self.Analysis_mode=="Analysis.Charges_1":
        

        if len(AllC1values)<1 or len(AllA1values)<1:
            msg="""
            <b>No Data</b>
            <p>Did you tag any trace?
            """
            Infos.Error(msg)    
            return
        
        if self.NormalizeMappingMode == 'Charge':
            Min=numpy.nanmin(AllC1values)
            Max=numpy.nanmax(AllC1values)
        elif self.NormalizeMappingMode == 'Amplitude':
            Min=numpy.nanmin(AllA1values)
            Max=numpy.nanmax(AllA1values)

        if self.CM.Types_of_Events_to_Measure == 'Negative':
            #because when events are negative, they are inverted in the analysis
            Min*=-1
            Max*=-1  
            self.Manual_Min_Field.setText(str(Max))
            self.Manual_Max_Field.setText(str(Min))            
        else:            
            self.Manual_Min_Field.setText(str(Min))
            self.Manual_Max_Field.setText(str(Max))         

        pyplot.figure()
        pyplot.plot(AllC1values)
        pyplot.plot(AllA1values)
        pyplot.show()

        self.Activate_Map.setEnabled(True)
        self.SuccessRate_Ready=False
        self.AllowToAddaMapping=True

    def Measure_Traces_By_Position(self,Measure_Filtered=False,Silent=False):
        """
        Cette fonction permet de faire les mesurese des traces points par points.
        Les parametres utilisés sont de du menu Measure  .
        On y créé des dictionnaires utiles:
            self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary : {id:(X,Y)}
            self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary : {(X,Y):[id1,id2,id3...]}
            self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary : {id:sweep#}
            self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary : {(X,Y): mean amp1 }
            self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary : {(X,Y): mean surface}
            self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary : {(X,Y) : Success rate}
            self.CM.Initially_Excluded_AnalogSignal_Ids : {excluded ids}
        Et 2 array importants:
            self.CM.Success_list
            self.CM.Success_rate
        """        
 

        abort=self.Create_Dictionnaries()  
        AllC1values=[]
        AllA1values=[]
        AllV1values=[]
        if abort == True:
            return 
            
        if self.Thresholding_Mode.currentIndex() == 1: #seuil en pA
            thr=float(self.Thresholding_Mode_Input_Field.text())
            self.Analysis_mode="Analysis.Amplitudes_1"
            
        elif self.Thresholding_Mode.currentIndex() == 2: #seuil en pC
            thr=float(self.Thresholding_Mode_Input_Field.text())  
            self.Analysis_mode="Analysis.Charges_1"
         
            
        elif self.Thresholding_Mode.currentIndex() == 5: #Combo regularité ET Seuil moyen
        
            choice, ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'Input Dialog', 
                'Please Enter the desired Threshold and the Unit (pA or pC):')
            if ok:   
                choice=str(choice)
                choice=choice.replace(' ','') #enleve les blanc
                
                try:
                    Value=float(choice[:-2])
                    if choice[-2:]=="pA":
                        self.Analysis_mode="Analysis.Amplitudes_1"
                        thr=Value
                    elif choice[-2:]=="pC":
                        self.Analysis_mode="Analysis.Charges_1"
                        thr=Value
                    else:
                        msg="""
                        <b>Error</b>
                        <p>Please re-try
                        """  
                        Infos.Error(msg)
                        raise "Error, the analysis is aborted"                        
                except ValueError:
                    msg="""
                    <b>Unit Error</b>
                    <p>You forget the unit!
                    """
                    Infos.Error(msg)
                    raise "Error in setting the Value"
            else:
                raise "Measure Cancelled"
                    
            choice, ok = QtGui.QInputDialog.getDouble(Main.FilteringWidget, 'Input Dialog', 
                'Now, please choose the desired mean Threshold in '+str(choice[-2:]))
            if ok:
                self.mean_threshold=float(choice)                    
            else:
                raise "Measure Cancelled"    

        elif self.Thresholding_Mode.currentIndex() == 6: #Variance
            thr=float(self.Thresholding_Mode_Input_Field.text())  
            self.Analysis_mode="Analysis.Variance_1"            

        elif self.Thresholding_Mode.currentIndex() == 7: #of events
            self.Analysis_mode="Analysis.Events"
            thr=float(self.Thresholding_Mode_Input_Field.text())
       
        #If no threshold was set, detection threshold is automatically set at -2 pA and mean threshold at -1 pA       
        else: 
            print "warning, AutoThreshold"
            print  "If no threshold was set, detection threshold is automatically set at -2 pA and mean threshold at -1 pA "      
            self.Thresholding_Mode.setCurrentIndex(1)
            self.Thresholding_Mode_Input_Field.setText("-2")       
            thr=float(self.Thresholding_Mode_Input_Field.text())
            self.mean_threshold=-1


        if self.Thresholding_Mode.currentIndex() == 7:
            self.CM.Types_of_Events_to_Measure = 'Positive'
            A1,A2,A3,C1,C2,C3=Analysis.Count_Events()
            for i,j in enumerate(A1):
                if j==0:
                   A1[i]=1E-30
                   C1[i]=1E-30          
        else:
            A1,A2,A3,C1,C2,C3 = Analysis.Measure(Rendering=False,Measure_Filtered=Measure_Filtered,Silent=Silent)

        #For each point, the measure is done. Average of individual measures is stored in self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary and self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary
        #array of all measured values is stored in self.CM.Coordinates_and_Corresponding_Amplitudes1_Dictionnary and self.CM.Coordinates_and_Corresponding_Charges1_Dictionnary
        for keys in self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary:
            
            accepted=0
            number_of_sweep_at_this_position=0
            currentIdsofInterest=[]

            #Navigate.UnTag_All_Traces()
            for i in self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[keys]:
                #i are all Analogsigna id at this point
                currentIdsofInterest.append(self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary[i])
                number_of_sweep_at_this_position+=1
            for i in A1:#eval(self.Analysis_mode):
                if self.CM.Types_of_Events_to_Measure == 'Negative' and float(i) <= float(thr):
                   accepted+=1 
                elif self.CM.Types_of_Events_to_Measure == 'Positive' and float(i) >= float(thr):
                   accepted+=1  
            
            A1loc=[]
            C1loc=[]
            V1loc=[]
            for i in range(len(A1)) :
                if i in currentIdsofInterest:
                    A1loc.append(A1[i])
                    C1loc.append(C1[i])
                    V1loc.append(A1[i])
                else:
                    A1loc.append(numpy.nan)
                    C1loc.append(numpy.nan)  
                    V1loc.append(numpy.nan) 
            
            if Silent == False:
                print "on a total of "+str(number_of_sweep_at_this_position)+" ,"+str(accepted)+" were accepted"
            success_rate=float(accepted)/float(number_of_sweep_at_this_position)

            self.CM.Coordinates_and_Corresponding_Amplitudes1_Dictionnary[keys]=A1loc
            self.CM.Coordinates_and_Corresponding_Charges1_Dictionnary[keys]=C1loc
            self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary[keys]=stats.nanmean(A1loc)
            self.Coordinates_and_Corresponding_Mean_Variance1_Dictionnary[keys]=stats.nanstd(V1loc)
            self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary[keys]=stats.nanmean(C1loc)                
            self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary[keys]=success_rate   
            AllC1values.append(stats.nanmean(C1loc))  
            AllA1values.append(stats.nanmean(A1loc)) 
            AllV1values.append(stats.nanstd(V1loc))
            #The % of values over thr is stored self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary

#                
#                counter+=1
#            except TypeError:
#                msgBox = QtGui.QMessageBox()
#                msgBox.setText(
#                """
#                <b>Tag Error</b>
#                <p>You must set correctly the Coordinates!
#                """)   
#                msgBox.exec_()
#                counter+=1         
        
             

        #On restaure les tags initiaux
        Navigate.Tag_All_Traces(ProgressDisplay=False)
        for i in range(len(Requete.Analogsignal_ids)):

            Requete.tag["Selection"][i][self.CurrentChannel]=1
        for i in self.CM.Initially_Excluded_AnalogSignal_Ids: #pour chaque key de la Initially_Excluded_AnalogSignal_Ids (= les sweepnumber)
            Requete.tag["Selection"][i][self.CurrentChannel]=0        
        
        print 'current', self.Thresholding_Mode.currentIndex()
        #Except in Combo mode, after every other measure, the self.Thresholding_Mode is set to % of success (--> 4)
        if self.Thresholding_Mode.currentIndex() == 5:
            pass
        elif self.Thresholding_Mode.currentIndex() == 7:
            self.Thresholding_Mode.setCurrentIndex(0) 
        else:
            self.Thresholding_Mode.setCurrentIndex(4) 
            self.Thresholding_Mode_Input_Field.setText('0.0')    

        if self.Analysis_mode=="Analysis.Amplitudes_1":
            Min=numpy.nanmin(AllA1values)
            Max=numpy.nanmax(AllA1values)
            
        elif self.Analysis_mode=="Analysis.Charges_1":
            Min=numpy.nanmin(AllC1values)
            Max=numpy.nanmax(AllC1values)

        elif self.Analysis_mode=="Analysis.Variance_1":
            Min=numpy.nanmin(AllV1values)
            Max=numpy.nanmax(AllV1values)
            

        if self.CM.Types_of_Events_to_Measure == 'Negative':
            #because when events are negative, they are inverted in the analysis
            Min*=-1
            Max*=-1  
            self.Manual_Min_Field.setText(str(Max))
            self.Manual_Max_Field.setText(str(Min))            
        else:            
            self.Manual_Min_Field.setText(str(Min))
            self.Manual_Max_Field.setText(str(Max))        

        self.Activate_Map.setEnabled(True)            
        self.SuccessRate_Ready=True 
        self.AllowToAddaMapping=True
        
    def Correspondance(self):
        
        self.ASid_to_SweepNb={}
        for i,j in enumerate(Requete.Analogsignal_ids):
            self.ASid_to_SweepNb[j]=i  
            
        self.STid_to_SweepNb={}
        try:
            for i,j in enumerate(Requete.Spiketrain_ids):
                self.ASid_to_SweepNb[j]=i              
        except:
            self.STid_to_SweepNb=" No Spiketrains "
           
        self.Segid_to_SweepNb={}
        for i,j in enumerate(Requete.Segment_ids):
            self.Segid_to_SweepNb[j]=i  
            

        msg="""
        <p><b>Segment.id to Sweep Number</b>
        <p>"""+str(self.Segid_to_SweepNb)+"""
        <p><b>Analogsignal.id to Sweep Number</b>
        <p>"""+str(self.ASid_to_SweepNb)+"""
        <p><b>Spiketrain.id to Sweep Number</b>
        <p>"""+str(self.STid_to_SweepNb)+"""
        """   
        Infos.Error(msg)
 

    def One_Stim_Average(self,X=None,Y=None,Silent=True): 
        
        """
        This function allows to display all tagged traces at position X - Y. By the way, we check that self.CM.Scanning_Direction_Mode contains some information
        """
        
        self.CM.Initially_Excluded_AnalogSignal_Ids={}
        blacklist=[]
        for i,j in enumerate(Requete.Analogsignal_ids):
            if Requete.tag["Selection"][i][self.CurrentChannel]==0:
                blacklist.append(j)
                self.CM.Initially_Excluded_AnalogSignal_Ids[i] = j
        
        print self.CM.Initially_Excluded_AnalogSignal_Ids, 'excluded'
        if self.CM.Scanning_Direction_Mode == "X" or self.CM.Scanning_Direction_Mode == "Y":
            pass
        else:
            abort=self.Create_Dictionnaries()        
            if abort == True:
                return 

        #If the function is called by 'Local Average', No X or Y parameters are passed, so they are read from self.X_Neuron and self.Y_Neuron
        if X == None and Y == None:
            if self.SweepPosition.text() == "" or None:
                keys=(int(self.X_Neuron.text()),int(self.Y_Neuron.text()))
            else:
                try:
                    self.X_Neuron.setText(str(self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[Requete.Analogsignal_ids[int(self.SweepPosition.text())][self.CurrentChannel]][0]))
                    self.Y_Neuron.setText(str(self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[Requete.Analogsignal_ids[int(self.SweepPosition.text())][self.CurrentChannel]][1]))
                    keys=self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[Requete.Analogsignal_ids[int(self.SweepPosition.text())][self.CurrentChannel]]
                except TypeError:
                    msg="""
                    This position contains no Data (Perhaps everything is unttaged)"""
                    Infos.Error(msg)
                    return    
                except AttributeError: #if analysi has never beeen done, we create the needed dict
                    abort=self.Create_Dictionnaries()        
                    if abort == True:
                        return 
                    self.X_Neuron.setText(str(self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[Requete.Analogsignal_ids[int(self.SweepPosition.text())][self.CurrentChannel]][0]))
                    self.Y_Neuron.setText(str(self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[Requete.Analogsignal_ids[int(self.SweepPosition.text())][self.CurrentChannel]][1]))
                    keys=self.CM.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary[Requete.Analogsignal_ids[int(self.SweepPosition.text())][self.CurrentChannel]]                                     
        #Otherwise, X and Y can be directly passed      
        else:
            keys=(X,Y) 
            
            
           
        Navigate.UnTag_All_Traces()
        
        
        self.Currently_Used_Sweep_nb_for_Local_Average=[]
        
        
        #try: #si la position est calculée directement au cours de l'analyse, les positions sont des int
        try:
            for i in self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[keys]:
                if i not in blacklist:

                    Requete.tag["Selection"][self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary[i]][self.CurrentChannel]=1 #Keys = ids , Values = Sweepnumber
                    self.Currently_Used_Sweep_nb_for_Local_Average.append(self.CM.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary[i])
            
            if Silent==False:
                print "Average Amplitudes on position ",keys
                print "Average On ",len(self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[keys])," Sweeps"
                print "Sweep # ",self.Currently_Used_Sweep_nb_for_Local_Average," were used"
    
            Analysis.Measure_on_Average(Display_Superimposed_Traces=True,Position=keys,Channel=[self.CurrentChannel]) #list of ids could be List_of_Ids=self.CM.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary[keys]



        except KeyError: #si la position est lue depuis la sauvegarde, les coordonnées sont des str, a fixer a l'occasion
            msg="""
            This position contains no Data (Perhaps everything is unttaged)"""
            Infos.Error(msg)  

        
        finally: #si jamais les coordonnées n'existent pas, on resaure les tags

            Navigate.Tag_All_Traces()
            if Silent == False:
                print Requete.tag["Selection"][self.CurrentChannel]

            for i in self.CM.Initially_Excluded_AnalogSignal_Ids: #pour chaque key de la Initially_Excluded_AnalogSignal_Ids (= les sweepnumber)
                Requete.tag["Selection"][i][self.CurrentChannel]=0              


    def DisplayMode(self,Display):
        '''
        This function allow to preprogram some specific set of config
        '''
        if Display == 1 :
            self.Thresholding_Mode.setCurrentIndex(0)            
            self.Amplitudes_Display_Mode.setCurrentIndex(0)
            self.Charges_Display_Mode.setCurrentIndex(2)
            self.Update_Display_Parameters()
        elif Display == 2 :
            self.Thresholding_Mode.setCurrentIndex(0)            
            self.Amplitudes_Display_Mode.setCurrentIndex(2)
            self.Charges_Display_Mode.setCurrentIndex(0) 
            self.Update_Display_Parameters()
        elif Display == 3 :
            self.Thresholding_Mode.setCurrentIndex(0)
            self.Amplitudes_Display_Mode.setCurrentIndex(0)
            self.Charges_Display_Mode.setCurrentIndex(1)  
            self.Update_Display_Parameters()        
        
    def ObjectiveParameters(self,ObjectiveIndex):
        #TODO : Move to a parameter file
        #Entrer ici les limites du champ CCD [Xupperleft, Yupperleft, Xlowerright,Ylowerright]
        #Xleft, XRight, Yleft, Yright
        if ObjectiveIndex == 0:
            self.CCDlimit=[-400,400,400,-400] #Y is reversed 
            #self.CCDlimit=[-400*float(self.Stim_Resolution.text()),400*float(self.Stim_Resolution.text()),400*float(self.Stim_Resolution.text()),-400*float(self.Stim_Resolution.text())]
        elif ObjectiveIndex == 1:
            self.CCDlimit=[-205+int(self.X_Offset.text()),-126+int(self.Y_Offset.text()),186+int(self.X_Offset.text()),175+int(self.Y_Offset.text())]#x=391,y=301        
        elif ObjectiveIndex == 2:
            self.CCDlimit=[-320,320,260,-212] 
        
        return self.CCDlimit
        #Could be used
        #Mapping_Field_Length=abs(self.CCDlimit[0]-self.CCDlimit[2])
        #Mapping_Field_Height=abs(self.CCDlimit[1]-self.CCDlimit[3])        
        
    def ModeSpecificProcessing(self,Mode,Local_Amplitude,Local_Surface,Local_Success):
        #In this condition, no threshold is applied, and all view are possible, because Amplitudes and charges were measured correctly
        
        
        if Mode == 0:
            print "Classic Normalized view"
        
        elif Mode == 1 or Mode == 2:
            if Mode == 1: var=Local_Amplitude
            if Mode == 2: var=Local_Surface   
            print "Amplitude/Charge Thresholded view"   
            try:
                thr=float(self.Thresholding_Mode_Input_Field.text())
                for i,j in enumerate(var):
                    print Local_Amplitude[i], Local_Surface[i]
                    if self.CM.Types_of_Events_to_Measure == 'Negative':
                        if j<thr:
                            Local_Amplitude[i]=-0.75
                            Local_Surface[i]=-1
                        else:
                            Local_Amplitude[i]=0.0
                            Local_Surface[i]=0.0
                    elif self.CM.Types_of_Events_to_Measure == 'Positive':
                        if j>thr:
                            Local_Amplitude[i]=0.75
                            Local_Surface[i]=1
                        else:
                            Local_Amplitude[i]=0.0
                            Local_Surface[i]=0.0                            
            except ValueError:
                msg="""
                <b>Error</b>
                <p>Please set correct Threshold value
                """  
                Infos.Error(msg)                            
        elif Mode == 3:
            print "% of Max amplitude Thresholded view"     
            
            try:
                thr=float(self.Thresholding_Mode_Input_Field.text())
                if self.CM.Types_of_Events_to_Measure == 'Negative':
                    Max=float(numpy.min(Local_Amplitude))
                elif self.CM.Types_of_Events_to_Measure == 'Positive':
                    Max=float(numpy.max(Local_Amplitude))  
                    
                for i,j in enumerate(Local_Amplitude):
                    
                    if (j*100)/Max > thr:
                        if self.CM.Types_of_Events_to_Measure == 'Negative': Local_Amplitude[i]=-0.75
                        elif self.CM.Types_of_Events_to_Measure == 'Positive': Local_Amplitude[i]=0.75    
                        Local_Surface[i]=1
                    else:
                        Local_Amplitude[i]=0.0
                        Local_Surface[i]=0.0

            except ValueError:
                msg="""
                <b>Error</b>
                <p>Please set a value in % (between 0 and 100)
                """       
                Infos.Error(msg)          
        

        #In this condition, the value in self.Thresholding_Mode_Input_Field is used as threshold. 
        #Local_Success corresponds to the % of events over the defined threshold (which must be between 0 and 100).
        #It can only be used if a measure was done before with self.Thresholding_Mode.currentIndex() == 1, 2 or 3 (then self.SuccessRate_Ready = True)
        #if needed, same protocol could be implemented for charges...  
        elif Mode == 4:

            if self.SuccessRate_Ready==True:
                print "Success Rate Thresholded view"
                            
                #if self.CM.Charge == 'Color' and self.CM.Amplitude == 'None':
                try:
                    thr=float(self.Thresholding_Mode_Input_Field.text())/100
                    for i,j in enumerate(Local_Success):
                        if j>thr:
                            print 'Position validated, ',i," > ",thr,j
                            Local_Success[i]=j
                        else:
                            Local_Success[i]=0.0
                           
                except ValueError:
                    msg="""
                    <b>Error</b>
                    <p>Please set a value between 0 and 100 %
                    """      
                    Infos.Error(msg)
            else:
                msg="""
                <b>Error</b>
                <p>You Can't use success rate filter if you didn't do "Mapping Measure" 
                """ 
                Infos.Error(msg)                    

        elif Mode == 5:# to check, and implement Local_Success
            if self.SuccessRate_Ready==True:
                print "Amplitude or Charge AND success rate Thresholded view"  
                #if self.CM.Charge == 'Color' and self.CM.Amplitude == 'None':
                thr=float(self.Thresholding_Mode_Input_Field.text())/100
                
                #First, we use the good list, depending if thr was computed on amplitudes or charges
                if self.Analysis_mode=="Analysis.Charges_1":
                    Local_to_use=Local_Surface
                elif self.Analysis_mode=="Analysis.Amplitudes_1" or self.Analysis_mode=="Analysis.Variance_1":
                    Local_to_use=Local_Amplitude   
                    
                for i,j in enumerate(Local_to_use): 
                    
                    #Second,  We check if the mean value is over the defined self.mean_threshold, taking into account the sign of the signal
                    if (self.CM.Types_of_Events_to_Measure == 'Negative' and j < self.mean_threshold) or (self.CM.Types_of_Events_to_Measure == 'Positive' and j > self.mean_threshold):
                        print "At position ", str(i)," threshold mean is reached, ", j, " over ", self.mean_threshold
                        
                        Local_Surface[i]=j #if ok, the value is kept, otherwise it is set to zero
                        
                        #Third, if the success rate is over thr we set the value to 0.65 (green)
                        #otherwise, the value is put in dark red
                        if j > thr:
                            print 'Position validated, success rate over '+self.Thresholding_Mode_Input_Field.text()+" %"
                            if self.CM.Types_of_Events_to_Measure == 'Negative': Local_to_use[i]=-0.55
                            elif self.CM.Types_of_Events_to_Measure == 'Positive':Local_to_use[i]=0.55                                 
                        else:
                            if self.CM.Types_of_Events_to_Measure == 'Negative': Local_to_use[i]=-0.95
                            elif self.CM.Types_of_Events_to_Measure == 'Positive':Local_to_use[i]=0.95   
                            print 'Position not validated, success rate under '+self.Thresholding_Mode_Input_Field.text()+" %"
                                
                    else:
                        print "At position ", str(i),"threshold mean is not reached,", abs(j), "<", abs(self.mean_threshold)
                        Local_to_use[i]=0.0
            else:
                msg="""
                <b>Error</b>
                <p>You Can't use success rate filter if you didn't do "Mapping Measure" 
                """      
                Infos.Error(msg)
                
        elif Mode == 6:
            print "variance of Amplitude Thresholded view"   
            
            try:
                thr=float(self.Thresholding_Mode_Input_Field.text())
                for i,j in enumerate(Local_Amplitude):
                    if self.CM.Types_of_Events_to_Measure == 'Negative':
                        if j<thr:
                            Local_Amplitude[i]=-0.75
                            Local_Surface[i]=-1
                        else:
                            Local_Amplitude[i]=0.0
                            Local_Surface[i]=0.0
                    elif self.CM.Types_of_Events_to_Measure == 'Positive':
                        if j>thr:
                            Local_Amplitude[i]=0.75
                            Local_Surface[i]=1
                        else:
                            Local_Amplitude[i]=0.0
                            Local_Surface[i]=0.0                            
                       
            except ValueError:
                msg="""
                <b>Error</b>
                <p>Please set a value in pA
                """   
                Infos.Error(msg)
                
        elif Mode == 7:
            print "Spike Counting Mode"   

            thr=0.0
            for i,j in enumerate(Local_Amplitude):
                if self.CM.Types_of_Events_to_Measure == 'Negative':
                    if j<thr:
                        Local_Amplitude[i]=-0.75
                        Local_Surface[i]=-1
                    else:
                        Local_Amplitude[i]=0.0
                        Local_Surface[i]=0.0
                elif self.CM.Types_of_Events_to_Measure == 'Positive':
                    if j>thr:
                        Local_Amplitude[i]=0.75
                        Local_Surface[i]=1
                    else:
                        Local_Amplitude[i]=0.0
                        Local_Surface[i]=0.0 
                        
        return Local_Amplitude,Local_Surface,Local_Success
                            
    def Display_Mapping_Results(self,Objective=None,Display=None,Picture=None,BypassReMapping=False,Title='Mapping',Marker='s',Bypass_Measuring=False,NoWarning=False,MeshMap=True,ContourMap=True): 
        
        """
        This function compute all the values to do the mapping. It reads SynaptiQs Comboboxes to apply some thresholding
        You can use it manually in a simplified mode, by setting some paramters
        Picture is the full path of the wanted picture
        """
        
        if Objective == 'PM' : self.Objective.setCurrentIndex(0)
        elif Objective == 'CCD' : self.Objective.setCurrentIndex(1)
        elif Objective == 'UCL' : self.Objective.setCurrentIndex(2)
         
        self.DisplayMode(Display)

        if Picture != None:
            self.Current_Picture_for_the_Map=Picture

        self.Correction_of_Abnormal_Parameters_for_Mapping()
        PictureLimits = self.ObjectiveParameters(self.Objective.currentIndex())

        self.Wid = MyMplWidget()
        self.Wid.canvas.axes.set_axis_bgcolor('black')
        self.Wid.canvas.axes.grid(41,color='r')
        
        if BypassReMapping == False:
            if self.CM.Scanning_Direction_Mode != 'UserDefined':
                self.Create_Mapping_Pathway()
        
        if Bypass_Measuring == False:    
            #To avoid to alter the recorded values, a copy of individual and average measures is done
            try:
                Local_Amplitude=numpy.array([None]*len(self.CM.Sorted_X_and_Y_Coordinates))
                Local_Amplitude_sd=numpy.array([None]*len(self.CM.Sorted_X_and_Y_Coordinates))
                Local_Surface=numpy.array([None]*len(self.CM.Sorted_X_and_Y_Coordinates))
                Local_Surface_sd=numpy.array([None]*len(self.CM.Sorted_X_and_Y_Coordinates))
                Local_Success=numpy.array([None]*len(self.CM.Sorted_X_and_Y_Coordinates)) 
            except AttributeError:    
                msg="""
                <b>Mapping Error</b>
                <p>Please define correct coordinates first
                """
                Infos.Error(msg)    
                return
            
            for i,j in enumerate(self.CM.Sorted_X_and_Y_Coordinates):
                try:
                    Local_Amplitude[i]=self.CM.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary[j]
                    try:
                        Local_Amplitude_sd[i]=numpy.std(self.CM.Coordinates_and_Corresponding_Amplitudes1_Dictionnary[j])
                        Local_Surface_sd[i]=numpy.std(self.CM.Coordinates_and_Corresponding_Charges1_Dictionnary[j])
                    except TypeError: 
                        Local_Amplitude_sd[i]=0
                        Local_Surface_sd[i]=0
                    Local_Surface[i]=self.CM.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary[j]
                    Local_Success[i]=self.CM.Coordinates_and_Corresponding_Success_Rate_Dictionnary[j]
                except KeyError:
                    #TODO : Put NaN instead of 0
                    print 'No Data (or untagged data) at ', j #if some coordinates dissapeared, because completely Untagged     
                    Local_Amplitude[i]=0#numpy.NaN
                    Local_Amplitude_sd[i]=0
                    Local_Surface[i]=0#numpy.NaN 
                    Local_Surface_sd[i]=0
                    Local_Success[i]=0#numpy.NaN  
                except AttributeError: #if 'Mapping' object has no attribute 'Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary'
                    self.Define_Coordinates()
                    return
                    
        #####################        
        ##################### 
        
        #Because NaN are bad...
        for i,j in enumerate(Local_Amplitude):
            if numpy.math.isnan(j) == True :
                Local_Amplitude[i]=float(0.0)
           
        self.CM.Local_Amplitude,self.CM.Local_Surface,self.CM.Local_Success=self.ModeSpecificProcessing(self.Thresholding_Mode.currentIndex(),
                                                                                               Local_Amplitude,
                                                                                               Local_Surface,
                                                                                               Local_Success)        
        fig,X_coord,Y_coord,Color_values,Surface_values,mesh,contour=self.Make_the_Map(Title=Title,Marker=Marker,Bypass_Measuring=Bypass_Measuring,NoWarning=NoWarning,MeshMap=MeshMap,ContourMap=ContourMap)
        
        if self.AllowToAddaMapping == True:
            self.Mapping_ID = self.Mapping_ID + 1
            print "Mapping ID is " , self.Mapping_ID            
            setattr(Analysis,'Map'+str(self.Mapping_ID),deepcopy(self.CM))
            self.MappingID.addItem(str(self.Mapping_ID))
            self.MappingID.setCurrentIndex(self.Mapping_ID)
            self.AllowToAddaMapping=False
        
        return fig,X_coord,Y_coord,Color_values,Surface_values,mesh,contour
        
    def pointValue(self,x,y,power,smoothing,xv,yv,values):
        nominator=0
        denominator=0
        for i in range(0,len(values)):
            dist = sqrt((x-xv[i])*(x-xv[i])+(y-yv[i])*(y-yv[i])+smoothing*smoothing);
            #If the point is really close to one of the data points, return the data point value to avoid singularities
            if(dist<1E-30):
                return values[i]
            nominator=nominator+(values[i]/pow(dist,power))
            denominator=denominator+(1/pow(dist,power))
        #Return NODATA if the denominator is zero
        if denominator > 0.:
            value = nominator/denominator
        else:
            value = -9999.
        return value
    
    def invDist(self,xv,yv,values,xsize=100,ysize=100,power=2,smoothing=0,subsampling=1,minRange=0):
        #TODO : Scientifically not clear, but visually nice
        valuesGrid = numpy.zeros((ysize,xsize))
        for x in range(0,int(xsize)):
            for y in range(0,int(ysize)):
                valuesGrid[y][x] = self.pointValue(x*subsampling+minRange,y*subsampling+minRange,power,smoothing,xv,yv,values)
        return valuesGrid
    
    
    def SmoothMap(self,
                  X,
                  Y,
                  Val,
                  power=3.,
                  smoothing=10.,
                  subsampling=10.,
                  cmap='gnuplot',
                  Manual_Min_Field=None,
                  Manual_Max_Field=None,
                  Max_Valid_Dist=None,
                  MeshMap=True,
                  ContourMap=True):
        
        power=power
        smoothing=smoothing
        subsampling=subsampling
        
        p = None
        p2 = None
        
        
        xv = X
        yv = Y
        values = Val
    
        minRange=min(min(xv),min(yv)) #it's the negative value of x-axis AND y-axis
        maxRange=max(max(xv),max(yv))
        TotRange=maxRange-minRange
        print 'maximal extent is', TotRange
        print 'point resolution is', subsampling 
        
        print float(TotRange)/subsampling, "should be an integer. If it's not, check code"
        
        #Creating the output grid (100x100, in the example)
        ti = numpy.linspace(minRange,maxRange,TotRange/subsampling)
        XI, YI = numpy.meshgrid(ti, ti)
        #Creating the interpolation function and populating the output matrix value
        ZI = self.invDist(xv,yv,values,TotRange/subsampling,TotRange/subsampling,power,smoothing,subsampling,minRange)
        
        points=zip(X.ravel(), Y.ravel())
        refpoints=zip(XI.ravel(), YI.ravel())
        tree = scipy.spatial.cKDTree(points)
        z=ZI.ravel()
        

        #n = pyplot.normalize(0.0, 100.0)
        if self.Manual_Min_Field.text() != "":
            Min=float(self.Manual_Min_Field.text())
        elif Manual_Min_Field!= None:
            Min=float(Manual_Min_Field)
        else:
            Min=float(numpy.min(ZI))
            
        if self.Manual_Max_Field.text() != "":
            Max=float(self.Manual_Max_Field.text())
        elif Manual_Max_Field!= None:
            Max=float(Manual_Max_Field)                
        else:
            Max=float(numpy.max(ZI))  


        for j,i in enumerate(refpoints):
            if len(tree.query_ball_point((i[0],i[1]), float(Max_Valid_Dist))) == 0:
                z[j]=Min
                #TODO :
                #hatched pattern : ax.add_patch(mpl.patches.Rectangle((2,2),20,20,hatch='//////////',fill=False,snap=False))
       
        alpha=float(self.Transparency.text())
        
        if MeshMap == True:
            p = pyplot.figure() 
            mesh = p.add_subplot(1, 1, 1)
            try:
                pic = image.imread(str(self.Current_Picture_for_the_Map))
                mesh.imshow(pic,extent=(self.CCDlimit[0],self.CCDlimit[1],self.CCDlimit[2],self.CCDlimit[3]))
            except:
                pass          
            n=mesh.pcolor(XI, YI, ZI,cmap=cmap,vmin=Min,vmax=Max,shading='flat',edgecolors='none',alpha=alpha)
            mesh.set_title('Inv dist interpolation - power: ' + str(power) + ' smoothing: ' + str(smoothing))
            mesh.set_xlim([minRange, maxRange])
            mesh.set_ylim([minRange, maxRange])
            cbar = p.colorbar(n)
            #cbar.set_clim(Min,Max)
            p.show()
      


        if ContourMap == True:
            p2 = pyplot.figure()
            contour = p2.add_subplot(1, 1, 1)
            try:
                pic = image.imread(str(self.Current_Picture_for_the_Map))
                contour.imshow(pic,extent=(self.CCDlimit[0],self.CCDlimit[1],self.CCDlimit[2],self.CCDlimit[3]))
                #pyplot.imshow(self.pic,extent=(-320,320,-260,252),cmap=self.Image_ColorMap)
            except:
                pass   
            NewNumberOfLevels=(numpy.nanmax(ZI)-numpy.nanmin(ZI))/((Max-Min)/self.NumberOfLevels)
            
            n2=contour.contourf(XI, YI, ZI, int(NewNumberOfLevels) ,vmin=Min,vmax=Max,alpha=alpha,cmap=cmap)
            contour.set_xlim([minRange, maxRange])
            contour.set_ylim([minRange, maxRange]) 
            cbar2 = p2.colorbar(n2)
            #cbar2.set_clim(Min,Max)
            p2.show()
            
        return p,p2 #mesh,contour
            

    def NormalizeSurfaceAndColors(self,):
        '''
        For the Final Map, the surface must be >0
        '''
        #TODO : IMPORTANT, This should be improved
        #For display purpose, all value are set to positive, so negative currents are inverted    
        if self.CM.Types_of_Events_to_Measure == 'Negative':
            self.CM.Local_Amplitude*=-1
            self.CM.Local_Surface*=-1   
            print 'Your displaying Negative currents only'
        elif self.CM.Types_of_Events_to_Measure == 'Positive':
            print 'Your displaying Positive currents only'
        elif self.CM.Types_of_Events_to_Measure == 'Both':
            print 'Your displaying both Positive and Negative currents'
            
        #TODO : IMPORTANT,0 should be replaced by Nan
        if self.CM.Types_of_Events_to_Measure == 'Negative' or self.CM.Types_of_Events_to_Measure == 'Positive':
            for i,j in enumerate(self.CM.Local_Amplitude):
                if j<=float(0.0):
                    self.CM.Local_Amplitude[i]=0.0 
            for i,j in enumerate(self.CM.Local_Surface):
                if j<=float(0.0):
                    self.CM.Local_Surface[i]=0.0 
                
    def CreateColorScaleAndSurfaceScale(self,defaultsurface=100,defaultcolor=0.75,Bypass_Measuring=False,NoWarning=False):
        '''
        Depending on the options selected Charge, Surface Amplitude etc can 
        all be represented either as a color or as a Surface, or as a constant (defaultsurface, defaultcolor)
        self.CM.Charge,self.CM.Normalized_Surface,self.CM.Local_Surface can all be set using these parameters
        eg:
        if Charge has to be represented as a color, self.CM.Charge = 'Color'
        if Charge has to be represented as a surface, self.CM.Charge = 'Surface'
        if Charge has to be represented as a constant, 
        
        
        '''
        #Creating some default values, for color and surface, which can be optionally used
        surface=self.CM.Normalized_Surface=[defaultsurface]*len(self.CM.Local_Surface)
        color=self.CM.Normalized_Amplitude=[defaultcolor]*len(self.CM.Local_Surface) 
        for param in [[self.CM.Charge,self.CM.Normalized_Surface,self.CM.Local_Surface],[self.CM.Amplitude,self.CM.Normalized_Amplitude,self.CM.Local_Amplitude]]:
            if param[0] == 'Color':
                try:
                    if Bypass_Measuring == False:
                        param[1]=numpy.array(param[2])/(float(numpy.max(param[2])))
                    else:#So if you manually set the values, they are not normalized.
                        param[1]=numpy.array(param[2])/1.0
                except ZeroDivisionError:
                    param[1]=numpy.zeros(len(param[2]))
                color=param[1]
            elif param[0] == 'Surface':
                try:
                    if Bypass_Measuring == False:                    
                        param[1]=numpy.array(param[2])*500./(float(numpy.max(param[2])))
                    else:#So if you manually set the values, they are not normalized.
                        param[1]=numpy.array(param[2])*500./1.0                       
                except ZeroDivisionError:
                    print 'error detected'
                    param[1]=numpy.array([1E-30]*len(param[2]))                  
                surface=list(param[1])
                
        return color,surface         

    def CreateInteractiveGrid(self,colorbar,xlim=(-320, 320),ylim=(-260, 252),ColorBar=True,Labels=False,Title='',NoWarning=False):
        if ColorBar==True:
            self.Wid.canvas.fig.colorbar(colorbar)
            
        #self.Wid.canvas.axes.set_xlim(-400*float(self.Stim_Resolution.text()), 400*float(self.Stim_Resolution.text()))
        #self.Wid.canvas.axes.set_ylim(-400*float(self.Stim_Resolution.text()), 400*float(self.Stim_Resolution.text()))
         
        self.Wid.canvas.axes.set_xlim(self.CCDlimit[0],self.CCDlimit[1])
        self.Wid.canvas.axes.set_ylim(self.CCDlimit[2],self.CCDlimit[3])
        #self.Wid.canvas.axes.set_xlim(*xlim)
        #self.Wid.canvas.axes.set_ylim(*ylim)
                
        if Labels==True:
            self.Wid.canvas.axes.set_xlabel("X Distance (in um)")
            self.Wid.canvas.axes.set_ylabel("Y Distance (in um)")
            self.Wid.canvas.axes.set_title(Title)      #see title for more info      
        else:
            self.Wid.canvas.axes.set_axis_off()
        
        #TODO : these 3 parameteres do not belong here 
        self.Red_Channel = QtGui.QCheckBox()
        self.Green_Channel = QtGui.QCheckBox()
        self.Blue_Channel = QtGui.QCheckBox()
        
        check=[self.Red_Channel,self.Green_Channel,self.Blue_Channel]
        c=['Red','Green','Blue']
        disp=self.Display_Red,self.Display_Green,self.Display_Blue
        List = [list(a) for a in zip(check,c,disp)]
        hbox=QtGui.QHBoxLayout()
        for i in List:
            #i[0]=QtGui.QCheckBox()
            i[0].setText(i[1])
            if i[2]==True:
                i[0].setCheckState(2)
            else:
                i[0].setCheckState(0)                    
            hbox.addWidget(i[0])
            QtCore.QObject.connect(i[0], QtCore.SIGNAL("stateChanged(int)"),self.Update_Channel_Status)
        self.Wid.vbox.addLayout(hbox)

        try:
            if self.DB_Picture==False:
                self.pic = image.imread(str(self.Current_Picture_for_the_Map))
        except IOError:
            self.pic = image.imread(Main.Script_Path+"/Black.png")
            if NoWarning == False:
                msg="""
                <b>Picture Error</b>
                <p>Defined Picture doesn't exist (anymore?)
                <p>Black Background used instead
                """   
                Infos.Error(msg)              
        except AttributeError:
            self.pic = image.imread(Main.Script_Path+"/Black.png")
            if NoWarning == False:
                msg="""
                <b>Picture Error</b>
                <p>No Picture set, black Background used
                """  
                Infos.Error(msg) 
            #pyplot.contour(self.pic,[120, 255],linestyles='dashed',colors='w',linewidths=4)
        
            
        if self.Display_Red==False:
            self.pic[:,:,0]=0
        if self.Display_Green==False:
            self.pic[:,:,1]=0
        if self.Display_Blue==False:
            self.pic[:,:,2]=0

        #extent = (-320,320,-260,252)
        extent = (self.CCDlimit[0],self.CCDlimit[1],self.CCDlimit[2],self.CCDlimit[3])
        self.Wid.canvas.axes.imshow(self.pic,extent=extent,cmap=self.Image_ColorMap)#,extent=[self.CCDlimit[0],self.CCDlimit[2],self.CCDlimit[3],self.CCDlimit[1]])
        
        self.Wid.canvas.Object_Selection_Mode = 'Coordinates'
   
        self.Wid.show() 
               
    def Make_the_Map(self,
                     Title='Mapping',
                     ColorBar=True,
                     Labels=True,
                     Marker='s',
                     Bypass_Measuring=False,
                     NoWarning=False,
                     MeshMap=True,
                     ContourMap=True):
        """
        This part of the script Normalize Data for display purpose
        Depending on if you want to display positive or negative or both currents, you can change
        
        """
        self.NormalizeSurfaceAndColors()
        self.CM.Scaling_Factor=float(self.Stim_Resolution.text())
        self.CM.ScaleAxis()#float(self.Stim_Resolution.text()))
        
        #If "success rate" is set, sucess rate is in color (instead of amplitude), charge in surface
        if self.Thresholding_Mode.currentIndex() == 4:
            self.CM.Local_Amplitude=self.CM.Local_Success
            self.CM.Amplitude='Color'
            self.CM.Charge='Surface'
        else:
            pass
        
        color,surface=self.CreateColorScaleAndSurfaceScale(Bypass_Measuring=Bypass_Measuring,NoWarning=NoWarning)    

                
                
        cmap=str(self.ColorMap.currentText())  

        n=self.Wid.canvas.axes.scatter(self.CM.Sorted_X_Coordinates_Scaled[:], self.CM.Sorted_Y_Coordinates_Scaled[:], c=color,s=surface, vmin=0, vmax=1, alpha=0.75,picker=1 , cmap=cmap, marker = Marker)
        
        XYTuple=[]
        for i in range(len(self.CM.Sorted_X_Coordinates_Scaled)):
            XYTuple.append((self.CM.Sorted_X_Coordinates_Scaled[i],self.CM.Sorted_Y_Coordinates_Scaled[i]))
        
        self.Table = SpreadSheet(Source=[XYTuple,self.CM.Normalized_Surface,self.CM.Local_Surface,self.CM.Normalized_Amplitude,self.CM.Local_Amplitude],Labels=["XY","Normalized C1","C1","Normalized A1","A1"])
        self.Table.show()


        ##############################################


        if self.CM.Charge=='Surface':
            mesh,contour = self.SmoothMap(self.CM.Sorted_X_Coordinates_Scaled[:], self.CM.Sorted_Y_Coordinates_Scaled[:],self.CM.Local_Surface,power=3,smoothing=10,subsampling=5,cmap=cmap,Max_Valid_Dist=self.Max_Valid_Dist,MeshMap=MeshMap,ContourMap=ContourMap)
        else:
            mesh,contour = self.SmoothMap(self.CM.Sorted_X_Coordinates_Scaled[:], self.CM.Sorted_Y_Coordinates_Scaled[:],self.CM.Local_Amplitude,power=3,smoothing=10,subsampling=5,cmap=cmap,Max_Valid_Dist=self.Max_Valid_Dist,MeshMap=MeshMap,ContourMap=ContourMap)
            
        self.CreateInteractiveGrid(n,ColorBar=ColorBar,Labels=Labels,Title=Title,NoWarning=NoWarning)
       
        return self.Wid.canvas.fig,self.CM.Sorted_X_Coordinates_Scaled,self.CM.Sorted_Y_Coordinates_Scaled,color,surface,mesh,contour
        
#        except ValueError:
#            Main.error = QtGui.QMessageBox.about(Main, "Error",
#                """
#                <b>Threshold Error</b>
#                <p>No Value over"""+str(self.Thresholding_Mode_Input_Field.text())+"""
#                <p>Check your threshold values and try again""")
 
    def ImportMapping(self):
        index=int(self.MappingID.currentIndex())
        temp='Analysis.Map'+str(index+1)
        print temp, 'loaded as current Mapping'
        self.CM=deepcopy(eval(temp))
        self.StoredMaps.append(temp)
        
    def Clear_Mappings(self):       
        self.Mapping_ID=0
        for i in self.StoredMaps:
            try:
                exec ('del '+i)
                print i, ' deleted'
            except AttributeError:
                pass        
        self.StoredMaps=[]
        self.MappingID.clear()
              
    def Update_Channel_Status(self):
        
        if self.Red_Channel.checkState()==2:
            self.Display_Red=True
        else:    
            self.Display_Red=False
        if self.Green_Channel.checkState()==2:
            self.Display_Green=True
        else:    
            self.Display_Green=False
        if self.Blue_Channel.checkState()==2:
            self.Display_Blue=True
        else:    
            self.Display_Blue=False   
        #BypassReMapping is needed because of a bug when using Main.sender()
        self.Display_Mapping_Results(BypassReMapping=True)
        
    def Save_Associated_Image(self):
        try:
            for i in list(set(Requete.Block_ids)):
                b=Block.load(i,session=Requete.Global_Session)
                b.picture=self.pic
                b.save()
             
            self.DB_Picture=True
            print "Picture saved"
        except AttributeError:
            msg="""
            <b>Picture Error</b>
            <p>No Picture set, no Picture Saved
            """  
            Infos.Error(msg)             

    def Set_Range(self,Min,Max):
        self.Manual_Min_Field.setText(str(Min))
        self.Manual_Max_Field.setText(str(Max))
     
    def Load_Associated_Image(self):
        
        try:
            
            self.DB_Picture=True
            self.pic=Block.load(list(set(Requete.Block_ids))[0],session=Requete.Global_Session).picture
            print 'Picture Loaded'
        except (AttributeError,sqlalchemy.exc.OperationalError):
            print 'Error while trying to use the block.picture table'
            print 'The field do not exist'
            print 'SynaptiQs is creating the required field. On a big database, it may take a while'
            print 'DO NOT INTERRUPT'
            from OpenElectrophy.gui.tabledesign import TableDesign
            from OpenElectrophy.gui.guiutil.paramwidget import *
            T=TableDesign(metadata = Requete.Global_Meta,session = Requete.Global_Session)
            T.addField(fieldname='picture',fieldtype='numpy.ndarray')
            T.tablename='block'
            T.apply()
