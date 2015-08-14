# -*- coding: utf-8 -*-
"""
widget for importing data into a db
    
"""


from PyQt4.QtCore import *
from PyQt4.QtGui import *



from guiutil.icons import icons
from guiutil.paramwidget import *

import os

from ..classes import *
from ..io import all_format
from ..io import transform_all_spiketrain_mode


# constructing possibles input and output
possibleInput = [ ]
dict_format = { }
for name,format in all_format :
    possibleInput.append(name)
    dict_format[name] = format



class ImportData(QDialog) :
    """
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            session = None,
                            globalApplicationDict = None,
                            ):
        QDialog.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        self.session = session
        
        self.setWindowTitle(self.tr('Importing new data'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.paramTypes = ParamWidget([ ('import_type' , {'value' :  possibleInput[0] , 'possible' : possibleInput , 'label' : 'Choose your data format'})])
        self.mainLayout.addWidget(self.paramTypes)
        self.connect(self.paramTypes , SIGNAL('paramChanged( QString )') , self.changeType )
        
        self.tab = QTabWidget()
        self.mainLayout.addWidget( self.tab )
        
        
        # Files tab
        w =  QWidget()
        v = QVBoxLayout()
        w.setLayout(v)
        self.tab.addTab(w, 'Files')
        self.butAdd = QPushButton(QIcon(':/list-add.png') , 'Add files')
        v.addWidget(self.butAdd)
        self.connect(self.butAdd , SIGNAL('clicked()') , self.addFiles)
        self.listFiles = QListWidget()
        v.addWidget(self.listFiles)
        
        # Options input tab
        self.widgetInput =  QWidget()
        v = QVBoxLayout()
        self.widgetInput.setLayout(v)
        self.tab.addTab(self.widgetInput, 'Options')
        
        # General options
        params = [
                            [ 'group_segment', {'value' : False , 'label' : 'If import object is segment, group them in one block' } ],
                            [ 'spiketrain_mode' , {'value' :'standalone' , 'label' : 'SpikeTrain mode (container = spike table, standalone = more efficient)',
                                                                    'possible' : ['standalone','container' ] }],
                        ]
        self.generalOptions = ParamWidget(params)
        self.tab.addTab(self.generalOptions, 'Advanced options')
        
        
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Open| QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , self.importData )
        self.connect( buttonBox , SIGNAL('rejected()') , self, SLOT('reject()') )
        
        # initiate options tab
        self.inputOptions = None
        self.changeType( 'import_type' )


    def changeType(self, name):
        formatname = self.paramTypes[name]
        if self.inputOptions is not None :
            self.inputOptions.hide()
            self.widgetInput.layout().removeWidget( self.inputOptions )
        if formatname is None:return
        
        cl = dict_format[formatname]['class']
        param = cl.read_params[cl.readable_objects[0]]
        print param
        self.inputOptions = ParamWidget( param )
        self.widgetInput.layout().addWidget( self.inputOptions )
        
        if cl.mode =='file':
            self.butAdd.setEnabled(True)
            self.butAdd.setText('Add files')
        elif cl.mode =='dir':
            self.butAdd.setEnabled(True)
            self.butAdd.setText('Add dir')
        elif cl.mode =='database':
            self.butAdd.setEnabled(False)
        elif cl.mode =='fake':
            self.butAdd.setEnabled(False)
        else:
            self.butAdd.setEnabled(False)
            
        
        
        self.listFiles.clear()
        

    def addFiles(self):
        formatname = self.paramTypes['import_type']
        cl = dict_format[formatname]['class']
        
        fd = QFileDialog()
        fd.setAcceptMode(QFileDialog.AcceptOpen)
        if cl.mode =='file':
            fd.setFileMode(QFileDialog.ExistingFiles)
        elif cl.mode =='dir':
            fd.setFileMode(QFileDialog.Directory)
        
        if (fd.exec_()) :
            names = fd.selectedFiles()
            #~ for name in names:
                #~ print  type(name)
            self.listFiles.addItems(names)
            

    def importData(self):
        #~ if self.generalOptions['group_segment'] and :
            #~ bl = Block()
            #~ self.session.add(bl)
            #~ self.session.commit()

        fileType = self.paramTypes['import_type']
        cl = dict_format[fileType]['class']
            
        bl = None
        error_list= [ ]
        
        if cl.mode =='file' or cl.mode =='dir':
            listname = [ ]
            for i in range(self.listFiles.count()):
                listname.append( unicode(self.listFiles.item(i).text()) )
        elif cl.mode =='database' or cl.mode =='fake':
            listname = [ None ]
        
        for i in range(len(listname)):
            name = listname[i]
            #~ try :
            if 1:
                
                if cl.mode =='file':
                    input = dict_format[ fileType ]['class'](filename = name  )
                    print name
                    print dict_format[ fileType ]
                    print dict_format[ fileType ]['class']
                  
                elif cl.mode =='dir':
                    input = dict_format[ fileType ]['class'](dirname = name  )
                elif cl.mode =='database':
                    input = dict_format[ fileType ]['class'](  )
                elif cl.mode =='fake':
                    input = dict_format[ fileType ]['class'](  )
                
                ob = input.read(**self.inputOptions.get_dict())
                
                if cl.mode =='file' or cl.mode =='dir':
                    ob.fileOrigin = os.path.basename(name)
                
                transform_all_spiketrain_mode(ob , self.generalOptions['spiketrain_mode'])
                
                if type(ob) is Block:
                    self.session.add(ob)
                    bl = ob
                elif type(ob) is Segment :
                    if not self.generalOptions['group_segment'] or bl is None:
                        bl = Block()
                        #~ bl._segments.append( ob )
                        bl.add_one_segment( ob )
                        self.session.add(bl)
                    else :
                        #~ bl._segments.append( ob )
                        bl.add_one_segment( ob )
                        
                

                    

                #~ for s in  bl._segments[0]._analogsignals:
                    #~ print s.signal.size
                
                self.session.commit()
            #~ except:
                    #~ error_list.append(filename)
            
        if len(error_list) >0:
            text = "Fail to import :"
            for f in error_list:
                if f is not None:
                    text+= '    '+f
                else:
                    text = 'nofile'
            
            QMessageBox.warning(self,self.tr('Fail'),text,
                    QMessageBox.Ok , QMessageBox.NoButton)
        
        self.accept()
        #~ self.close()
        

