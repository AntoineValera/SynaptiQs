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



class QueryBox(QWidget) :
    """
    Widget for writting a sql query.
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            globalApplicationDict = None,
                            table = None,
                            query = None,
                            ):
        QWidget.__init__(self, parent)
        self.metadata = metadata
        self.globalApplicationDict = globalApplicationDict
        self.table = table

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        if query is None:
            query = """SELECT %s.id
FROM %s
LIMIT 100
""" %(self.table, self.table,)

        param = [
                        ('query' , { 'value' : query , 'widgettype' : QTextEdit  , 'type' : unicode}   ), 
                        ]
        self.param = ParamWidget(param,
                            keyformemory = 'query/'+self.table,
                            applicationdict = self.globalApplicationDict)
        self.mainLayout.addWidget(self.param)
        
        but = QPushButton(QIcon(':/view-filter.png') , 'filter with query')
        self.mainLayout.addWidget(but)
        self.connect(but, SIGNAL('clicked()'), self.applyQuery)
        
    def applyQuery(self):
        query= str(self.param['query'])
        #~ session = create_session(bind=self.metadata.bind, autocommit=False, autoflush=True )
        #~ list_id = []
        #~ for id, in session.execute(text(query)).fetchall():
            #~ list_id.append(id)
        self.emit( SIGNAL('New query applied') , query )
    
    def query(self):
        return str(self.param['query'])


