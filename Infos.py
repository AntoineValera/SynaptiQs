# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:07:35 2013

@author: Antoine Valera
"""
import os,sys
from OpenElectrophy import *#gui,sql,open_db,AnalogSignal,Segment,Block,RecordingPoint,
import datetime
from PyQt4 import QtCore, QtGui
from matplotlib import numpy,pyplot




class Infos(object):
    """
    This class contains various tools to handle Files, Databases, textfiles etc...
    """
    def __init__(self):
        self.__name__="Infos"
        self.NumberOfFilesSentToIgor=-1
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
    def Help(self,File_Path=None): 
        """
        This function display a text file
        If File=None, file is the readme.txt 
        else, set the entire path
        
        ex: File_Path= 'C:\\Myfolder\\Myfile.txt'
        """
        
        if File_Path==None:
            try:
                helpfile = open(str(Main.userpath)+'/.SynaptiQs/README')
            except IOError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>No Help File here</b>
                <p>You can still go on http://synaptiqs.wix.com/synaptiqs
                """)
                msgBox.exec_()
                return
            a=helpfile.readlines()
            temp=''
            for i in range(len(a)):
                temp=temp+a[i]+'<br>'
        else:
            helpfile = open(str(File_Path))
            a=helpfile.readlines()
            temp=''
            for i in range(len(a)):
                temp=temp+a[i]+'<br>'            
                
        #Display Part        
        self.HelpWidget = QtGui.QWidget()
        self.HelpWidget.setGeometry(0,0,800,600)
            
        info = QtGui.QTextEdit(temp,self.HelpWidget) 
        info.setGeometry(10,10,790,590)
        
        self.HelpWidget.show()

    def Zip(self,params):
        if type(params) not in [list,tuple,numpy.ndarray]:
            print "Input error, please put a list of list here"
            return []
        temp=[list(a) for a in zip(*params)]
        return temp

    def Error(self,message):
        '''
        display an error message as a popup
        '''
        msgBox = QtGui.QMessageBox()
        msgBox.setText(message)  
        msgBox.exec_()        
        

        
    def LineEdited(self):
        obj=QtCore.QObject().sender().objectName()
        obj=obj.split('.')
        val = str(QtCore.QObject().sender().text())
        setattr(eval(obj[0]),obj[1],val)
        
    def Retag(self):
        
        try:
            self.List_Tables()
        except sqlalchemy.exc.OperationalError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>No Database</b>
            <p>Please Select an existing database first
            """)
            msgBox.exec_()
            return

            
        self.Tag_tools_Widget = QtGui.QWidget()#self.popupDialog)
        self.Tag_tools_Widget.setMinimumSize(600,600) #definit la taille minimale du Widget (largeur, hauteur)          

    
        self.ValueWidget = QtGui.QWidget(self.Tag_tools_Widget)
        self.ValueWidget.setGeometry(10,10,600,600)
        
        
        self.date_Label = QtGui.QLabel(self.ValueWidget)
        self.date_Label.setGeometry(10, 155, 100, 14)
        self.date_Label.setText( "Date YYYY-MM-DD") 
        self.date = QtGui.QLineEdit(self.ValueWidget) #Lines, columns, Parent
        self.date.setGeometry(110,150,150,20)
        self.date.setInputMask("0000-00-00")

        self.Condition_Label = QtGui.QLabel(self.ValueWidget)
        self.Condition_Label.setGeometry(10, 100, 150, 30)
        self.Condition_Label.setText( "Condition") 

               
        self.Table_List = QtGui.QComboBox(self.ValueWidget)
        self.Table_List.setGeometry(50, 100, 100, 30)
        self.Table_List.addItems(self.List_of_tables)

        self.Column_List = QtGui.QComboBox(self.ValueWidget)
        self.Column_List.setGeometry(150, 100, 100, 30)
        
        self.Condition = QtGui.QLineEdit(self.ValueWidget) #Lines, columns, Parent
        self.Condition.setGeometry(250, 100, 160, 30)   
        self.Condition.setPlaceholderText("Information")

        self.BlockFrom_Label = QtGui.QLabel(self.ValueWidget)
        self.BlockFrom_Label.setGeometry(115, 15, 55, 14)
        self.BlockFrom_Label.setText( "First Block")          
        self.BlockFrom = QtGui.QLineEdit(self.ValueWidget) #Lines, columns, Parent
        self.BlockFrom.setGeometry(210,10,50,20)

        self.BlockTo_Label = QtGui.QLabel(self.ValueWidget)
        self.BlockTo_Label.setGeometry(265, 15, 55, 14)
        self.BlockTo_Label.setText( "Last Block")            
        self.BlockTo = QtGui.QLineEdit(self.ValueWidget) #Lines, columns, Parent
        self.BlockTo.setGeometry(360,10,50,20) 
        
        self.AnalogFrom_Label = QtGui.QLabel(self.ValueWidget)
        self.AnalogFrom_Label.setGeometry(115, 35, 100, 14)
        self.AnalogFrom_Label.setText( "First Segment.id")          
        self.AnalogFrom = QtGui.QLineEdit(self.ValueWidget) #Lines, columns, Parent
        self.AnalogFrom.setGeometry(210,30,50,20)
        self.AnalogFrom.setEnabled(False)

        self.AnalogTo_Label = QtGui.QLabel(self.ValueWidget)
        self.AnalogTo_Label.setGeometry(265, 35, 100, 14)
        self.AnalogTo_Label.setText( "Last Segment.id")            
        self.AnalogTo = QtGui.QLineEdit(self.ValueWidget) #Lines, columns, Parent
        self.AnalogTo.setGeometry(360,30,50,20)
        self.AnalogTo.setEnabled(False)
        
        self.AnalogList = QtGui.QLabel(self.ValueWidget)
        self.AnalogList.setGeometry(420, 35, 200, 14)
        self.AnalogList.setText( "Only if one Block is selected")          


        self.OK_Block_Range = QtGui.QPushButton(self.ValueWidget) #creation du bouton
        self.OK_Block_Range.setGeometry(420,10,120,20) #taille et position (X,Y,Xsize,Ysize)
        self.OK_Block_Range.setText( "Validate Blocks")
        

        self.OK_Date = QtGui.QPushButton(self.ValueWidget) #creation du bouton
        self.OK_Date.setGeometry(420,150,80,20) #taille et position (X,Y,Xsize,Ysize)
        self.OK_Date.setText( "Apply Date")

        self.OK_Condition = QtGui.QPushButton(self.ValueWidget) #creation du bouton
        self.OK_Condition.setGeometry(420, 100, 120, 30)  #taille et position (X,Y,Xsize,Ysize)
        self.OK_Condition.setText( "Apply Condition")        
             
        self.DetectErrors = QtGui.QPushButton(self.ValueWidget) #creation du bouton
        self.DetectErrors.setGeometry(10,450,200,50) #taille et position (X,Y,Xsize,Ysize)
        self.DetectErrors.setText( "Recording regularity detector")

        self.remove_range_of_ids = QtGui.QPushButton(self.ValueWidget) #creation du bouton
        self.remove_range_of_ids.setGeometry(10,400,200,50) #taille et position (X,Y,Xsize,Ysize)
        self.remove_range_of_ids.setText( "Delete a Range of Ids")  
        self.remove_range_of_ids.setToolTip("""You can remove a range of segment.id\n value can be given like [x0,x1,x2,xn] or [x0:xn]\n""")
        
        
        self.ids_or_sn = QtGui.QComboBox(self.ValueWidget)
        self.ids_or_sn.setGeometry(10, 30, 100, 22)
        self.ids_or_sn.addItems(["Ids","Sweep #"])
        self.ids_or_sn.setEnabled(False)

        self.Use_Segment_ids = QtGui.QCheckBox(self.ValueWidget)
        self.Use_Segment_ids.setGeometry(420, 55, 200, 14)
        self.Use_Segment_ids.setText("Use segment.id range")
        self.Use_Segment_ids.setEnabled(False)
        
        
        self.BlockFrom.setText(str(Requete.Block_ids[0]))
        self.BlockTo.setText(str(Requete.Block_ids[0]))

        
        
        QtCore.QObject.connect(self.OK_Block_Range, QtCore.SIGNAL("clicked()"),self.FillDB)
        QtCore.QObject.connect(self.OK_Date, QtCore.SIGNAL("clicked()"),self.ChangeDate)
#        QtCore.QObject.connect(self.OK3, QtCore.SIGNAL("clicked()"),self.ImportPicture)
#        QtCore.QObject.connect(self.OK4, QtCore.SIGNAL("clicked()"),self.ChangeInfo)
#        QtCore.QObject.connect(self.OK5, QtCore.SIGNAL("clicked()"),self.ChangePosition)
        QtCore.QObject.connect(self.OK_Condition, QtCore.SIGNAL("clicked()"),self.ChangeCondition_Internal_Input)
        QtCore.QObject.connect(self.BlockFrom, QtCore.SIGNAL('editingFinished ()'),self.Copy)
        QtCore.QObject.connect(self.BlockTo, QtCore.SIGNAL('editingFinished ()'),self.Copy)

        QtCore.QObject.connect(self.AnalogFrom, QtCore.SIGNAL('editingFinished ()'),self.Copy2)
        QtCore.QObject.connect(self.AnalogTo, QtCore.SIGNAL('editingFinished ()'),self.Copy2)
        
        QtCore.QObject.connect(self.DetectErrors, QtCore.SIGNAL("clicked()"),self.AutoCheckErrors)
        QtCore.QObject.connect(self.remove_range_of_ids, QtCore.SIGNAL("clicked()"),self.RangeDelete)
        QtCore.QObject.connect(self.ids_or_sn, QtCore.SIGNAL("activated(int)"),self.Switch_from_Segment_ids_to_Sweep_Number)
        
     
        
        
        QtCore.QObject.connect(self.Table_List, QtCore.SIGNAL('activated(int)'),self.List_Columns)

        self.Tag_tools_Widget.show()           


    def List_Tables(self):
        #if Main.SQLTabWidget.currentIndex() == 0 :
            #print "/////////////// You are using a MySQL DataBase"
            #self.url = 'mysql://'+str(Main.User.text())+':'+str(Main.Password.text())+'@'+str(Main.IPAdress.text())+'/'+str(Main.DBname.text())

        #elif Main.SQLTabWidget.currentIndex() == 1 :
            #print "/////////////// You are using a SQLite DataBase"
            #self.url = "sqlite:///"+str(Main.SQLite_path.text()) 
        
        #open_db( url = self.url)


        if Main.SQLTabWidget.currentIndex() == 0 :
            user="'"+str(Main.DBname.text())+"'"
            query ="""
            SELECT Table_name,table_Schema
            FROM INFORMATION_SCHEMA.TABLES
            WHERE Table_schema =%s
            """ %(user)  

    
        elif Main.SQLTabWidget.currentIndex() == 1 :
            query ="""
            SELECT name,type
            FROM sqlite_master
            WHERE type = 'table'
            """      

        name,Type=sql(query)
        
        self.List_of_tables=[]
        name.sort()
        for i in name:
            #if i not in ['PRIMARY','FOREIGN','id','datetime','signal_shape','signal_dtype','signal_blob']:
            self.List_of_tables.append(i)
            
           
    def List_Columns(self):
        
        self.Column_List.clear()


        if Main.SQLTabWidget.currentIndex() == 0 :
            print "/////////////// You are using a MySQL DataBase"
            self.url = 'mysql://'+str(Main.User.text())+':'+str(Main.Password.text())+'@'+str(Main.IPAdress.text())+'/'+str(Main.DBname.text())

        elif Main.SQLTabWidget.currentIndex() == 1 :
            print "/////////////// You are using a SQLite DataBase"
            self.url = "sqlite:///"+str(Main.SQLite_path.text()) 
        
        if Main.SQLTabWidget.currentIndex() == 0 :
            user="'"+str(Main.DBname.text())+"'"
            query ="""
            select column_name,Table_schema
            from information_schema.columns
            WHERE Table_schema = %s
            AND table_name='%s'
            """ %(user,self.Table_List.currentText())  
            name,Type=sql(query)
            
        elif Main.SQLTabWidget.currentIndex() == 1 :
            user="'"+str(Main.DBname.text())+"'"
            
            query ="""
            SELECT sql,type FROM SQLITE_MASTER
            WHERE name = '%s'
            """ %(self.Table_List.currentText())
             
            temp,Type=sql(query)
            name=''
            for i in temp[0]:
                name+=str(i)
            name=name.replace('CREATE TABLE %s (' %(self.Table_List.currentText()),'')
            name=name.replace('\n','')
            name=name.replace('\t','')
            name=name.replace('"','')
            name=name[0:-2]
            newname=name.split(',')
            name=[]
            for i in newname:
                i=i.lstrip()
                i=i.split(' ')
                i=i[0]
                

                name.append(i)

        
        self.List_of_Columns=[]
        name.sort()
        for i in name:
            if i not in ['PRIMARY','FOREIGN','datetime']:#Blacklist
                if i.find("id") == -1 and i.find("_shape") == -1 and i.find("_dtype") == -1 and i.find("_blob") == -1:
                    self.List_of_Columns.append(i)   
        
        self.Column_List.addItems(self.List_of_Columns)
        

    def Copy(self):
        Max=int(Main.Filter_BlockId.count()-1)
        self.BlockFrom.setText(str(int(self.BlockFrom.text())))
        #self.BlockTo.setText(self.BlockFrom.text())
        
        if int(self.BlockFrom.text()) < int(Main.Filter_BlockId.itemText(1)):
            self.BlockFrom.setText(str(int(Main.Filter_BlockId.itemText(1))))
        if int(self.BlockFrom.text()) > int(Main.Filter_BlockId.itemText(Max)):
            self.BlockFrom.setText(str(int(Main.Filter_BlockId.itemText(Max))))
        if int(self.BlockTo.text()) < int(self.BlockFrom.text()):
            self.BlockTo.setText(str(int(self.BlockFrom.text())))
        if int(self.BlockTo.text()) > int(Main.Filter_BlockId.itemText(Max)):
            self.BlockTo.setText(str(int(Main.Filter_BlockId.itemText(Max))))


        
        
    
    def Copy2(self):
        self.AnalogFrom.setText(str(int(self.AnalogFrom.text())))
        #self.AnalogTo.setText(self.AnalogFrom.text())
        if self.ids_or_sn.currentText() == "Ids":
            if int(self.AnalogFrom.text()) < self.segment[0]:
                self.AnalogFrom.setText(str(self.segment[0]))
            if int(self.AnalogFrom.text()) > self.segment[-1]:
                self.AnalogFrom.setText(str(self.segment[-1])) 
            if int(self.AnalogTo.text()) < int(self.AnalogFrom.text()):
                self.AnalogTo.setText(str(int(self.AnalogFrom.text())))            
            if int(self.AnalogTo.text()) > self.segment[-1]:
                self.AnalogTo.setText(str(self.segment[-1]))
        elif self.ids_or_sn.currentText() == "Sweep #":
            if int(self.AnalogFrom.text()) < 0:
                self.AnalogFrom.setText('0')
            if int(self.AnalogFrom.text()) > len(self.segment)-1:
                self.AnalogFrom.setText(str(len(self.segment)-1)) 
            if int(self.AnalogTo.text()) < int(self.AnalogFrom.text()):
                self.AnalogTo.setText(str(int(self.AnalogFrom.text())))            
            if int(self.AnalogTo.text()) > len(self.segment)-1:
                self.AnalogTo.setText(str(len(self.segment)-1))                
                
            
        

    def Switch_from_Segment_ids_to_Sweep_Number(self):
        
        if self.ids_or_sn.currentText() == "Sweep #":
            self.AnalogFrom_Label.setText( "First Sweep #")
            self.AnalogTo_Label.setText( "Last Sweep #")
            self.AnalogFrom.setText('0')
            self.AnalogTo.setText(str(len(self.segment)-1))    
        elif self.ids_or_sn.currentText() == "Ids":
            self.AnalogFrom_Label.setText( "First segment.id")
            self.AnalogTo_Label.setText( "Last segment.id")
            self.AnalogFrom.setText(str(self.segment[0]))
            self.AnalogTo.setText(str(self.segment[-1]))             
            

    def FillDB(self,From=None,To=None,Mode='block'):
        """
        This function is calling all the block.id,segment.id and analogsignal.id
        between 'From' and 'To'.
        
        If From == None AND To == None , From and To are read from the SynaptiQs Widget 
        
        If Mode == 'segment', From and To are segment.ids instead of block.ids
        
        """
        
        try:
            self.ids_or_sn.setCurrentIndex(0)
            #self.Switch_from_Segment_ids_to_Sweep_Number()
        except AttributeError: #First execution
            pass
        
        
        if From==None and To==None and Mode == 'block':
            From=str(self.BlockFrom.text())
            To=str(self.BlockTo.text())
        elif From==None and To==None and Mode == 'segment':
            From=str(self.AnalogFrom.text())
            To=str(self.AnalogTo.text())
        else:
            print 'Maybe not supported yet'
            return
        print 'requete is done between %s.id %s and %s' % (Mode,From,To)
        
        try:
            url = Requete.url
        except AttributeError: #if url doesn't exist, an automatic request is done with first block id
            Main.Filter_BlockId.setCurrentIndex(1)
            Requete.Request_ComboBoxes_update()        
            Requete.Final_Request()
            
        open_db( url = Requete.url)
       
        query ="""
        SELECT block.id, segment.id, analogsignal.id
        FROM block, analogsignal, segment
        WHERE %s.id BETWEEN :origin AND :end
        AND block.id=segment.id_block
        AND segment.id=analogsignal.id_segment
        ORDER BY analogsignal.id
        """ % (Mode)
        
        self.block,self.segment,self.analogsignal = sql(query,origin = From,end=To)
        self.nb_of_blocks = list(set(self.block)) 
        
    
        if len(self.nb_of_blocks)==1:
            self.AnalogFrom.setEnabled(True)
            self.AnalogTo.setEnabled(True)
            self.ids_or_sn.setEnabled(False)
            self.Use_Segment_ids.setEnabled(True)
            self.AnalogList.setText("Ids from # "+str(self.segment[0])+" to # "+str(self.segment[-1])+" ; "+str(len(self.segment))+" Sweeps")          

            self.AnalogFrom.setText(str(self.segment[0]))
            self.AnalogTo.setText(str(self.segment[-1]))
        else:
            self.AnalogFrom.setEnabled(False)
            self.AnalogTo.setEnabled(False)
            self.ids_or_sn.setEnabled(False)
            self.Use_Segment_ids.setEnabled(False)

            self.AnalogFrom.setText('')
            self.AnalogTo.setText('')            

 
        
    def ChangeDate(self,From=None,To=None,New_Date=None):
        """
        This function set the date New_Date (format must be 'YYYY-MM-DD')
        if New_Date == None , New_Date = self.date.text() (in the Widget)
        in the block range [From:To]
        """
        
        if New_Date==None:
            text = self.date.text()
        Year = int(text[0:4])
        Month = int(text[5:7])
        Day = int(text[8:10])
        
        self.FillDB(From,To)
        
        try:
            for i in list(set(self.block)):
                bl = Block.load(int(i),session=Requete.Global_Session)
                dt = datetime.date(Year,Month,Day)
                bl.datetime = dt
                bl.save()
                
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Date Changed.</b>
            <p>Date of Blocks """+str(list(set(self.block)))+""" has changed to
            """+str(text))
            msgBox.exec_()
                
        except ValueError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Date Error</b>
            <p>Format is YYYY MM DD
            """)     
            msgBox.exec_()

    def ChangeCondition_Internal_Input(self):
        
        if self.Use_Segment_ids.checkState() == 2:
            mode = 'segment'
            if self.ids_or_sn.currentText() == "Sweep #": 
                self.AnalogFrom.setText(str(self.segment[int(self.AnalogFrom.text())]))
                self.AnalogTo.setText(str(self.segment[int(self.AnalogTo.text())]))
                self.ids_or_sn.setCurrentText('Ids')
                
            self.ChangeCondition(table=self.Table_List.currentText(),column=self.Column_List.currentText(),value=str(self.Condition.text()),Mode=mode)

        elif self.Use_Segment_ids.checkState() == 0:
            mode = 'block' 
            self.ChangeCondition(table=self.Table_List.currentText(),column=self.Column_List.currentText(),value=str(self.Condition.text()),Mode=mode)

    def ChangeCondition(self,table=None,column=None,value=None,From=None,To=None,Mode='block'):
        """
        This function allow to set 'value' in any field in table.column between From and To block.id
        
        """
        
        table=str(table.replace("'",""))
        table=str(table.replace('"',''))
        column=str(column.replace("'",""))
        column=str(column.replace('"',''))
        value=str(value.replace("'",""))
        value=str(value.replace('"',''))    
        
        print "using url : ", Requete.url
        print value,' is set to ',table+'.'+column,' field'
        self.FillDB(From,To,Mode)
        
        
        try:
            print eval('self.'+table)
        except AttributeError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Table Error</b>
            <p>The Table """+table+""" is not implemented yet""")  
            msgBox.exec_() 
            return
        
        for i in list(set(eval('self.'+table))):
            Loading_Command='obj = '+table.capitalize()+'().load(i)'
            
            #Exception List, case correction.
            if table.capitalize() == 'Analogsignal':
                Loading_Command='obj = AnalogSignal().load(i,session=Requete.Global_Session)'
            elif table.capitalize() == 'Spiketrain':
                Loading_Command='obj = SpikeTrain().load(i,session=Requete.Global_Session)'
            elif table.capitalize() == 'Recordingpoint':
                Loading_Command='obj = RecordingPoint().load(i,session=Requete.Global_Session)' 
                
        
            exec(Loading_Command)
            command=str('obj.'+column+'='+"'"+value+"'")
            print command
            exec(command)
            exec('obj.save(session=Requete.Global_Session)')
            
        msgBox = QtGui.QMessageBox()
        msgBox.setText(
        """
        <b>Info Changed.</b>
        <p>Experimental Info of %s""" % (table.capitalize())+str(list(set(eval('self.'+table))))+""" has changed to
        """+value) 
        msgBox.exec_()

        print 'done'
        
         
    def AutoCheckErrors(self):
        

        self.FillDB()

        self.t_start_list=[0]*len(Requete.Analogsignal_ids)
        self.corrected_t_start_list=[0]*len(Requete.Analogsignal_ids)
        ISIlist=[]
        
        for i in range(len(Requete.Analogsignal_ids)):
            anasig=AnalogSignal().load(Requete.Analogsignal_ids[i],session=Requete.Global_Session)
            self.t_start_list[i]=anasig.t_start
            self.corrected_t_start_list[i]=anasig.t_start
            
            if i > 0:
                self.corrected_t_start_list[i]=self.t_start_list[i]-self.t_start_list[i-1]
                ISIlist.append(self.t_start_list[i]-self.t_start_list[i-1])
                
        ctrlISI=numpy.median(ISIlist)
        
        value,ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'positive or negative?', 
            """Median inter sweep interval is """+str(ctrlISI)+""" seconds \nChoose if you want to exclude positive ("+"), negative("-") or both("+-") values \n above/under 5% of the mean inter sweep interval \nor a positive or negative relative value ('+6') or (-4.2)\n""")
        value=str(value)    
        
        self.rejected_list=[0]*len(Requete.Analogsignal_ids)
        self.rejected_list_of_ids=[]
        self.rejected_list_of_ids2=[]
        self.rejected_list_of_ids3=[]
        
        for i in range(len(Requete.Analogsignal_ids)):
            if self.corrected_t_start_list[i] > ctrlISI+(ctrlISI/20) and value==("+" or "+-"):
                print "positive included"
                self.rejected_list[i]=self.corrected_t_start_list[i]
                self.rejected_list_of_ids.append(i)
                self.rejected_list_of_ids2.append(Requete.Analogsignal_ids[i])
                self.rejected_list_of_ids3.append(Requete.Segment_ids[i])
              
                
            elif self.corrected_t_start_list[i] < ctrlISI-(ctrlISI/20) and value==("-" or "+-"):
                print "negative included"
                
                self.rejected_list[i]=self.corrected_t_start_list[i]
                self.rejected_list_of_ids.append(i)
                self.rejected_list_of_ids2.append(Requete.Analogsignal_ids[i])
                self.rejected_list_of_ids3.append(Requete.Segment_ids[i])
                
            else:
                self.rejected_list[i]=None

            if value !="+" and value !="-" and value !="+-" and value !="":
                
                if float(value)<0:
                    if self.corrected_t_start_list[i] < ctrlISI+float(value):
                        self.rejected_list[i]=self.corrected_t_start_list[i]
                        self.rejected_list_of_ids.append(i)
                        self.rejected_list_of_ids2.append(Requete.Analogsignal_ids[i])
                        self.rejected_list_of_ids3.append(Requete.Segment_ids[i])    
                    else:
                        self.rejected_list[i]=None    
                        
                elif float(value)>0:
                    if self.corrected_t_start_list[i] > ctrlISI+float(value):
                        self.rejected_list[i]=self.corrected_t_start_list[i]
                        self.rejected_list_of_ids.append(i)
                        self.rejected_list_of_ids2.append(Requete.Analogsignal_ids[i])
                        self.rejected_list_of_ids3.append(Requete.Segment_ids[i]) 
                    else:
                        self.rejected_list[i]=None                

                
        if value[0] =="-" or value == "+-" :
            print "negative threshold, first value removed"
            try:
                self.rejected_list_of_ids.pop(0)
                self.rejected_list_of_ids2.pop(0)
                self.rejected_list_of_ids3.pop(0)
            except IndexError: #if nothing to remove
                pass
        
        self.Experiment_Time_Course = MyMplWidget(title='Time Course')
        self.Experiment_Time_Course.canvas.axes.plot(self.rejected_list,'ro',ms=10)
        self.Experiment_Time_Course.canvas.axes.plot(self.corrected_t_start_list,'bo',ms=5)
        self.Experiment_Time_Course.show() 
        
        self.rejected_list_of_ids2=str(self.rejected_list_of_ids2) 
        self.rejected_list_of_ids2 = self.rejected_list_of_ids2.replace("L", '')
        self.rejected_list_of_ids2 = self.rejected_list_of_ids2.replace("'", '')
        
        self.rejected_list_of_ids3=str(self.rejected_list_of_ids3) 
        self.rejected_list_of_ids3 = self.rejected_list_of_ids3.replace("L", '')
        self.rejected_list_of_ids3 = self.rejected_list_of_ids3.replace("'", '')        
        
        
        
        msgBox = QtGui.QMessageBox()
        msgBox.setText(
        """
        <b>The following sweeps do not match your criteria</b>
        <p>You may have to remove them.
        
        <p>"""+str(self.rejected_list_of_ids)+"""
        <p> or AnalogSignal.id
        <p>"""+str(self.rejected_list_of_ids2)+"""
        <p> or Segment.id
        <p>"""+str(self.rejected_list_of_ids3))
        msgBox.exec_()  
        
        print self.rejected_list_of_ids3


#    def RemoveSelection(self):
#        
#        print self.rejected_list_of_ids
#        for i in range(len(Requete.Analogsignal_ids)):
#            if self.rejected_list[i] != None:
#                Requete.tag["Selection"][i]=2
                
    def Delete_Current_Segment(self):
        
        
        if Main.SQLTabWidget.currentIndex() == 2:
            self.Delete_Local_Current_Segment()
        else:
            warning = QtGui.QMessageBox.warning(Main.NavigationWidget,'WARNING',"You are currently using "+str(Requete.url)+" database, be sure it's the good one!",
                    QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                    QtGui.QMessageBox.NoButton)  
            if warning == QtGui.QMessageBox.Cancel : return        
            
    
    
            warning = QtGui.QMessageBox.warning(Main.NavigationWidget,'WARNING',"You are about to delete Segment.id"+str(Requete.Segment_ids[Requete.Current_Sweep_Number])+" and all it's children (shame on you!)",
                    QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                    QtGui.QMessageBox.NoButton)  
            if warning == QtGui.QMessageBox.Cancel : return    
            else : value=int(Requete.Segment_ids[Requete.Current_Sweep_Number])
    
            ok = QtGui.QMessageBox.warning(Main.NavigationWidget,'delete',"Are you sure you want to delete the Segment.id #"+str(value),#(None,self.tr('delete'),self.tr("Sure?"), 
                    QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                    QtGui.QMessageBox.NoButton)
                    
                    
            if ok == QtGui.QMessageBox.Cancel : print "exit"
            elif ok == QtGui.QMessageBox.Ok :
                
                open_db( url = Requete.url)
                
                session=Session()
                segid,=sql(("""SELECT segment.id FROM segment WHERE segment.id="""+str(value)))
    
                OEclass = Requete.Global_Meta.dictMappedClasses['segment']
                q = session.query(OEclass).filter(OEclass.id==segid[0])
                OEinstance = q.one()
                session.delete(OEinstance)
    
                session.commit()
                
                Requete.Final_Request()
            
    def Delete_Local_Current_Segment(self):

        warning = QtGui.QMessageBox.warning(Main.NavigationWidget,'WARNING',"You are about to delete Sweep"+str(Requete.Current_Sweep_Number),
                QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                QtGui.QMessageBox.NoButton)  
        if warning == QtGui.QMessageBox.Cancel : return 
        
        else : value=int(Requete.Current_Sweep_Number)

        ok = QtGui.QMessageBox.warning(Main.NavigationWidget,'delete',"Are you sure you want to delete the Segment.id #"+str(value),#(None,self.tr('delete'),self.tr("Sure?"), 
                QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                QtGui.QMessageBox.NoButton)
    
        if ok == QtGui.QMessageBox.Cancel : print "exit"
        elif ok == QtGui.QMessageBox.Ok :
            
            Navigate.ArrayList.pop(int(Requete.Current_Sweep_Number))
            Requete.Analogsignal_ids.pop(int(Requete.Current_Sweep_Number))
            if Requete.Current_Sweep_Number>0:
                Requete.Current_Sweep_Number-=1
            Main.slider.setRange(0, len(Requete.Analogsignal_ids))
            Navigate.Check_From_To()
            Navigate.Update_SweepNumber_Slider()
            #TODO: Other arrays should probably be updated

        
    def RangeDelete(self):
        
        try:
            warning = QtGui.QMessageBox.warning(Main.NavigationWidget,'WARNING',"You are currently using "+str(Requete.url)+" database, be sure it's the good one!",
                    QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                    QtGui.QMessageBox.NoButton)  
            if warning == QtGui.QMessageBox.Cancel : return     
            
        except:
            print "Please first do a request to have a Database"

        
        text, ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'Input Dialog', 
            'Please Enter the Segment.ids you want to remove:',
            text='[]')
        if not ok:
            return
            
        ok = QtGui.QMessageBox.warning(Main.NavigationWidget,'delete',"Are you sure ?",
                QtGui.QMessageBox.Ok ,QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                QtGui.QMessageBox.NoButton)
           
        test=':' in text
        text=text.replace('[','')
        text=text.replace(']','')
        b=[]
        if test==False:
            try: text=text.split(',')
            except:print 'oups'
            for i in text:
                print i
                b.append(int(i))
        
        else:
            text=text.split(':')
            for i in range(int(text[0]),int(text[-1])+1):
                b.append(int(i))    
                
        if ok == QtGui.QMessageBox.Cancel : print "exit"
        elif ok == QtGui.QMessageBox.Ok :

            open_db( url = Requete.url)
            
            for i in b:
                #print i
                
                session=Session()
                segid,=sql(("""SELECT segment.id FROM segment WHERE segment.id="""+str(i)))
                OEclass = Requete.Global_Meta.dictMappedClasses['segment']
                q = session.query(OEclass).filter(OEclass.id==i)
                try:
                    OEinstance = q.one()
                    session.delete(OEinstance)
                except:
                    pass
                session.commit()
            
            Requete.Final_Request()
            
    def Open_a_Folder(self):
        
        folder=QtCore.QObject().sender().text()
        
        if folder == "Plugins Folder":
            url=str(os.getenv("HOME"))+"\.SynaptiQs"
        if folder == "UserPref":
            url=str(os.getenv("HOME"))+"\.SynaptiQs\Core"            
        QtGui.QDesktopServices().openUrl(QtCore.QUrl("file:///"+url,0))


    def List_All_Globals(self,option='All'):
        
        import __builtin__
        
        Plugins.Reload()
        
        L=[]
        
        for i in Plugins.Plugin_List:
            L.append("__builtin__."+i)
        
        for i in self.Class_List: #Coming from Main SynaptiQs
            L.append(i.__name__)
        
        LList=[]
        LArray=[]
        LVar=[]
        LStr=[]
        
        for i in L:
            for j in dir(eval(i)):
                try:
                    if type(eval(i+'.'+j)) == list:
                        if option=='All':
                            LList.append(i+'.'+j)
                        elif option=='numericalonly':
                            for k in eval(i+'.'+j):
                                if type(k) == float() or  type(k) in LList == int():
                                    pass
                                else:
                                    break
                                LList.append(i+'.'+j)
                                 
                    elif type(eval(i+'.'+j)) == numpy.ndarray:
                        LArray.append(i+'.'+j)
                    elif type(eval(i+'.'+j)) == int or float:
                        LVar.append(i+'.'+j)
                    elif type(eval(i+'.'+j)) == str:
                        LStr.append(i+'.'+j)   
                    else:
                        print type(eval(i+'.'+j))
                except:
                    pass
                
        self.Add_Array(LList)
        self.Add_Array(LArray)
        return LList,LArray,LVar,LStr
 

                
    def Data_Browser(self,VAR=0,STR=0):
        #TODO : Explain VAR=0, STR=0
        #       Add a silent mode where lists are updated but not shown
        #       Add a fork function returning a list matching specific criterions

        self.DataBrowser=QtGui.QWidget()
         
        hbox=QtGui.QHBoxLayout()

        vbox=QtGui.QVBoxLayout()
        
        self.Refresh=QtGui.QPushButton()
        self.Refresh.setIcon(QtGui.QIcon(Main.Script_Path+"/refresh.png"))
        self.Refresh.setIconSize(QtCore.QSize(70, 70))        

        self.PlotMultiple=QtGui.QPushButton()
        self.PlotMultiple.setText('Plot')
        
        self.Display_Var=QtGui.QCheckBox()
        self.Display_Var.setCheckState(VAR)
        self.Display_Var.setText('Show Variables')
        self.Display_Str=QtGui.QCheckBox()
        self.Display_Str.setCheckState(STR)  
        self.Display_Str.setText('Show Strings')
        
        vbox.addWidget(self.Refresh)
        vbox.addWidget(self.Display_Var)
        vbox.addWidget(self.Display_Str)
        vbox.addWidget(self.PlotMultiple)
        
        self.YList=QtGui.QListWidget(self.DataBrowser)
        
        L1,L2,L3,L4=self.List_All_Globals()
        
        
        for i in L1:
            a=QtGui.QListWidgetItem(i)
            a.setTextColor(QtGui.QColor('black'))
            self.YList.addItem(a)
        for i in L2:
            a=QtGui.QListWidgetItem(i)
            a.setTextColor(QtGui.QColor('darkblue'))
            self.YList.addItem(a)
        if self.Display_Var.checkState()==2:
            for i in L3:
                if '__' not in i:
                    a=QtGui.QListWidgetItem(i)
                    a.setTextColor(QtGui.QColor('red'))
                    self.YList.addItem(a)
        if self.Display_Str.checkState()==2:
            for i in L4:
                if '__' not in i:
                    a=QtGui.QListWidgetItem(i)
                    a.setTextColor(QtGui.QColor('green'))
                    self.YList.addItem(a)            
        
        self.YList.setSelectionMode(3) #1 = one item at the time
        self.YList.setWindowTitle('Data Browser')
        self.YList.itemActivated.connect(self.Selected_To_Display)
        self.YList.setAcceptDrops(True) 
        
        self.XList=QtGui.QListWidget(self.DataBrowser)
        L5=L1+L2+L3+L4
        for i in L5:
            self.XList.addItem(QtGui.QListWidgetItem(i))   
        
        self.XList.setSelectionMode(1)
        #self.XList.setWindowTitle('Data Browser')
        self.XList.itemActivated.connect(self.Selected_To_Display)       
        
        self.XList.setEnabled(False)
        hbox.addLayout(vbox)
        hbox.addWidget(self.YList)
        hbox.addWidget(self.XList)        

        self.DataBrowser.setLayout(hbox)
        QtCore.QObject.connect(self.YList, QtCore.SIGNAL("itemSelectionChanged()"),self.Filter_X_Axis)
#        QtCore.QObject.connect(self.XList, QtCore.SIGNAL("clicked())"),self.Selected_To_Display)
#        QtCore.QObject.connect(self.YList, QtCore.SIGNAL("clicked())"),self.Selected_To_Display)
        QtCore.QObject.connect(self.Refresh, QtCore.SIGNAL("clicked()"),self.Actualize)
        QtCore.QObject.connect(self.PlotMultiple, QtCore.SIGNAL("clicked()"),self.Selected_To_Display)


        self.DataBrowser.show()
        
    def Actualize(self):
        try:
            self.Data_Browser(VAR=self.Display_Var.checkState(),STR=self.Display_Str.checkState())
        except AttributeError:
            self.Data_Browser()
            
 
    def Filter_X_Axis(self):
        #self.XList.clearSelection()
        self.XList.clear()
        Array_to_Display=[]
        Array_length=[]
        selected=self.YList.selectedItems()
        
        #var=list(eval(str(var)))
        for i in selected:
            try:
                Array_length.append(len(eval(str(i.text()))))
            except TypeError: # For non-lists
                pass
            Array_to_Display.append((str(i.text())))
            
        if len(set(Array_length)) !=1:
            self.XList.setEnabled(False)
            return
        else:
            self.XList.setEnabled(True)
            
        
        counter=0
        for i in Main.ExistingSweeps:
            if type(eval(i)) in [list,numpy.array,numpy.ndarray]:
                if len(eval(i)) == len(eval(Array_to_Display[0])):
                    self.XList.addItem(QtGui.QListWidgetItem(i))
                    counter+=1
           
        
    def Selected_To_Display(self):
        
        
        self.Widget=QtGui.QWidget()
        hbox=QtGui.QHBoxLayout()

        self.Wid = MyMplWidget()
        
      
        Array_to_Display=[]
        if self.XList.isEnabled() == True and len(self.XList.selectedItems()) > 0:
            ax=str(self.XList.currentItem().text())
            Array_to_Display.append(eval(ax))
            for i in self.YList.selectedItems():
                t=eval(str(i.text()))
                Array_to_Display.append(t)
                if all(isinstance(x, (int, long, float, complex)) for x in t): 
                    self.Wid.canvas.axes.plot(eval(ax),t,color='red',alpha=0.3)
                else:
                    print str(i.text()), "is a TextWave, No rendering"
        else:
            for i in self.YList.selectedItems():
                t=eval(str(i.text()))
                Array_to_Display.append(t)
                try:
                    if all(isinstance(x, (int, long, float, complex)) for x in t):
                        self.Wid.canvas.axes.plot(t,color='red',alpha=0.3)
                    else:
                        print str(i.text()), "is a TextWave, No rendering"
                except TypeError: #For non-lists
                    print str(i.text()), " = ", t
                    return
  
                        
                
        self.smallbrowser=SpreadSheet(Source=Array_to_Display,Rendering=False)

        hbox.addWidget(self.Wid)
        
        hbox.addWidget(self.smallbrowser)

        self.Widget.setLayout(hbox)
        self.Widget.show()

    def Import_Data(self):

        try:
        #Session=Requete.Global_Session
            self.importmodule=gui.importdata.ImportData(metadata=Requete.Global_Meta,session=Requete.Global_Session)
            self.importmodule.show()
        except WindowsError: 
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Windows Error</b>
            <p>Try to import less files at once
            """)           
            msgBox.exec_()            
        except AttributeError:
            # TODO : Must be automated
            if Main.SQLTabWidget.currentIndex() == 0 or Main.SQLTabWidget.currentIndex() == 1:
                Main.error = QtGui.QMessageBox.about(Main, "Error",
                """
                <b>Database Selection Error</b>
                <p>You must do an initial query on the good database first
                (for example, just select a block, or click or Reset Fields)
                """)  
            elif Main.SQLTabWidget.currentIndex() == 2:
                Main.error = QtGui.QMessageBox.about(Main, "Error",
                """
                <b>Not Available</b>
                <p>This option is currently not available for local files
                You can drag and drop Ibw, pxp, txt and csv file into the import window
                """)                  

    def Create_DB(self):

        try:
            self.createdbmodule=gui.createdb.CreateDB()
            self.createdbmodule.show()
           
        except AttributeError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Database Selection Error</b>
            <p>You must do a query on the good database first
            """)     
            msgBox.exec_() 
        
    def Tree_View(self):
       
        self.explorer=gui.explorer.MainExplorer(metadata=Requete.Global_Meta)
        #Main.Analyze_Tab_Widget.addTab(explorer,"Spike Analysis")
        self.explorer.show()
    
    def Start_OE(self):
        
        from OpenElectrophy.gui import MainWindow,OpenDB
        self.explorer=gui.explorer.MainExplorer(metadata=Requete.Global_Meta)
        self.w = MainWindow(applicationname ='OpenElectrophy_0_2')
        database = {'dbname' : 'Demo withfake fields.db',
                    'dbtype' : 'sqlite', 
                    'explorer' : self.explorer,
                    'metadata' : Requete.Global_Meta}
        if self.w.tabDatabases.count()==1:
            self.w.tabDatabases.removeTab(0)
            self.w.openedDatabases = [ ]
        
        self.w.openedDatabases.append(database )
        self.w.tabDatabases.addTab( database['explorer'] , database['dbname'])
        
        self.w.figureTools.setEnabled( True )
        self.w.figureMenu.setEnabled(True)
     
        self.w.show()
        
    def About(self):
        
        msgBox = QtGui.QMessageBox()
        msgBox.setText(
        """
        <b>About the Software</b>
        <p>SynaptiQs is a free PyQt tool written by Antoine Valera, PhD
        <p>INCI-CNRS UPR 3212, 5 rue Blaise Pascal 67084 Strasbourg, France
        <p>& UCL Silver Lab, Gower Street, WC1E 6BT, London, UK
        <p>You can find more informations on the website : http://wix.synatiQs.com/SynaptiQs" 
        <p>or contact me at a.valera@ucl.ac.uk" 
        """)   
        msgBox.exec_()

    def Add_Array(self,Arrays=None):
        
        Main.Current_or_Average.clear()   
        for i in Arrays: 
            if i not in Main.ExistingSweeps:
                Main.ExistingSweeps.append(i)
        Main.Current_or_Average.addItems(Main.ExistingSweeps)  
        
        
    def SpikeSorting(self):
        
        if Main.SQLTabWidget.currentIndex() == 0 or Main.SQLTabWidget.currentIndex() == 1:
            from OpenElectrophy import sql,open_db,Session

            bl=numpy.array(Requete.Block_ids).flatten()
            ch=list(set(numpy.array(Requete.Analogsignal_channel).flatten()))
            
            if len(list(set(bl))) == 1 and  Requete.Block_ids[0] != None:
                list_of_block="(%s)" % bl[0]
            else:
                list_of_block=str(tuple(set(bl)))
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                <b>Caution!</b>
                <p>Please Select only one block for SpikeSorting""")     
                msgBox.exec_() 
                return
            
            channel= str(ch[int(Mapping.CurrentChannel)])
            if len(ch) >1:
                print 'More than one channel detected, only channel %s was used' %(Mapping.CurrentChannel)
                
            list_of_block=list_of_block.replace("L","")
        
               
            
            query="""
            SELECT recordingpoint.id,recordingpoint.id_block
            FROM recordingpoint,analogsignal
            WHERE recordingpoint.id_block in %s
            AND analogsignal.id_recordingpoint = recordingpoint.id
            AND analogsignal.channel = %s
            ORDER BY recordingpoint.id""" % (list_of_block,channel)
            
            
            print "##################################"
            print "This is the RecordingPoint query:"
            print query
            
            #For SQLite and mySQL database
            try:
                rp,b =  sql(query)
                if rp == []:
                    print 'No recording point here'
                    return
  
            #For LocalFiles
            except (sqlalchemy.exc.OperationalError,TypeError):
                if Main.SQLTabWidget.currentIndex() == 2:
                    warning = QtGui.QMessageBox.warning(QtCore.QObject().sender().parent(),'Warning, option not available without database','To perform SpikeSorting, data must be integrated in a database. Do you want to put this file in in a temporary SQLite Database?',
                            QtGui.QMessageBox.Ok , QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                            QtGui.QMessageBox.NoButton)
                            
                    if warning == 4194304:#QtGui.QMessageBox.NoButton:
                        return   
                    else:
                        from sqlalchemy import create_engine
                        from OpenElectrophy.gui.guiutil.paramwidget import *
                        from OpenElectrophy import Session,open_db,sql
                        from OpenElectrophy.io import all_format
                       
                        dict_format = { }
                        for name,format in all_format :
                            #possibleInput.append(name)
                            dict_format[name] = format
    
    
                        url = Requete.url#sqlite:///C:/Users/Antoine/Desktop/Test.db"
                        Main.SQLite_path.setText(url)
                        Requete.url = url
                        
                        engine = create_engine( url )
                        engine.connect()
                        
                        Requete.Global_Meta=open_db(url)
                        Requete.Global_Session=Session()
                        
                        try:
                            sql("ALTER TABLE analogsignal ADD COLUMN Tag varchar(512)", metadata=Requete.Global_Meta , session=Session())
                        except sqlalchemy.exc.ResourceClosedError: # Bug, script must continue
                            pass
                        except sqlalchemy.exc.OperationalError: # if tag already exists
                            pass
                            
                            
                            
                        
                        Main.SQLTabWidget.setCurrentIndex(1)
                        
                        Main.SQLite_path.setText(url)
                        Requete.Record_User_Parameters()
                        
                        #Requete.Request_ComboBoxes_update() #Empty datbase loaded
                        
                        #Requete.Global_Meta=open_db(url)
                        #Requete.Global_Session=Session()
                        
                        param = [('delimiter', {'possible': ['\t', ' ', ',', ';'], 'value': '\t'}), ('usecols', {'type': int, 'value': None}), ('skiprows', {'value': 0}), ('timecolumn', {'type': int, 'value': None}), ('samplerate', {'value': 1000.0}), ('t_start', {'value': 0.0}), ('method', {'possible': ['genfromtxt', 'csv', 'homemade'], 'value': 'homemade'})]
                        
                        inputOptions=ParamWidget( param )
                        #input = dict_format[ fileType ]['class'](filename = name  )
                        input = dict_format['ascii signal']['class'](filename = 'C:\\Users\\Antoine\\Desktop\\file.txt'  )
                        ob = input.read(**inputOptions.get_dict())
                        #OpenElectrophy.io.io.AsciiSignalIO
                        Requete.Global_Session.add(ob)
                        #bl = ob
                  
                        Requete.Global_Session.commit()                    
                        
                        
                        return 
                else :
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    <b>Error</b>
                    <p>An unknown SQL error occured""")     
                    msgBox.exec_()                  
                    return 
                    
                    
                    
                    
            gui.contextmenu.newSpikeSorting_from_full_band_signal(parent=Main.MainWindow,metadata=Requete.Global_Meta,Session=Requete.Global_Session,id=rp[0])
            
            
    #        except AttributeError:
    #            msgBox = QtGui.QMessageBox()
    #            msgBox.setText(
    #            """
    #            <b>SQL query error</b>
    #            <p>Please select your file and do a query first""")       
    #            msgBox.exec_() 
    #            return        
            
             
            """
            Pour sauver sous forme de fichier ASCII les données
            """
            #Analysis.si=Navigate.si
            #Analysis.tag=Requete.tag["Selection"]
        elif Main.SQLTabWidget.currentIndex() == 2:     
            #from OpenElectrophy.computing.spikesorting.detection import CrossingThreshold
            #from scipy import signal

            Value, ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'Input Dialog', 
                'Please Enter the Spike Threshold',
                text='')
            if not ok:
                return
            
            Thr=float(Value) 
            Analysis.DetectSpikesOnLocalFile(Thr)

           
        
    def SendToIgor(self,array=None,name=None):
        '''
        Send an array to igor. The array will be in in :root
        and will be named Wave0
        
        '''

        from win32com.client import Dispatch

        self.NumberOfFilesSentToIgor+=1
        
        
        if array == None and name== None:
            #TODO :
            #       -Use the real name of the array for importation
            #       -check more carefully all situations
            currentname = str(Main.Current_or_Average.currentText())
            print currentname, ' sent to Igor as Wave'+str(self.NumberOfFilesSentToIgor)
            savename = currentname.split(".")[1]
            currentpath = str(Main.desktop)+'/'+'Wave'+str(self.NumberOfFilesSentToIgor)+'.txt'
            print 'temp file is ', currentpath
        elif array != None and name== None:
            savename= 'Wave'+str(self.NumberOfFilesSentToIgor)
            currentname = 'Wave'+str(self.NumberOfFilesSentToIgor)
            currentpath = str(Main.desktop)+'/'+savename+'.txt'
        else:
            currentname=array
            currentpath = str(Main.desktop)+'/'+str(array)+'.txt'
           
        try:
            if savename == 'Wave'+str(self.NumberOfFilesSentToIgor):
                numpy.savetxt(currentpath, array)
            else:
                numpy.savetxt(currentpath, eval(currentname))
            Igor = Dispatch('IgorPro.Application')
            Igor.Visible = True
            #Igor.Execute('NewDataFolder/O/S root:localstring')
            Igor.Execute('SetDataFolder root:')
            Igor.Execute('newpath/o/q path "%s"' %(str(Main.desktop).replace('\\',':').replace('::',':')))#%(os.environ['USERPROFILE'].replace('\\',':').replace('::',':')))
            cmd = 'LoadWave/J/W/A/D/O/P=path "%s.txt"' % (savename) #/T for textwaves
            Igor.Execute(cmd) #See N option for overwriting options
            cmd='Display wave'+str(self.NumberOfFilesSentToIgor)
            Igor.Execute(cmd)
            os.remove(currentpath)
            
         
        except TypeError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Saving Error</b>
            <p>Did you set a name for your variable?
            use name=''
            """)
            msgBox.exec_()       
        except IOError: 
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Saving Error</b>
            <p>This Folder do not exist, please set a new Saving folder
            """)
            msgBox.exec_()            
#        except pywintypes.com_error: 
#            msgBox = QtGui.QMessageBox()
#            msgBox.setText(
#            """
#            <b>Software not Found</b>
#            <p>This error usually happens when Igor is not installed
#            """)
#            msgBox.exec_()            


        

        #wb = xl.SendToHistory('C:\\Users\\Antoine\\Na.txt')
        #xl.Visible = True    # optional: if you want to see the spreadsheet

        
    def Navigator(self):
        #s=computing.spikesorting.spikesorter.SpikeSorter(mode='from_full_band_signal',session=Requete.Global_Session,recordingPointList=[1])
        self.a=gui.spikesortingwidgets.FullBandSignal()#,Session=RSession)
        self.a.show()