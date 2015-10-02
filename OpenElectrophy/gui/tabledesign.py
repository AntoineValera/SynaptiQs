# -*- coding: utf-8 -*-


"""
This modules provide a widget able to design a treeview that can be displayed
in a qtsqltreeview

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from ..classes.base import OEBase, addColumnToTable, removeColumnToTable, addAChildToTable
from ..classes.sqlalchemyutil import mapAll

from guiutil.paramwidget import *

from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, Binary, Text, LargeBinary, DateTime, VARCHAR
import sqlalchemy
from sqlalchemy.orm import mapper
import migrate.changeset
from sqlalchemy.orm import sessionmaker , create_session

translate1 = {
                    Text : 'Text',
                    Float : 'Float',
                    Integer : 'Integer',
                    numpy.ndarray : 'numpy.ndarray',
                    DateTime : 'DateTime',
                    }

translate2 = { }
for k,v in translate1.iteritems():
    translate2[v] = k



class TableDesign(QDialog) :
    """
    Dialog to design or modify a table
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            session = None,
                            globalApplicationDict = None,
                            explorer = None,
                            **kargs
                            ):
        QDialog.__init__(self, parent)
        self.metadata = metadata
        self.session = session
        self.explorer = explorer
        self.globalApplicationDict = globalApplicationDict
        
        self.setWindowTitle(self.tr('Table designer'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        
        h  = QHBoxLayout()
        self.mainLayout.addLayout(h)
        self.comboTable = QComboBox()
        self.connect(self.comboTable, SIGNAL('currentIndexChanged(int)') , self.comboChanged )
        h.addWidget( self.comboTable , 3)
        but = QPushButton(QIcon(':/list-add.png'), 'Create a new table')
        self.connect( but , SIGNAL('clicked()') , self.createTable)
        h.addWidget(but)
        self.mainLayout.addSpacing(10)
        
        
        h  = QHBoxLayout()
        self.mainLayout.addLayout(h)
        h.addWidget( QLabel('Fields list') )
        h.addStretch(1)
        but = QPushButton(QIcon(':/list-add.png'), '')
        self.connect( but , SIGNAL('clicked()') , self.addField)
        h.addWidget(but)
        but = QPushButton(QIcon(':/list-remove.png'), '')
        self.connect( but , SIGNAL('clicked()') , self.removeField)
        h.addWidget(but)


        self.listFields = QTableWidget()
        self.mainLayout.addWidget( self.listFields )
        self.mainLayout.addSpacing(10)
        self.listFields.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.listFields.setSelectionMode(QAbstractItemView.SingleSelection)
        
        h1 = QHBoxLayout()
        self.mainLayout.addLayout(h1)
        
        v = QVBoxLayout()
        h1.addLayout(v)
        h  = QHBoxLayout()
        v.addLayout(h)
        h.addWidget( QLabel('Parents') )
        h.addStretch(1)
        but = QPushButton(QIcon(':/list-add.png'), '')
        self.connect( but , SIGNAL('clicked()') , self.addParent)
        #~ h.addWidget(but)
        #~ but = QPushButton(QIcon(':/list-remove.png'), '')
        h.addWidget(but)
        self.listParents = QListWidget()
        v.addWidget( self.listParents )
        
        h1.addSpacing( 10 )
        
        v = QVBoxLayout()
        h1.addLayout(v)
        h  = QHBoxLayout()
        v.addLayout(h)
        h.addWidget( QLabel('Children') )
        h.addStretch(1)
        but = QPushButton(QIcon(':/list-add.png'), '')
        self.connect( but , SIGNAL('clicked()') , self.addChild)
        #~ h.addWidget(but)
        #~ but = QPushButton(QIcon(':/list-remove.png'), '')
        h.addWidget(but)
        self.listChildren = QListWidget()
        v.addWidget( self.listChildren )

        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        #~ self.connect( buttonBox , SIGNAL('apply()') , self, SLOT('accept()') )
        self.connect( buttonBox.buttons()[1] , SIGNAL('clicked()') , self.apply )
        self.connect( buttonBox , SIGNAL('rejected()') , self, SLOT('reject()') )
    
        #
        self.new_children = [ ]
        self.new_parents = [ ]
        self.new_fields = [ ]
        self.removed_fields = [ ]
        self.tablename = None
        
        self.allTableNames =  [ name for name in self.metadata.tables ]
        self.comboTable.addItems( self.allTableNames )
        self.comboChanged(0)
        
    
    def comboChanged(self, num):
        if self.tablename is not None and str(self.comboTable.currentText()) == self.tablename : return
        if (len(self.new_children) or \
            len(self.new_parents) or \
            len(self.new_fields) or \
            len(self.removed_fields) ) :
            
            warn = 'some changes occures : do you want to apply them ?'
            mb = QMessageBox.warning(self,self.tr('Apply changes'),self.tr(warn),
                    QMessageBox.Apply ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                    QMessageBox.NoButton)
            if mb == QMessageBox.Apply :
                # put old one
                self.apply()
        
        
        self.tablename = str(self.comboTable.currentText())
        
        self.fields = [ e for e in self.metadata.dictMappedClasses[self.tablename].fields ]
        self.parents = [ e for e in  self.metadata.dictMappedClasses[self.tablename].parents ]
        self.children = [ e for e in  self.metadata.dictMappedClasses[self.tablename].children ]
        
        self.new_children = [ ]
        self.new_parents = [ ]
        self.new_fields = [ ]
        self.removed_fields = [ ]
        
        self.refresh()
        
    def refresh(self):
        self.listFields.clear()
        self.listFields.setColumnCount(2)
        self.listFields.setHorizontalHeaderLabels(['fieldname', 'fieldtype'])
        self.listFields.setRowCount(len(self.fields)+len(self.new_fields))
        r=0
        for fields in [ self.fields, self.new_fields ]:
            for fieldname, fieldtype in fields:
                item = QTableWidgetItem(fieldname)
                self.listFields.setItem(r, 0 , item)
                if  [fieldname, fieldtype ] in self.removed_fields:
                    item.setIcon(QIcon(':/list-remove.png'))
                if  [fieldname, fieldtype ] in self.new_fields:
                    item.setIcon(QIcon(':/list-add.png'))
                
                if fieldtype in translate1:
                    t = translate1[fieldtype]
                else:
                    t = 'unknown'
                item = QTableWidgetItem(t)
                self.listFields.setItem(r, 1 , item)
                #item.setBackground(QBrush('red'))
                r+=1

        self.listParents.clear()
        self.listParents.addItems( self.parents )
        for name in self.new_parents:
            item = QListWidgetItem(QIcon(':/list-add.png'), name)
            self.listParents.addItem(item)
        
        self.listChildren.clear()
        self.listChildren.addItems( self.children )
        for name in self.new_children:
            item = QListWidgetItem(QIcon(':/list-add.png'), name)
            self.listChildren.addItem(item)
        
        
    
    def createTable(self):
        params = [
                            [ 'tablename' ,  { 'value' :  '' }],
                        ]
        dia = ParamDialog(params , title = 'table name')
        if dia.exec_():
            tablename = dia.get_dict()['tablename']
            #~ print tablename
            if tablename in self.metadata.tables:
                return
            #create table
            columns = [ Column('id', Integer, primary_key=True) ,]
            table =  Table(tablename, self.metadata, *columns  )
            
            table.create()
        
            # create class
            classname = str(tablename[0].upper() + tablename[1:])
            newclass = type(classname,(OEBase,),{})
            newclass.tablename = tablename
            newclass.parents = [ ]
            newclass.children = [ ]
            newclass.fields = [ ]
            
            #map
            mapper(newclass , table ,  )
            self.metadata.dictMappedClasses[tablename] = newclass
            
            # GUI
            self.allTableNames.append( tablename)
            self.comboTable.addItem( tablename )
            
            self.comboTable.setCurrentIndex( len(self.allTableNames)-1)
        
    def addField(self,fieldname=None,fieldtype=None):
        f = translate2.keys()
        if fieldname == None or fieldtype == None:
            params = [
                                [ 'fieldname' ,  { 'value' :  '' }],
                                [ 'fieldtype' ,  { 'value' :  'Text' , 'possible' : f }],
                            ]
            dia = ParamDialog(params)
            if dia.exec_():
                d = dia.get_dict()
                self.new_fields+= [ [ d['fieldname'] , translate2[d['fieldtype']]  ] ]
                print self.new_fields
                self.refresh()        
        else:
            self.new_fields+= [ [ fieldname , translate2[fieldtype] ] ]
            self.refresh()  
            


        
    
    def removeField(self):
        if len(self.listFields.selectedItems())==0: return
        item = self.listFields.selectedItems()[0]
        if item.column() != 0: return
        r = item.row()
        if r < len( self.fields ):
            self.removed_fields.append( self.fields[r] )
        else:
            self.new_fields.pop( len( self.fields ) - r )
        self.refresh( )
    
    
    def addChildOrParent(self , type):
        alltables = self.metadata.dictMappedClasses.keys()
        if self.tablename is not None:
            alltables.remove( self.tablename )
        menu =  QMenu()
        for table in alltables:
            menu.addAction(table)
        
        act = menu. exec_(QCursor.pos())
        if act is None: return
        name = str( act.text() )
        if name in self.children : return
        if name in self.new_children : return
        if name in self.parents : return
        if name in self.new_parents : return
        
        if type =='child': 
            self.new_children.append( name )
        else:
            self.new_parents.append( name )
        
        self.refresh()

    def addChild(self):
        self.addChildOrParent( 'child')

    def addParent(self):
        self.addChildOrParent( 'parent')

        
    def apply(self):
        oeclass = self.metadata.dictMappedClasses[self.tablename] 
        for childname in self.new_children:
            if childname not in self.metadata.dictMappedClasses: continue
            childclass = self.metadata.dictMappedClasses[childname] 
            addAChildToTable(self.metadata, oeclass , childname)
            oeclass.children.append(childname)
            childclass.parents.append(self.tablename)
            
        for parentname in self.new_parents:
            parentclass =  self.metadata.dictMappedClasses[parentname] 
            addAChildToTable(self.metadata, parentclass , self.tablename)
            parentclass.children.append( self.tablename )
            oeclass.parents.append(parentname)
            
        
        for fieldname, fieldtype in self.new_fields:
            addColumnToTable(self.metadata, oeclass , fieldname, fieldtype)
            oeclass.fields.append( [ fieldname, fieldtype])
        
        for fieldname, fieldtype in self.removed_fields:
            removeColumnToTable(self.metadata, oeclass , fieldname)
            oeclass.fields.remove( [ fieldname, fieldtype])
        
        mapAll( self.metadata , self.metadata.dictMappedClasses )
        
        self.new_children = [ ]
        self.new_parents = [ ]
        self.new_fields = [ ]
        self.removed_fields = [ ]
        
        # deep refresh
        self.fields = [ e for e in self.metadata.dictMappedClasses[self.tablename].fields ]
        self.parents = [ e for e in  self.metadata.dictMappedClasses[self.tablename].parents ]
        self.children = [ e for e in  self.metadata.dictMappedClasses[self.tablename].children ]
        self.refresh()
        
        
        if self.explorer is not None:
            self.explorer.deepRefresh()


