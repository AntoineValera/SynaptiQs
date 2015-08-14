# -*- coding: utf-8 -*-


"""
This modules provide a widget to design SQL query
"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
from guiutil.globalapplicationdict import *
from guiutil.paramwidget import ParamWidget

#~ from qtsqltreeview import QtSqlTreeView
#~ from viewdesigner import *

from sqlalchemy.orm import sessionmaker , create_session
from sqlalchemy.sql import text

from qtsqltreeview import QtSqlTreeView
from querybox import QueryBox


class QueryResultBox(QWidget) :
    """
    Widget to write sql query et get the result in a list.
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            session = None,
                            globalApplicationDict = None,
                            table = None,
                            #~ orientation = Qt.Horizontal,
                            orientation = Qt.Vertical,
                            query = None,
                            ):
        QWidget.__init__(self, parent)
        self.metadata = metadata
        self.globalApplicationDict = globalApplicationDict
        self.table = table
        
        sp = QSplitter(orientation) 

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(sp)
        
        
        self.queryBox = QueryBox(metadata = metadata,
                            globalApplicationDict = globalApplicationDict,
                            table = table,
                            query = query )
        sp.addWidget(self.queryBox)
        self.connect(self.queryBox, SIGNAL('New query applied'), self.refreshTree)
        
        #~ self.tree = QTreeWidget()
        self.tree = QtSqlTreeView(metadata = metadata,
                                                session = session,
                                                dictChildren = { table:[] },
                                                showColumns = { },
                                                topHierarchyTable = table,
                                                topHierarchyQuery = query,
                                                context_menu = None,
                                                )
        sp.addWidget( self.tree )
        
    
    def refreshTree(self):
        query = self.queryBox.query()
        self.tree.applyNewFilterWithQuery( query )
