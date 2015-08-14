# -*- coding: utf-8 -*-


"""

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.paramwidget import ParamWidget, LimitWidget, ParamDialog
from guiutil.multiparamwidget import WidgetMultiMethodsParam
import numpy
from numpy import inf, zeros, ones, unique, mean, std,median,  arange, where, ceil, sqrt, diff, concatenate, amax, amin, histogram, random, array

from OpenElectrophy.classes import *
from OpenElectrophy.computing.spikesorting import spikesorter, filtering, detection, extraction, feature, clustering

from spikesortingwidgets import spikesortingwidgets


import time

#OK:
# global interaction with selection for selection
# context menu
# dock closed remove from list
# refresh all
# save all
# regroup small cluster
# better template for widget organization
# amplitude signal temps
# signal histogram
# icon for plots
# bug threshold
# revoir les random
# ndviewer random point
# ndviewer point size
# Control speed refreshement
# param widgets
# add channel to neuron
# name and note neurons
# Summary size
# signal streamer zoom
# nd viewer when refresh keep projection
# signal streamer step popup
# ndviewer bug lasso 
# hide a cluster


# TODO LIST:
# nd viewer optimized tour avec subset
# nd viewer selection avec subset
# spike list slow problems
# up and down for clusters
# thread for all widgets refresh
# spikesorter get neurons when present from_full_band
# method features : max relative amplitude
# memory of last parameters
# zoom with mouse on signal streamer
# mouse action on 3D viewer
# snapshot on ND viewer
# multi select with CTRL






class SpikeSorting(QMainWindow):
    def __init__(self  , parent = None ,
                            metadata =None,
                            session = None,
                            Session = None,
                            globalApplicationDict = None,

                            mode = None,
                            tablename = None,
                            id_recordingpoint = None,
                            
                            
                            ):
        QMainWindow.__init__(self, parent)
        

        
        
        
        
        
        
        #~ self.setWindowFlags(  Qt.Dialog)
        self.metadata = metadata
        self.globalApplicationDict = globalApplicationDict
        
        #self.setWindowTitle( 'Spike sorting for recordingpoint %d' % id_recordingpoint )
        
        self.setAnimated(False)
        
        self.Session = Session
        self.session = Session
        
#        self.session = Session()
        self.mode = mode
        
        # recording point in the same group
        recordingPoint = self.session.query(RecordingPoint).filter_by(id=id_recordingpoint).one()
        
        # Window title
        self.setWindowTitle((
            'Spike sorting for recordingpoint id=%d channel=%s group=%s' 
            % (id_recordingpoint, str(recordingPoint.channel), 
            str(recordingPoint.group))))
        
        # look for recording point with same group
        if recordingPoint.group is not None :
            query = self.session.query(RecordingPoint)
            query = query.filter(RecordingPoint.id_block == recordingPoint.id_block )
            query = query.filter(RecordingPoint.group == recordingPoint.group )
            query = query.order_by(RecordingPoint.id)
            rPointListNonSorted = [  ]
            recordingPointList = [  ]
            ids = [ ]
            for rp in query.all() :
                rp.metadata = metadata
                rPointListNonSorted.append( rp )
                ids.append( rp.id )
            ind = numpy.argsort( ids)
            for i in ind :
                recordingPointList.append( rPointListNonSorted[i] )
        else :
            recordingPointList = [ recordingPoint ]
        
        self.spikesorter = spikesorter.SpikeSorter( mode = mode,
                                                session = self.session,
                                                recordingPointList = recordingPointList,
                                                )

        
        # Compute steps widget
        #TEST3
        self.toolboxSteps = QToolBox()
        dock = QDockWidget('Steps',self)
        dock.setWidget(self.toolboxSteps)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.toolboxSteps.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        
        #TEST 2
        #~ w = QWidget()
        #~ w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #~ v = QVBoxLayout()
        #~ w.setLayout(v)
        #~ self.toolboxSteps = QToolBox()
        #~ v.addWidget(self.toolboxSteps)
        #~ self.setCentralWidget(w)
        #~ w.setMaximumSize(300,600)
        
        
        # TEST 1
        #~ self.toolboxSteps = QToolBox()
        #~ self.setCentralWidget(self.toolboxSteps)
        #~ self.toolboxSteps.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.hboxes = { }
        self.vboxes = { }
        self.widgetMultimethods = { }
        self.buttonCompute = { }
        s = 0
        for name, module,  in spikesorter.steps:
            w = QWidget()
            self.toolboxSteps.addItem(w,QIcon(':/'+name+'.png'), name)
            h= QHBoxLayout()
            self.hboxes[name] = h
            w.setLayout(h)
            
            v = QVBoxLayout( )
            h.addLayout( v )
            self.vboxes[name] = v
            wMeth = WidgetMultiMethodsParam(  list_method = module.list_method,
                                                                method_name = '<b>Choose method for %s</b>:'%name,
                                                                globalApplicationDict = self.globalApplicationDict,
                                                                keyformemory = 'spikesorting',
                                                                )
            self.widgetMultimethods[name] = wMeth
            v.addWidget(wMeth)
            v.addStretch(0)
            but = QPushButton('Compute %s'%name)
            v.addWidget(but)
            self.buttonCompute[name] = but
            but.clicked.connect(self.computeAStep)
            but.stepNum = s
            but.setEnabled(name in spikesorter.mode_steps[self.mode])
            s += 1
            
        
        if self.mode == 'from_full_band_signal':
            self.toolboxSteps.setCurrentIndex(0)
        elif self.mode == 'from_filtered_signal':
            self.toolboxSteps.setCurrentIndex(1)
        elif self.mode == 'from_detected_spike':
            self.toolboxSteps.setCurrentIndex(3)

        
        
        # dockable area for plottings
        self.setDockNestingEnabled(True)
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Menu for view template
        #but =  QToolButton( 	popupMode = QToolButton.InstantPopup, toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        but =  QToolButton( )
        but.setPopupMode( QToolButton.InstantPopup )
        but.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.addWidget(but)
        but.setIcon(QIcon(':/view-choose.png' ) )
        but.setText('Views template')
        
        self.templateNames =['Best', 'Good ensemble', 'Nothing', 'One cell', 'Manual clustering', 'Detection', 'Before to save', 'Controls']
        self.list_actTemplate = [ ]
        for name in self.templateNames:
            act = QAction(name,but)
            act.setCheckable(True)
            self.list_actTemplate.append(act)
            but.addAction(act)
            act.triggered.connect( self.templateChanged)
        
        # Menu for selecting view
        #but =  QToolButton( 	popupMode = QToolButton.InstantPopup, toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        but =  QToolButton( )
        but.setPopupMode( QToolButton.InstantPopup )
        but.setToolButtonStyle( Qt.ToolButtonTextBesideIcon)
        self.toolbar.addWidget(but)
        but.setIcon(QIcon(':/plot.png' ) )
        but.setText('Select displayed plots')
        
        self.list_actionView = [ ]
        self.list_widget = [ ]
        self.list_dock = [ ]
        for W in spikesortingwidgets:
            # Menu
            act = QAction(W.name,but)
            act.setCheckable(True)
            self.list_actionView.append(act)
            if hasattr(W, 'icon_name'):
                act.setIcon(QIcon(':/'+W.icon_name))
            but.addAction(act)
            act.triggered.connect( self.selectPlotChanged)
            
            # Widget and dock
            w = W( spikesorter = self.spikesorter , globalApplicationDict= self.globalApplicationDict, )
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            dock = QDockWidget(W.name,self)
            dock.setObjectName(  W.name )
            dock.setWidget(w)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            self.list_dock.append(dock)
            self.list_widget.append(w)
            
            self.connect(w, SIGNAL('SpikeLabelsChanged'), self.spikeLabelsChanged)
            self.connect(w, SIGNAL('SpikeSelectionChanged'), self.spikeSelectionChanged)
            self.connect(w, SIGNAL('SpikeSubsetChanged'), self.spikeSubsetChanged)
            dock.visibilityChanged.connect(self.oneDockVisibilityChanged)
            
                
        self.toolbar.addSeparator()
        
        #but =  QToolButton( toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        but =  QToolButton()
        but.setToolButtonStyle( Qt.ToolButtonTextBesideIcon)
        self.toolbar.addWidget(but)
        but.setIcon(QIcon(':/view-refresh.png' ) )
        but.setText('Refresh all')
        but.clicked.connect(self.refreshAll)
        
        #but =  QToolButton( toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        but =  QToolButton()
        but.setToolButtonStyle( Qt.ToolButtonTextBesideIcon)
        self.toolbar.addWidget(but)
        but.setIcon(QIcon(':/roll.png' ) )
        but.setText('Sample subset n=')
        but.clicked.connect(self.sampleSubset)
        but.clicked.connect(self.refreshAll)
        
        #self.spinboxSubsetLimit = QSpinBox( minimum = 0 , maximum =  1e9, specialValueText = "All", singleStep = 500, )
        self.spinboxSubsetLimit = QSpinBox( )
        self.spinboxSubsetLimit.setMinimum( 0 )
        self.spinboxSubsetLimit.setMaximum (  1e9 )
        self.spinboxSubsetLimit.setSpecialValueText( "All" )
        self.spinboxSubsetLimit.setSingleStep( 500 )
        self.spinboxSubsetLimit.setValue(5000)
        self.toolbar.addWidget(self.spinboxSubsetLimit)
        
        
        self.toolbar.addSeparator()
        
        #but =  QToolButton( toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        but =  QToolButton( )
        but.setToolButtonStyle( Qt.ToolButtonTextBesideIcon)
        self.toolbar.addWidget(but)
        but.setIcon(QIcon(':/document-save.png' ) )
        but.setText('Save to db')
        but.clicked.connect(self.save)
        
        
        
        
        self.changeTemplate(self.templateNames[0])
        self.refreshAll( )

    def closeEvent(self, event):
        self.session.expunge_all()
        self.session.close()
        del self.spikesorter
        event.accept()

    ## PLOT, COLOR AND SELECTION
    def refreshAll(self, shuffle = True):
        self.spikesorter.refreshColors()
        if shuffle:
            self.sampleSubset()
        import time
        for w,dock in zip(self.list_widget, self.list_dock):
            if dock.isVisible():
                t1 = time.time()
                w.refresh()
                t2 = time.time()
                print 'refresh ', w.name, t2-t1
    
    def spikeSubsetChanged(self):
        self.refreshAll( shuffle = False)
    
    def sampleSubset(self):
        val = self.spinboxSubsetLimit.value()
        if val == 0: val = numpy.inf
        self.spikesorter.refreshShuffle(max_size_by_cluster = val)

    def spikeLabelsChanged(self):
        self.spikesorter.refreshColors()
        self.sampleSubset()
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender(): continue
            if dock.isVisible() and 'Clustering' in w.refresh_on:
                w.refresh()
        
        self.spikeSelectionChanged( numpy.array([ ],'i') )
    
    def spikeSelectionChanged(self, ind):
        #~ print 'in spikeSelectionChanged spikesorting'
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender():
                #~ print 'sender'
                continue
            if dock.isVisible() and hasattr(w, 'setSpikeSelection'):
                w.setSpikeSelection(ind)
        
    
    ## COMPUTE
    def computeAStep(self,):
        but = self.sender()
        num = but.stepNum
        name, _ = spikesorter.steps[num]
        self.actualCompute = name
        self.computeNum = num
        self.computeName = name
        
        # Disable other button
        for  but in self.buttonCompute.itervalues():
            but.setEnabled(False)
        
        # Timer and flash
        #self.timerFlash = QTimer( 	singleShot = False , interval = 500)
        self.timerFlash = QTimer( )
        self.timerFlash.setSingleShot( False )
        self.timerFlash.setInterval( 500)
        
        self.timerFlash.timeout.connect(self.flashCompute)
        self.boolFlash = True
        pix = QPixmap(64,64 )
        pix.fill( QColor('red'))
        self.redIcon = QIcon(pix)
        self.timerFlash.start()
        
        
        self.startCompute = time.time()
        
        method_class = self.widgetMultimethods[name].get_method()
        kargs = self.widgetMultimethods[name].get_dict()
        self.threadCompute = ThreadCompute(self, self.spikesorter, name, method_class, **kargs)
        self.threadCompute.finished.connect(self.computeTerminated)
        self.threadCompute.start(QThread.LowestPriority)


    def computeTerminated(self):
        self.stopCompute = time.time()
        print 'compute', self.actualCompute,  self.stopCompute - self.startCompute
        
        #stop flash
        self.timerFlash.stop()
        self.boolFlash = True
        self.flashCompute( )
        
        for  name,but in self.buttonCompute.iteritems():
            but.setEnabled(name in spikesorter.mode_steps[self.mode])
        
        self.spikesorter.refreshColors()
        self.sampleSubset()
        
        for w,dock in zip(self.list_widget, self.list_dock):
            if dock.isVisible():
                w.refresh(step = self.actualCompute)
    
    def flashCompute(self):
        self.boolFlash = not(self.boolFlash)
        if self.boolFlash:
            self.toolboxSteps.setItemIcon(self.computeNum, self.redIcon)
        else:
            self.toolboxSteps.setItemIcon(self.computeNum, QIcon(':/'+self.computeName+'.png'))
    
    
    ## DOCK AND TEMPLATE
    def oneDockVisibilityChanged(self):
        dock = self.sender()
        i = self.list_dock.index(dock)
        self.list_actionView[i].setChecked(dock.isVisible())
    
    
    def selectPlotChanged(self):
        act = self.sender()
        i = self.list_actionView.index(act)
        if act.isChecked():
            # TODO position of dock
            self.list_dock[i].setVisible(True)
            self.list_widget[i].refresh()
        else:
            self.list_dock[i].setVisible(False)
        
    
    def templateChanged(self):
        act = self.sender()
        i = self.list_actTemplate.index(act)
        for a in self.list_actTemplate: a.setChecked(False)
        act.setChecked(True)
        
        self.changeTemplate(self.templateNames[i])
    
    def changeTemplate(self, name = None):
        
        # hide all
        for dock in self.list_dock:
            dock.setVisible(False)
        
        dWidget = dict( [ (w.name, w) for w in self.list_widget] )
        dDock = dict( [ (self.list_widget[i].name, self.list_dock[i]) for i in range(len(self.list_widget)) ]  ) 
        dAct = dict( [ (self.list_widget[i].name, self.list_actionView[i]) for i in range(len(self.list_widget)) ]  ) 
        
        
        if name == 'Best':
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Full band signal'] , )
            dDock['Full band signal'].setVisible(True)
            dDock['Unit list'].setVisible(True)
            self.splitDockWidget(dDock['Full band signal'], dDock['Unit list'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)            
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Horizontal)
            self.tabifyDockWidget ( dDock['Full band signal'], dDock['Filtered signal'])
            dDock['Filtered signal'].setVisible(True)
            
            dDock['Features NDViewer'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Features NDViewer'] , )
            #self.splitDockWidget(dDock['Unit list'], dDock['Features NDViewer'], Qt.Horizontal)
        
        elif name == 'Good ensemble':
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Full band signal'] , )
            dDock['Full band signal'].setVisible(True)
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Full band signal'], dDock['Waveforms'], Qt.Horizontal)
            dDock['Cross-correlogram'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Cross-correlogram'], Qt.Horizontal)
            self.tabifyDockWidget ( dDock['Full band signal'], dDock['Filtered signal'])
            dDock['Filtered signal'].setVisible(True)

            dDock['Unit list'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Unit list'] , )
            dDock['Features NDViewer'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Features NDViewer'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Vertical)

        elif name == 'Nothing':
            pass
        
        elif name == 'One cell':
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Full band signal'] , )
            dDock['Full band signal'].setVisible(True)
            self.splitDockWidget(dDock['Full band signal'], dDock['Filtered signal'], Qt.Vertical)
            dDock['Filtered signal'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Spike list'] , )
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Spike list'], dDock['Waveforms'], Qt.Horizontal)
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Average waveforms'], Qt.Horizontal)
            dDock['Average waveforms'].setVisible(True)
                        
            
        elif name == 'Manual clustering':
            
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Waveforms'] , )
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Average waveforms'], Qt.Horizontal)
            dDock['Average waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Average waveforms'], dDock['Features Parallel Plot'], Qt.Horizontal)
            dDock['Features Parallel Plot'].setVisible(True)
            self.splitDockWidget(dDock['Features Parallel Plot'], dDock['Features 3D'], Qt.Horizontal)
            dDock['Features 3D'].setVisible(True)
            self.splitDockWidget(dDock['Features 3D'], dDock['Features Wilson Plot'], Qt.Horizontal)
            dDock['Features Wilson Plot'].setVisible(True)
            
            dDock['Unit list'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Unit list'] , )
            dDock['Features NDViewer'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Features NDViewer'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Vertical)
            
        elif name == 'Detection':
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Filtered signal'] , )
            dDock['Filtered signal'].setVisible(True)
            self.splitDockWidget(dDock['Filtered signal'], dDock['Average waveforms'], Qt.Vertical)
            dDock['Average waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Average waveforms'], dDock['Waveforms'], Qt.Horizontal)
            dDock['Waveforms'].setVisible(True)
            self.tabifyDockWidget ( dDock['Filtered signal'], dDock['Full band signal'])
            dDock['Full band signal'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Signal statistics'], Qt.Horizontal)
            dDock['Signal statistics'].setVisible(True)


            
        elif name == 'Before to save':
            dDock['Unit list'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Unit list'] , )
            dDock['Summary'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Summary'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Vertical)
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Summary'], dDock['Waveforms'], Qt.Vertical)

        elif name == 'Controls':
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Cross-correlogram'] , )
            dDock['Cross-correlogram'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Interval Inter Spike'] , )
            dDock['Interval Inter Spike'].setVisible(True)            
        
        
        self.refreshAll()
        

        
    def save(self):
        params = [   [ 'save_waveform' , {'value' :'save filtered waveform' , 'label' : 'Save waveform in database',
                                                                    'possible' : ['save filtered waveform','do not save' ,  'save natural waveform' ] }],
                            [ 'spiketrain_mode' , {'value' :'standalone' , 'label' : 'SpikeTrain mode (container = spike table, standalone = more efficient)',
                                                                    'possible' : ['standalone','container' ] }],
                            [ 'save_trash' , {'value' : True , 'label' : 'Save spike in trash', } ],
                            [ 'create_empty' , {'value' : True , 'label' : 'If no spikes have been detected, create an empty neuron', } ],
                            
                            
                        ]
        d =  ParamDialog(params,
                                    applicationdict = self.globalApplicationDict,
                                    keyformemory = 'spikesorting/databaseoptions'  ,
                                    title = 'database options',
                                    )
        if d.exec_():
            try:
                self.spikesorter.save_to_db(**d.get_dict())
            except:
                warn = """A problem occured during saving to db..."""
                mb = QMessageBox.warning(self,self.tr('Save'),self.tr(warn), 
                        QMessageBox.Ok ,)
                 
    


class ThreadCompute(QThread):
    def __init__(self, parent, spikesorter, stepName,  classMethod, **kargs):
        QThread.__init__(self, parent)
        self.spikesorter = spikesorter
        self.stepName = stepName
        self.classMethod = classMethod
        self.kargs = kargs
    
    def run(self):
        #~ print 'start run', self.stepName
        getattr( self.spikesorter , 'compute%s'%self.stepName)( self.classMethod, **self.kargs)
        #~ time.sleep(4)
        #~ print 'end run', self.stepName
        




