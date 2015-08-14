# -*- coding: utf-8 -*-


"""
This modules provide a explorer for managing treeviews

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
from guiutil.globalapplicationdict import *
from qtsqltreeview import QtSqlTreeView
from viewdesigner import *
from querybox import QueryBox
from contextmenu import context_menu

from sqlalchemy.orm import sessionmaker

class MainExplorer(QWidget) :
    """
    Dialog to design the treeview
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            globalApplicationDict = None,
                            ):
        QWidget.__init__(self, parent)
        self.metadata = metadata
        #~ self.session = create_session(bind=metadata.bind, autocommit=False, autoflush=True )
        self.Session = sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
        self.session = self.Session()
        
        # experimental
        self.session.cache_for_all = [ ]
        
        
        self.setWindowTitle(self.tr('Database explorer'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # listWiews
        self.listViews = [  { 'name' : 'BySegment',
                                        'topHierarchyTable'  :'block',
                                        'showColumns' : { },
                                        'dictChildren' : { 
                                                                    'block' : ['segment' ],
                                                                    'segment' : [ 'analogsignal', 'event' , 'epoch'],
                                                                    'analogsignal' : [ 'oscillation'],
                                                                    },
                                    },
                                    
                                    { 'name' : 'ByRecordingPoint',
                                        'topHierarchyTable'  :'block',
                                        'showColumns' : { },
                                        'dictChildren' : { 
                                                                    'block' : ['recordingpoint' ],
                                                                    'recordingpoint' : [ 'analogsignal'  , ],
                                                                    },
                                    },
                                    
                                    { 'name' : 'Neurons',
                                        'topHierarchyTable'  :'block',
                                        'showColumns' : { },
                                        'dictChildren' : { 
                                                                    'block' : ['neuron' ],
                                                                    'neuron' : [ 'spiketrain' ],
                                                                    },
                                    },
                                    
                                    { 'name' : 'SpikeByRecPoint',
                                        'topHierarchyTable'  :'block',
                                        'showColumns' : { },
                                        'dictChildren' : { 
                                                                    'block' : ['recordingpoint' ],
                                                                    'recordingpoint' : [ 'spiketrain' ],
                                                                    },
                                    },                                    
                                    
                                ]
        self.globalApplicationDict = globalApplicationDict
        if self.globalApplicationDict is None :
            pass
        else :
            if self.globalApplicationDict[ str(self.metadata.bind.url)+'/listViews']  is None :
                self.globalApplicationDict[ str(self.metadata.bind.url)+'/listViews'] = self.listViews
            else:
                self.listViews = [ ]
                for lw in self.globalApplicationDict[ str(self.metadata.bind.url)+'/listViews']:
                    if lw['topHierarchyTable'] in self.metadata.dictMappedClasses:
                        self.listViews.append(lw)
                    
                    
        
        self.tabViews = QTabWidget()
        self.buttonMenu = QPushButton(QIcon(':/configure.png'), '')
        self.connect(self.buttonMenu, SIGNAL('clicked()'), self.showConfigureMenu)
        self.tabViews.setCornerWidget(self.buttonMenu)
        self.mainLayout.addWidget(self.tabViews)
        
        for view in self.listViews:
            sqltreeview = QtSqlTreeView(metadata = self.metadata,
                                                Session = self.Session,
                                                session = self.session,
                                                dictChildren = view['dictChildren'],
                                                showColumns =  view['showColumns'],
                                                topHierarchyTable =  view['topHierarchyTable'],
                                                context_menu = context_menu,
                                                globalApplicationDict = self.globalApplicationDict,
                                                )
            self.tabViews.addTab(sqltreeview , view['name'],)
        
        self.tabViews.setTabsClosable(True)
        self.connect(self.tabViews , SIGNAL('tabCloseRequested( int )') , self.closeOneTab)
        
        self.createAction()
        self.createConfigureMenu()
        
        DeleteShortcut = QShortcut(QKeySequence("Ctrl+T"),self)
        self.connect(DeleteShortcut, SIGNAL("activated()"), self.addOneTab)
        
        
    def createAction(self):
        self.actionRefresh = QAction(self.tr("&Refresh view"), self)
        self.actionRefresh.setIcon(QIcon(':/view-refresh.png'))
        self.connect(self.actionRefresh, SIGNAL("triggered()"), self.refresh)
        
        self.actionAddTab = QAction(self.tr("&Add a new view"), self)
        self.actionAddTab.setIcon(QIcon(':/list-add.png'))
        self.connect(self.actionAddTab, SIGNAL("triggered()"), self.addOneTab)
        
        self.actionDelTab = QAction(self.tr("&Remove this view"), self)
        self.actionDelTab.setIcon(QIcon(':/list-remove.png'))
        self.connect(self.actionDelTab, SIGNAL("triggered()"), self.closeCurrentTab)
        
        self.actionEditTab = QAction(self.tr("&Edit this view"), self)
        self.actionEditTab.setIcon(QIcon(':/document-properties.png'))
        self.connect(self.actionEditTab, SIGNAL("triggered()"), self.editCurrentTab)
        
        self.actionFilterTab = QAction(self.tr("&Edit a SQL query to filter"), self)
        self.actionFilterTab.setIcon(QIcon(':/view-filter.png'))
        self.connect(self.actionFilterTab, SIGNAL("triggered()"), self.openQueryBox)
        


    def createConfigureMenu(self):
        self.menuConfigure = QMenu()
        self.menuConfigure.addAction(self.actionRefresh)
        self.menuConfigure.addAction(self.actionAddTab)
        self.menuConfigure.addAction(self.actionDelTab)
        self.menuConfigure.addAction(self.actionEditTab)
        self.menuConfigure.addAction(self.actionFilterTab)
    
    
    def deepRefresh(self):
        
        self.session.close()
        #~ self.Session = sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
        self.session = self.Session()
        
        #~ self.session = create_session(bind=self.metadata.bind, autocommit=False, autoflush=True )
        
        
        for i in range(len(self.listViews)):
            sqltreeview = self.tabViews.widget(i)
            sqltreeview.session = self.session
        
        self.session.cache_for_all = [ ]
        self.refresh()
    
    def refresh(self):
        for i in range(len(self.listViews)):
            sqltreeview = self.tabViews.widget(i)
            sqltreeview.refresh()
    
    def closeCurrentTab(self):
        self.closeOneTab(self.tabViews.currentIndex())
    
    def closeOneTab(self, num):
        if len(self.listViews) ==1:
            return
        self.tabViews.removeTab(num)
        self.listViews.pop(num)
        if self.globalApplicationDict is not None :
            self.globalApplicationDict[ str(self.metadata.bind.url)+'/listViews'] = self.listViews   
            
    
    def addOneTab(self):
        w = ViewDesigner(metadata = self.metadata)
        ok = w.exec_()
        if ok : 
            view = w.getViewDict()
            self.listViews += [ view ]
            sqltreeview = QtSqlTreeView(metadata = self.metadata,
                                                Session = self.Session,
                                                session = self.session,
                                                dictChildren = view['dictChildren'],
                                                showColumns =  view['showColumns'],
                                                topHierarchyTable =  view['topHierarchyTable'],
                                                context_menu = context_menu,
                                                globalApplicationDict = self.globalApplicationDict,
                                                )
            self.tabViews.addTab(sqltreeview , view['name'],)
            
            if self.globalApplicationDict is not None :
                self.globalApplicationDict[ str(self.metadata.bind.url)+'/listViews'] = self.listViews    
                
    def editCurrentTab(self):
        num = self.tabViews.currentIndex()
        view = self.listViews[num]
        w = ViewDesigner(metadata = self.metadata , **view)
        ok = w.exec_()
        if ok : 
            view = w.getViewDict()
            self.listViews[num] = view
            sqltreeview = QtSqlTreeView(metadata = self.metadata,
                                                Session = self.Session,
                                                session = self.session,
                                                dictChildren = view['dictChildren'],
                                                showColumns =  view['showColumns'],
                                                topHierarchyTable =  view['topHierarchyTable'],
                                                context_menu = context_menu,
                                                globalApplicationDict = self.globalApplicationDict,
                                                )
            self.tabViews.removeTab(num)
            self.tabViews.insertTab ( num, sqltreeview , view['name'],)
            self.tabViews.setCurrentIndex(num)
            
            if self.globalApplicationDict is not None :
                self.globalApplicationDict[ str(self.metadata.bind.url)+'/listViews'] = self.listViews
        
    def openQueryBox(self):
        num = self.tabViews.currentIndex()
        view = self.listViews[num]
        qb = QueryBox(parent = self,
                                metadata = self.metadata,
                                globalApplicationDict = self.globalApplicationDict,
                                table = view['topHierarchyTable'],
                                )
        qb.setWindowFlags(Qt.Dialog)
        qb.setWindowModality(Qt.WindowModal)
        qb.setWindowTitle('Edit a query for table '+view['topHierarchyTable'])
        qb.show()
        self.connect(qb, SIGNAL('New query applied'), self.newQueryApplied)
        
    def newQueryApplied(self, query):
        qb = self.sender()
        num = self.tabViews.currentIndex()
        view = self.listViews[num]
        treeview = self.tabViews.currentWidget()
        treeview.applyNewFilterWithQuery(query)
        

    def showConfigureMenu(self):
        self.menuConfigure. exec_(QCursor.pos())
            
    
    def getCurrentSqlTreeView(self):
        return  self.tabViews.currentWidget()

