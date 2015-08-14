# -*- coding: utf-8 -*-
"""
widget for creating a db
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os


from guiutil.icons import icons
from guiutil.globalapplicationdict import GlobalApplicationDict,get_working_dir
from createdb import CreateDB
from opendb import OpenDB
from explorer import MainExplorer
from importdata import ImportData
from tabledesign import TableDesign
from figurezone import FigureTools

from ..sqlmapper import open_db

if __name__ == '__main__' :
    app = QApplication(sys.argv)

    
class MainWindow(QMainWindow) :
    def __init__(self, parent = None,
                applicationname = 'OpenElectrophy_0_2',
                ) :
        QMainWindow.__init__(self, parent)
        
        
        self.globalApplicationDict = GlobalApplicationDict(applicationname=applicationname)
        self.applicationname = applicationname
        
        
        self.setWindowTitle(self.tr('OpenElectrophy'))
        self.setWindowIcon(QIcon(':/openelectrophy.png'))
        self.setMinimumSize(600,400)
        
        self.tabDatabases = QTabWidget()
        self.setCentralWidget(self.tabDatabases)
        self.setDockNestingEnabled(True)

        # dock figure tools
        self.figureTools = FigureTools(globalApplicationDict = self.globalApplicationDict)
        self.dockFigureTools = QDockWidget('Figure tools' , self)
        self.dockFigureTools.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockFigureTools.setWidget(self.figureTools)
        self.dockFigureTools.setObjectName('Figure tools')
        self.dockFigureTools.setFeatures(QDockWidget.DockWidgetMovable| QDockWidget.DockWidgetFloatable)# | QDockWidget.DockWidgetVerticalTitleBar )
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockFigureTools)
        self.figureTools.setEnabled( False )


        self.createActions()
        self.createMenus()
        #self.createToolBars()



        self.openedDatabases = [ ]
        
    def createActions(self):
        self.actionCreateDb = QAction(self.tr("&Create a new database"), self)
        self.actionCreateDb.setShortcut(self.tr("Ctrl+C"))
        self.actionCreateDb.setIcon(QIcon(':/create-db.png'))
        self.connect(self.actionCreateDb, SIGNAL("triggered()"), self.createDatabase)

        self.actionOpenDb = QAction(self.tr("&Open a database"), self)
        self.actionOpenDb.setShortcut(self.tr("Ctrl+O"))
        self.actionOpenDb.setIcon(QIcon(':/open-db.png'))
        self.connect(self.actionOpenDb, SIGNAL("triggered()"), self.openDatabase)
        
        self.actionImport = QAction(self.tr("&Import data in this db"), self)
        self.actionImport.setShortcut(self.tr("Ctrl+I"))
        self.actionImport.setIcon(QIcon(':/svn-update.png'))
        self.connect(self.actionImport, SIGNAL("triggered()"), self.importData)
        
        self.actionTableDesign = QAction(self.tr("&Modify database schema (table design)"), self)
        self.actionTableDesign.setIcon(QIcon(':/vcs_diff.png'))
        self.connect(self.actionTableDesign, SIGNAL("triggered()"), self.openTableDesign)
        

        self.quitAct = QAction(self.tr("&Quit"), self)
        self.quitAct.setShortcut(self.tr("Ctrl+Q"))
        self.quitAct.setStatusTip(self.tr("Quit the application"))
        self.quitAct.setIcon(QIcon(':/window-close.png'))
        self.connect(self.quitAct, SIGNAL("triggered()"), self.close)

        self.aboutAct = QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.aboutAct.setIcon(QIcon(':/help-about.png'))
        self.connect(self.aboutAct,SIGNAL("triggered()"), self.about)

        self.helpAct = QAction(self.tr("&Help"), self)
        self.helpAct.setStatusTip(self.tr("Help"))
        self.helpAct.setIcon(QIcon(':/help-contents.png'))
        self.connect(self.helpAct,SIGNAL("triggered()"), self.openHelp)




    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(self.tr("&Database"))
        self.fileMenu.addAction(self.actionCreateDb)
        self.fileMenu.addAction(self.actionOpenDb)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actionImport)
        self.fileMenu.addAction(self.actionTableDesign)
        
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.menuBar().addSeparator()
        self.figureMenu = self.menuBar().addMenu(self.tr("&Figure"))
        for act in self.figureTools.getAllActions():
            self.figureMenu.addAction(act)
        #~ self.openFigureMenu = self.figureMenu.addMenu(self.tr("Opened Figures"))
        
        self.figureMenu.setEnabled(False)
        
        self.menuBar().addSeparator()
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.helpAct)
        

    def createDatabase(self):
        d = CreateDB(parent = self,globalApplicationDict =self.globalApplicationDict)
        d.exec_()
        
        
    
    def openDatabase(self):
        """Creates OpenDB opbject and then opens database from choice"""
        d = OpenDB(parent = self,globalApplicationDict =self.globalApplicationDict)
        self.openDatabaseFromOpenDB(d)
    
    def openDatabaseFromOpenDB(self, d):
        """Actually open a database, given OpenDB-like object.
        
        startOpenElectrophy.py may mimic an OpenDB object for opening
        from command line.
        """
        if d.exec_():
            url = d.get_url()
            dbname = d.get_dict_url()['name']
            dbtype = d.get_dict_url()['type']
            try:
                metadata = open_db( url = url)
            except:
                QMessageBox.warning(self,self.tr('Fail'),self.tr("Fail to open database."), 
                    QMessageBox.Ok , QMessageBox.NoButton)
                return
            explorer = MainExplorer(metadata = metadata , 
                                    globalApplicationDict = self.globalApplicationDict,
                                    )
            
            database = {    'dbname' : dbname,
                                    'dbtype' : dbtype, 
                                    'explorer' : explorer,
                                    'metadata' : metadata,
                                }
            
            # only one database for the moment:
            if self.tabDatabases.count()==1:
                self.tabDatabases.removeTab(0)
                self.openedDatabases = [ ]
            
            self.openedDatabases.append(database )
            self.tabDatabases.addTab( explorer , dbname)
            
            self.figureTools.setEnabled( True )
            self.figureMenu.setEnabled(True)
    
    def getCurrentExporer(self):
        num = self.tabDatabases.currentIndex()
        explorer = self.openedDatabases[num]['explorer']
        return explorer
            
    def importData(self):
        d = ImportData(globalApplicationDict = self.globalApplicationDict,
                                session = self.getCurrentExporer().session,
                                )
        
        if d.exec_():
            self.getCurrentExporer().refresh( )
    

    def openTableDesign(self):
        d = TableDesign(metadata =self.getCurrentExporer().metadata,
                                    session = self.getCurrentExporer().session,
                                    explorer = self.getCurrentExporer(),
                                    )        
        d.exec_()
    
    
    def about(self):
        QMessageBox.about(self, self.tr("About Dock Widgets"),
                    self.tr("""<b>OpenElectrophy</b> : <BR/>
                    A all-in-one GUI+toolbox+datastorage+framework<BR/>
                    for analysing extra or intra cellular data, dev by<BR/>
                    <b>Samuel GARCIA</b>, <BR/>
                    in Neurosciences Sensorielles, Comportement, Cognition. CNRS, Lyon, France
                    """
                    ))

    def openHelp(self):
        from PyQt4.QtWebKit import QWebView
        
        if not hasattr(self, 'helpview'):
            self.helpview = QWebView()
            self.helpview.setWindowFlags(Qt.SubWindow)
            self.helpview.load(QUrl('http://packages.python.org/OpenElectrophy/index.html'))
        
        self.helpview.setVisible(True)
        

if __name__ == '__main__' :
	MainWindow
	
	

	mw =MainWindow()
	mw.show()
	
	
	sys.exit(app.exec_())