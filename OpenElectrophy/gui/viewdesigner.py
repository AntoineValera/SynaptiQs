# -*- coding: utf-8 -*-


"""
This modules provide a widget able to design a treeview that can be displayed
in a qtsqltreeview

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from querybox import QueryBox


class ViewDesigner(QDialog) :
    """
    Dialog to design the treeview
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            globalApplicationDict = None,
                            **kargs
                            ):
        QDialog.__init__(self, parent)
        self.metadata = metadata
        self.globalApplicationDict = globalApplicationDict
        
        self.setWindowTitle(self.tr('Table view designer'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        g = QGridLayout()
        self.mainLayout.addLayout(g)
        g.addWidget(QLabel('View name'),0,0)
        self.lineName = QLineEdit('NewView')
        g.addWidget(self.lineName,0,1)
        g.addWidget(QLabel('Possible tables'),1,0)
        self.listPossibleTable = QListWidget()
        g.addWidget(self.listPossibleTable,2,0)
        g.addWidget(QLabel('Tables to display'),1,1)
        self.listDisplayedTable = QListWidget()
        g.addWidget(self.listDisplayedTable,2,1)
        
        but = QPushButton(QIcon(':/configure.png') , 'Field to display for selected table'  )
        g.addWidget(but,3,1)
        self.connect( but , SIGNAL('clicked()') , self.editField )
        
        g.addWidget(QLabel('Top Hierarchy table :'),4,0)
        self.comboTop = QComboBox()
        g.addWidget(self.comboTop,4,1)
        allTableNames =  [ name for name in self.metadata.tables ]
        self.comboTop.addItems( allTableNames )
        
        
        #~ self.queryBox = QueryBox(metadata = metadata,
                            #~ globalApplicationDict = self.globalApplicationDict,
                            #~ table = self.getTopHierarchyTable(),
                            #~ )
        #~ self.mainLayout.addWidget( self.queryBox )
       
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , self, SLOT('accept()') )
        self.connect( buttonBox , SIGNAL('rejected()') , self, SLOT('reject()') )
        
        
        # drap n drop
        #~ self.listPossibleTable.setDragEnabled(True)
        self.listPossibleTable.setDragDropMode(QAbstractItemView.DragOnly)
        self.listDisplayedTable.setDragDropMode(QAbstractItemView.DropOnly)
        
        # shorcuts
        DeleteShortcut = QShortcut(QKeySequence(Qt.Key_Delete),self.listDisplayedTable)
        self.connect(DeleteShortcut, SIGNAL("activated()"), self.deleteSelection)
        
        if 'showColumns' in kargs:
            self.showColumns = {}
            self.showColumns.update(kargs['showColumns'])
            self.lineName.setText(kargs['name'])
            if kargs['topHierarchyTable'] in allTableNames:
                self.comboTop.setCurrentIndex( allTableNames.index( kargs['topHierarchyTable']  ) )
            tablesToDisplay = [ ]
            for k,v in kargs['dictChildren'].iteritems():
                tablesToDisplay += [k]
                tablesToDisplay += v
            tablesToDisplay = numpy.unique(tablesToDisplay).tolist()
            for tableName in tablesToDisplay:
                self.listDisplayedTable.addItem( tableName )
            
        else:
            self.showColumns = { }
        
        self.refresh()
        
        
    def refresh(self):
        self.listPossibleTable.clear()
        self.listPossibleTable.addItems( [ name for name in self.metadata.tables ] )
            
    def deleteSelection(self):
        for i in self.listDisplayedTable.selectedIndexes():
            self.listDisplayedTable.takeItem(i.row())

    def editField(self):
        
        for i in self.listDisplayedTable.selectedIndexes():
            tableName = str(self.listDisplayedTable.item(i.row()).text())
            d = FieldListdesigner(metadata = self.metadata, 
                                            tableName = tableName,
                                            showColumns = self.showColumns)
            ok = d.exec_()
            if ok :
                self.showColumns = d.getShowColumns()
    
    def getTableToDisplay(self):
        all = [ str(self.listDisplayedTable.item(n).text()) for n in range(self.listDisplayedTable.count()) ]
        return all
        
    def getTopHierarchyTable(self):
        return str(self.comboTop.currentText())
    
    def getShowColumns(self):
        return  self.showColumns
        
    def getName(self):
        return self.lineName.text()
    
    def getViewDict(self):
        view = {   'name' : self.getName(),
                        'topHierarchyTable'  : self.getTopHierarchyTable(),
                        'showColumns' :  self.getShowColumns(),
                        'dictChildren': constructDictChildren( self.metadata,
                                                                                    self.getTableToDisplay(),
                                                                                    self.getTopHierarchyTable()),
                        'topHierarchyQuery' : None,
                        }
        return view

def constructDictChildren( metadata, tableList, topHierarchyTable):
    
    dictChildren = { }
    if topHierarchyTable in tableList:
        table = tableList.pop(tableList.index(topHierarchyTable))
        dictChildren[table] = [ ]
    else :
        return { }
    
    possibleTable = [ ]
    
    while True :
        for childName in metadata.dictMappedClasses[table].children :
            if childName in tableList:
                possibleTable += [ childName ]
                dictChildren[table] += [ childName ]
                
        if len(possibleTable)>0:
            print len(possibleTable)
            table = possibleTable.pop(0)
            dictChildren[table] = [ ]
        else:
            break
        
    return dictChildren


class FieldListdesigner(QDialog) :
    """
    Dialog for choosing the field list to dislplay
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                             tableName = None,
                            showColumns = None,
                            ):
        QDialog.__init__(self, parent)
        self.metadata = metadata
        self.tableName = tableName
        
        self.showColumns = {}
        self.showColumns.update(showColumns)
        
        self.possibleFields = []
        for n, t in self.metadata.dictMappedClasses[self.tableName].fields :
            if t != numpy.ndarray:
                self.possibleFields += [n]
        
        if  self.tableName not in self.showColumns:
            self.showColumns[self.tableName] = self.possibleFields

        self.setWindowTitle(self.tr('Choose fields to be dislpayed in the tree'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        g = QGridLayout()
        self.mainLayout.addLayout(g)
        
        #~ self.check = QCheckBox('Show all fields')
        #~ g.addWidget(self.check , 0,0)
        
        self.listField = QListWidget()
        g.addWidget(self.listField , 1,0)
        
        
        #~ self.connect( self.check , SIGNAL('stateChanged( int)') , self.changeCheck )
        
        for fieldName in self.possibleFields :
            it = QListWidgetItem(fieldName)
            it.setCheckState(fieldName in self.showColumns[self.tableName])
            
            self.listField.addItem(it)
        
       
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , self, SLOT('accept()') )
        self.connect( buttonBox , SIGNAL('rejected()') , self, SLOT('reject()') )
        
    #~ def changeCheck(self, check ):
        #~ if check :
            #~ self.listField.setEnabled(False)
        #~ else:
            #~ self.listField.setEnabled(True)
        
    def getShowColumns(self):
        self.showColumns[self.tableName] = []
        for i in range( self.listField.count()):
            f = self.listField.item(i)
            if f.checkState() :
                self.showColumns[self.tableName] += [str(f.text())]
        return self.showColumns


