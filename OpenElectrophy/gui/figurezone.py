# -*- coding: utf-8 -*-


"""
widget for managing several matplotlib figure
"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
from guiutil.globalapplicationdict import *
from guiutil.paramwidget import ParamDialog, ParamWidget
from enhancedmatplotlib import *

from ..classes import allclasses


class FigureZone(QWidget) :
    """
    Scroll area resazible for stacking matplotlib canvas
    
    """
    def __init__(self  , parent = None ,
                            globalApplicationDict = None,
                            ):
        QWidget.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # expandable scroll area
        widget = QWidget()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(widget)
        self.scrollArea.setWidgetResizable(True)
        
        self.vBoxFig = QVBoxLayout()
        widget.setLayout(self.vBoxFig)
        
        qg = QGridLayout()
        qg.addWidget(self.scrollArea,0,0)
        self.sliderH = QSlider(Qt.Horizontal)
        self.sliderH.setMinimum(50)
        self.sliderH.setMaximum(1000)
        self.sliderH.setValue(200)
        qg.addWidget(self.sliderH,1,0)
        self.connect(self.sliderH,SIGNAL('sliderReleased()'),self.adjustAll)
        self.sliderV = QSlider(Qt.Vertical)
        self.sliderV.setMinimum(50)
        self.sliderV.setMaximum(1000)
        self.sliderV.setValue(250)
        qg.addWidget(self.sliderV,0,1)
        self.connect(self.sliderV,SIGNAL('sliderReleased()'),self.adjustAll)
        
        self.mainLayout.addLayout(qg)
        
        self.listWidgets = [ ]

    def addWidget(self , widget):
        self.vBoxFig.addWidget(widget)
        self.listWidgets.append(widget)
        self.adjustAll()

    def removeOneWidget(self, widget) :
        if widget in self.listWidgets :
            widget.setVisible(False)
            self.vBoxFig.removeWidget(widget)
            self.listWidgets.remove(widget)

    def closeAll(self):
        while  len(self.listWidgets)>0:
            self.removeOneWidget(self.listWidgets[0])

    def adjustAll(self) :
        for w in self.listWidgets :
            w.setMinimumSize(self.sliderH.value() , self.sliderV.value())


class FigureTools(QWidget) :
    """
    """
    def __init__(self  , parent = None ,
                            globalApplicationDict = None,
                            ):
        QWidget.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # Buttons
        but = QPushButton( QIcon(':/office-chart-line.png') , 'Draw selection' )
        self.mainLayout.addWidget(but)
        self.connect(but, SIGNAL('clicked()') , self.drawSelection)
        but.setIconSize(QSize(48, 48))
        
        self.comboStack = QComboBox()
        self.comboStack.addItems(['In separated axes', 'One same axe' ])
        self.mainLayout.addWidget(self.comboStack)
        
        self.comboFigureMode = QComboBox()
        self.comboFigureMode.addItems(['New figure in a stack', 'New figure in a tab' ])
        self.mainLayout.addWidget(self.comboFigureMode)
        
        self.mainLayout.addSpacing(30)
        
        
        but = QPushButton( QIcon(':/tab-new-background.png') , 'Add one tab' )
        self.mainLayout.addWidget(but)
        self.connect(but, SIGNAL('clicked()') , self.addOneTab)
        
        but = QPushButton( QIcon(':/window-close.png') , 'Close all tabs' )
        self.mainLayout.addWidget(but)
        self.connect(but, SIGNAL('clicked()') , self.closeAllTabs)
        
        but = QPushButton( QIcon(':/fileclose.png') , 'Close all figures in current tab' )
        self.mainLayout.addWidget(but)
        self.connect(but, SIGNAL('clicked()') , self.closeAllFigures)
        
        self.mainLayout.addSpacing(30)
        
        # Options
        but = QPushButton( 'Show/Hide options' )
        self.mainLayout.addWidget(but)
        self.connect(but, SIGNAL('clicked()') , self.showHideSlect)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        #~ self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selectPlottingMethods = SelectPlottingMethods(  globalApplicationDict = globalApplicationDict,)
        self.selectPlottingMethods.updateGeometry()
        
        self.scrollArea.setMinimumWidth(self.selectPlottingMethods.sizeHint().width()+30)
        #~ self.scrollArea.setMinimumWidth(self.selectPlottingMethods.minimumWidth())
        self.scrollArea.setWidget(  self.selectPlottingMethods ) 
        self.mainLayout.addWidget( self.scrollArea ,1) 
        
        self.mainLayout.addStretch(0)
        
        self.createAction()
        
        self.dockFigures = [ ]
        self.nFigZone = 0
    
    def createAction(self):
        self.actionDrawSelection = QAction(self.tr("&Draw selection"), self)
        self.actionDrawSelection.setShortcut(self.tr("D"))
        self.actionDrawSelection.setIcon(QIcon(':/office-chart-line.png'))
        self.connect(self.actionDrawSelection, SIGNAL("triggered()"), self.drawSelection)
        
        self.actionAddOneTab = QAction(self.tr("Add one tab"), self)
        self.actionAddOneTab.setIcon(QIcon(':/tab-new-background.png'))
        self.actionAddOneTab.setShortcut(self.tr("Ctrl+T"))
        self.connect(self.actionAddOneTab, SIGNAL("triggered()"), self.addOneTab)        
        
        self.actionCloseAllTabs = QAction(self.tr("Close all tabs"), self)
        self.actionCloseAllTabs.setIcon(QIcon(':/window-close.png'))
        self.connect(self.actionCloseAllTabs, SIGNAL("triggered()"), self.closeAllTabs)

        self.actionCloseAllFigures = QAction(self.tr("Close all figures in current tab"), self)
        self.actionCloseAllFigures.setIcon(QIcon(':/fileclose.png'))
        self.connect(self.actionCloseAllFigures, SIGNAL("triggered()"), self.closeAllFigures)

    def getAllActions(self):
        all = [self.actionDrawSelection,
                self.actionAddOneTab,
                self.actionCloseAllTabs,
                self.actionCloseAllFigures,
                ]
        
        return all
    
    def showHideSlect(self):
        if self.scrollArea.isHidden():
            self.scrollArea .show()
        else:
            self.scrollArea .hide()
        
    def addOneTab(self):
        self.nFigZone +=1
        mainWin = self.parent().parent()
        
        dockFigureZone = QDockWidget('Figure tools%d'%self.nFigZone , self)
        dockFigureZone.setAllowedAreas(Qt.AllDockWidgetAreas)
        figureZone = FigureZone(globalApplicationDict = self.globalApplicationDict)
        dockFigureZone.setWidget(figureZone)
        dockFigureZone.setObjectName('Figure zone %d'%self.nFigZone)
        #~ figureZone.setMinimumSize(QSize(100,100))
        mainWin.addDockWidget(Qt.RightDockWidgetArea, dockFigureZone)
        figureZone.setMinimumSize(QSize(600,500))
        
        self.dockFigures.append( dockFigureZone )
        for i in range(1,len(self.dockFigures)):
            mainWin.tabifyDockWidget(self.dockFigures[0] , self.dockFigures[i])
            #FIXME last widget on top
        
        return figureZone
        
    def closeAllTabs(self):
        mainWin = self.parent().parent()
        for dock in self.dockFigures:
            mainWin.removeDockWidget(dock)
        self.dockFigures = [ ]
        
    def closeAllFigures(self):
        if len(self.dockFigures)==0: return
        figureZone = self.dockFigures[-1].widget()
        figureZone.closeAll()
        
    def closeOneFigure(self):
        canvas =  self.sender()
        for dockFigure in self.dockFigures:
            figureZone = dockFigure.widget()
            if canvas in figureZone.listWidgets :
                figureZone.removeOneWidget(canvas)
        
    def drawSelection(self):
        mainWin = self.parent().parent()
        explorer = mainWin.getCurrentExporer()
        treeview = explorer.getCurrentSqlTreeView()
        
        for ob in treeview.getSelectedObject():
            
            plotNames = self.selectPlottingMethods.getSelectedMethods(ob.tablename)
            for plotName in plotNames:
                
                if self.comboFigureMode.currentText() == 'New figure in a tab' or len(self.dockFigures)==0:
                    # add a tab
                    self.addOneTab()
                figureZone = self.dockFigures[-1].widget()
                
                plotInfo = dict(ob.plotAptitudes)[plotName]
                
                if plotInfo['ax_needed'] ==1 :
                    if self.comboStack.currentText() == 'In separated axes':
                        # add a canvas
                        canvas = SimpleCanvasAndTool(orientation = Qt.Vertical , close_button = True)
                        self.connect(canvas, SIGNAL('want_to_be_closed'), self.closeOneFigure)
                        ax = canvas.fig.add_subplot(1,1,1)
                        figureZone.addWidget(canvas)
                    elif  self.comboStack.currentText() == 'One same axe' :
                        if len(figureZone.listWidgets)==0:
                            canvas = SimpleCanvasAndTool(orientation = Qt.Vertical , close_button = True)
                            self.connect(canvas, SIGNAL('want_to_be_closed'), self.closeOneFigure)
                            ax = canvas.fig.add_subplot(1,1,1)
                            figureZone.addWidget(canvas)
                        canvas = figureZone.listWidgets[-1]
                        ax = canvas.fig.get_axes()[0]
                    
                    # apply plot function
                    plotOptions = self.selectPlottingMethods.getPlotOptions(ob.tablename , plotName)
                    func = getattr(ob , 'plot_'+plotName)
                    func( ax=ax, **plotOptions)
                    canvas.draw()
                    
                
                if plotInfo['fig_needed'] ==1 :
                    # add a canvas
                    canvas = SimpleCanvasAndTool(orientation = Qt.Vertical , close_button = True)
                    self.connect(canvas, SIGNAL('want_to_be_closed'), self.closeOneFigure)
                    figureZone.addWidget(canvas)
                    
                    # apply plot function
                    plotOptions = self.selectPlottingMethods.getPlotOptions(ob.tablename , plotName)
                    func = getattr(ob , 'plot_'+plotName)
                    func( fig = canvas.fig, **plotOptions)
                    canvas.draw()
                    
                    
                    
                
                
        




class SelectPlottingMethods(QWidget) :
    """
    """
    def __init__(self  , parent = None ,
                            globalApplicationDict = None,
                            ):
        QWidget.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        gd = QGridLayout()
        self.mainLayout.addLayout(gd)
        self.plotParams = { }
        self.checkBoxes = {}
        self.optButtons = { }
        l=0
        for  tablename , OEclass in  allclasses.iteritems():
            if hasattr(OEclass, 'plotAptitudes'):
                lab = QLabel()
                lab.setPixmap( QIcon(':/'+ tablename+'.png').pixmap(32,32))
                gd.addWidget(lab,l,0)
                gd.addWidget(QLabel(tablename), l, 1,)
                self.checkBoxes[tablename]={}
                self.plotParams[tablename]={}
                l+=1
                for plotName, d in OEclass.plotAptitudes :
                    cb = QCheckBox(plotName)
                    if d['default_selected']:
                        cb.setChecked(True)
                    self.checkBoxes[tablename][plotName] = cb
                    self.plotParams[tablename][plotName] =  ParamWidget(d['params']).get_dict()
                    gd.addWidget(cb , l,1, )
                    but = QPushButton(QIcon(':/preferences-system.png'),'Options')
                    gd.addWidget(but , l,2, )
                    self.connect(but , SIGNAL('clicked()'), self.openOptions)
                    self.optButtons[but] = [ tablename, plotName]
                    l+=1
    
    def getSelectedMethods(self, tablename):
        l = [ ]
        for k, v in self.checkBoxes[tablename].iteritems():
            if v.isChecked():
                l.append(k)
                
        return l
        
        
    def getPlotOptions(self, tablename, plotName):
        return self.plotParams[tablename][plotName]
    
    
    def openOptions(self):
        tablename, plotName =  self.optButtons[self.sender()]
        params = dict(allclasses[tablename].plotAptitudes)[plotName]['params']
        d = ParamDialog(params,
                                    keyformemory = 'plotOptions/'+plotName , 
                                    applicationdict = self.globalApplicationDict,
                                    )
        d.update(self.plotParams[tablename][plotName])
        if d.exec_():
            self.plotParams[tablename][plotName] = d.get_dict()





