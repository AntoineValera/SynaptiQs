# -*- coding: utf-8 -*-
"""
widget for creating a db
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from guiutil.icons import icons
from guiutil.paramwidget import *
import os

from sqlalchemy import create_engine


infomysql = """
For creating you need a functional  MySQL server.
You also need a sql administrator account to create the db.

"""

sqliteinfo ="""
SQLite is leighweigt DB system contained in a single (big) file.
Creating a db with sqlite is just like creating a local file.

"""

dbtypes = [
                 {
                'name' :  'mysql',
                'info'  :infomysql,
                'param' : [
                                    ('host' , { 'value' : '' ,  }   ),
                                    ('port' , { 'value' : '3306' ,  }   ),
                                    ('adminName' , { 'value' : 'root' ,   'label' : 'Admin login' }   ),
                                    ('adminPassword' , { 'value' : '' ,  'password' : True , 'label' : 'Admin password' }   ),
                                    ('user' , { 'value' : '' , 'label' : 'User which will acces the db'  }   ),
                                    ('dbName' , { 'value' : '' , 'label' : 'DB name',   }   ),
                                    
                                ],
                'dbNameSelection' : True,
                'icon' : ':/mysql.png',
                },

                {
                'name' :  'sqlite',
                'info'  :sqliteinfo,
                'param' : [
                                    ('dir' , { 'value' : '' ,  'widgettype' :ChooseDirWidget }   ),
                                    ('name' , { 'value' : '' }   ),
                                ],
                'dbNameSelection' : False,
                'icon' : ':/sqlite.png',
                },
                
                 {
                'name' :  'postgres',
                'info'  :infomysql,
                'param' : [
                                    ('host' , { 'value' : '' ,  }   ),
                                    ('adminName' , { 'value' : 'postgres' ,   'label' : 'Admin login' }   ),
                                    ('adminPassword' , { 'value' : '' ,  'password' : True , 'label' : 'Admin password' }   ),
                                    ('user' , { 'value' : '' , 'label' : 'User which will acces the db'  }   ),
                                    ('dbName' , { 'value' : '' , 'label' : 'DB name',   }   ),
                                ],
                'dbNameSelection' : True,
                'icon' : ':/postgres.png',
                },                

                ]

class CreateDB(QDialog) :
    def __init__(self  , parent = None ,
                            metadata = None,
                            globalApplicationDict = None,
                            ):
        QDialog.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        
        self.setWindowTitle(self.tr('Create a new database'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.mainLayout.addWidget(QLabel('Select the appropriate tab for SQL engine'))
        
        self.tabEngines = QTabWidget()
        self.mainLayout.addWidget(self.tabEngines)
        self.params ={ }
        self.combos = { }
        
        for d in dbtypes:
            w = QWidget()
            v = QVBoxLayout()
            w.setLayout(v)
            h = QHBoxLayout()
            v.addLayout(h)
            #~ print type(QIcon(d['icon']))
            l = QLabel()
            l.setPixmap( QIcon(d['icon']).pixmap(64,64))
            h.addWidget(l)
            h.addWidget(QLabel(d['info']))
            
            self.params[d['name']] = ParamWidget(d['param'] )
            v.addWidget( self.params[d['name']] )
                
            
            self.tabEngines.addTab(w , d['name'])
            
        
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , self.create_db )
        self.connect( buttonBox , SIGNAL('rejected()') , self, SLOT('reject()') )
        


    def create_db(self):
        num = self.tabEngines.currentIndex()
        name = dbtypes[num]['name']
        p = self.params[name]
        if name == 'sqlite':
            url = name+':///'+os.path.join(p['dir'], p['name']+'.db')
            print url
            engine = create_engine( url )
            engine.connect()
            self.close()
        
        elif name == 'mysql':
            url = name+'://'+p['adminName']+':'+p['adminPassword']+'@'+p['host']+':'+p['port']+'/'
            engine = create_engine( url )
            try:
                res= engine.execute("CREATE DATABASE `%s`"%(p['dbName']) )
                res= engine.execute("GRANT ALL on `%s`.* TO `%s` " %(p['dbName'] , p['user'] ) )
                self.close()
            except:
                QMessageBox.warning(self,self.tr('Fail'),self.tr("Failed to create a database : check host, user and password"), 
                    QMessageBox.Ok , QMessageBox.NoButton)
        elif name=='postgres':
            import psycopg2
            try:
            
                conn = psycopg2.connect("dbname=template1 user=%s password=%s"%(  p['adminName'], p['adminPassword']))
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                cur.execute('CREATE DATABASE %s OWNER %s' % (p['dbName'],p['user'] ) )
                cur.close()
                conn.close()
            except:
                QMessageBox.warning(self,self.tr('Fail'),self.tr("Failed to create a database : check host, user and password"), 
                    QMessageBox.Ok , QMessageBox.NoButton)
                
            
            self.close()
        
        
        else : 
            self.close()
        
    

