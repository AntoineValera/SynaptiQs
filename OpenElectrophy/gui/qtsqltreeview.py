# -*- coding: utf-8 -*-


"""
This modules provide a widget able to display a treeview of a SQL schema

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy

from guiutil.icons import icons

class QtSqlTreeView(QWidget) :
    def __init__(self  , parent = None ,
                            metadata = None,
                            Session = None,
                            session = None,
                            dictChildren = { },
                            showColumns = { },
                            topHierarchyTable = None,
                            topHierarchyQuery = None,
                            context_menu = None,
                            globalApplicationDict = None,
                            ):
        QWidget.__init__(self, parent)
        self.metadata = metadata
        self.context_menu = context_menu
        self.Session = Session
        if session is None:
            self.session = Session()
        else:
            self.session = session
        
        self.globalApplicationDict = globalApplicationDict
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.treeview = MyView()
        self.mainLayout.addWidget(self.treeview)
        self.model = MyModel(  metadata = metadata ,
                                            session = self.session,
                                            dictChildren = dictChildren ,
                                            showColumns = showColumns,
                                            topHierarchyTable = topHierarchyTable,
                                            topHierarchyQuery = topHierarchyQuery,
                                            
                                            )
        self.treeview.setModel(self.model)
        for n in range( self.model.maxColumn+1 ):
            self.treeview.resizeColumnToContents(n)
        
        if self.context_menu is not None:
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.connect(self,SIGNAL('customContextMenuRequested( const QPoint &)'),self.callContextMenu)
        
    def applyNewFilterWithQuery(self , topHierarchyQuery):
        self.model = MyModel(  metadata = self.model.metadata ,
                                            session = self.session,
                                            dictChildren = self.model.dictChildren ,
                                            showColumns = self.model.showColumns,
                                            topHierarchyTable = self.model.topHierarchyTable,
                                            topHierarchyQuery = topHierarchyQuery,
                                            )
        self.treeview.setModel(self.model)
        
    def refresh(self):
        
        self.model = MyModel(  metadata = self.model.metadata ,
                                            session = self.session,
                                            dictChildren = self.model.dictChildren ,
                                            showColumns = self.model.showColumns,
                                            topHierarchyTable = self.model.topHierarchyTable,
                                            topHierarchyQuery = self.model.topHierarchyQuery,
                                            )
        self.treeview.setModel(self.model)
        #~ self.model.emit(SIGNAL('modelReset()'))
        
        # resize column
        for c in range( self.model.columnCount(QModelIndex()) ):
            if c == 0: N=300
            else: N = 150
            if self.treeview.columnWidth(c) <N:
                self.treeview.setColumnWidth(c, N)
    
    
    
    def callContextMenu(self):
        # is selection uniform
        tablenames= [ ]
        ids = [ ]
        for index in self.treeview.selectedIndexes():
            if index.column()==0:
                tablename, id = self.model.data(index , 'table_and_id')
                tablenames.append(tablename)
                ids.append( id )
        homogeneous = numpy.unique(tablenames).size == 1
        
        
        # create menu
        menu = QMenu()
        actions = { }
        # all
        for name, callback, icon,mode in  self.context_menu['alltable']:
            
            if (mode =='unique' and len(ids)==1) or \
                    (mode =='homogeneous' and homogeneous) or \
                    (mode =='all' )  or\
                    (mode =='empty' and len(ids)==0):
                act = menu.addAction(QIcon(icon), name)
                actions[act] = [ callback, mode ]
        
        if len(ids) ==1 or homogeneous:
            tablename = tablenames[0]
            if tablename in self.context_menu :
                for name, callback, icon,mode in  self.context_menu[tablename]:
                    if (mode =='unique' and len(ids)==1) or \
                        (mode =='homogeneous' and homogeneous) :
                        act = menu.addAction(QIcon(icon), name)
                        actions[act] = [ callback, mode ]
        
        
        
        
        act = menu.exec_(self.cursor().pos())
        if act is None : return
        
        if act in actions :
            callback, mode = actions[act]
            
            if mode =='unique':
                id = ids[0]
                #~ OEclass = self.metadata.dictMappedClasses[tablename]
                #~ obj = self.session.query(OEclass).filter_by(id=id).one()
                callback(parent=self,
                                    id =id, 
                                    #~ instance = obj,
                                    tablename = tablename,
                                    metadata = self.metadata, 
                                    Session = self.Session,
                                    session = self.session,
                                    globalApplicationDict = self.globalApplicationDict,
                                    )
            
            elif mode == 'homogeneous' :
                callback(parent=self,
                    ids =ids,
                    tablenames = tablenames,
                    metadata = self.metadata, 
                    Session = self.Session,
                    session = self.session,
                    globalApplicationDict = self.globalApplicationDict,
                    )
            
            elif mode == 'all':
                callback(parent=self,
                                    ids =ids,
                                    tablenames = tablenames,
                                    metadata = self.metadata, 
                                    Session = self.Session,
                                    session = self.session,
                                    globalApplicationDict = self.globalApplicationDict,
                                    )
            elif mode =='empty':
                callback(parent=self,
                                    
                                    metadata = self.metadata, 
                                    Session = self.Session,
                                    session = self.session,
                                    globalApplicationDict = self.globalApplicationDict,
                                    
                                    topHierarchyTable = self.model.topHierarchyTable,
                                    )           

    
    def getSelectedObject(self):
        objects = [ ]
        for index in self.treeview.selectedIndexes():
            if index.column()==0:
                objects.append(self.model.data(index , 'object'))
        return objects
    
    def getSelectedTableAndIDs(self):
        tablenames= [ ]
        ids = [ ]
        for index in self.treeview.selectedIndexes():
            if index.column()==0:
                tablename, id = self.model.data(index , 'table_and_id')
                tablenames.append(tablename)
                ids.append( id )
        return tablenames, ids
    

#~ class MyView(QColumnView):
class MyView(QTreeView):    
    def __init__(self, parent =None) :
        QTreeView.__init__(self,parent)
        #~ QColumnView.__init__(self,parent)
        self.setIconSize(QSize(22,22))
        #~ self.setIconSize(QSize(32,32))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        #~ self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)        


class MyModel(QAbstractItemModel):
    """
    Implementation of a treemodel base on OpenElectrophy mapper layer on top of  sqlalchemy
    """
    def __init__(self, parent =None ,
                        metadata = None ,
                        session = None,
                        dictChildren ={ },
                        showColumns = { },
                        topHierarchyTable = None,
                        topHierarchyQuery = None,
                        ) :
        QAbstractItemModel.__init__(self,parent)
        self.metadata = metadata
        self.session= session
        self.dictChildren = dictChildren
        self.topHierarchyTable = topHierarchyTable
        self.topHierarchyQuery = topHierarchyQuery
        self.dictMappedClasses = metadata.dictMappedClasses
        self.showColumns = showColumns
        for tablename, oeClass in self.dictMappedClasses.iteritems():
            if tablename not in self.showColumns :
                fields = []
                for n, t in oeClass.fields :
                    if t != numpy.ndarray:
                        fields += [n]
                self.showColumns[tablename] = fields
        self.maxColumn = 0
        for fieldnames in self.showColumns.values() :
            if len(fieldnames)>self.maxColumn:
                self.maxColumn = len(fieldnames)
                
        
        topClass = self.dictMappedClasses[self.topHierarchyTable]
        self.rootQuery = self.session.query(topClass)
        if self.topHierarchyQuery is not None:
            list_id = []
            for id, in self.session.execute(self.topHierarchyQuery).fetchall():
                list_id.append(id)
            self.rootQuery = self.rootQuery.filter(topClass.id.in_( list_id ))

        
        if not hasattr(self.session, 'cache_for_all'):
            self.session.cache_for_all = [ ]
        self.firstChildren = self.rootQuery.all()
        for child in self.firstChildren:
            self.session.refresh(child)
            child.metadata = metadata
            child.session = session
            if child not in self.session.cache_for_all : 
                self.session.cache_for_all.append(child)
    
    
    
    def columnCount(self , parentIndex):
        #~ print '##columnCount', parentIndex, parentIndex.isValid()
        if not parentIndex.isValid():
            return self.maxColumn
        else :
            parentItem = parentIndex.internalPointer()
            columns = self.showColumns[parentItem.tablename]
            return len(columns)+1
            
    def rowCount(self, parentIndex):
        #~ print '##rowCount', parentIndex, parentIndex.isValid()
        if not parentIndex.isValid():
            return len(self.firstChildren)
        else :
            parentItem = parentIndex.internalPointer()
            return len(parentItem.childrenInTree(self.dictChildren, self.session))
        
    def index(self, row, column, parentIndex):
        #~ print '##index()', row, column, parentIndex,  parentIndex.isValid()
        if not parentIndex.isValid():
            children = self.firstChildren
        else:
            parentItem = parentIndex.internalPointer()
            children = parentItem.childrenInTree(self.dictChildren, self.session)
        if row >= len(children):
            return QModelIndex()
        childItem = children[row]
        return self.createIndex(row, column, childItem)

    def parent(self, index):
        #~ print '##parent' , index, index.row(), index.column(), index.isValid()
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parentInTree(self.dictChildren, self.session , self.dictMappedClasses)
        if parentItem is None :
            return QModelIndex()
        gparentItem = parentItem.parentInTree(self.dictChildren, self.session , self.dictMappedClasses)
        if gparentItem is None :
            parent_row = self.firstChildren.index(parentItem)
        else :
            childrenOfGParent = gparentItem.childrenInTree(self.dictChildren, self.session)
            parent_row = childrenOfGParent.index(parentItem)
        return self.createIndex(parent_row, 0, parentItem)
        
    def data(self, index, role):
        #~ print '##data' , index, index.row(), index.column(), index.isValid()
        
        if not index.isValid():
            return None

        #~ if role != Qt.DisplayRole:
            #~ return None
        #~ item = index.internalPointer()
        #~ return QVariant( '%s : %d'%( item.tablename, item.id) )
        
        
        item = index.internalPointer()

        col = index.column()
        if role ==Qt.DisplayRole :
            
            if  col ==0:
                #~ return QVariant( '<b>%s</b> : %d'%( item.tablename, item.id) )
                return QVariant( '%s : %d'%( item.tablename, item.id) )
            else :
                fieldnames = self.showColumns[item.tablename]
                if col > len(fieldnames):
                    return QVariant('')
                fieldname= fieldnames[col-1]
                if hasattr(item, fieldname):
                    value = getattr(item, fieldname)
                    return QVariant( '%s : %s'%( fieldname, str(value)) )
                else:
                    return None
        
        elif role == Qt.DecorationRole :
            if col == 0:
                #~ if item.tablename in self.dictMappedClasses.keys():
                    #~ return QIcon(':/'+ item.tablename+'.png')
                #~ else:
                    #~ return QIcon(':/magic.png')
                
                return QIcon(':/'+ item.tablename+'.png')
            else:
                return QVariant()
        elif role == 'table_and_id':
            return  item.tablename, item.id
            
        elif role == 'object':
            return item
            
        #~ elif role == 'table_index' :
            #~ #for drag and drop
            #~ return table+':'+str(id_principal)
        else :
            return QVariant()

    #~ def hasChildren ( self, parentIndex) :
        #~ if not parentIndex.isValid():
            #~ return True
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled

