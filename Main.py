# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:32:43 2013

@author: Antoine Valera
"""
import sys,os
from PyQt4 import QtCore, QtGui
from matplotlib import pyplot,numpy
#import Analysis,Navigate,MyMplWidget,Mapping,Requete.Requete,Histogram,Fitting,Import


class Main(QtGui.QWidget,object):#

    """This Class set up the Main Window"""
    def __init__(self):

        self.__name__="Main"
        super(Main,self).__init__()
        self.setAcceptDrops(True)
    #Drag and Drop section
        
#    def dragEnterEvent(self, event):
#        if event.mimeData().hasUrls:
#            event.accept()
#        else:
#            event.ignore()

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
    
    def File_loading(self):

        """
        This function load the Userpref.txt file
        or create a new one if it doesn't exist.
        It also copy these values in self.user_parameters
        """

        self.userpath=os.getenv("HOME")

        if self.userpath == None: #Happens when started as executable, out of Winpython
            value,ok = QtGui.QInputDialog.getText(self,
                                                  'Winpython Path',
                                                  """UserPath Not Found, please indicate Your WinPython installation Folder""",
                                                  QtGui.QLineEdit.Normal,
                                                  'C:\Users\Antoine\WinPython-64bit-2.7.10.1')
            value=str(value)              
            self.userpath = value+'\settings'

        
        self.Script_Path=os.path.dirname(os.path.realpath(__file__))
        #if self.userpath == None:
        #    self.userpath='C:\\Users\\Downstairs-PC\\WinPython-32bit-2.7.10.2\\settings'
        self.path = self.userpath+"/.SynaptiQs/Core/Userpref.txt" #Adresse du Fichier de parametres. Penser a laisser les droits d'ecriture
        self.Analysis_Preferences_Path=self.userpath+"/.SynaptiQs/Core/Analysis_Pref.txt"
        self.Mapping_Preferences_Path=self.userpath+"/.SynaptiQs/Core/Mapping_Pref.txt"
        if os.path.isfile(self.path) and  os.path.isfile(self.Analysis_Preferences_Path) and  os.path.isfile(self.Mapping_Preferences_Path): #Si le fichier Userpref existe:
            print "########### SynaptiQs Started ############"
            print "-----------> Loading Preference Files"
            print "-----------> Userpref.txt Loaded correctly"
            parameters = open(self.path) #On ouvre
            self.user_parameters=parameters.readlines() #on lit
            if len(self.user_parameters) != 40: #S'il Ny a pas 10 lignes, on etend le fichier à 30 lignes
                self.user_parameters.extend(['']*(40-len(self.user_parameters)))
            self.param_inf=['']*40 #On cree un liste des parametres
          
            #Lecture des parametres:
                #Ligne0      Last SQLite DB             
                #Ligne1      Last MySQL User
                #Ligne2      Last MySQL Password
                #Ligne3      Last MySQL DBname                
                #Ligne4      Last MySQL DB_IP_adress:port               
                #Ligne5      Basic Analysis.tag Fields
                #Ligne6      Working folder
                #Ligne7      *empty*                
                #Ligne8      *empty*   
                #Ligne9      *empty*
                #Lignes10 à 40 : Main.measurecoord dans l'ordre suivant:
#                    "Baseline1_begin"10
#                    "Baseline1_end"11
#                    "Peak1_begin"12
#                    "Peak1_end"13
#                    "Baseline2_begin"14
#                    "Baseline2_end"15
#                    "Peak2_begin"16
#                    "Peak2_end"17
#                    "Baseline3_begin"18
#                    "Baseline3_end"19
#                    "Peak3_begin"20
#                    "Peak3_end"21
#                    "Baseline1_size"22
#                    "Peak1_size"23
#                    "Baseline2_size"24
#                    "Peak2_size"25
#                    "Baseline3_size"26
#                    "Peak3_size"27
#                    "Baseline1_meth"28
#                    "Peak1_meth"29
#                    "Baseline2_meth"30
#                    "Peak2_meth"31
#                    "Baseline3_meth"32
#                    "Peak3_meth"33   
                                        

            

            #Securités pour le bon lancement de l'appli, ême en l'absence de paramètres:
            if self.user_parameters[0]=='\n' or '': #S'il n'y a pas de base de données SQLlite
                self.user_parameters[0] = self.userpath+"/Core/.SynaptiQs/empty.db"

            rescuelist=[198.0,200.0,202.0,215.0,218.0,220.0,222.0,235.0,238.0,240.0,242.0,255.0,1.0,1.0,1.0,1.0,1.0,1.0, 'Min', 'Min', 'Min', 'Min', 'Min', 'Min']   #les points par defaut, pour la mesure d'un triplet à 50Hz commençant 200ms après le départ          
            for i in range(10,34):
                if self.user_parameters[i]=='': #S'il n'y a pas paramètres de mesure
                    self.user_parameters[i] = str(rescuelist[i-10])

            for i in range(len(self.user_parameters)): 
                self.param_inf[i] = str(self.user_parameters[i].split('\n')[0])
                #on la remplit avec le contenu du fichier de préférences
            self.desktop=self.param_inf[6]
            parameters.close() #on ferme le fichier
            
    
        #Dans le pire des cas, le fichier a été supprimé    
        else : #Si le fichier de parametres n'existe pas, on le crée, mais il faut les droits d'ecriture dans le dossier
            if not os.path.isdir(self.userpath+"/.SynaptiQs/"):
                os.makedirs(self.userpath+"/.SynaptiQs/")
            if not os.path.isdir(self.userpath+"/.SynaptiQs/Core/"):
                os.makedirs(self.userpath+"/.SynaptiQs/Core/")
                
            print "error, Userpref.txt does not exist, file created"
            try:
                parameters = open(self.path,'w')
                self.user_parameters=parameters.readlines()
                if len(self.user_parameters) != 40: #S'il Ny a pas 10 lignes, on etend le fichier à 30 lignes
                    self.user_parameters.extend(['']*(40-len(self.user_parameters)))
                self.param_inf=['']*40 #On cree un liste des parametres                
                #self.param_inf=['']*30
                self.user_parameters[0] = self.userpath+"/Core/.SynaptiQs/empty.db"
                for i in range(len(self.user_parameters)): 
                    self.param_inf[i] = str(self.user_parameters[i].split('\n')[0])
                parameters.close()
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Welcome To SynaptiQs</b>
                <p>This is your first faunch, (or maybe you just deleted Userpref.txt)
                <p>A new Userpref.txt file was created.
                <p>SynaptiQs Will now exit. Please Restart. Default value will be used""")
                msgBox.exec_()
                
                pyplot.show()

            except IOError: #si le fichier ne peut pas etre crée, erreur
                print "You don't have the right to print in this folder"
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>SynaptiQs was unable to create the Userpref.txt file.</b>
                <p>Please give writting access to SynaptiQs folder to all users.
                <p>SynaptiQs should be in 
                $HOME/.SynaptiQs/Core/""")
                msgBox.exec_()
                sys.exit()
                #sys.exit(app.exec_())  
                


        #Then, we open the Analysis_Pref.txt file, which contains user defined parameters for measurments 
        try:

            print "-----------> Analysis_Pref.txt Loaded correctly"
            parameters = open(self.Analysis_Preferences_Path)
            Analysis_Preferences=parameters.readlines() #on lit
            self.Analysis_Preferences=['']*len(Analysis_Preferences)
            for i in range(len(Analysis_Preferences)):
                Analysis_Preferences[i]=Analysis_Preferences[i].replace('\n','')
                self.Analysis_Preferences[i] = eval(Analysis_Preferences[i])
                
            self.List_of_User_Defined_Parameters=[]
            for i in range(len(self.Analysis_Preferences)):
                self.List_of_User_Defined_Parameters.append(self.Analysis_Preferences[i][0])
            parameters.close() #on ferme le fichier
            
        except : #Si le fichier de parametres n'existe pas, on le crée, mais il faut les droits d'ecriture dans le dossier
            print "error, Analysis_Pref.txt does not exist, file created"

            parameters = open(self.Analysis_Preferences_Path,'w')
            self.Analysis_Preferences=[]
            self.Analysis_Preferences.append(['Default',198.0,200.0,202.0,215.0,218.0,220.0,222.0,235.0,238.0,240.0,242.0,255.0,1.0,1.0,1.0,1.0,1.0,1.0])
            parameters.close()
            
            self.List_of_User_Defined_Parameters=[]
            for i in range(len(self.Analysis_Preferences)):
                self.List_of_User_Defined_Parameters.append(self.Analysis_Preferences[i][0])                



        

    def Create_Window(self):
        """
        This function create the Main window and all the buttons
        """
        
        #Creation de la fenetre principale        
        self.MainWindow = QtGui.QMainWindow() 
        self.MainWindow.setContextMenuPolicy(0)   


            #Les propriété de la fenetre principale
        self.MainWindow.resize(1280, 350) #la taille d'origine de la fenetre
        self.MainWindow.setAnimated(True) #Donne un aspect fluide au déplacement des Widget;Facultatif
        self.MainWindow.setWindowTitle("SynaptiQs")
        
        #Creation de la barre de menu

        #Definition de la barre de menu

        self.File_Menu = QtGui.QMenu("File")
        self.Plugins_Menu = QtGui.QMenu("Plugins")
        self.About_Menu = QtGui.QMenu("About")
        self.Options_Menu = QtGui.QMenu("Options")
        self.Mapping_Options_Menu = QtGui.QMenu("Mapping Options")

        self.File_Menu.addAction("Show Main Figure",self.Show_Main_Figure,"CTRL+S")
        self.File_Menu.addAction("Navigator",Infos.Navigator)
        self.File_Menu.addAction("Create db",Infos.Create_DB)
        self.File_Menu.addAction("Edit DB Structure",Requete.Modify_DB_Structure,"CTRL+E")
        self.File_Menu.addAction("Import Data",Infos.Import_Data,"CTRL+L")

        self.File_Menu.addAction("Data Browser",Infos.Data_Browser,"CTRL+D")
        self.File_Menu.addAction("SpikeSorting",Infos.SpikeSorting)
        self.File_Menu.addAction("Tree View",Infos.Tree_View,"CTRL+T")
        self.File_Menu.addAction("start OpenElectrophy",Infos.Start_OE,"CTRL+O")
        self.File_Menu.addAction("IPython Console",self.EmbeddedIpython,"CTRL+I")
        self.File_Menu.addAction("Exit",QtCore.QCoreApplication.instance().quit,"CTRL+Q")
        
        self.Mapping_Options_Menu.addAction("Load Mapping Coordinate File",Mapping.Load_Coordinates)
        #self.Mapping_Options_Menu.addAction("Mapping on Negative currents",self.Update_Menu_Options)
        self.Mapping_Options_Menu.addAction("More Options",Mapping.More_Options)
        

        self.About_Menu.addAction("Help",Infos.Help,'CTRL+H')
        self.About_Menu.addAction("Plugins Folder",Infos.Open_a_Folder,'CTRL+P')
        self.About_Menu.addAction("UserPref Folder",Infos.Open_a_Folder,'CTRL+U')
        self.About_Menu.addAction("About",Infos.About)

        self.FastMode= False
        self.Sort_Blocks_by_FileName = False
   
        #self.Options_Menu.addAction("Fast Mode",self.Update_Menu_Options,'CTRL+F').setCheckable(True) OBSOLETE
        #self.Options_Menu.addAction("Sort Block by File Name (not working yet)",self.Update_Menu_Options,'CTRL+B').setCheckable(True)
        self.Options_Menu.addAction("Select Saving Directory",self.Saving_Directory)
        self.Options_Menu.addAction("Fitting Tools",Fitting.Helper)
        self.Options_Menu.addAction("Histogram Manager",Histogram.Manager)


        self.MainWindow.menuBar().addMenu(self.File_Menu)
        self.MainWindow.menuBar().addMenu(self.Plugins_Menu)
        self.MainWindow.menuBar().addMenu(self.Options_Menu)
        self.MainWindow.menuBar().addMenu(self.Mapping_Options_Menu)
        self.MainWindow.menuBar().addMenu(self.About_Menu)
        

        #Definition du Widget de Requete
        self.Whole_Request = QtGui.QDockWidget(self.MainWindow)
        self.MainWindow.addDockWidget(4,self.Whole_Request) #On attache le Widget au Widget parent, et on definit sa position
        self.Whole_Request.setMinimumSize(330,200) #definit la taille minimale du Widget (largeur, hauteur)        
 
        self.SQLTabWidget = QtGui.QTabWidget(self.Whole_Request)
        self.SQLTabWidget.setGeometry(0,0,330,50)
        
        self.FilteringWidget = QtGui.QWidget(self.Whole_Request)
        self.FilteringWidget.setWindowTitle("Filtering_Widget")
        self.FilteringWidget.setGeometry(0,52,330,200)
        self.FilteringWidget.setMinimumSize(330,300)

        self.RequestWidget = QtGui.QWidget()
        self.SQLTabWidget.addTab(self.RequestWidget,"MySQL_Request")
        self.RequestWidget.setWindowTitle("MySQL_Request")
        self.RequestWidget.setMinimumSize(330,300)

        self.SQLIteRequestWidget = QtGui.QWidget()
        self.SQLTabWidget.addTab(self.SQLIteRequestWidget,"SQLite Request")
        self.SQLIteRequestWidget.setWindowTitle("SQLIteRequestWidget")
        self.SQLIteRequestWidget.setMinimumSize(330,300) 
        
        self.LocalFileWidget = QtGui.QWidget()
        self.SQLTabWidget.addTab(self.LocalFileWidget,"Local File")
        self.LocalFileWidget.setWindowTitle("LocalFileWidget")
        self.LocalFileWidget.setMinimumSize(330,800)
        
        self.NavigationWidget = QtGui.QDockWidget(self.MainWindow)
        self.NavigationWidget.setWindowTitle("Navigation Tools")#donne un titre à la fenetre
        self.MainWindow.addDockWidget(4,self.NavigationWidget)
        self.NavigationWidget.setMinimumSize(260,300)
        
        self.ImportWindow = Import.MyWindow(self.LocalFileWidget)
        self.ImportWindow.setGeometry(0,0,260,160)
        Navigate.ArrayList=[]
        Navigate.VarList={}
        
        #Definition du Widget d'analyse 
        self.Whole_Analysis = QtGui.QDockWidget(self.MainWindow)
        self.MainWindow.addDockWidget(4,self.Whole_Analysis) #On attache le Widget au WIdget parent, et on definit sa position
        self.Whole_Analysis.setMinimumSize(400,300) #definit la taille minimale du Widget (largeur, hauteur)


        self.Analyze_Tab_Widget = QtGui.QTabWidget(self.Whole_Analysis)
        self.Analyze_Tab_Widget.setMinimumSize(400,300)
 

        self.AnalysisWidget = QtGui.QWidget()
        self.Analyze_Tab_Widget.addTab(self.AnalysisWidget,"Signal Measures")
        self.AnalysisWidget.setWindowTitle("Measure Tools")
        

        self.SpikesWidget = QtGui.QWidget()
        self.Analyze_Tab_Widget.addTab(self.SpikesWidget,"Spike Analysis")
        self.SpikesWidget.setWindowTitle("Spike Tools")
        

        self.MappingWidget = QtGui.QWidget()
        self.Analyze_Tab_Widget.addTab(self.MappingWidget,"Mapping")
        self.MappingWidget.setWindowTitle("Mapping Tools")

        Mapping.Tools()#Only If using mapping functions, which I do...
   
        #Les boutons
            #Les Boutons de Requete
        self.GetData = QtGui.QPushButton(self.FilteringWidget)
        self.GetData.setGeometry(5, 160, 83, 23)
        self.GetData.setText("Get Data")
        self.GetData.setToolTip("""Do the SQL request.\nIf you need the spiketrains,\nplease select a Neuron """)


        self.Reset_Check = QtGui.QCheckBox(self.FilteringWidget)
        self.Reset_Check.setGeometry(5, 200, 120, 23)
        self.Reset_Check.setText( "Reset All Tags")   
        self.Reset_Check.setToolTip("""To reset the Analogsignal.tag field\n Check this box and do the SQL request""")
    

        self.Personalize = QtGui.QPushButton(self.FilteringWidget)
        self.Personalize.setGeometry(5, 180, 110, 23)
        self.Personalize.setText("Personalize Request")


        self.Post_Filtering_Button = QtGui.QPushButton(self.FilteringWidget)
        self.Post_Filtering_Button.setGeometry(115, 180, 100, 23)
        self.Post_Filtering_Button.setText("Add Extra Filtering")
        

        self.Reset_Fields = QtGui.QPushButton(self.FilteringWidget)
        self.Reset_Fields.setGeometry(115, 200, 100, 23)
        self.Reset_Fields.setText("Reset Fields")
        
        
        
        self.SaveData = QtGui.QPushButton(self.FilteringWidget)
        self.SaveData.setGeometry(240, 180, 83, 23)
        self.SaveData.setText( "Save Params")
        self.SaveData.setToolTip("""Save the Tags in the\nAnalogsignal.tag field""")
        
        self.Tagging_Tools = QtGui.QPushButton(self.FilteringWidget) #creation du bouton
        self.Tagging_Tools.setGeometry(240, 200, 83, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Tagging_Tools.setText( "Tagging Tools")  
        
        self.IOTools = QtGui.QDockWidget(self.FilteringWidget)
        self.IOTools.setGeometry(240, 0, 83, 123)
        
        self.ExistingSweeps=[]
        self.Current_or_Average = QtGui.QComboBox(self.IOTools)
        self.Current_or_Average.setGeometry(0, 0, 83, 23)
        self.Current_or_Average.setSizeAdjustPolicy(0)
        self.Current_or_Average.addItems(self.ExistingSweeps)
        

        self.SaveName = QtGui.QLineEdit(self.IOTools)
        self.SaveName.setGeometry(0, 20, 83, 23)
        #self.SaveName.setText("mean")
        self.SaveName.setPlaceholderText( "set file suffix") 
        
        self.SaveTrace = QtGui.QPushButton(self.IOTools)
        self.SaveTrace.setGeometry(0, 40, 83, 23)
        self.SaveTrace.setText( "Save Array")
        self.SaveTrace.setToolTip("""You can save the selected trace in the "User" folder.\nWrite here the name of the file (without extension).\nTo save in a subfolder, please complete the path\n Exemple: \subfolder\ffilename will save filename.txt in\n \HOME\USER\subfolder\ """)

        self.Send_To_Igor = QtGui.QPushButton(self.IOTools)
        self.Send_To_Igor.setGeometry(0, 60, 83, 23)
        self.Send_To_Igor.setText( "Send To Igor")
        

        
        self.ShellButton = QtGui.QPushButton(self.IOTools) #creation du bouton
        self.ShellButton.setGeometry(0, 80, 83, 23) #taille et position (X,Y,Xsize,Ysize)
        self.ShellButton.setText( "IPython Shell") 
        self.ShellButton.setEnabled(1)

        self.SendToSQl = QtGui.QPushButton(self.IOTools) #creation du bouton
        self.SendToSQl.setGeometry(0, 100, 83, 23) #taille et position (X,Y,Xsize,Ysize)
        self.SendToSQl.setText( "Send to SQLite") 
     
        self.Menu_with_List_of_Positive_Steps = QtGui.QMenu()
        self.Menu_with_List_of_Negative_Steps = QtGui.QMenu()
        
        Navigate.Step=6 #The default Value

        for step in ["+2","+3","+4","+5","+6","+7","+8","+9","+10","+20","+50"]:
            Plus_Button = self.Menu_with_List_of_Positive_Steps.addAction(step)
            self.connect(Plus_Button,QtCore.SIGNAL('triggered()'), lambda step=step: Navigate.Modify_Step_Range(step))
           
        for step in ["-2","-3","-4","-5","-6","-7","-8","-9","-10","-20","-50"]:
            Minus_Button = self.Menu_with_List_of_Negative_Steps.addAction(step)
            self.connect(Minus_Button,QtCore.SIGNAL('triggered()'), lambda step=step: Navigate.Modify_Step_Range(step))            


     
            #Les boutons de Navigation

        self.Previous = QtGui.QPushButton(self.NavigationWidget)
        self.Previous.setGeometry(5, 40, 80, 23)
        self.Previous.setText( "Previous")
        self.Previous.setShortcut('Left')

        self.Next = QtGui.QPushButton(self.NavigationWidget)
        self.Next.setGeometry(85, 40, 80, 23)
        self.Next.setText( "Next")
        self.Next.setShortcut('Right')

        self.FirstSweep = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.FirstSweep.setGeometry(5, 80, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.FirstSweep.setText( "First Sweep") 
        self.FirstSweep.setShortcut('Home')

        self.LastSweep = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.LastSweep.setGeometry(85, 80, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.LastSweep.setText( "Last Sweep")
        self.LastSweep.setShortcut('End')

        self.Minus_Step = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Minus_Step.setGeometry(35, 60, 50, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Minus_Step.setText( "- 6")
        self.Minus_Step.setShortcut('PgDown')
        
        self.Choose_Negative_Step = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Choose_Negative_Step.setGeometry(5, 60, 30, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Choose_Negative_Step.setMenu(self.Menu_with_List_of_Negative_Steps) 

        self.Plus_Step = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Plus_Step.setGeometry(115, 60, 50, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Plus_Step.setText( "+ 6")
        self.Plus_Step.setShortcut('PgUp')
        
        self.Choose_Positive_Step = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Choose_Positive_Step.setGeometry(85, 60, 30, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Choose_Positive_Step.setMenu(self.Menu_with_List_of_Positive_Steps)         
        
            #From To
        self.From = QtGui.QLineEdit(self.NavigationWidget)
        self.From.setGeometry(5, 120, 80, 22)
        self.From.setText("0")
        self.From.setPlaceholderText( "UserName") 
        
        self.To = QtGui.QLineEdit(self.NavigationWidget)
        self.To.setGeometry(85, 120, 80, 22)
        self.To.setText("Max")
        self.To.setPlaceholderText( "UserName")
        
        self.Delete_Current_Segment_Button = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Delete_Current_Segment_Button.setGeometry(120,270,120,30) #taille et position (X,Y,Xsize,Ysize)
        self.Delete_Current_Segment_Button.setText( "Delete current Signal")           

            #Les boutons de fonction
            
        self.Average = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Average.setGeometry(5, 45, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Average.setText( "Average") #Le texte dans le bouton

        self.Superimpose = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Superimpose.setGeometry(5, 65, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Superimpose.setText( "Superimpose") 
        
        self.Start_Spike_Sorting = QtGui.QPushButton(self.SpikesWidget) #creation du bouton
        self.Start_Spike_Sorting.setGeometry(5, 5, 120, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Start_Spike_Sorting.setText( "Spike Sorting")        
        
        self.Rasterplot = QtGui.QPushButton(self.SpikesWidget) #creation du bouton
        self.Rasterplot.setGeometry(5, 25, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Rasterplot.setText( "Raster plot")
        
        self.Raster_Start = QtGui.QLineEdit(self.SpikesWidget)
        self.Raster_Start.setGeometry(100, 25, 80, 23)
        self.Raster_Start.setText('0.200')
        self.Raster_Start.setPlaceholderText("start in s")

        self.Raster_Duration = QtGui.QLineEdit(self.SpikesWidget)
        self.Raster_Duration.setGeometry(200, 25, 80, 23)
        self.Raster_Duration.setText('0.050')
        self.Raster_Duration.setPlaceholderText( "Duration in s")        

        self.ShowEvents = QtGui.QPushButton(self.SpikesWidget) #creation du bouton
        self.ShowEvents.setGeometry(5, 105, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.ShowEvents.setText( "Show Events")
        self.ShowEvents.setEnabled(False)
        
        
        
        self.ModifySpikes = QtGui.QCheckBox(self.SpikesWidget) #creation du bouton
        self.ModifySpikes.setGeometry(5, 140, 120, 23) #taille et position (X,Y,Xsize,Ysize)
        self.ModifySpikes.setText( "Modify Spikes") 
        self.ModifySpikes.setDisabled(0)
        
        self.Measure_Button = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Measure_Button.setGeometry(5, 85, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Measure_Button.setText( "Measure!")

        self.Checkup = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Checkup.setGeometry(5, 105, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Checkup.setText( "Manip Diagnosis")

        self.inf = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.inf.setGeometry(5, 125, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.inf.setText( "Infos")
        


        
        #Les Champs de Filtrage
        self.SQLite_path = QtGui.QLineEdit(self.SQLIteRequestWidget)
        self.SQLite_path.setGeometry(2, 0, 290, 22)
        self.SQLite_path.setText(self.param_inf[0])
        self.SQLite_path.setPlaceholderText( "Path")
        
        self.SQLight_File_Select_Window = QtGui.QPushButton(self.SQLIteRequestWidget)
        self.SQLight_File_Select_Window.setGeometry(292, 0, 27, 22)
        self.SQLight_File_Select_Window.setText( "...")
        
        self.DBinf = [self.param_inf[1],self.param_inf[2],self.param_inf[3],self.param_inf[4]] ##Pour court circuiter l'enregistrement des parametres
        
        
        self.User = QtGui.QLineEdit(self.RequestWidget)
        self.User.setGeometry(5, 0, 70, 22)
        self.User.setText(self.DBinf[0])
        self.User.setPlaceholderText( "UserName")        
        
        self.Password = QtGui.QLineEdit(self.RequestWidget)
        self.Password.setGeometry(85, 0, 70, 22)
        self.Password.setText(self.DBinf[1])
        self.Password.setPlaceholderText( "PassWord")
        self.Password.setEchoMode(2)

        self.DBname = QtGui.QLineEdit(self.RequestWidget)
        self.DBname.setGeometry(165, 0, 70, 22)
        self.DBname.setText(self.DBinf[2])
        self.DBname.setPlaceholderText( "DBName")      
        
        self.IPAdress = QtGui.QLineEdit(self.RequestWidget)
        self.IPAdress.setGeometry(245, 0, 70, 22)
        self.IPAdress.setText(self.DBinf[3])
        self.IPAdress.setToolTip("""in my lab it's 130.79.38.117:3306""")
        self.IPAdress.setPlaceholderText( "xxx.xxx.xxx.xxx:yyyy")   
        
            #La date                     
        self.label_filter1 = QtGui.QLabel(self.FilteringWidget)
        self.label_filter1.setGeometry(5, 5, 48, 14)
        self.label_filter1.setText( "Date")
            #Le fichier = blockid       
        self.label_filter2 = QtGui.QLabel(self.FilteringWidget)
        self.label_filter2.setGeometry(5, 25, 48, 14)
        self.label_filter2.setText( "Block id")
            #La condition de manip
        self.label_filter3 = QtGui.QLabel(self.FilteringWidget)
        self.label_filter3.setGeometry(5, 45, 48, 14)
        self.label_filter3.setText( "Condition")
            #Le mode de patch        
        self.label_filter4 = QtGui.QLabel(self.FilteringWidget)
        self.label_filter4.setGeometry(5, 65, 48, 14)
        self.label_filter4.setText( "Rec Mode")   
            #Le numero du cannal       
        self.label_filter5 = QtGui.QLabel(self.FilteringWidget)
        self.label_filter5.setGeometry(5, 85, 48, 14)
        self.label_filter5.setText( "Channel #")
            #Le numero du neurone (après spikesorting seulement)       
        self.label_filter6 = QtGui.QLabel(self.FilteringWidget)
        self.label_filter6.setGeometry(5, 125, 48, 14)
        self.label_filter6.setText( "Neuron id") 
        
        self.Filter_Date = QtGui.QComboBox(self.FilteringWidget)
        self.Filter_Date.setGeometry(60, 0, 180, 22)
        self.Filter_Date.addItems(["None"])

        self.Filter_BlockId = QtGui.QComboBox(self.FilteringWidget)
        self.Filter_BlockId.setGeometry(60, 20, 180, 22)
        self.Filter_BlockId.addItems(["None"])
        
        self.Filter_BlockInfo = QtGui.QComboBox(self.FilteringWidget)
        self.Filter_BlockInfo.setGeometry(60, 40, 180, 22)
        self.Filter_BlockInfo.addItems(["None"])
        

        self.Filter_ChannelName = QtGui.QComboBox(self.FilteringWidget)
        self.Filter_ChannelName.setGeometry(60, 60, 180, 22)
        self.Filter_ChannelName.addItems(["None"])
        
        self.Filter_ChannelNumber = QtGui.QComboBox(self.FilteringWidget)
        self.Filter_ChannelNumber.setGeometry(60, 80, 180, 22)
        self.Filter_ChannelNumber.addItems(["None"])
        
        self.Filter_NeuronName = QtGui.QComboBox(self.FilteringWidget)
        self.Filter_NeuronName.setGeometry(60, 120, 180, 22)
        self.Filter_NeuronName.addItems(["None"])
        self.Filter_NeuronName.setEnabled(False)

    
        self.fileOrigin = QtGui.QLabel(self.FilteringWidget)
        self.fileOrigin.setGeometry(90, 165, 200, 15)
        self.fileOrigin.setText( "None")


        self.LoadTags = QtGui.QPushButton(self.NavigationWidget)
        self.LoadTags.setGeometry(170, 20, 80, 23)
        self.LoadTags.setText( "Load Tags")
        self.LoadTags.setToolTip("""Load the Tags in the\nAnalogsignal.tag["Selection"] field""")   
        
        self.TagAll = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.TagAll.setGeometry(170, 60, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.TagAll.setText( "Tag All") #Le texte dans le bouton

        self.UnTagAll = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.UnTagAll.setGeometry(170, 80, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.UnTagAll.setText( "UnTag All") #Le texte dans le bouton
        
        self.Invert = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Invert.setGeometry(170, 100, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Invert.setText( "Invert Tags") #Le texte dans le bouton

        self.Correspondance_info = QtGui.QPushButton(self.NavigationWidget) #creation du bouton
        self.Correspondance_info.setGeometry(170, 120, 80, 23) #taille et position (X,Y,Xsize,Ysize)
        self.Correspondance_info.setText( "Id Links Infos")            
        
        #Les checkbox
        
        self.Tagging_Button = QtGui.QCheckBox(self.NavigationWidget)
        self.Tagging_Button.setGeometry(170, 40, 80, 21)
        self.Tagging_Button.setText( "Tag")
        self.Tagging_Button.setShortcut('T')
        
        
        self.Display_Measures_Button = QtGui.QCheckBox(self.AnalysisWidget)
        self.Display_Measures_Button.setGeometry(5, 200, 80, 21)
        self.Display_Measures_Button.setText( "Measuring")
        self.Display_Measures_Button.setObjectName("Display_Measures_Button")
        
        self.Analyze_Filtered_Traces_Button = QtGui.QCheckBox(self.AnalysisWidget)
        self.Analyze_Filtered_Traces_Button.setGeometry(5, 220, 120, 21)
        self.Analyze_Filtered_Traces_Button.setText( "Analyze filtered")
        
        self.Display_Charge_Button = QtGui.QCheckBox(self.AnalysisWidget)
        self.Display_Charge_Button.setGeometry(5, 240, 120, 21)
        self.Display_Charge_Button.setText( "Show Charge")
        
        self.Remove_Leak_Button = QtGui.QCheckBox(self.AnalysisWidget)
        self.Remove_Leak_Button.setGeometry(130, 200, 120, 21)
        self.Remove_Leak_Button.setText( "Remove Leak") 
        self.Remove_Leak_Button.setObjectName("Remove_Leak_Button")
        
        self.Measure_From_Baseline1_Button = QtGui.QCheckBox(self.AnalysisWidget)
        self.Measure_From_Baseline1_Button.setGeometry(130, 220, 120, 21)
        self.Measure_From_Baseline1_Button.setText( "Measure from bsl1") 
    
        self.Measure_From_Zero_Button = QtGui.QCheckBox(self.AnalysisWidget)
        self.Measure_From_Zero_Button.setGeometry(130, 240, 120, 21)
        self.Measure_From_Zero_Button.setText( "Measure from 0") 
        self.Measure_From_Zero_Button.setObjectName("Measure_From_Zero_Button")
    
        self.Display_Spikes_Button = QtGui.QCheckBox(self.SpikesWidget)
        self.Display_Spikes_Button.setGeometry(5, 45, 120, 21)
        self.Display_Spikes_Button.setText( "Show Spikes")

        self.Use_Spiketrains_Button = QtGui.QCheckBox(self.FilteringWidget)
        self.Use_Spiketrains_Button.setGeometry(5, 100, 120, 21)
        self.Use_Spiketrains_Button.setText( "Use SpikeTrains ?") 
        
        self.Create_Measure_Variables()

  
            #Les titres des colonnes
        
        self.label_begin = QtGui.QLabel(self.AnalysisWidget)
        self.label_begin.setGeometry(135, 20, 35, 14)
        self.label_begin.setText( "begin") 
        
        self.label_end = QtGui.QLabel(self.AnalysisWidget)
        self.label_end.setGeometry(175, 20, 35, 14)
        self.label_end.setText( "end") 
        
        self.label_length = QtGui.QLabel(self.AnalysisWidget)
        self.label_length.setGeometry(210, 20, 35, 14)
        self.label_length.setText( "length") 


        self.User_Defined_Measurement_Parameters = QtGui.QComboBox(self.AnalysisWidget)
        self.User_Defined_Measurement_Parameters.setGeometry(250, 20, 80, 20)
        self.User_Defined_Measurement_Parameters.addItems(self.List_of_User_Defined_Parameters)

        self.Add_User_Defined_Measurement_Parameters_Button = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Add_User_Defined_Measurement_Parameters_Button.setGeometry(335, 20, 15, 14) #taille et position (X,Y,Xsize,Ysize)
        self.Add_User_Defined_Measurement_Parameters_Button.setText("+")  
        
        self.Remove_User_Defined_Measurement_Parameters_Button = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Remove_User_Defined_Measurement_Parameters_Button.setGeometry(350, 20, 15, 14) #taille et position (X,Y,Xsize,Ysize)
        self.Remove_User_Defined_Measurement_Parameters_Button.setText("-")          

        self.Set_User_Defined_Measurement_Parameters_to_Zero_Button = QtGui.QPushButton(self.AnalysisWidget) #creation du bouton
        self.Set_User_Defined_Measurement_Parameters_to_Zero_Button.setGeometry(365, 20, 15, 14) #taille et position (X,Y,Xsize,Ysize)
        self.Set_User_Defined_Measurement_Parameters_to_Zero_Button.setText("0")    



            #Tous les labels des champs de mesure 

        Button_Labels=["Bsln1","Peak1","Bsln2","Peak2","Bsln3","Peak3"]
                        
        for j in range(len(Button_Labels)):
            eval(compile("self."+Button_Labels[j]+"= QtGui.QLabel(self.AnalysisWidget)",'<string>','exec'))
            eval(compile("self."+Button_Labels[j]+".setGeometry(90, 45+20*j, 45, 14)",'<string>','exec'))
            eval(compile("self."+Button_Labels[j]+".setText(Button_Labels[j])",'<string>','exec'))

        
            #Tous les champs de mesure 
        Button_Names=[  ["Baseline1_begin","Peak1_begin","Baseline2_begin","Peak2_begin","Baseline3_begin","Peak3_begin"],
                        ["Baseline1_end","Peak1_end","Baseline2_end","Peak2_end","Baseline3_end","Peak3_end"],
                        ["Baseline1_size","Peak1_size","Baseline2_size","Peak2_size","Baseline3_size","Peak3_size"]]
                        
        for i in range(len(Button_Names)):
            for j in range(len(Button_Names[i])):
                eval(compile("self."+Button_Names[i][j]+"= QtGui.QLineEdit(self.AnalysisWidget)",'<string>','exec'))
                eval(compile("self."+Button_Names[i][j]+".setGeometry(130+i*40, 40+20*j, 40, 22)",'<string>','exec'))
                eval(compile("self."+Button_Names[i][j]+".setText(str(self.measurecoord[Button_Names[i][j]]))",'<string>','exec'))
                eval(compile("self."+Button_Names[i][j]+".setPlaceholderText('in ms')",'<string>','exec'))

        self.PositiveOrNegativeMeasure = QtGui.QCheckBox(self.AnalysisWidget)
        self.PositiveOrNegativeMeasure.setGeometry(90, 165, 105, 14)
        self.PositiveOrNegativeMeasure.setText( "Negative Current")
        self.PositiveOrNegativeMeasure.setCheckState(2)
        Mapping.CM.Types_of_Events_to_Measure='Negative'
            #Affichage du sweep en cours
        
        self.Sweep_Number_Label = QtGui.QLabel(self.NavigationWidget)
        self.Sweep_Number_Label.setGeometry(90, 20, 50, 22)
        self.Sweep_Number_Label.setText("Sweep")
        
        self.Sweep_Number_Input_Field = QtGui.QLineEdit(self.NavigationWidget)
        self.Sweep_Number_Input_Field.setGeometry(130, 20, 40, 22)
        self.Sweep_Number_Input_Field.setText("0")
  
            #Methode de calcul
        #La variable de methode d'analyse en cours :
        Analysis_Mode=["Baseline1_meth","Peak1_meth","Baseline2_meth","Peak2_meth","Baseline3_meth","Peak3_meth"]
                        
        for j in range(len(Analysis_Mode)):
            eval(compile("self."+Analysis_Mode[j]+"= QtGui.QComboBox(self.AnalysisWidget)",'<string>','exec'))
            eval(compile("self."+Analysis_Mode[j]+".setGeometry(250, 40+20*j, 80, 22)",'<string>','exec'))
            eval(compile("self."+Analysis_Mode[j]+".addItems(['Min','Max'])",'<string>','exec'))
                
        
       
        #Creation du Widget d'affichage  

#        self.displaying = QtGui.QDockWidget(self.MainWindow)
#        self.MainWindow.addDockWidget(8, self.displaying) #8 est la position; cf documentation 
        self.IPythonOpened=False
        self.Show_Main_Figure()


        #la barre de navigation
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal,self.NavigationWidget)
        self.slider.setGeometry(5, 100, 150, 23)
        self.slider.setRange(0, 1)
        self.slider.setValue(0.5)
        self.slider.setTracking(True)
        
        
        
        #Barre de Status
        
        self.status_text = QtGui.QLabel("Welcome in SynaptiQs")
        self.MainWindow.statusBar().addWidget(self.status_text, 1)
        
        
        
        #Barre de progression
        self.progress = QtGui.QProgressBar(self.NavigationWidget)
        self.progress.setGeometry(50, 170, 150, 23)
        


      
        #Connexion des boutons de navigation avec leur signal
            #Les Signaux d'appels des sweeps
        QtCore.QObject.connect(self.Filter_Date, QtCore.SIGNAL('activated(int)'),Requete.Request_ComboBoxes_update)
        QtCore.QObject.connect(self.Filter_BlockId, QtCore.SIGNAL('activated(int)'),Requete.Request_ComboBoxes_update)
        QtCore.QObject.connect(self.Filter_BlockInfo, QtCore.SIGNAL('activated(int)'),Requete.Request_ComboBoxes_update)
        QtCore.QObject.connect(self.Filter_ChannelName, QtCore.SIGNAL('activated(int)'),Requete.Request_ComboBoxes_update)
        QtCore.QObject.connect(self.Filter_ChannelNumber, QtCore.SIGNAL('activated(int)'),Requete.Request_ComboBoxes_update)
        QtCore.QObject.connect(self.Filter_NeuronName, QtCore.SIGNAL('activated(int)'),Requete.Request_ComboBoxes_update)      
        
        
            #Les signaux de Navigation
        QtCore.QObject.connect(self.Previous, QtCore.SIGNAL("clicked()"),Navigate.Display_Previous_Trace) #Signal_Widget, Signal, Slot_Widget, Slot
        QtCore.QObject.connect(self.Next, QtCore.SIGNAL("clicked()"),Navigate.Display_Next_Trace)
        QtCore.QObject.connect(self.GetData, QtCore.SIGNAL("clicked()"),Requete.Final_Request)
        QtCore.QObject.connect(self.Personalize, QtCore.SIGNAL("clicked()"),Requete.Personalize_Request)
        QtCore.QObject.connect(self.Post_Filtering_Button, QtCore.SIGNAL("clicked()"),Requete.Post_Filtering_Widget)#Requete.Post_Filtering_Widget)
        
        QtCore.QObject.connect(self.Minus_Step, QtCore.SIGNAL("clicked()"),Navigate.Display_Trace_minus_Step) #Signal_Widget, Signal, Slot_Widget, Slot
        QtCore.QObject.connect(self.Plus_Step, QtCore.SIGNAL("clicked()"),Navigate.Display_Trace_plus_Step) #Signal_Widget, Signal, Slot_Widget, Slot
        QtCore.QObject.connect(self.Reset_Fields, QtCore.SIGNAL("clicked()"),Requete.Resetfields) #Signal_Widget, Signal, Slot_Widget, Slot

        QtCore.QObject.connect(self.SaveData, QtCore.SIGNAL("clicked()"),Requete.Save_Tags_To_Db)
        QtCore.QObject.connect(self.LoadTags, QtCore.SIGNAL("clicked()"),Analysis.Load_Tags)
        QtCore.QObject.connect(self.SaveTrace, QtCore.SIGNAL("clicked()"),self.Save_Trace)
        QtCore.QObject.connect(self.Send_To_Igor, QtCore.SIGNAL("clicked()"),Infos.SendToIgor)
        QtCore.QObject.connect(self.FirstSweep, QtCore.SIGNAL("clicked()"),Navigate.Display_First_Trace)
        QtCore.QObject.connect(self.LastSweep, QtCore.SIGNAL("clicked()"),Navigate.Display_Last_Trace)
        QtCore.QObject.connect(self.TagAll, QtCore.SIGNAL("clicked()"),Navigate.Tag_All_Traces)
        QtCore.QObject.connect(self.UnTagAll, QtCore.SIGNAL("clicked()"),Navigate.UnTag_All_Traces)
        QtCore.QObject.connect(self.Invert, QtCore.SIGNAL("clicked()"),Navigate.Invert_All_Tag_Values)
        QtCore.QObject.connect(self.Sweep_Number_Input_Field, QtCore.SIGNAL('editingFinished ()'),Navigate.Load_This_Sweep_Number)
        QtCore.QObject.connect(self.From, QtCore.SIGNAL('editingFinished ()'),Navigate.Check_From_To)
        QtCore.QObject.connect(self.To, QtCore.SIGNAL('editingFinished ()'),Navigate.Check_From_To)
        QtCore.QObject.connect(self.SQLight_File_Select_Window, QtCore.SIGNAL("clicked()"),Requete.Change_SQL_File)
        QtCore.QObject.connect(self.Delete_Current_Segment_Button, QtCore.SIGNAL("clicked()"),Infos.Delete_Current_Segment)
        QtCore.QObject.connect(self.Correspondance_info, QtCore.SIGNAL("clicked()"),Mapping.Correspondance)
       
#        QtCore.QObject.connect(self.Current_or_Average, QtCore.SIGNAL('activated(int)'),Infos.List_All_Globals)


            #Les signaux d'analyses globales
      
        averageaction = lambda: Analysis.Measure_on_Average(Display_Superimposed_Traces=True)
        QtCore.QObject.connect(self.Average, QtCore.SIGNAL("clicked()"),averageaction)
        QtCore.QObject.connect(self.Superimpose, QtCore.SIGNAL("clicked()"),Analysis.Display_Superimposed_Traces)
        QtCore.QObject.connect(self.Rasterplot, QtCore.SIGNAL("clicked()"),Analysis.Raster_Plot)
        QtCore.QObject.connect(self.Start_Spike_Sorting, QtCore.SIGNAL("clicked()"),Infos.SpikeSorting)
        QtCore.QObject.connect(self.ShowEvents, QtCore.SIGNAL("clicked()"),Analysis.Display_Events)


        #QtCore.QObject.connect(self.CallSpikes, QtCore.SIGNAL("clicked()"),Requete.Call_Spikes)
         
      
        QtCore.QObject.connect(self.Measure_Button, QtCore.SIGNAL("clicked()"),Analysis.Measure)
        QtCore.QObject.connect(self.Checkup, QtCore.SIGNAL("clicked()"),Analysis.Manip_Check_up)
        QtCore.QObject.connect(self.inf, QtCore.SIGNAL("clicked()"),Analysis.Display_Infos)
        QtCore.QObject.connect(self.Tagging_Tools, QtCore.SIGNAL("clicked()"),Infos.Retag)
        QtCore.QObject.connect(self.ShellButton, QtCore.SIGNAL("clicked()"),self.EmbeddedIpython)
        QtCore.QObject.connect(self.SendToSQl, QtCore.SIGNAL("clicked()"),Infos.SendToSQl)
        
       

            
            #Les signaux de mesure d'amplitude
        
        
        QtCore.QObject.connect(self.Baseline1_begin, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak1_begin, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline2_begin, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak2_begin, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline3_begin, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak3_begin, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline1_end, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak1_end, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline2_end, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak2_end, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline3_end, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak3_end, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline1_size, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak1_size, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline2_size, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak2_size, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Baseline2_size, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)
        QtCore.QObject.connect(self.Peak3_size, QtCore.SIGNAL('editingFinished ()'),Analysis.Check_Measuring_Parameters_Validity)

        QtCore.QObject.connect(self.PositiveOrNegativeMeasure, QtCore.SIGNAL('stateChanged(int)'),self.UpdatePositiveOrNegative)

        QtCore.QObject.connect(self.User_Defined_Measurement_Parameters, QtCore.SIGNAL('activated(int)'),Analysis.Load_User_Defined_Parameters)
        QtCore.QObject.connect(self.Add_User_Defined_Measurement_Parameters_Button, QtCore.SIGNAL("clicked()"),Analysis.Add_User_Defined_Measurement_Parameters)
        QtCore.QObject.connect(self.Remove_User_Defined_Measurement_Parameters_Button, QtCore.SIGNAL("clicked()"),Analysis.Remove_User_Defined_Measurement_Parameters)
        QtCore.QObject.connect(self.Set_User_Defined_Measurement_Parameters_to_Zero_Button, QtCore.SIGNAL("clicked()"),Analysis.Set_User_Defined_Measurement_Parameters_to_Zero)




        QtCore.QObject.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), Navigate.Update_SweepNumber_Slider)

        QtCore.QObject.connect(self.Tagging_Button, QtCore.SIGNAL("stateChanged(int)"),Navigate.Change_Tag_Checkbox_State)
        QtCore.QObject.connect(self.Display_Measures_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.Analyze_Filtered_Traces_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.Measure_From_Baseline1_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.Measure_From_Zero_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.Display_Spikes_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.Display_Charge_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.Remove_Leak_Button, QtCore.SIGNAL("stateChanged(int)"),Analysis.Measure_On_Off_Activated)
              
        QtCore.QObject.connect(self.Use_Spiketrains_Button, QtCore.SIGNAL("stateChanged(int)"),Requete.Activate_Spiketrains)

        QtCore.QObject.connect(self.SQLTabWidget, QtCore.SIGNAL('currentChanged(int)'),Requete.SetDBcall)
        
      
        
        QtCore.QObject.connect(self.SQLite_path, QtCore.SIGNAL('editingFinished ()'),Requete.Request_ComboBoxes_update)
        
        
        QtCore.QObject.connect(self.User, QtCore.SIGNAL('editingFinished ()'),Requete.Record_User_Parameters)
        QtCore.QObject.connect(self.Password, QtCore.SIGNAL('editingFinished ()'),Requete.Record_User_Parameters)
        QtCore.QObject.connect(self.DBname, QtCore.SIGNAL('editingFinished ()'),Requete.Record_User_Parameters)
        QtCore.QObject.connect(self.IPAdress, QtCore.SIGNAL('editingFinished ()'),Requete.Record_User_Parameters)
        QtCore.QObject.connect(self.SQLite_path, QtCore.SIGNAL('editingFinished ()'),Requete.Record_User_Parameters)

        QtCore.QObject.connect(self.Filtered_Display, QtCore.SIGNAL("stateChanged(int)"),Navigate.Load_This_Sweep_Number)
        QtCore.QObject.connect(self.SQLTabWidget, QtCore.SIGNAL("currentChanged(int)"),Requete.Adjust_Authorized_Functions)




        self.Superimpose_Used_Traces=False
        
        self.AnalysisWidget.setEnabled(False)
        self.SpikesWidget.setEnabled(False)
        self.NavigationWidget.setEnabled(False)
        self.MappingWidget.setEnabled(False)


        self.LoadedList=[]

        

        

        if os.path.isfile(self.param_inf[0]) == True:
            self.SQLTabWidget.setCurrentIndex(0) ## mettre ici la derniere condition en memoire
            
       
        else:
        
            try:
                self.SQLTabWidget.setCurrentIndex(0)
            except:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>SynaptiQs was unable to open SQLite or MySQL db.</b>
                <p>Please correct the path and Restart SynaptiQs.
                """)
                msgBox.exec_()

    def Create_Measure_Variables(self):
        
        #Les outils de mesure d'amplitude (Calcul de 3 pics)
        
            #Le dictionnaire contenant les valeurs
        try:
            liste = [("Baseline1_begin",float(self.param_inf[10])),
                            ("Baseline1_end",float(self.param_inf[11])),
                            ("Peak1_begin",float(self.param_inf[12])),
                            ("Peak1_end",float(self.param_inf[13])),
                            ("Baseline2_begin",float(self.param_inf[14])),
                            ("Baseline2_end",float(self.param_inf[15])),
                            ("Peak2_begin",float(self.param_inf[16])),
                            ("Peak2_end",float(self.param_inf[17])),
                            ("Baseline3_begin",float(self.param_inf[18])),
                            ("Baseline3_end",float(self.param_inf[19])),
                            ("Peak3_begin",float(self.param_inf[20])),
                            ("Peak3_end",float(self.param_inf[21])),
                            ("Baseline1_size",float(self.param_inf[22])),
                            ("Peak1_size",float(self.param_inf[23])),
                            ("Baseline2_size",float(self.param_inf[24])),
                            ("Peak2_size",float(self.param_inf[25])),
                            ("Baseline3_size",float(self.param_inf[26])),
                            ("Peak3_size",float(self.param_inf[27])),
                            ("Baseline1_meth",str(self.param_inf[28])),
                            ("Peak1_meth",str(self.param_inf[29])),
                            ("Baseline2_meth",str(self.param_inf[30])),
                            ("Peak2_meth",str(self.param_inf[31])),
                            ("Baseline3_meth",str(self.param_inf[32])),
                            ("Peak3_meth",str(self.param_inf[33]))]
                             
        except ValueError:
            sys.exit()
            #sys.exit(app.exec_()) 
        self.measurecoord={}
        for i in range(len(liste)):
            self.measurecoord[liste[i][0]]=liste[i][1]
                             
                 
        self.listofmeasurecoord = ["Baseline1_begin","Baseline1_end",
                                   "Peak1_begin","Peak1_end",
                                   "Baseline2_begin","Baseline2_end",
                                   "Peak2_begin","Peak2_end",
                                   "Baseline3_begin","Baseline3_end",
                                   "Peak3_begin","Peak3_end"]


        self.listofcoord=[("Baseline1_begin","Baseline1_end","Baseline1_size"),
                   ("Peak1_begin","Peak1_end","Peak1_size"),
                   ("Baseline2_begin","Baseline2_end","Baseline2_size"),
                   ("Peak2_begin","Peak2_end","Peak2_size"),
                   ("Baseline3_begin","Baseline3_end","Baseline3_size"),
                   ("Peak3_begin","Peak3_end","Peak3_size")]        


    def UpdatePositiveOrNegative(self):
        if self.PositiveOrNegativeMeasure.checkState() == 2:
            Mapping.CM.Types_of_Events_to_Measure = 'Negative'
        else:
            Mapping.CM.Types_of_Events_to_Measure = 'Positive'
            
    def Update_Menu_Options(self):
        if QtCore.QObject().sender().text()==  "Sort Block by File Name"  :
            self.Sort_Blocks_by_FileName= not self.Sort_Blocks_by_FileName
#        elif QtCore.QObject().sender().text()==  "Mapping on Negative currents"  :
#            QtCore.QObject().sender().setText("Mapping on Positive currents")
#            Mapping.CM.Types_of_Events_to_Measure = 'Positive'
#        elif QtCore.QObject().sender().text()==  "Mapping on Positive currents"  :
#            QtCore.QObject().sender().setText("Mapping on Negative currents")
#            Mapping.CM.Types_of_Events_to_Measure = 'Negative'

    def Saving_Directory(self):
        """
        This function will change (and save) the working directory
        """

        
        path = QtGui.QFileDialog()
        path.setDirectory(self.desktop)
        #path.setNameFilter("Image files (*.png *.xpm *.jpg *.bmp)")
        #path.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        path.setFileMode(QtGui.QFileDialog.Directory)
        
        if (path.exec_()) :
            self.desktop=path.directory().absolutePath()  
            self.param_inf[6]=self.desktop
            Requete.Record_User_Parameters()
            return True

    def Show_Main_Figure(self):
        self.displaying=QtGui.QWidget()

        self.MainFigure = MyMplWidget(subplots=None,title = 'Current trace',sharex=True)

        self.MainFigure.canvas.Compute_Initial_Figure()
        self.RAW_Display = QtGui.QCheckBox("RAW signal")
        
        self.Filtered_Display = QtGui.QCheckBox("Filtered signal")
        self.Median_Filtered_Display = QtGui.QCheckBox("Median Filter")
        self.low_freq = QtGui.QLineEdit("0")
        self.low_freq.setPlaceholderText( "in Hz")
        self.low_freq_label = QtGui.QLabel("Low frequency")
        self.high_freq = QtGui.QLineEdit("2000")
        self.high_freq.setPlaceholderText( "in Hz")
        self.high_freq_label = QtGui.QLabel("High frequency")
        self.median_filt = QtGui.QLineEdit("1")
        self.median_filt.setPlaceholderText( "in pts")
        self.median_filt_label = QtGui.QLabel("median filter")
        self.Superimposetraces = QtGui.QCheckBox("Superimpose Traces")
        self.Autoscale = QtGui.QCheckBox("AutoScale")
        self.Autoscale.setCheckState(2)   
        
        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.RAW_Display)
        hbox.addWidget(self.Filtered_Display)
        hbox.addWidget(self.Median_Filtered_Display)
        hbox.addWidget(self.low_freq)
        hbox.addWidget(self.low_freq_label)
        hbox.addWidget(self.high_freq)
        hbox.addWidget(self.high_freq_label)
        hbox.addWidget(self.median_filt)
        hbox.addWidget(self.median_filt_label)
        
        vbox=QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.MainFigure)
        
        hbox=QtGui.QHBoxLayout()
        hbox.addWidget(self.Superimposetraces)
        hbox.addWidget(self.Autoscale)
        vbox.addLayout(hbox)
        
        self.displaying.setLayout(vbox)

        QtCore.QObject.connect(self.high_freq, QtCore.SIGNAL('editingFinished ()'),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.low_freq, QtCore.SIGNAL('editingFinished ()'),Analysis.Measure_On_Off_Activated)
        QtCore.QObject.connect(self.median_filt, QtCore.SIGNAL('editingFinished ()'),Analysis.Measure_On_Off_Activated)


        self.displaying.show()
        
        
        try:
            Navigate.Load_This_Trace(Requete.Analogsignal_ids[Requete.Current_Sweep_Number])
            self.MainFigure.canvas.Update_Figure()
        except (AttributeError,IndexError):
            pass

       
    def Save_Trace(self,array=None):
        
        """
        Pour sauver sous forme de fichier ASCII les données
        """
        
       
        if array == None:
            print str(self.Current_or_Average.currentText())
            currentname = str(self.Current_or_Average.currentText())
            currentpath = str(self.desktop)+'/'+currentname+'_'+str(self.SaveName.text())+'.txt'
        else:
            currentname=array
            currentpath = str(self.desktop)+'/'+str(array)+'.txt'
            
        
        try:
            if type(eval(currentname)) in [numpy.array,numpy.ndarray,list,int,float,tuple]:
                numpy.savetxt(currentpath, eval(currentname))
                print "--> Array was saved in ",currentpath
            elif type(eval(currentname)) == dict:
                import csv
                w = csv.writer(open(currentpath, "w"))
                for key, val in dict.items():
                    w.writerow([key, val])
                print "--> Dictionnary was saved in ",currentpath
            else:
                print 'data type ',type(eval(currentname)),' not supported yet'
                return
                
        except IOError: 
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Saving Error</b>
            <p>This Folder do not exist, please set a new Saving folder
            """)
            msgBox.exec_()            
            Val=self.Saving_Directory()
            
            if Val == True:
               self.Save_Trace() 

    def IpythonClosed(self):
        self.IPythonOpened=False
        
        
    def EmbeddedIpython(self):
        
        if self.IPythonOpened==False:
            from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
            from IPython.frontend.qt.inprocess import QtInProcessKernelManager
            #from IPython.lib import guisupport
            
            self.Shell_Widget = QtGui.QDockWidget()
            self.MainWindow.addDockWidget(4,self.Shell_Widget) #On attache le Widget au WIdget parent, et on definit sa position
            self.Shell_Widget.setMinimumSize(640,480)  
            self.Shell_Widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
            QtCore.QObject.connect(self.Shell_Widget, QtCore.SIGNAL('destroyed()'),self.IpythonClosed)            
           
  
            kernel_manager = QtInProcessKernelManager()
            kernel_manager.start_kernel()
            kernel = kernel_manager.kernel
            kernel.gui = 'qt4'
            
            kernel_client = kernel_manager.client()
            kernel_client.start_channels()
            
            def stop():
                kernel_client.stop_channels()
                kernel_manager.shutdown_kernel()
                # here you should exit your application with a suitable call
                sys.exit()
            
            widget = RichIPythonWidget()
            widget.kernel_manager = kernel_manager
            widget.kernel_client = kernel_client
            widget.exit_requested.connect(stop)
            widget.setWindowTitle("IPython shell")
            widget.setMinimumSize(640,480)
            widget.setGeometry(0, 20, 640, 500)
            widget.setParent(self.Shell_Widget)
            
            self.Shell_Widget = widget
            self.Shell_Widget.show()
            
    
        
            self.Shell_Widget.show()        
            self.IPythonOpened=True
        else:
            #self.Shell_Widget.deleteLater()
            self.Shell_Widget.setVisible(False)
            #self.Shell_Widget.stop()
            self.Shell_Widget.hide()
            self.Shell_Widget.destroy()
            
            #self.Shell_Widget.close()
            self.IPythonOpened=False
            

        
       
#    def Backup_All(self):
#        
#        import shelve
#        
#        filename='C:\\Users\\Antoine.VALERA.NEUROSCIENCE\\Desktop\\test'
#        my_shelf = shelve.open(filename,'n')
#        
#        for key in dir():
#            try:
#                my_shelf[key] = globals()[key]
#            except:
#                #
#                # __builtins__, my_shelf, and imported modules can not be shelved.
#                #
#                print('ERROR shelving: {0}'.format(key))
#                
#        my_shelf.close()