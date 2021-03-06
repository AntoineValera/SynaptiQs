# -*- coding: utf-8 -*-
"""
Created on Tue May 21 22:40:47 2013

@author: Antoine Valera
"""




import os
from PyQt4 import QtCore, QtGui
from matplotlib import numpy
from OpenElectrophy import gui,AnalogSignal,SpikeTrain,Session,open_db,sql,sqlalchemy
import time



class Requete(object):

    """
    This Class controls the SQL request and do the initial request by calling Datacall()
    
    important arrays are:
        Requete.url : the url of the request
        Requete.analogsignal_zero : The first Analogsignal (the whole class) of the request
        Requete.Current_Signal : the first Analogsignal.signal
        Requete.sr : the first Analogsignal.sampling_rate
        Requete.timescale : a timescale array as long as the first signal 
        Requete.Current_Sweep_Number : The currently displayed sweep number.
                                       It is also the position of this sweep in all the "request arrays" (see below)
        
        When doing a request, following arrays are created (length of the array is the number of analogsignals in the request,
                                                            thus, if you type <<array>>[Requete.Current_Sweep_Number], you have all the information
                                                            of the currently displayed sweep.)
    
        Requete.Block_ids : all the block.id 's of the traces, in one array
        Requete.Block_date : all the block.date of the traces, in one array
        Requete.Segment_ids : all the segment.id 's of the traces, in one array
        Requete.Analogsignal_ids : all the analogsignal.id 's of the traces, in one list
                                   OR if multiple chanels
                                   a list of tuples
        Requete.Analogsignal_name : all the analogsignal.name of the traces, in one array
        tag  : all the analogsignal.tag of the traces, in one array
            --> This one is then converted in Requete.tag, which is a dictionnary. XXXXXXXXXX explanations to be added here
        Requete.Analogsignal_channel : all the analogsignal.channel of the traces, in one array
        Requete.Analogsignal_sampling_rate : all the analogsignal.sampling_rate 's of the traces, in one array
        Requete.Block_fileOrigin : all the block.fileorigin of the traces, in one array
        Requete.Block_Info : all the block.info of the traces, in one array
        Requete.Analogsignal_signal_shape : The length in points of the signal, in one array

       
        ***If you activate the spiketrains, and if there is at least a Neuron
        Requete.Spiketrain_ids : all the spiketrain.id 's of the traces, in one array
        Requete.Spiketrain_neuron_name : all the spiketrain.name of the traces, in one array
        Requete.Spiketrain_t_start  : all the spiketrain.t_start of the traces, in one array
        Requete.Spiketrain_Neuid  : all the spiketrain.id_Neuron of the traces, in one array
    
    
    """
    def __init__(self):
        self.__name__="Requete"
        self.Select_Supplement=''
        self.Where_Supplement=''
        self.Arraylist=''
        self.query=""
        
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
            
    def Adjust_Authorized_Functions(self):
        if Main.SQLTabWidget.currentIndex() == 2:
            Main.SpikesWidget.setEnabled(True)
            self.SpikeTrainfromLocal={}
            self.AmpSpikeTrainfromLocal={} 
            if hasattr(Requete, 'Analogsignal_ids'):
                self.Spiketrain_ids=numpy.copy(Requete.Analogsignal_ids)            
        else:
            pass

        
    def Modify_DB_Structure(self):
        try:
            self.modifydbmodule=gui.tabledesign.TableDesign(metadata=self.Global_Meta,session=self.Global_Session)#,globalApplicationDict=self.globalApplicationDict)
            self.modifydbmodule.show()
        except AttributeError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Error</b>
            <p>No database selected yet.
            <p>Please access the database you want to use once
            """)    
            msgBox.exec_()            

    def Change_SQL_File(self,New_File_Path=None):
        """
        This function open a dialog window to change the SQLite database file
        You can directly change the path with New_File_Path input
        """
        if New_File_Path != None:
            Main.SQLite_path.setText(File_Selector.selectedFiles()[0])
            self.Record_User_Parameters()
            
        else:
            File_Selector = QtGui.QFileDialog()
            File_Selector.setNameFilter("SQLite DB files (*.db)")
            File_Selector.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            File_Selector.setFileMode(QtGui.QFileDialog.ExistingFiles)
            
            #If it worked, the loacation of the file is saved in Record_User_Parameters
            if (File_Selector.exec_()) : 
                Main.SQLite_path.setText(File_Selector.selectedFiles()[0])
                self.Record_User_Parameters()

   
    def Convert(self):
        new=[]
        for i in range(len(self.Analogsignal_ids)):
            new.append([0]*int(self.NumberofChannels))
            for j in range(self.NumberofChannels):
                    new[i][j]=int(self.tag["Selection"][i*self.NumberofChannels+j]) 
        
        self.tag["Selection"]=new 
   
                    
    def Final_Request(self):
        """
        This function call the final request.
        It loads all the parameters into SynaptiQs
        """
            
            
        if Main.Reset_Check.checkState()==2:
            self.Datacall()
            Main.Reset_Check.setCheckState(0)
            
        self.Datacall()

        #check if it's the first load.
        if Main.AnalysisWidget.isEnabled() == False:
            firstload=True
        else:
            firstload=False    

        #Once the request is done, we can activate all the Widgets
        Main.AnalysisWidget.setEnabled(True)
        Main.NavigationWidget.setEnabled(True)
        Main.MappingWidget.setEnabled(True)

        #This auto-activates the "Display Spikes" function, if there is a loaded SpikeTrain.
        if Main.Use_Spiketrains_Button.checkState() == 2 and Main.Filter_NeuronName.count() > 1 :         
            Main.Display_Spikes_Button.setCheckState(2)
        else:       
            Main.Display_Spikes_Button.setCheckState(0)
        
        
        self.Current_Signal = self.analogsignal_zero.signal #First Signal is created
        

        
        if len(set(self.Signal_Length))>1:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>WARNING</b>
            <p>Caution, the total length of the sweeps vary.
            Only the shortest common duration is used.
            i.e. """ +str(self.Shortest_Sweep_Length*1000.)+ """ ms.            
            SOME TRACES WILL BE CROPPED COMPARED TO THE ORIGINAL ONES
            """)    
            msgBox.exec_()            
            
            
        
        
            
        self.timescale=numpy.array(range(int(self.BypassedSamplingRate*self.Shortest_Sweep_Length)))*1000/self.BypassedSamplingRate #This is a one second timescale with the highest sampling rate
        Main.slider.setRange(0, len(self.Analogsignal_ids)-1)#/self.NumberofChannels-1) #definit le range du slider sweepnb
        Main.From.setText(str(0))
        Main.To.setText(str(len(self.Analogsignal_ids)-1))#/self.NumberofChannels-1)) 
        
        Mapping.Autofill_Coordinates_Values_from_Tag_Field()
        
        Mapping.CurrentMapFocus.clear()
        for i in range(self.NumberofChannels):
            Mapping.CurrentMapFocus.addItem(str(i))
        
        
        Navigate.Load_This_Sweep_Number(0)

        if firstload == True:
            Main.User_Defined_Measurement_Parameters.setCurrentIndex(0)
            Analysis.Load_User_Defined_Parameters(0,True)

            #Mapping.Load_User_Defined_Parameters(0,True)
            #Mapping.Load_User_Defined_Parameters(0,True)
    

    def copythis(self,indexes,new):
        from copy import deepcopy
        temp=deepcopy(indexes)
        for i in range(len(indexes)):#aka channels
            for j in range(len(indexes[i])): #aka individual analogsignals or spiketrains
                temp[i][j]=new[indexes[i][j]]
        return temp


        
                 

    def Datacall(self): #Fait la requete SQL et affiche la premiere trace
        """
        This function do the final request
        It creates important variables:
            self.url is the currently used URL
        
        """
        
        # Ouverture de la base de données
        print '################################################################################' 
        print '################################################################################'
        print "########################   THIS IS THE FINAL QUERY   ##########################" 
        Main.Current_or_Average.clear()
        Main.ExistingSweeps=[]
        Main.Current_or_Average.addItems(Main.ExistingSweeps)
        
        if Main.SQLTabWidget.currentIndex() == 0 :
            print "-----------> You are using a MySQL DataBase"
            self.url = 'mysql://'+str(Main.User.text())+':'+str(Main.Password.text())+'@'+str(Main.IPAdress.text())+'/'+str(Main.DBname.text())
            Info_Message="You Are Using a MySQL DataBase with "+self.url+" URL"
            Main.status_text.setText(Info_Message)  


        if Main.SQLTabWidget.currentIndex() == 1 :
            print "-----------> You are using a SQLite DataBase"
            self.url = "sqlite:///"+str(Main.SQLite_path.text()) 
            Info_Message="You Are Using a SQLite DataBase with "+self.url+" URL"
            Main.status_text.setText(Info_Message)  
  
        self.Global_Meta=open_db( url = self.url)
        self.Global_Session=Session()
        

        #self.globalApplicationDict = gui.guiutil.globalapplicationdict.GlobalApplicationDict()

        
        
        print "-----------> used URL is :  ",self.url,"\n\n\n"
        
        try :
            
            exec(self.Arraylist+"self.Block_ids,self.Block_date,self.Segment_ids,self.Analogsignal_ids,self.Analogsignal_name,self.tag,self.Analogsignal_channel,self.Analogsignal_sampling_rate,self.Block_fileOrigin,self.Block_Info,self.Spiketrain_ids,self.Spiketrain_neuron_name,self.Spiketrain_t_start,self.Spiketrain_Neuid,self.Analogsignal_signal_shape = sql(self.query)")
            Main.SpikesWidget.setEnabled(True)
            
            
            print "-----------> This is the whole query command\n", self.query
            print "-----------> End of the Query"
            
        except:
            try:
                exec(self.Arraylist+"self.Block_ids,self.Block_date,self.Segment_ids,self.Analogsignal_ids,self.Analogsignal_name,self.tag,self.Analogsignal_channel,self.Analogsignal_sampling_rate,self.Block_fileOrigin,self.Block_Info,self.Analogsignal_signal_shape = sql(self.query)")
                self.Spiketrain_ids = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                self.Spiketrain_neuron_name = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                self.Spiketrain_t_start = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                self.Spiketrain_Neuid = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                Main.SpikesWidget.setEnabled(True)
                
                print "-----------> This is the whole query command\n", self.query,"\n\n\n"
                print "-----------> End of the Query"


            except sqlalchemy.exc.ResourceClosedError:  
                
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Error</b>
                <p>Your SQL query returned nothing 
                <p>Did You swithched from MySQL to SQLite without refreshing the database?
                """)    
                msgBox.exec_()
                self.Request_ComboBoxes_update()
                
                return
                
            except sqlalchemy.exc.OperationalError:  
                
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Error</b>
                <p>Your personalized SQL query probably contains an error 
                <p>Is the Table/Column name correct?
                <p>Please re-check the syntax
                """)    
                msgBox.exec_()
                self.Request_ComboBoxes_update()
                return
            except sqlalchemy.exc.ProgrammingError: 
                
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Error</b>
                <p>Your personalized SQL query probably contains an error 
                <p>Please re-check the syntax
                <p>Did you forget the Operation Symbol? (eg: > // < // = // IN() // like '%' // IS NULL //etc...)
                
                """)    
                msgBox.exec_()
                self.Request_ComboBoxes_update()
                
                return
            except ValueError: # If a personalized request was updated in the text editor, we must adjust the nuumber of arrays so it matches each SELECT element
                #self.Arraylist=""
                bypass=False
                counter=0
                while bypass==False and counter<10:
                    try:
                        print "self.UnnamedArray"+str(counter)+" created"
                        counter+=1
                        self.Arraylist+="self.UnnamedArray"+str(counter)+","
                        exec(self.Arraylist+"self.Block_ids,self.Block_date,self.Segment_ids,self.Analogsignal_ids,self.Analogsignal_name,self.tag,self.Analogsignal_channel,self.Analogsignal_sampling_rate,self.Block_fileOrigin,self.Block_Info,self.Analogsignal_signal_shape = sql(self.query)")
                        bypass=True
                        self.Spiketrain_ids = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                        self.Spiketrain_neuron_name = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                        self.Spiketrain_t_start = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                        self.Spiketrain_Neuid = list(numpy.zeros(int(len(self.Block_ids)))*numpy.NaN)
                        Main.SpikesWidget.setEnabled(True)   
                    except:
                        pass
      
        Mapping.Reset_Mapping_Variables() #here so it can know if there are some spiketrains to use or not        
        
        #TODO : recheck all variables to be deleted here
        RequeteArrays=["Requete.Block_ids",
                       "Requete.Segment_ids",
                       "Requete.Analogsignal_ids",
                       "Requete.Block_date",
                       "Requete.Analogsignal_name",
                       "Requete.Analogsignal_channel",
                       "Requete.Block_fileOrigin",
                       "Requete.Block_Info",
                       "Requete.Spiketrain_ids",
                       "Requete.Spiketrain_neuron_name",
                       "Requete.Spiketrain_t_start",
                       "Requete.Spiketrain_Neuid"]
                       
                       
                       
        OtherRequeteArrays=["Requete.tag['Selection']",
                            "Requete.Analogsignal_sampling_rate",
                            "Requete.Analogsignal_signal_shape"]
                
        OtherArrays=["Navigate.si",
                     "Navigate.timescale",
                     "Requete.NumberofChannels"]
        
        Infos.Add_Array(Arrays=RequeteArrays+OtherRequeteArrays+OtherArrays)  
        
        self.NumberofChannels=len(list(set(self.Analogsignal_name)))
        
        print 'There are ',self.NumberofChannels,' channels'
        
        List=zip(list(self.Analogsignal_name),list(self.Analogsignal_ids))
        
        ListOfIndexesPerChannel=[]
        #We split the channels using self.Analogsignal_name
        #a list is created for each name : eg if the channel name is RecordA
        #we create self.RecordA, which contains all the analogsiganl ids of this channel
        for i,j in enumerate(list(set(self.Analogsignal_name))):
            #we create one list per channel
            try:
                setattr(self,j,[])
            except TypeError:
                j='noname'
                setattr(self,j,[])
                
            
            #We detect all ids form this channel
            for k in range(len(self.Analogsignal_ids)):
                if str(List[k][0]) == str(j):
                    eval('self.'+j).append(k)
            
            #we add the list to a list of list
            ListOfIndexesPerChannel.append(eval('self.'+j))
            #print 'channel ',j,' ids are ',eval('self.'+j)
        
        
            
        for i in RequeteArrays:
            i=i.replace('Requete.','self.')
            temp=self.copythis(ListOfIndexesPerChannel,eval(i))
            i=i.replace('self.','')
            setattr(self,i,Infos.Zip(temp))
            
       
        self.Current_Sweep_Number=0
        self.st_currentid=0
    

        try:
            Initial_Points_by_ms=self.Analogsignal_sampling_rate[0]/1000#self.Analogsignal_sampling_rate[0]/1000 #This is the sampling rate of the first array
        except IndexError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("""
            <b>Error</b>
            <p>The SQL request returned nothing 
            <p>I would suspect an error in you query.
            <p>click on Reset Fields and try again
            """)                   
            msgBox.exec_()
            return
        
        #In some query, the sampling rate and/or the wavelength can be different.
        #The sampling rate issue is solved by downscaling all waves to the lowest sampling rate detected
        #The wavelength issue is solved by croping all waves to fit the shortest one
        self.BypassedSamplingRate=min(self.Analogsignal_sampling_rate)
        
        for i in range(len(self.Analogsignal_signal_shape)):
            self.Analogsignal_signal_shape[i]=float(self.Analogsignal_signal_shape[i].replace('L',''))


        self.Signal_Length=self.Analogsignal_signal_shape/self.Analogsignal_sampling_rate
        self.Shortest_Sweep_Length=min(self.Signal_Length)  
        
        if len(list(set(self.Analogsignal_sampling_rate)))>1: 
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Warning</b>
            <p>You have different sampling rate in your request. 
            <p>All files are downsampled to the lowest sampling rate
            i.e. """+str(int(self.BypassedSamplingRate)/1000)+""" points per ms 
            """)                  
            msgBox.exec_()

        
        
        Info_Message="sampling rate =" + str(Initial_Points_by_ms)+"points per ms. The total number of sweeps is "+str(len(self.Analogsignal_ids))
        Main.status_text.setText(Info_Message)          

        print "-----------> Spiketrains Ids (if exist) are :",self.Spiketrain_ids
        
        self.SpikeTrain_id_and_Corresponding_AnalogSignal_id_Dictionnary={}
 
        
        for n in range(self.NumberofChannels):
            for i in range(len(self.Spiketrain_ids)):
                self.SpikeTrain_id_and_Corresponding_AnalogSignal_id_Dictionnary[self.Spiketrain_ids[i][n]]=self.Analogsignal_ids[i][n]
 
        
        Main.MainFigure.canvas.fig.clear()
        flatlist=[item for sublist in self.Analogsignal_name for item in sublist]
        for i in range(len(list(set(flatlist)))):
            Main.MainFigure.canvas.fig.add_subplot(len(list(set(flatlist))),1,i+1)
            #TODO : set subplot title

        try:
            self.analogsignal_zero = AnalogSignal().load(self.Analogsignal_ids[0][0],session=self.Global_Session)
                
        except:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Request Error</b>
            <p>This may be due to an incorrect request or an error in the UserPref file,
            <p>or a error while initially importing the file in the database
            <p>If the error persists, you can try to delete the UserPref.txt file (in home/$USER$/.SynaptiQs/Core/)
            """)                  
            msgBox.exec_()

        #Todo: the tag thing is ugly and must be improved. this is a hack to keep it working with multichannel
        select=range(0,len(self.tag),self.NumberofChannels)  
        temp=[]
        for i in select:
            temp.append(self.tag[i])
            
        tag = self.Transform_a_String_in_Dictionnary(source=temp)

        
        #For Selection, we still have to do it the old way
        self.tag = self.Transform_a_String_in_Dictionnary(source=self.tag)

        if Main.Reset_Check.checkState()==2:
            self.Reset_the_Tag_Field(self.tag)
            return
        
        #Pour le champs Tag, controle systematique de son existence    
        NewSystem=True

        if self.tag.has_key("Selection")==False:
            #for some reason, I had to to that since I move to multichannel
            new=[]
            for i in range(len(self.Analogsignal_ids)):
                new.append([0]*int(self.NumberofChannels))            
            self.tag["Selection"]=new
            for i in range(len(self.Analogsignal_ids)):
                for j in range(self.NumberofChannels):
                    self.tag["Selection"][i][j]=0
        elif self.tag.has_key("Selection")==True:
            for i in range(len(self.Analogsignal_ids)):
                for j in range(self.NumberofChannels):
                    try: 
                        self.tag["Selection"][i][j]=int(self.tag["Selection"][i][j])
                    except ValueError:
                        self.tag["Selection"][i][j]=0
                    except TypeError:
                        NewSystem=False
                        break
                    except IndexError:
                        msgBox = QtGui.QMessageBox()
                        msgBox.setText(
                        """
                        <b>Warning</b>
                        <p>One of the file in the query use the old tag system
                        blocks are %s
                        please load each block
                        """ %(list(set(self.Block_ids))))                    
                        msgBox.exec_()
                        #self.Convert()
                        return
                        
        #If the old tag system was used, we convert it here to the new system
        if NewSystem==False:
            print 'Old tag system detected'
            self.Convert()
          
        #Finally, we overwrite the whole self.tag except Selection
        for keys in self.tag:
            if keys != 'Selection':
                self.tag[keys]=tag[keys]

        
        
        Main.Current_or_Average.setCurrentIndex(Main.Current_or_Average.findText('Navigate.si'))
        self.Add_Dictionnary_Arrays()
        self.Record_User_Parameters()

                                       

    def Transform_a_String_in_Dictionnary(self,source=None):
        
        destination={}
        compteur=0
        if Main.Reset_Check.checkState()==0:
            try:    
                for i in source:
                    i=str(i)
                    for j in i.split(','):
                        ##on créé les bonnes entrées dans le dico au 1er tour
                        for u in ['{','}',' ','"',"'"," "]:
                            j = j.replace(u, '')
                        k=j.split(':')
                        if compteur == 0:
                            destination[k[0]]=['']*len(source)
                        destination[k[0]][compteur]=k[1]
                    compteur+=1
            except IndexError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Error in Tag Field or missing Info</b>
                <p>SynaptiQs was Unable to import all Tags info,
                <p>Missing fields were created""")                    
                msgBox.exec_()
 
                print destination        
        return destination
        
    def Add_Dictionnary_Arrays(self):

        if Main.param_inf[5]=='':
            Main.param_inf[5]=["X_coord","Y_coord","Amplitude 1","Amplitude 2","Amplitude 3"]
            self.Record_User_Parameters()
            self.DefaultTagList=Main.param_inf[5]
        else:
            self.DefaultTagList=str(Main.param_inf[5])
            self.DefaultTagList=self.DefaultTagList.replace("[","")
            self.DefaultTagList=self.DefaultTagList.replace("]","")
            self.DefaultTagList=self.DefaultTagList.replace("'","")
            self.DefaultTagList=self.DefaultTagList.replace(" ","")

            self.DefaultTagList=self.DefaultTagList.split(",")
            
        
        for i in self.DefaultTagList:
            if self.tag.has_key(i)==False:
                self.tag[i]=[0]*len(self.Analogsignal_ids)
                for j in range(len(self.Analogsignal_ids)):
                    self.tag[i][j]=None   




    def Reset_the_Tag_Field(self,tag=None):
        """
        If the AnalogSignal.Tag field is corrupted, it can be restored
        """
        print 'this function is sensitive and was not checked yet'
        
        
        if Main.Reset_Check.checkState()==2:
            for n in range(self.NumberofChannels):
                for i in range(len(self.Analogsignal_ids)):
                    self.ResetTag = AnalogSignal().load(self.Analogsignal_ids[i][n])
                    self.ResetTag.tag=None
                    self.ResetTag.save() 
                    print 'Analogsignal', self.Analogsignal_ids[i][n], 'reset to initial Values'
#                self.tag["Selection"]=[0]*len(tag)
#            
#            try:
#                Navigate.UnTag_All_Traces()
#            except IndexError:
#                print "Error in final untaging. It shouldn't have consequences"
#                pass

            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Reset Complete</b>
            <p>The AnalogSignal.Tag Field was erased
            """)                 
            msgBox.exec_()
            
            
            
            
            
            
    def Request_ComboBoxes_update(self):
        print "############################ NEW DYNAMIC QUERY #################################" 
        # Ouverture de la base de données
        
        if Main.SQLTabWidget.currentIndex() == 0 :
            print "-----------> You are using a MySQL DataBase"
            print "-----------> MySQL used parameters are: ",Main.DBinf
            self.url = 'mysql://'+str(Main.User.text())+':'+str(Main.Password.text())+'@'+str(Main.IPAdress.text())+'/'+str(Main.DBname.text())
            Info_Message="You Are Using a MySQL DataBase with "+self.url+" URL"
            Main.status_text.setText(Info_Message)
        
 
        elif Main.SQLTabWidget.currentIndex() == 1 :
            self.url = "sqlite:///"+str(Main.SQLite_path.text()) 
            
            print "-----------> You are using SQLite DataBase : ",self.url
            Info_Message="You Are Using a SQLite DataBase with "+self.url+" URL"
            Main.status_text.setText(Info_Message) 
            
        elif Main.SQLTabWidget.currentIndex() == 2:
            self.url=""
            self.query=""
            return
            
#        try:    
        self.Global_Meta=open_db( url = self.url)
        self.Global_Session=Session()
            #self.globalApplicationDict = gui.guiutil.globalapplicationdict.GlobalApplicationDict()

        # Eléments de la requete    
        
        Date=' = '+"'"+Main.Filter_Date.currentText()+"%')"
        Block=' = '+Main.Filter_BlockId.currentText()+")"
        Experiment=' = '+"'"+Main.Filter_BlockInfo.currentText()+"')"
        Name=' = '+"'"+Main.Filter_ChannelName.currentText()+"')"
        Chan=' = '+Main.Filter_ChannelNumber.currentText()+")"
        Neu=' = '+Main.Filter_NeuronName.currentText()+")"

        ###


        if Main.Filter_Date.currentText()=='None':
            Date= " like '%' or block.datetime IS NULL)"   
        if Main.Filter_BlockId.currentText()=='None':
            Block=" like '%' or block.id IS NULL)" 
        if Main.Filter_BlockInfo.currentText()=='None':
            Experiment=" like '%' or block.info IS NULL)" 
        if Main.Filter_ChannelName.currentText()=='None':
            Name=" like '%' or analogsignal.name IS NULL)" 
        if Main.Filter_ChannelNumber.currentText()=='None':
            Chan=" like '%' or analogsignal.channel IS NULL)" 
        if Main.Filter_NeuronName.currentText()=='None' and Main.Use_Spiketrains_Button.checkState() == 2:
            Neu=" like '%' or analogsignal.channel IS NULL)" 
      
        ###


        if Main.SQLTabWidget.currentIndex() == 1 :
            Select_Option = "SELECT"
        elif Main.SQLTabWidget.currentIndex() == 0 :
            Select_Option = "SELECT STRAIGHT_JOIN"
        
        if Main.Use_Spiketrains_Button.checkState() == 0:
            Select_Core ="""
            block.id,
            block.datetime,
            segment.id,
            analogsignal.id,
            analogsignal.name,
            analogsignal.Tag,
            analogsignal.channel,
            analogsignal.sampling_rate,
            block.fileOrigin,
            block.info,
            analogsignal.signal_shape
            """
            From_Core="""
            FROM analogsignal
            JOIN segment on analogsignal.id_segment = segment.id
            JOIN block on segment.id_block = block.id"""
            Where_Core="""
            WHERE (block.datetime %s
            AND (block.id %s
            AND (block.info %s
            AND (analogsignal.name %s 
            AND (analogsignal.channel %s"""
            Order_Core="""
            ORDER BY analogsignal.id
            """
            
            self.query = Select_Option+self.Select_Supplement+Select_Core+From_Core+Where_Core % (Date,Block,Experiment,Name,Chan)+self.Where_Supplement+Order_Core 
            
            if Main.SQLTabWidget.currentIndex() == 1 :
                self.query = self.query.replace("block.datetime  =","block.datetime  like")            
            
            try :
                exec(self.Arraylist+"self.Block_ids,self.Block_date,channels,ids,self.Analogsignal_name,self.tag,self.Analogsignal_channel,samprate,self.Block_fileOrigin,self.Block_Info,self.Analogsignal_signal_shape = sql(self.query)")
            except sqlalchemy.exc.OperationalError:
                
                metadata.bind = self.Global_Meta
                metadata.reflect()                
                for tablename, table in metadata.tables.iteritems() :
                    print tablename
                    print table, type(table)
                
                
                
                
                
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>SynaptiQs was unable to do the request</b>
                <p>Please check database filepath
                <p>You may have to create analogsignal.tag column
                <p>Table editor can be accessed with CTRL+E""")                    
                msgBox.exec_()
                
            except sqlalchemy.exc.ArgumentError:
                pass
               
                   
        elif Main.Use_Spiketrains_Button.checkState() == 2:  
            if Chan == " like '%' or analogsignal.channel IS NULL)":
                Chan = " = spiketrain.channel)"
            Select_Core = """
            block.id,
            block.datetime,
            segment.id,
            analogsignal.id,
            analogsignal.name,
            analogsignal.Tag,
            analogsignal.channel,
            analogsignal.sampling_rate,
            block.fileOrigin,
            block.info,
            spiketrain.id,
            spiketrain.name,
            spiketrain.t_start,
            spiketrain.id_neuron,
            analogsignal.signal_shape"""
            From_Core = """
            FROM analogsignal
            JOIN segment on analogsignal.id_segment = segment.id
            JOIN spiketrain on segment.id=spiketrain.id_segment 
            JOIN block on segment.id_block = block.id"""
            Where_Core="""
            WHERE (block.datetime %s
            AND (block.id %s
            AND (block.info %s
            AND (analogsignal.name %s 
            AND (analogsignal.channel %s
            AND (spiketrain.id_neuron %s"""
            Order_Core="""
            ORDER BY analogsignal.id
            """   
            self.query = Select_Option+self.Select_Supplement+Select_Core+From_Core+Where_Core % (Date,Block,Experiment,Name,Chan,Neu)+self.Where_Supplement+Order_Core 
            
            if Main.SQLTabWidget.currentIndex() == 1 :
                self.query = self.query.replace("block.datetime  =","block.datetime  like")
            
            
            try :
                exec(self.Arraylist+"self.Block_ids,self.Block_date,channels,ids,self.Analogsignal_name,self.tag,self.Analogsignal_channel,samprate,self.Block_fileOrigin,self.Block_Info,self.Spiketrain_ids,self.Spiketrain_neuron_name,self.Spiketrain_t_start,self.Spiketrain_Neuid,self.Analogsignal_signal_shape = sql(self.query)")
                print self.query
            except sqlalchemy.exc.OperationalError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>SynaptiQs can't do the query</b>
                <p>Please check Table organization
                <p>You may have to create analogsignal.Tag column
                """)         
                msgBox.exec_()
      
        
        
        #La requete
        print "-----------> Current dynamic query is;\n",self.query
        print "-----------> End of the Dynamic query"                


        self.Comboboxes_Field_Autofill()
    
        
    def Comboboxes_Field_Autofill(self):
        
        
        if QtCore.QObject().sender() != Main.Filter_NeuronName:
            Main.Filter_NeuronName.setCurrentIndex(0)
            
        #On filtre les possibilités des comboboxes en fonction de ce qui est dispo dans la DB
        try:
            if Main.Filter_Date.currentText()=='None':
                tri1 = set(self.Block_date)
                tri2 = list(tri1)
                tri2.sort()
                Main.Filter_Date.clear()
                Main.Filter_Date.insertItem(0,"None")
                for i in tri2:
                    NewItem = str(i)[0:10]
                    Main.Filter_Date.insertItem(99999,NewItem)
        except TypeError:
            Main.Filter_Date.clear()
            Main.Filter_Date.insertItem(0,"None")               
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Date Error</b>
            <p>Some Blocks have no date, so Date filter can't be used
            <p>You can complete missing infos with 'Tagging Tools'""")         
            msgBox.exec_()
        except AttributeError:
            self.Block_ids=[None]
            self.Block_Info=[None]
            self.Analogsignal_name=[None]
            self.Analogsignal_channel=[None]
            self.Block_fileOrigin=[None]
            
        if Main.Filter_BlockId.currentText()=='None':
            #TODO :
            #developper un tri par numero de fichier
            #temp=zip(self.Block_fileOrigin,self.Block_ids)
            
            
            tri1 = set(self.Block_ids)
            tri2 = list(tri1)
            tri2.sort()
            self.number_of_blocks = tri2
            Main.Filter_BlockId.clear()
            Main.Filter_BlockId.insertItem(0,"None")
            for i in tri2:
                NewItem = str(i)
                Main.Filter_BlockId.insertItem(99999,NewItem)
            
        if Main.Filter_BlockInfo.currentText()=='None':
            tri1 = set(self.Block_Info)
            tri2 = list(tri1)
            tri2.sort()
            Main.Filter_BlockInfo.clear()
            Main.Filter_BlockInfo.insertItem(0,"None")
            for i in tri2:
                NewItem = str(i)
                Main.Filter_BlockInfo.insertItem(99999,NewItem)
            
        if Main.Filter_ChannelName.currentText()=='None':
            tri1 = set(self.Analogsignal_name)
            tri2 = list(tri1)
            Main.Filter_ChannelName.clear()
            Main.Filter_ChannelName.insertItem(0,"None")
            for i in tri2:
                NewItem = str(i)
                Main.Filter_ChannelName.insertItem(99999,NewItem)
            
  
        if Main.Filter_ChannelNumber.currentText()=='None':
            tri1 = set(self.Analogsignal_channel)
            tri2 = list(tri1)
            Main.Filter_ChannelNumber.clear()
            Main.Filter_ChannelNumber.insertItem(0,"None")
            for i in tri2:
                NewItem = str(i)
                Main.Filter_ChannelNumber.insertItem(99999,NewItem)
                
      
        if Main.Filter_NeuronName.currentText()=='None' and Main.Filter_NeuronName.isEnabled()==True:
            
            tri1 = set(self.Spiketrain_Neuid)
            tri2 = list(tri1)
            tri2.sort()
            Main.Filter_NeuronName.clear()
            Main.Filter_NeuronName.insertItem(0,"None")
            for i in tri2:
                NewItem = str(i)
                Main.Filter_NeuronName.insertItem(99999,NewItem)


        
        tri=''
        compteur=0
        for i in list(set(self.Block_fileOrigin)):
            if len(list(set(self.Block_fileOrigin)))<3:
                tri+=(str(i)+' ')
                compteur+=1
            else:
                while compteur<1:
                    tri+=('Many Files')
                    compteur+=1

        Main.fileOrigin.setText(tri)
        
    def Personalize_Request(self):
        
        
        
        self.persoWidget = QtGui.QWidget()
        self.persoWidget.setMinimumSize(400,400)

        self.Edit_Request = QtGui.QTextEdit(self.persoWidget)
        self.Edit_Request.setGeometry(0, 0, 400, 380)
        self.Edit_Request.setText(str(self.query))

        Ok_edit = QtGui.QPushButton(self.persoWidget)
        Ok_edit.setGeometry(180, 380, 40, 20)
        Ok_edit.setText("OK")

        QtCore.QObject.connect(Ok_edit, QtCore.SIGNAL("clicked()"),self.Updated_Request)
        
            
        self.persoWidget.show()




    def Post_Filtering_Widget(self):
        """
        This Widget displays post-filtering fields
        """
        
        self.persoWidget2 = QtGui.QWidget()
        self.persoWidget2.setMinimumSize(400,400)

        InfoLabel= QtGui.QLabel(self.persoWidget2)
        InfoLabel.setGeometry(5, 5, 400, 85)
        InfoLabel.setText('''Main classes are : Block, Segment, Neuron, AnalogSignal, SpikeTrain
                            ex:Field to Filter: <i> Block.Info </i>   Filter :<i> ='Spike Map' </i>
                            ex:Field to Filter: <i> AnalogSignal.Calcium </i>   Filter :<i> >1.5 </i>
                            Leave the filtering field empty to select all ''')
        
        self.Filter_Fields_Labels=["a","b","c","d","e","f","g","h","i","j"]
        for j in range(len(self.Filter_Fields_Labels)):
            eval(compile("self."+self.Filter_Fields_Labels[j]+"= QtGui.QLineEdit(self.persoWidget2)",'<string>','exec'))
            eval(compile("self."+self.Filter_Fields_Labels[j]+".setGeometry(5, 100+20*j, 150, 22)",'<string>','exec'))
            eval(compile("self."+self.Filter_Fields_Labels[j]+".setText('')",'<string>','exec'))
            eval(compile("self."+self.Filter_Fields_Labels[j]+".setPlaceholderText('Field to Filter')",'<string>','exec'))
            

        Filter_Fields_List=["a1","b1","c1","d1","e1","f1","g1","h1","i1","j1"]
        for j in range(len(Filter_Fields_List)):
            eval(compile("self."+Filter_Fields_List[j]+"= QtGui.QLineEdit(self.persoWidget2)",'<string>','exec'))
            eval(compile("self."+Filter_Fields_List[j]+".setGeometry(165, 100+20*j, 80, 22)",'<string>','exec'))
            eval(compile("self."+Filter_Fields_List[j]+".setText('')",'<string>','exec'))
            eval(compile("self."+Filter_Fields_List[j]+".setPlaceholderText('Filter')",'<string>','exec'))


        Ok_edit = QtGui.QPushButton(self.persoWidget2)
        Ok_edit.setGeometry(180, 380, 40, 20)
        Ok_edit.setText("OK")

        #QtCore.QObject.connect(Ok_edit, QtCore.SIGNAL("clicked()"),self.Request_AddOn)
        QtCore.QObject.connect(Ok_edit, QtCore.SIGNAL("clicked()"),self.Extra_Filtering)
        
        self.persoWidget2.show()


    def Updated_Request(self,query=None):
        
        if query == None:
            self.query=str(self.Edit_Request.document().toPlainText())
            self.persoWidget.close()
        else:
            self.query = query
        
        self.Final_Request()

#    def Request_AddOn(self):
#        """
#        This is a postfiltering Widget.
#        each Requete.Filter_Fields_Labels is filtered
#        with the corresponding Requete.Filter_Fields_List keyword
#        """
#
#        for i in self.Filter_Fields_Labels:
#            if eval("self."+i+".text()") != '':
#                temp=eval("self."+i+".text()").replace(".","_") #Le nom du nouvel array
#                exec("Requete."+str(temp)+"=[]")
#                Class=eval("self."+i+".text()").split('.')
#                for j in eval("Requete."+str(Class[0]).capitalize()+"_ids"):
#                    print j
#                    exec("z="+str(Class[0])+".load(j)")
#                    eval("Requete."+str(temp)).append(eval("z."+str(Class[1])))
#                Requete.Post_Request_Filtering(source = eval("Requete."+str(temp)),Filter = eval("Requete."+i+"1.text()"))
#                
#       
#        print "Filtering done, ", len(eval("Requete."+str(temp))), " sweep left" 
#        Mapping.Reset_Mapping_Variables()        
#        
#        
#        self.analogsignal_zero = AnalogSignal().load(self.Analogsignal_ids[0])
#        self.Current_Signal = self.analogsignal_zero.signal #First Signal is created
#        self.timescale=numpy.array(range(len(self.Current_Signal)))/self.Initial_Points_by_ms #Timescale array is created based on first signal of the request
#        Main.slider.setRange(0, len(self.Analogsignal_ids)-1) #definit le range du slider sweepnb
#        Main.To.setText(str(len(self.Analogsignal_ids)-1)) 
#        
#        Mapping.Autofill_Coordinates_Values_from_Tag_Field()
#        Navigate.Load_This_Sweep_Number(0)

    def Extra_Filtering(self):
        """
        This is a filtering Widget.
        each Requete.Filter_Fields_Labels is filtered
        with the corresponding Requete.Filter_Fields_List keyword
        """
        self.Select_Supplement=''
        self.Where_Supplement=''
        self.Arraylist=''
        
        for i in self.Filter_Fields_Labels:
            if eval("self."+i+".text()") != '':
                array=eval("self."+i+".text()").replace(".","_") #Le nom du futur array
                Class=eval("self."+i+".text()").split('.')
                row = str(Class[0]).lower()+'.'+Class[1]
                condition=eval("self."+i+"1.text()")
                if condition == "":
                    condition = "like '%' or "+str(row)+" IS NULL"
                
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                str(row) + " will be filtered with <b>"+ str(condition) +"</b> and saved in array <b>"+ str(array)+"</b>")         
                msgBox.exec_()
                
                select= '\n \t'+row+','
                And='\n \tAND (%s %s)' % (row,condition)
                #print self.query.find(self.Select_Supplement)
                #print "ARRAY IS ",array
                #if self.query.find(self.Select_Supplement) == -1:
                if self.query.find(str(row)) == -1:
                    self.Select_Supplement+=select
                    self.Arraylist+=self.Arraylist
                    self.Where_Supplement+=And
                
                
      
        self.persoWidget2.close()
        self.Request_ComboBoxes_update() #still bugguy
        self.Personalize_Request()
        


    def Resetfields(self):
        '''
        this function is called when a SQL tab is called'
        It should reset all parameters linked to db
        '''
        
        
        
        
        Main.Filter_Date.setCurrentIndex(0)
        Main.Filter_BlockId.setCurrentIndex(0)
        Main.Filter_BlockInfo.setCurrentIndex(0)
        Main.Filter_ChannelName.setCurrentIndex(0)
        Main.Filter_ChannelNumber.setCurrentIndex(0)
        Main.Filter_NeuronName.setCurrentIndex(0)
        Main.Use_Spiketrains_Button.setCheckState(0)
        Main.Filter_NeuronName.setEnabled(False)
        try:
            del Requete.Global_Meta
            del Requete.Global_Session
        except AttributeError:
            pass

        self.query=''
        self.Select_Supplement=''
        self.Where_Supplement=''
        self.Arraylist=''
            
#        Requete.Global_Meta=open_db( url = Requete.url)
#        Requete.Global_Session=Session()
        
        Main.Filter_Date.setCurrentIndex(0)
        Main.Filter_BlockId.setCurrentIndex(0)
        Main.Filter_BlockInfo.setCurrentIndex(0)
        Main.Filter_ChannelName.setCurrentIndex(0)
        Main.Filter_ChannelNumber.setCurrentIndex(0)
        if Main.Use_Spiketrains_Button.checkState() == 2:
            Main.Filter_NeuronName.setCurrentIndex(0)
        
        self.Request_ComboBoxes_update()
 
        

        
        
        
    def Activate_Spiketrains(self):
        
        if Main.Use_Spiketrains_Button.checkState()==0:
            Main.Filter_NeuronName.setEnabled(False)
            Main.Filter_NeuronName.setCurrentIndex(0)
            self.Request_ComboBoxes_update()
            
            
        elif Main.Use_Spiketrains_Button.checkState()==2:
            Main.Filter_NeuronName.setEnabled(True)
            self.Request_ComboBoxes_update()
            Main.Filter_NeuronName.setCurrentIndex(1)

        
    def SetDBcall(self):
        
        
        if Main.SQLTabWidget.currentIndex()==0:
            Main.FilteringWidget.setEnabled(True)
            Main.FilteringWidget.show()
            
            Main.SQLTabWidget.setGeometry(0,0,330,50)
            
            Main.IOTools.setParent(Main.FilteringWidget)
            Main.IOTools.setGeometry(240, 0, 83, 123)
            Main.IOTools.show()
            
            Main.User.setText(Main.DBinf[0])
            Main.Password.setText(Main.DBinf[1])
            Main.DBname.setText(Main.DBinf[2])
            try:
                self.Resetfields()
            
                #Modifier ICI pour eviter l'autochargement de la database
            except AttributeError:
                print 'AttributeError'
                pass
            except:
              
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>SynaptiQs was unable to open MySQL db.</b>
                <p>Please check the path and Restart the Request.
                <p>You may also have to create analogsignal.Tag columns
                """)      
                msgBox.exec_()

              
        elif Main.SQLTabWidget.currentIndex()==1:
            print "/////////////// Following SQLite path exists and can be used : ",Main.param_inf[0]
            Main.FilteringWidget.setEnabled(True)
            Main.FilteringWidget.show()
            
            Main.SQLTabWidget.setGeometry(0,0,330,50)
            
            try:
                self.Resetfields()
                
            
            except:
                #identifying the error
                for i in self.Global_Meta.sorted_tables:
                    if 'analogsignal' in str(i):
                        Analogsignalcolumns=[]
                        for j in i.columns:
                            Analogsignalcolumns.append(str(j))
                            
                if 'analogsignal.Tag' in Analogsignalcolumns:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    <b>SynaptiQs was unable to open SQLite db.</b>
                    <p>Please check the path and Restart the Query.
                    """)    
                    msgBox.exec_()
                else:
                    
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    <b>First Query on this DB. Some fields are automatically added
                    <p> SynaptiQs will now exit. please restart
                    """)    
                    msgBox.exec_()
                    for i in self.Global_Meta.sorted_tables:
                        if 'analogsignal' in str(i):
                           try: 
                               sql("ALTER TABLE analogsignal ADD COLUMN tag varchar(512)")
                               #this command add a column but raise an error
                           except sqlalchemy.exc.ResourceClosedError:
                               print 'done'
                               exit()
               
        elif Main.SQLTabWidget.currentIndex()==2:
            
            print "Imported files will be used, Please use import tools"
            Main.FilteringWidget.setEnabled(False)
            Main.SQLTabWidget.setGeometry(0,0,330,500)
            Main.FilteringWidget.hide()
            Main.IOTools.setParent(Main.LocalFileWidget)
            Main.IOTools.setGeometry(10, 170, 83, 123)
            Main.IOTools.show()
            self.Resetfields()
            #Main.FilteringWidget = QtGui.QWidget(self.Whole_Request)
            #try:
                #self.Resetfields()                




            
    def Record_User_Parameters(self):
        
        #if Main.sender() == Main.DBname or Main.User or Main.Password or Main.IPAdress:
            #self.Resetfields()
        
        try:
            #On enregistre les nouveaux parametres que si la DB s'est ouverte avec succés            
            if os.path.isfile(str(Main.SQLite_path.text())) == True: #the file indicated in the "SQLite_path" filed must exist
                #If it worked,  Main.param_inf is updated first   
                
                Main.param_inf[0]=str(Main.SQLite_path.text())
            else:
                Main.param_inf[0]=''
                
            Main.param_inf[1]=Main.User.text()
            Main.param_inf[2]=Main.Password.text()
            Main.param_inf[3]=Main.DBname.text()
            Main.param_inf[4]=Main.IPAdress.text()
            Main.DBinf = [str(Main.User.text()),str(Main.Password.text()),str(Main.DBname.text()),str(Main.IPAdress.text())]
            
            #Then the whole Userpref.txt file is saved
            #print "############ Saving Parameters in Userpref.txt ################"
            
            parameters = open(Main.path,'w')
            saving = ''
            for i in Main.param_inf:
                #print "--> ",i, " saved"
                saving=saving+str(i)+"\n"
                
                        
            parameters.write(saving)       
            parameters.close()
            print "-----------> Userpref.txt saved"
            
            
            
        except AttributeError:

            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>SynaptiQs was unable find this DataBase.</b>
            <p>Please change the path or leave it empty.
            <p>Switching to default (and empty) DataBase
            """)
            msgBox.exec_()

            Main.SQLite_path.setText(Main.Script_Path+"/empty.db")

                
    def Call_Spikes(self):
        """
        This function call the spiketrain corresponding to a given analogsignal.id
        Then it creates an array containing the amplitude of the signal when a spikes occurs (for display purpose)
        """
        NbOfST=len(self.Spiketrain_ids[0])
        self.Current_Spike_Times=[]
        self.Amplitude_At_Spike_Time=[]
        for i in range(NbOfST):
            self.Current_Spike_Times.append([])
            self.Amplitude_At_Spike_Time.append([])
            
        
        Main.CurrentSpikeTrainToModify.setMaximum(NbOfST-1)
        for n in range(NbOfST):
            try:
                f = SpikeTrain().load(self.Spiketrain_ids[self.Current_Sweep_Number][n],session=self.Global_Session)
                self.Current_Spike_Times[n]=(f._spike_times-f.t_start)*1000
                self.Amplitude_At_Spike_Time[n]=numpy.ones(len(self.Current_Spike_Times[n]))
                for i in range(len(self.Current_Spike_Times[n])):
                    self.Amplitude_At_Spike_Time[n][i]=Navigate.si[n][self.Current_Spike_Times[n][i]/1000*self.Analogsignal_sampling_rate[self.Current_Sweep_Number]]    
            except (IndexError):
                self.Current_Spike_Times[n]=[]
                self.Amplitude_At_Spike_Time[n]=[]
                print "!!!!!  INFO  !!!!! No Spiketrains in this segment, in channel %s" %(n)

    
    def Save_Tags_To_Db(self):

        for i in range(len(self.Analogsignal_ids)):
            for n in range(self.NumberofChannels):
                Main.progress.setMinimum(0)
                Main.progress.setMaximum(len(self.Analogsignal_ids)-1)
                Main.progress.setValue(i)
                A=AnalogSignal().load(self.Analogsignal_ids[i][n])
                Tag_Field_Dictionnary={}
                
                if 'None' in self.tag: #When some informations like Mapping were never set
                    del self.tag['None']  
                    
                for keys in self.tag:
                    if type(self.tag[keys][i]) == list:
                        Tag_Field_Dictionnary[keys]=self.tag[keys][i][n]
                    else:
                        Tag_Field_Dictionnary[keys]=self.tag[keys][i]

                dic=str(Tag_Field_Dictionnary).replace("'", '')
                dic=dic.replace('"', '')
                A.tag = dic
                print 'AS = ', i, dic
                #print "sweep#",i,"tag (chan.", n," ; analogsignal",self.Analogsignal_ids[i][n],")saved as : ",A.tag
                #TODO # Check why duplicate load
                A.save()
                #A=AnalogSignal().load(self.Analogsignal_ids[i][n])
        print "-----------> Saving completed"



