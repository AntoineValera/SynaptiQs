# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:07:35 2013

@author: Antoine Valera
"""
#import os,sys
#from OpenElectrophy import *#gui,sql,open_db,AnalogSignal,Segment,Block,RecordingPoint,
from matplotlib import numpy,pyplot


class Map(object):
    """
    A Map objects contains all the information of a spatial mapping, i.e.
    The type of mapping ['Grid','User_Defined']
    
    Some grid information (if its a grid) [X_start,X_End,Y_Start,Y_End, Number_of_Turns]
    The step size in X and Y. Both grid information and step size are in arbitrary units (pixels or other)
    A Scaling Factor to convert coordinates using internal units into µm
    
    The position of each point is mapped with either 
    The 
    """
    def __init__(self):
        self.__name__="Map"
        
        self.Mapping_Type = 'Grid'
        
        self.Structure = None
        
        self.Number = None
        
        self.X_End = None
        self.X_Start = None
        self.X_Step = None
        self.Y_End = None
        self.Y_Start = None
        self.Y_Step = None
        self.Scanning_Direction_Mode = None
        
        self.Scaling_Factor =1.        
        
        self.Number_of_Turns = None    
        self.Sorted_Y_Coordinates = []
        self.Sorted_X_Coordinates = []
        self.Sorted_X_Coordinates_Full = []
        self.Sorted_Y_Coordinates_Full = []
        self.Sorted_X_and_Y_Coordinates = []
        self.Sorted_X_and_Y_Coordinates_Full = []
        self.Sorted_Y_Coordinates = []
        self.Sorted_X_Coordinates  = []    
            
        self.Types_of_Events_to_Measure = 'Negative'
        self.Charge = 'Surface'
        self.Amplitude = 'Color'


        self.Sorted_X_and_Y_Coordinates = []
        self.Sorted_Mean_Amplitudes_1 = []
        self.Sorted_Mean_Charges_1 = []
        self.Coordinates_and_Corresponding_Mean_Amplitude1_Dictionnary = {}
        self.Coordinates_and_Corresponding_Amplitudes1_Dictionnary = {}
        self.Coordinates_and_Corresponding_Mean_Charge1_Dictionnary = {}
        self.Coordinates_and_Corresponding_Charges1_Dictionnary = {}
        self.Coordinates_and_Corresponding_Success_Rate_Dictionnary = {}
        self.AnalogSignal_Ids_and_Corresponding_Coordinates_Dictionnary = {}
        self.Coordinates_and_Corresponding_AnalogSignal_Ids_Dictionnary = {}
        self.AnalogSignal_Ids_and_Corresponding_SweepNumber_Dictionnary = {}
        self.Initially_Excluded_AnalogSignal_Ids = []
        self.Success_list = []
        self.Success_rate = []
        self.Local_Amplitude = []
        self.Local_Amplitude_sd = []
        self.Local_Surface = []
        self.Local_Surface_sd = []
        self.Local_Success = []

        
    def Save_Map(self):
        '''
        This function save the map in a txt file that can be exported
        
        '''
        numpy.savetxt('Map.txt',)


    def GenerateGridCoordinates(self,Scanning_Direction_Mode,List_of_X_Points, List_of_Y_Points):
        '''
        This function generate a grid of coordinates using SynaptiQs inputs
        '''
        self.Scanning_Direction_Mode = Scanning_Direction_Mode
       
        if Scanning_Direction_Mode == 'X':
            Y, X = numpy.meshgrid(List_of_Y_Points, List_of_X_Points)
        elif Scanning_Direction_Mode == 'Y':
            X, Y = numpy.meshgrid(List_of_X_Points, List_of_Y_Points)
            
        self.Number_of_Turns= int(Mapping.Number_of_Turns.text())   
        self.Sorted_X_Coordinates=list(X.flatten())
        self.Sorted_Y_Coordinates=list(Y.flatten())
        self.Sorted_X_Coordinates_Full=self.Sorted_X_Coordinates*self.Number_of_Turns
        self.Sorted_Y_Coordinates_Full=self.Sorted_Y_Coordinates*self.Number_of_Turns    
        self.Sorted_X_and_Y_Coordinates=zip(self.Sorted_X_Coordinates,self.Sorted_Y_Coordinates)
        self.Sorted_X_and_Y_Coordinates_Full=self.Sorted_X_and_Y_Coordinates*self.Number_of_Turns
        
    def ScaleAxis(self):
        self.Sorted_X_Coordinates_Scaled=numpy.array(self.Sorted_X_Coordinates)*self.Scaling_Factor
        self.Sorted_Y_Coordinates_Scaled=numpy.array(self.Sorted_Y_Coordinates)*self.Scaling_Factor 

        
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

    def describe(self,All=False):
        #import __builtin__
        for j in dir(Map):
            print j
            try:
                acceptable = [list,numpy.ndarray,int,float,str]
                if type(eval('Map.'+j)) in acceptable :
                    print j, '=', eval('Map.'+j)
            except:
                pass

