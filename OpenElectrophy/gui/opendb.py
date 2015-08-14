# -*- coding: utf-8 -*-
"""
widget for openning a existing db
"""


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from guiutil.icons import icons
from guiutil.paramwidget import *

from sqlalchemy import create_engine
import os

dbtypes = [
                 {
                'name' :  'mysql',
                'info'  :'To use MySQL, you need a configured server (distant or local)',
                'param' : [
                                    ('host' , { 'value' : '' ,  }   ),
                                    ('port' , { 'value' : '3306' ,  }   ),
                                    ('user' , { 'value' : '' ,  }   ),
                                    ('password' , { 'value' : '' ,  'password' : True}   ),
                                    
                                ],
                'dbNameSelection' : True,
                'icon' : ':/mysql.png',
                },

                {
                'name' :  'sqlite',
                'info'  :'SQLite is a lightweight DB system contained in a single (big) file',
                'param' : [
                                    ('filename' , { 'value' : '' ,  'widgettype' :ChooseFileWidget }   ),
                                ],
                'dbNameSelection' : False,
                'icon' : ':/sqlite.png',
                },
                
                {
                'name' :  'postgresql',
                'info'  :'To use PostgreSql, you need a configured server (distant or local)',
                'param' : [
                                    ('host' , { 'value' : '' ,  }   ),
                                    ('port' , { 'value' : '5432' ,  }   ),
                                    ('user' , { 'value' : '' ,  }   ),
                                    ('password' , { 'value' : '' ,  'password' : True}   ),
                                ],
                'dbNameSelection' : True,
                'icon' : ':/postgres.png',
                },                
                

                ]

class OpenDB(QDialog) :
    """
    """
    def __init__(self  , parent = None ,
                            metadata = None,
                            globalApplicationDict = None,
                            ):
        QDialog.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        
        self.setWindowTitle(self.tr('Open an existing database'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.mainLayout.addWidget(QLabel('Select the appropriate tab for SQL engine'))
        
        self.tabEngines = QTabWidget()
        self.mainLayout.addWidget(self.tabEngines)
        self.params ={ }
        self.combos = { }
        #~ self.buttons = { }
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
            
            self.params[d['name']] = ParamWidget(d['param'] ,
                                                                    keyformemory = d['name']+'/dbconnections',
                                                                    applicationdict = self.globalApplicationDict)
            v.addWidget( self.params[d['name']] )
            if d['dbNameSelection']:
                h = QHBoxLayout()
                v.addLayout(h)
                combo = QComboBox()
                combo.setEditable(True)
                self.combos[d['name']] = combo
                h.addWidget(combo)
                but = QPushButton(QIcon(':/server-database') , 'Get db list')
                h.addWidget(but)
                self.connect(but, SIGNAL('clicked()') , self.get_db_list)
                
                
            self.tabEngines.addTab(w , d['name'])
        
        
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Open| QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , self, SLOT('accept()') )
        self.connect( buttonBox , SIGNAL('rejected()') , self, SLOT('reject()') )
        
    def get_db_list(self):
        num = self.tabEngines.currentIndex()
        name = dbtypes[num]['name']
        combo = self.combos[name]
        if name == 'mysql':
            url = self.half_url()
        else:
            url = self.half_url()+'postgres'
        engine = create_engine( url )
        try:
            if name == 'mysql':
                res= engine.execute('show databases')
            elif name == 'postgresql':
                res= engine.execute('select datname from pg_database')
            
            db_list = []
            for l, in  res.fetchall():
                if l not in [ 'information_schema', 'template1', 'template0', 'postgres']:
                    db_list.append(l)
            combo.clear()
            combo.addItems(db_list)
        except:
            QMessageBox.warning(self,self.tr('Fail'),self.tr("Failed to get list : check host, user and password"), 
                QMessageBox.Ok , QMessageBox.NoButton)

        
        
    def half_url(self):
        num = self.tabEngines.currentIndex()
        name = dbtypes[num]['name']
        p = self.params[name]
        if name == 'mysql':
            url = name+'://'+p['user']+':'+p['password']+'@'+p['host']+':'+p['port']+'/'
        if name == 'postgresql':
            url = name+'://'+p['user']+':'+p['password']+'@'+p['host']+':'+p['port']+'/'
        return url

    def get_url(self):
        num = self.tabEngines.currentIndex()
        name = dbtypes[num]['name']
        
        p = self.params[name]
        if name == 'sqlite':
            url = name+':///'+p['filename']
        elif name == 'mysql':
            url = self.half_url()+self.combos[name].currentText()
        elif name == 'postgresql':
            url = self.half_url()+self.combos[name].currentText()
        else : 
            url = None
        return str(url)

    def get_dict_url(self):
        num = self.tabEngines.currentIndex()
        name = dbtypes[num]['name']
        p = self.params[name]
        d = { }
        if name == 'sqlite':
            d['name'] = os.path.basename(p['filename'])
            d['type'] = 'sqlite'
        elif name == 'mysql':
            d['name'] = self.combos[name].currentText()
            d['type'] = 'mysql'
        elif name == 'postgresql':
            d['name'] = self.combos[name].currentText()
            d['type'] = 'postgresql'
        else : 
            d['name'] = ''
            d['type'] = ''
        print d    
        return d




