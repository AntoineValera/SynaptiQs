# -*- coding: utf-8 -*-


"""

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
#~ from guiutil.globalapplicationdict import *
from guiutil.paramwidget import ParamWidget, LimitWidget, ParamDialog
from guiutil.multiparamwidget import WidgetMultiMethodsParam
from enhancedmatplotlib import *
import numpy
from numpy import inf, zeros, ones, unique, mean, std,median,  arange, where, ceil, sqrt, diff, concatenate, amax, amin, histogram, random, array

from OpenElectrophy.classes import *
from OpenElectrophy.computing.spikesorting import filtering, detection, extraction, feature, clustering

#~ from ..classes import allclasses, Oscillation
#~ from ..computing.timefrequency import LineDetector, PlotLineDetector
from enhancedmatplotlib import SimpleCanvasAndTool,  SimpleCanvas
from spikeplotutilities import PlotWaveform, PlotISI, PlotCrossCorrelogram



#~ from sqlalchemy import and_, or_
from matplotlib.colors import ColorConverter
from matplotlib.cm import get_cmap

from mpl_toolkits.mplot3d import Axes3D
from ndviewer import NDViewer



#~ colors = [ 'c' , 'g' , 'r' , 'b' , 'k' , 'm' , 'y']*100




class WidgetFiltering(QWidget):
    """
    widget to plot the filtering
    """
    def __init__(self , parent=None ,):
        QWidget.__init__(self,parent )
        
        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.canvas = SimpleCanvasAndTool(orientation = Qt.Horizontal )
        mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
        self.ax1 = self.fig.add_subplot(2,1,1)
        self.ax2 = self.fig.add_subplot(2,1,2, sharex = self.ax1)
        
        # plot non filtered
        anaSigList = self.spikeSortingWin.tab.anaSigList
        trodness = self.spikeSortingWin.tab.trodness
        sr = self.spikeSortingWin.tab.sampling_rate
        self.ax1.clear()
        t_start = 0.
        for i in range(len(anaSigList)):
            self.ax1.axvline(t_start, color = 'r')
            for j in range(trodness):
                #~ print anaSigList[i][j].signal
                t = arange(anaSigList[i][j].signal.size, dtype='f')/sr + t_start
                self.ax1.plot(t, anaSigList[i][j].signal , color = 'b')
            t_start += anaSigList[i][0].signal.size/sr
        self.canvas.draw()
        
        self.lastFilteredSignal = None
        
        
    def refresh(self):
        
        
        
        anaSigList = self.spikeSortingWin.tab.anaSigList
        trodness = self.spikeSortingWin.tab.trodness
        sr = self.spikeSortingWin.tab.sampling_rate        
        anaSigFilteredList = self.spikeSortingWin.tab.anaSigFilteredList
        if anaSigFilteredList is None : return
        if self.lastFilteredSignal == anaSigFilteredList[0][0]: return 
        self.ax2.clear()
        
        t_start = 0.
        for i in range(len(anaSigList)):
            self.ax2.axvline(t_start, color = 'r')
            for j in range(trodness):
                t = arange(anaSigList[i][j].signal.size , dtype='f')/sr + t_start
                self.ax2.plot(t, anaSigFilteredList[i][j].signal ,color = 'b')
            t_start += anaSigList[i][0].signal.size/sr
        self.canvas.draw()
        
        # to test if redraw sigs is needed
        self.lastFilteredSignal = anaSigFilteredList[0][0]


class WidgetDetection(QWidget):
    """
    Widget to plot the detection
    """
    def __init__(self , parent=None ,):
        QWidget.__init__(self,parent )
        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.canvas = SimpleCanvasAndTool(orientation = Qt.Horizontal )
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)
        
        self.ax1s = None
        self.ax2s = None
    
    def createAxes(self):
        self.fig.clear()
        
        trodness = self.spikeSortingWin.tab.trodness
        
        self.ax1s = [ ]
        self.ax2s = [ ]
        ax1 = None
        for j in range(trodness):
            h =  .8/trodness
            ax1 = self.fig.add_axes( [ .1, .9-(j+1)*h, .65, h*.9 ]  , sharex = ax1, sharey = ax1)
            self.ax1s.append(ax1)
            ax2 = self.fig.add_axes( [ .8, .9-(j+1)*h, .15, h*.9 ]  , sharey = ax1)
            self.ax2s.append(ax2)
        
        self.canvas.draw()
        self.lines = [ ]
        self.lastSignal = None
        
        
    def plotSigs(self):
        anaSigList = self.spikeSortingWin.tab.anaSigList
        trodness = self.spikeSortingWin.tab.trodness
        sr = self.spikeSortingWin.tab.sampling_rate        
        anaSigFilteredList = self.spikeSortingWin.tab.anaSigFilteredList
        
        if anaSigFilteredList is None : return
        
        # plot
        for j in range(trodness):
            ax1 = self.ax1s[j]
            ax1.clear()
            t_start = 0.
            
            for i in range(len(anaSigList)):
                ax1.axvline(t_start, color = 'r')
                t = arange(anaSigList[i][j].signal.size, dtype = 'f')/sr + t_start
                ax1.plot(t, anaSigFilteredList[i][j].signal , color = 'b')
                t_start += anaSigList[i][0].signal.size/sr
        
        # stats
        min, max = inf, -inf
        all_mean = zeros( ( len(anaSigList), trodness) ,dtype = 'f')
        all_std = zeros( ( len(anaSigList), trodness) ,dtype = 'f')
        all_median = zeros( ( len(anaSigList), trodness) ,dtype = 'f')
        for j in range(trodness):
            for i in range(len(anaSigList)):
                mi, ma = anaSigFilteredList[i][j].signal.min() , anaSigFilteredList[i][j].signal.max()
                if mi < min : min=mi
                if ma > max: max=ma
                all_mean[i,j] = mean(anaSigFilteredList[i][j].signal) 
                all_std[i,j] =  std(anaSigFilteredList[i][j].signal)
                all_median[i,j] =median(anaSigFilteredList[i][j].signal)
        
        # histo
        nbins = 1000.
        bins = arange(min,max, (max-min)/nbins)
        for j in range(trodness):
            ax2 = self.ax2s[j]
            ax2.clear()
            ax2.axhline( mean(all_mean[:,j]) , color = 'r')
            ax2.axhline( mean(all_median[:,j]) , color = 'g')
            ax2.axhline( mean(all_mean[:,j]) + sqrt(mean(all_std[:,j]**2)) , color = 'r' , linestyle = '--')
            ax2.axhline( mean(all_mean[:,j]) - sqrt(mean(all_std[:,j]**2)) , color = 'r' , linestyle = '--')
            
            counts = zeros( (bins.shape[0]-1), dtype = 'i')
            for i in range(len(anaSigList)):
                count, _ = histogram(anaSigFilteredList[i][j].signal , bins = bins)
                counts += count
            ax2.plot( counts, bins[:-1])
        
        self.canvas.draw()
        self.lines = [ ]
        
        # to test if redraw sigs is needed
        self.lastSignal = anaSigFilteredList[0][0]
    
    
    def refresh(self):
        anaSigList = self.spikeSortingWin.tab.anaSigList
        trodness = self.spikeSortingWin.tab.trodness
        sr = self.spikeSortingWin.tab.sampling_rate        
        anaSigFilteredList = self.spikeSortingWin.tab.anaSigFilteredList
        spikePosistionList = self.spikeSortingWin.tab.spikePosistionList
        
        if anaSigFilteredList is None : return

        if self.ax1s is None:
            self.createAxes()
            self.plotSigs()
            
        
        
        if self.lastSignal != anaSigFilteredList[0][0]:
            self.plotSigs()
        
        sorted = self.spikeSortingWin.tab.sorted
        if sorted is None : return
        
        
        #remove old detection
        for i in range(len(self.lines)):
            for l in self.lines[i]:
                self.ax1s[i].lines.remove(l)
        self.lines = [ ]
        
        #plot spike positions
        
        for j in range(trodness):
            self.lines.append([ ])
            t_start = 0.
            p = 0
            for i in range(len(anaSigList)):
                t = arange(anaSigList[i][j].signal.size, dtype='f')/sr + t_start
                pos = spikePosistionList[i]
                sorted2 = sorted[p:p+pos.size]
                for c in unique(sorted2):
                    sp = pos[c==sorted2]
                    l = self.ax1s[j].plot( t[sp] , anaSigFilteredList[i][j].signal[sp], 
                                                            linestyle = 'None', 
                                                            marker = 'o', 
                                                            color = self.spikeSortingWin.colors[c],
                                                            )
                    self.lines[j] += l
                t_start += anaSigList[i][0].signal.size/sr
                p += pos.size
                
        self.canvas.draw()
        
        
        
        

class WidgetExtraction(QWidget):
    def __init__(self , parent=None ,):
        QWidget.__init__(self,parent )
        self.spikeSortingWin = self.parent()
        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)
        
        self.plotWaveform = PlotWaveform(
                                                    waveforms = None ,
                                                    sorted= None , 
                                                    show_button = True,
                                                    plotParams = dict(
                                                                                plot_average = True,
                                                                                plot_individual = True,
                                                                                max_waveform_by_cluster = 70,
                                                                                )        
                                                            )
        
        mainLayout.addWidget( self.plotWaveform )

    
    def refresh(self):
        sorted = self.spikeSortingWin.tab.sorted
        waveforms = self.spikeSortingWin.tab.waveforms
        #~ trodness = self.spikeSortingWin.tab.trodness
        colors = self.spikeSortingWin.colors
        
        self.plotWaveform. changeData(waveforms, sorted = sorted , colors = colors)





class Widget3DViewer(QWidget):
    def __init__(self , parent=None ,spikeSortingWin= None):
        QWidget.__init__(self,parent )
        self.spikeSortingWin = spikeSortingWin
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        h.addWidget(QLabel('Choose dim'))
        self.combos = [ ]
        for i in range(3):
            cb = QComboBox()
            self.combos.append(cb)
            self.connect(cb, SIGNAL('activated(int)'),self.change_dim )
            h.addWidget(cb)
        
        #~ but = QPushButton(QIcon(':/view-refresh.png'), 'refresh')
        #~ h.addWidget(but)
        #~ self.connect(but, SIGNAL('clicked()'),  self.change_dim)
            
        self.canvas1 = SimpleCanvas()
        #~ self.canvas1 = SimpleCanvasAndTool()
        self.ax = Axes3D(self.canvas1.fig)
        mainLayout.addWidget( self.canvas1 )
        
        self.projected = None
        self.sorted = None        
    
    def change_dim(self, index = None):
        if self.projected is None : return
        self.ax.clear()
        vects = [ ]
        for i in range(3):
            ind = self.combos[i].currentIndex()
            vects.append( self.projected[:,ind] )
        
        for c in unique(self.sorted):
            ind = self.sorted==c
            self.ax.scatter(vects[0][ind], vects[1][ind], vects[2][ind], 
                                                color = self.spikeSortingWin.colors[c],
                                                )
        self.canvas1.draw()
    
    def refresh(self, projected, sorted):
        ndim = projected.shape[1]
        for i in range(3):
            self.combos[i].clear()
            self.combos[i].addItems( [ str(n) for n in range(ndim) ] )
            if i<ndim:
                self.combos[i].setCurrentIndex(i)
        
        self.projected = projected
        self.sorted = sorted
        
        self.change_dim()
        



class WidgetFeatures(QWidget):
    def __init__(self , parent=None ,):
        QWidget.__init__(self,parent )
        
        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        h.addWidget(QLabel('<b>Choose a view for projection</b>'))
        self.comboView = QComboBox()
        h.addWidget(self.comboView)
        h.addStretch(1)
        mainLayout.addSpacing(10)
        self.stacked = QStackedWidget()
        mainLayout.addWidget(self.stacked)
        self.connect(self.comboView, SIGNAL('activated(int)'),self.stacked, SLOT('setCurrentIndex(int)') )
        self.connect(self.comboView, SIGNAL('activated(int)'), self.refreshVisibleTab)
        
        
        # flatened 1D view
        self.comboView.addItem('flatened 1D view')
        self.canvas1 = SimpleCanvasAndTool()
        self.stacked.addWidget(self.canvas1)
        self.ax1 = self.canvas1.fig.add_subplot(1,1,1)
        
        # combinated 2D
        self.comboView.addItem('combinated 2D')
        self.canvas2 = SimpleCanvasAndTool()
        self.stacked.addWidget(self.canvas2)
        
        # 3D viewer
        self.comboView.addItem('3D viewer')
        self.widget3Dviewer = Widget3DViewer(spikeSortingWin = self.spikeSortingWin)
        self.stacked.addWidget(self.widget3Dviewer)
        
        # ND viewer
        self.comboView.addItem('ND viewer')
        self.widgetNDviewer = NDViewer(globalApplicationDict = None,
                                                            show_tour = True,
                                                            show_select_tools = False,)
        self.stacked.addWidget(self.widgetNDviewer)
        
        self.max_lines = 50
        
        
    def refresh(self):
        self.needRefresh = [ True for i in range(4) ]
        self.refreshVisibleTab(self.comboView.currentIndex())
    
    
    def refreshVisibleTab(self, index):
        sorted = self.spikeSortingWin.tab.sorted
        waveforms = self.spikeSortingWin.tab.waveforms
        projected = self.spikeSortingWin.tab.projected
        if projected is None : return
        ndim = projected.shape[1]
        
        if index == 0 and self.needRefresh[0]:
            # flatened 1D view
            self.ax1.clear()
            for c in unique(sorted):
                ind, = where(c==sorted)
                step = 1.*len(ind)/self.max_lines
                if step<=1. :
                    start,step = 0,1
                else:
                    start,step = int(random.rand()*step), int(step)
                ind = ind[start::step]
                self.ax1.plot( projected[ind,:].transpose() , 
                                                    color = self.spikeSortingWin.colors[c],
                                                    )
            self.canvas1.draw()
            self.needRefresh[0] = False
            
        
        # combinated 2D
        if index == 1 and self.needRefresh[1]:
            ndim2 = min(ndim, 16)
            self.canvas2.fig.clear()
            if projected.shape[1]>1:
                for c in unique(sorted):
                    ind = c==sorted
                    
                    
                    for i in range(ndim2):
                        for j in range(i+1, ndim2):
                            p = (j-1)*(ndim2-1)+i+1
                            ax = self.canvas2.fig.add_subplot(ndim2-1, ndim2-1, p)
                            ax.plot(projected[ind,i], projected[ind,j], 
                                                            marker = '.',
                                                            linestyle = 'None',
                                                            color = self.spikeSortingWin.colors[c]
                                                            ) 
                            #ax.set_title('%d %d'%(i,j))
                            if i==0:
                                ax.set_ylabel( str(j) )
                            if j==ndim-1:
                                ax.set_xlabel( str(i) )
                            ax.set_xticks([ ])
                            ax.set_yticks([ ])
            self.canvas2.draw()
            self.needRefresh[1] = False
        
        # 3D viewer
        if index == 2 and self.needRefresh[2]:
            self.widget3Dviewer.refresh( projected, sorted)
            self.needRefresh[2] = False
        
        # ND viewer
        if index == 3 and self.needRefresh[3]:
            self.widgetNDviewer.change_point(projected, sorted = sorted, 
                                                            colors = self.spikeSortingWin.colors,
                                                            )
            self.needRefresh[3] = False
        



class ModelSpikeList(QAbstractItemModel):
    """
    Implementation of a treemodel for a long spike list
    """
    def __init__(self, parent =None ,
                        spike_times = None,
                        sorted = None,
                        colors = None,
                        ) :
        QAbstractItemModel.__init__(self,parent)
        self.spike_times = spike_times
        self.sorted = sorted
        self.colors = colors
        self.icons = { }
        for c in unique(self.sorted):
            pix = QPixmap(10,10 )
            r,g,b = ColorConverter().to_rgb( self.colors[c] )
            pix.fill(QColor( r*255,g*255,b*255  ))
            self.icons[c] = QIcon(pix)
        
    def columnCount(self , parentIndex):
        return 2
        
    def rowCount(self, parentIndex):
        if not parentIndex.isValid():
            return self.spike_times.size
        else :
            return 0
        
    def index(self, row, column, parentIndex):
        if not parentIndex.isValid():
            if column==0:
                childItem = row
            elif column==1:
                childItem = self.spike_times[row]
            return self.createIndex(row, column, None)
        else:
            return QModelIndex()
    
    def parent(self, index):
        return QModelIndex()
        
    def data(self, index, role):
        
        if not index.isValid():
            return None
        col = index.column()
        row = index.row()
        if role ==Qt.DisplayRole :
            if col == 0:
                return QVariant(str(row))
            elif col == 1:
                return QVariant(str(self.spike_times[row]))
            else:
                return QVariant()
        elif role == Qt.DecorationRole :
            if col == 0:
                return self.icons[self.sorted[row]]
            else:
                return QVariant()
        else :
            return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled


class WidgetClustering(QWidget):
    def __init__(self , parent=None ,):
        QWidget.__init__(self,parent )

        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        
        v = QVBoxLayout()
        h.addLayout(v,1)
        
        v.addWidget(QLabel('<b>For manual clustering:</b> <br> - Select and rigth-click on spike(s) and/or neuron(s) list<br>- Make a selection in ndviewer'))
        
        v.addSpacing(30)
        
        g = QGridLayout()
        v.addLayout(g)
        
        g.addWidget(QLabel('<b>Neurons</b>') , 0,0)
        
        self.treeNeuron = QTreeWidget()
        self.treeNeuron.setColumnCount(2)
        self.treeNeuron.setHeaderLabels(['Num', 'Nb sikes', ])
        self.treeNeuron.setMinimumWidth(100)
        self.treeNeuron.setColumnWidth(0,60)
        g.addWidget(self.treeNeuron, 1,0 )
        self.treeNeuron.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.treeNeuron,SIGNAL('customContextMenuRequested( const QPoint &)'),self.contextMenuNeuron)
        self.treeNeuron.setSelectionMode( QAbstractItemView.ExtendedSelection)
        
        
        g.addWidget(QLabel('<b>All spikes</b>') , 0, 1)
        self.treeSpike = QTreeView()
        self.treeSpike.setMinimumWidth(100)
        self.treeSpike.setColumnWidth(0,80)
        g.addWidget(self.treeSpike,1, 1 )
        self.treeSpike.setSelectionMode( QAbstractItemView.ExtendedSelection)
        self.treeSpike.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.treeSpike,SIGNAL('customContextMenuRequested( const QPoint &)'),self.contextMenuSpike)
        
        
        v.addSpacing(30)
        v.addWidget(QLabel('<b>Controls</b>'))
        h2 = QHBoxLayout()
        h2.addSpacing(10)
        v.addLayout( h2 )
        but = QPushButton(QIcon(':/plot-waveform.png') , 'Waveforms')
        self.connect( but , SIGNAL('clicked( )') ,self.openWaveforms )
        h2.addWidget( but )
        but = QPushButton(QIcon(':/plot-isi.png') , 'ISI')
        self.connect( but , SIGNAL('clicked( )') ,self.openISI )
        h2.addWidget( but )
        but = QPushButton(QIcon(':/plot-crosscorrelogram.png') , 'Cross-correlogram')
        self.connect( but , SIGNAL('clicked( )') ,self.openCrossCorrelogram )
        h2.addWidget( but )
        h2.addSpacing(10)
        
        self.needRefresh  = { }
        
        
        
        self.widgetNDviewer = NDViewer(globalApplicationDict = None,
                                                            show_tour = True,
                                                            show_select_tools = True,)
        h.addWidget(self.widgetNDviewer,4)
        self.connect(self.widgetNDviewer , SIGNAL('selectionChanged') , self.newSelectionInViewer )
        self.widgetNDviewer.canvas.mpl_connect('button_press_event', self.rigthClickOnNDViewer)
        
        
        
    def refresh(self):
        sorted = self.spikeSortingWin.tab.sorted
        waveforms = self.spikeSortingWin.tab.waveforms
        projected = self.spikeSortingWin.tab.projected
        spikeTimes = self.spikeSortingWin.tab.spikeTimes
        colors = self.spikeSortingWin.colors
        
        
        if sorted is None : return
        
        # treeNeuron
        self.treeNeuron.clear()
        self.list_neuron = unique(sorted)
        for c in unique(sorted):
                ind, = where(c==sorted)
                if c==-1:
                    item = QTreeWidgetItem(["Trash"  , str(ind.size)  ] )
                    icon = QIcon(':/user-trash')
                    item.setIcon(0,icon)
                else:
                    item = QTreeWidgetItem(["%s" % (c)  , str(ind.size)  ] )
                    pix = QPixmap(10,10 )
                    r,g,b = ColorConverter().to_rgb( self.spikeSortingWin.colors[c] )
                    pix.fill(QColor( r*255,g*255,b*255  ))
                    icon = QIcon(pix)
                    item.setIcon(0,icon)
                self.treeNeuron.addTopLevelItem(item)
        
        # treeSpike
        self.modelSpike = ModelSpikeList(
                                                        spike_times = spikeTimes,
                                                        sorted = sorted,
                                                        colors = colors,                                                            
                                                            )
        self.treeSpike.setModel(self.modelSpike)
        self.connect(self.treeSpike.selectionModel() ,SIGNAL('selectionChanged(QItemSelection, QItemSelection)') , self.newSelectionInSpikeTree)
        
        # widgetNDviewer
        if projected is None : return
        self.widgetNDviewer.change_point(projected, sorted = sorted, colors = self.spikeSortingWin.colors)
        
        
        for k in self.needRefresh:
            self.needRefresh[k] = True

    

    def contextMenuNeuron(self, point):
        
        #~ pos = self.treeNeuron.indexFromItem(item).row()
        menu = QMenu()
        act = menu.addAction(QIcon(':/window-close.png'), self.tr('Delete definitively to selection'))
        self.connect(act,SIGNAL('triggered()') ,self.deleteSelection)
        act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Move selection to trash cluster'))
        self.connect(act,SIGNAL('triggered()') ,self.moveToTrash)
        act = menu.addAction(QIcon(':/TODO.png'), self.tr('Create new cluster with selection'))
        self.connect(act,SIGNAL('triggered()') ,self.groupSelection)
        act = menu.addAction(QIcon(':/TODO.png'), self.tr('Select theses spikes'))
        self.connect(act,SIGNAL('triggered()') ,self.selectSpikeFromCluster)
        act = menu.addAction(QIcon(':/TODO.png'), self.tr('Explode cluster (sub clustering)'))
        self.connect(act,SIGNAL('triggered()') ,self.subComputeCluster)
        menu.exec_(self.cursor().pos())
    
    
    
    def deleteSelection(self):
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            #~ print 'deleting', self.list_neuron[r]
            self.spikeSortingWin.tab.deleteOneNeuron(self.list_neuron[r])
        self.spikeSortingWin.refreshAllPlots()
    
    
    def moveToTrash(self):
        #~ print 'moveToTrash'
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            sorted = self.spikeSortingWin.tab.sorted
            self.spikeSortingWin.tab.sorted[ sorted == self.list_neuron[r] ]= -1
        self.spikeSortingWin.refreshAllPlots()
        
    
    def groupSelection(self):
        sorted = self.spikeSortingWin.tab.sorted
        n = max(unique(sorted)) +1
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            self.spikeSortingWin.tab.sorted[ sorted == self.list_neuron[r] ]= n
        self.spikeSortingWin.refreshAllPlots()
    
    def selectSpikeFromCluster(self):
        sorted = self.spikeSortingWin.tab.sorted
        ind = array([ ])
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            a, = where( sorted == self.list_neuron[r] )
            ind = concatenate( ( ind, a))
        self.widgetNDviewer.changeSelection(ind)
        self.newSelectionInViewer()


    def subComputeCluster(self):

        dia = QDialog(parent = self)
        v = QVBoxLayout()
        dia.setLayout(v)
        
        for name, module, plotWidget in steps:
            if name == 'Clustering': break
        
        wMeth = WidgetMultiMethodsParam(  list_method = module.list_method,
                                                            method_name = '<b>Choose methd for %s</b>:'%name,
                                                            globalApplicationDict = self.spikeSortingWin.globalApplicationDict,
                                                            keyformemory = 'spikesorting',
                                                            )
        v.addWidget(wMeth)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        v.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , dia, SLOT('accept()') )
        self.connect( buttonBox , SIGNAL('rejected()') , dia, SLOT('close()') )
        if not dia.exec_(): return

        sorted = self.spikeSortingWin.tab.sorted
        projected = self.spikeSortingWin.tab.projected
        spikeTimes = self.spikeSortingWin.tab.spikeTimes
        for index in self.treeNeuron.selectedIndexes():
            if index.column() != 0: continue
            r = index.row()
            ind, = where( sorted == self.list_neuron[r] )            
            m = wMeth.get_method()()
            kargs =  wMeth.get_dict()
            new_sorted = m.compute( projected[ind] , spikeTimes[ind] , **kargs )
            new_sorted += max(sorted)+1
            sorted[ind] = new_sorted.astype(sorted.dtype)
        
        self.spikeSortingWin.refreshAllPlots()
    
    def newSelectionInViewer(self):
        
        # to avoid larsen:
        self.disconnect(self.treeSpike.selectionModel() ,SIGNAL('selectionChanged(QItemSelection, QItemSelection)') , self.newSelectionInSpikeTree)
        
        ind = self.widgetNDviewer.actualSelection
        
        #~ self.treeSpike.clearSelection()
        #~ self.treeSpike.selectionModel().clear()
        self.treeSpike.selectionModel().clearSelection()
        
        # important efficiency problems here due to Qt4 selection in model/view framework
        # for big list and big sparsed selection you need a half year to select
        flags = QItemSelectionModel.Select #| QItemSelectionModel.Rows
        itemsSelection = QItemSelection()
        if self.spikeSortingWin.tab.spikeTimes.size>10000:
            # only the first one
            if ind.size>0:
                for j in range(2):
                    index = self.treeSpike.model().index(ind[0],j,QModelIndex())
                    ir = QItemSelectionRange( index )
                    itemsSelection.append( ir )
        else:
            for i in ind:
                for j in range(2):
                    index = self.treeSpike.model().index(i,j,QModelIndex())
                    ir = QItemSelectionRange( index )
                    itemsSelection.append( ir )
        self.treeSpike.selectionModel().select( itemsSelection , flags)

        # set selection visible
        if len(ind)>=1:
            index = self.treeSpike.model().index(ind[0],0,QModelIndex())
            self.treeSpike.scrollTo(index)
        
        # to avoid larsen:
        self.connect(self.treeSpike.selectionModel() ,SIGNAL('selectionChanged(QItemSelection, QItemSelection)') , self.newSelectionInSpikeTree)
    
    
    #~ def newSelectionInSpikeTree(self):
    def newSelectionInSpikeTree(self, selected, diselected):
        ind = [ ]
        for index in self.treeSpike.selectedIndexes():
            if index.column() == 0: ind.append(index.row())
        self.widgetNDviewer.changeSelection(ind)
    
    def rigthClickOnNDViewer(self, event):
        if event.button == 3: 
            self.contextMenuSpike(None)
    
    def contextMenuSpike(self, point):
        menu = QMenu()
        act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Move selection to trash cluster'))
        self.connect(act,SIGNAL('triggered()') ,self.moveSpikeToTrash)
        act = menu.addAction(QIcon(':/TODO.png'), self.tr('Create new cluster with theses spikes'))
        self.connect(act,SIGNAL('triggered()') ,self.createNewClusterWithSpikes)
        menu.exec_(self.cursor().pos())

    def moveSpikeToTrash(self):
        ind = self.widgetNDviewer.actualSelection
        sorted = self.spikeSortingWin.tab.sorted
        #~ n = max(unique(sorted)) +1
        self.spikeSortingWin.tab.sorted[ ind ]= -1
        self.spikeSortingWin.refreshAllPlots()
        
    def createNewClusterWithSpikes(self):
        ind = self.widgetNDviewer.actualSelection
        sorted = self.spikeSortingWin.tab.sorted
        n = max(unique(sorted)) +1
        self.spikeSortingWin.tab.sorted[ ind ]= n
        self.spikeSortingWin.refreshAllPlots()
        


    def openWaveforms(self):
        if not(hasattr(self, 'widgetPlotWaveform')):
            self.widgetPlotWaveform = PlotWaveform(waveforms = self.spikeSortingWin.tab.waveforms ,
                                        sorted= self.spikeSortingWin.tab.sorted , 
                                        colors = self.spikeSortingWin.colors,
                                        
                                        show_button = True,
                                        plotParams = dict(
                                                                    plot_average = True,
                                                                    plot_individual = True,
                                                                    max_waveform_by_cluster = 70,
                                                                    )
                                                    )
            self.widgetPlotWaveform.setWindowFlags(Qt.Dialog)
            self.widgetPlotWaveform.setWindowModality(Qt.WindowModal)
            self.widgetPlotWaveform.setWindowTitle('Waveform')
            self.needRefresh['Waveforms'] = False
            
        if self.needRefresh['Waveforms'] :
            self.widgetPlotWaveform.changeData(self.spikeSortingWin.tab.waveforms ,
                                            sorted= self.spikeSortingWin.tab.sorted , 
                                            colors = self.spikeSortingWin.colors,
                                            )
            self.needRefresh['Waveforms'] = False
        self.widgetPlotWaveform.show()

    def openISI(self):
        
        
        if not(hasattr(self, 'widgetPlotISI')):
            self.widgetPlotISI = PlotISI(
                                        spike_times = self.spikeSortingWin.tab.spikeTimes , 
                                        sorted= self.spikeSortingWin.tab.sorted , 
                                        colors = self.spikeSortingWin.colors,
                                        
                                        show_button = True,

                                                    )
            self.widgetPlotISI.setWindowFlags(Qt.Dialog)
            self.widgetPlotISI.setWindowModality(Qt.WindowModal)
            self.widgetPlotISI.setWindowTitle('ISI')
            self.needRefresh['ISI'] = False
            
        if self.needRefresh['ISI'] :
            self.widgetPlotISI.changeData(self.spikeSortingWin.tab.spikeTimes , 
                                            sorted= self.spikeSortingWin.tab.sorted , 
                                            colors = self.spikeSortingWin.colors,
                                            )
            self.needRefresh['ISI'] = False
        
        self.widgetPlotISI.show()

    def openCrossCorrelogram(self):
        if not(hasattr(self, 'widgetPlotCrossCorrelogram')):
            self.widgetPlotCrossCorrelogram = PlotCrossCorrelogram(
                                        spike_times = self.spikeSortingWin.tab.spikeTimes , 
                                        sorted= self.spikeSortingWin.tab.sorted , 
                                        colors = self.spikeSortingWin.colors,
                                        
                                        show_button = True,

                                                    )
            self.widgetPlotCrossCorrelogram.setWindowFlags(Qt.Dialog)
            self.widgetPlotCrossCorrelogram.setWindowModality(Qt.WindowModal)
            self.widgetPlotCrossCorrelogram.setWindowTitle('CrossCorrelogram')
            self.needRefresh['CrossCorrelogram'] = False
            
        if self.needRefresh['CrossCorrelogram'] :
            self.widgetPlotCrossCorrelogram.changeData(self.spikeSortingWin.tab.spikeTimes , 
                                            sorted= self.spikeSortingWin.tab.sorted , 
                                            colors = self.spikeSortingWin.colors,
                                            )
            self.needRefresh['CrossCorrelogram'] = False
        
        self.widgetPlotCrossCorrelogram.show()



steps = [ 
                        ['Filtering' , filtering, WidgetFiltering],
                        ['Detection' , detection, WidgetDetection],
                        ['Extraction' , extraction, WidgetExtraction],
                        ['Features' , feature, WidgetFeatures],
                        ['Clustering' , clustering, WidgetClustering],
                   ]

    
class TabSpikeSorting(QTabWidget) :
    """
    Widget displaying all tabs and methods options.
    Used in :
            -
            - 
    
    This widget can work in two way :
        - all_mode : work directly on signal and compute all steps : filtering, detection, features, clustering
                In this case anaSiglist is a list of list of AnalogSignal.
                The first list is a collection of segment
                The nested list is :
                    If the size  is 1, this is the normal case.
                    If the size  is 4, this is the tetrod case.
                    If the size  is N, this is the "N-trodness" case.
            
            
        - reclustering_mode : work on a list on spiketrain to re-compute the cluster
    
    
    """
        
    def __init__(self , parent=None ,
                            metadata =None,
                            session = None,
                            Session = None,
                            globalApplicationDict = None,
                            
                            id_recordingpoint = None,
                            
                            # all_step_mode = detection+clustring
                            # reclustering_mode = feature+clustering
                            mode = None,
                            
                            
                    ):
        QTabWidget.__init__(self,parent )
        self.setTabPosition(QTabWidget.West)
        
        #~ self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.metadata = metadata
        self.session = Session()
        self.globalApplicationDict = globalApplicationDict
        
        recordingPoint = self.session.query(RecordingPoint).filter_by(id=id_recordingpoint).one()
        self.recordingPoint = recordingPoint
        self.mode = mode
        
        # look for recording point with same group
        if recordingPoint.group is not None :
            query = self.session.query(RecordingPoint)
            query = query.filter(RecordingPoint.id_block == recordingPoint.id_block )
            query = query.filter(RecordingPoint.group == recordingPoint.group )
            rPointListNonSorted = [  ]
            rPointList = [  ]
            ids = [ ]
            for rp in query.all() :
                rp.metadata = metadata
                rPointListNonSorted.append( rp )
                ids.append( rp.id )
            ind = numpy.argsort( ids)
            for i in ind :
                rPointList.append( rPointListNonSorted[i] )
        else :
            rPointList = [ recordingPoint ]
        
        self.recordingPointList = rPointList
        self.recordingPoint =  rPointList[0]
        
        

        # take block
        #~ self.block = session.query(Block).filter( Block.id == rPointList[0].id_block ).one()
        self.block = rPointList[0].block

        if self.mode =='all_step_mode':
            self.trodness = len( rPointList )
            # construction the anaSigList
            self.anaSigList = [ ]
            for seg in self.block._segments :
                l = [ ]
                for rp in rPointList :
                    query2 = self.session.query(AnalogSignal)
                    query2 = query2.filter( AnalogSignal.id_recordingpoint == rp.id)
                    query2 = query2.filter( AnalogSignal.id_segment == seg.id)
                    anaSig = query2.one()
                    anaSig.metadata = metadata
                    #~ print 'anaSig' , type(anaSig), anaSig
                    l.append( anaSig )
                self.anaSigList.append( l )
            

            self.sampling_rate = self.anaSigList[0][0].sampling_rate
            
            self.anaSigFilteredList = None
            self.spikePosistionList = None
            self.spikeSign = None
            self.left_sweep = None
            self.right_sweep = None
            
            self.spikeTimes = None
            self.waveforms = None
            self.projected = None
            self.sorted = None
            self.id_segments = None
        
        elif self.mode =='reclustering_mode':
            
            self.anaSigList= None
            self.anaSigFilteredList = None
            
            self.spikeTimes = None
            self.sampling_rate = None
            self.waveforms = None
            self.projected = None
            self.sorted = None
            self.id_segments = None
            
            # construction the spikeTrainList
            spikeTrainList = [ ]
            for seg in self.block._segments :
                query2 = self.session.query(SpikeTrain)
                query2 = query2.filter( SpikeTrain.id_recordingpoint == self.recordingPoint.id)
                query2 = query2.filter( SpikeTrain.id_segment == seg.id)
                l = query2.all()
                spikeTrainList.append( l )
                
                for spikeTrain in l :
                    if spikeTrain.waveforms is None : 
                        # db do not hold spike waveform
                        continue
                        
                    if spikeTrain.id_neuron is not None:
                        id_neuron = spikeTrain.id_neuron
                    else:
                        #~ id_neuron = -1
                        id_neuron = spikeTrain.id
                    
              
                        
                    if self.spikeTimes is None :
                        self.spikeTimes = spikeTrain.spike_times
                        self.sampling_rate = spikeTrain.sampling_rate
                        self.waveforms = spikeTrain.waveforms
                        self.left_sweep = spikeTrain.left_sweep
                        self.right_sweep = spikeTrain.right_sweep      

                        self.sorted = ones( (spikeTrain.spike_times.size), dtype='i')* id_neuron
                        
                        self.id_segments = ones((spikeTrain.spike_times.size), dtype='i')*spikeTrain.id_segment
                    else:
                        # FIXME
                        # from one segment to another there is a disontinuity of time so 'spikeTimes' concatenated is False
                        # It is normally not a problem but some methods need the time for clustering .... to FIX
                        self.spikeTimes = concatenate( (self.spikeTimes, spikeTrain.spike_times, ), axis = 0)
                        self.waveforms = concatenate( (self.waveforms, spikeTrain.waveforms, ), axis = 0)
                        self.sorted = concatenate( (self.sorted, ones((spikeTrain.spike_times.size), dtype='i') * id_neuron ), axis = 0)
                        self.id_segments = concatenate( (self.id_segments, ones( (spikeTrain.spike_times.size), dtype='i')*spikeTrain.id_segment) , axis = 0)
                
            self.trodness = self.waveforms.shape[1]
        # construct all tabs
        self.hboxes = { }
        self.vboxes = { }
        self.widgetMultimethods = { }
        
        for name, module, plotWidget in steps:
            w = QWidget()
            self.addTab(w,name)
            h= QHBoxLayout()
            self.hboxes[name] = h
            w.setLayout(h)
            
            v = QVBoxLayout( )
            h.addLayout( v )
            self.vboxes[name] = v
            wMeth = WidgetMultiMethodsParam(  list_method = module.list_method,
                                                                method_name = '<b>Choose methd for %s</b>:'%name,
                                                                globalApplicationDict = self.globalApplicationDict,
                                                                keyformemory = 'spikesorting',
                                                                )
            self.widgetMultimethods[name] = wMeth
            v.addWidget(wMeth)
            v.addStretch(0)
        
        if self.mode == 'reclustering_mode':
            self.widgetMultimethods['Filtering'].setEnabled(False)
            self.widgetMultimethods['Detection'].setEnabled(False)
            self.widgetMultimethods['Extraction'].setEnabled(False)
        
        # tab for database options
        w = QWidget()
        self.addTab(w,'Database option')
        self.hboxDatabase= QHBoxLayout()
        w.setLayout(self.hboxDatabase)
        
        self.vboxDatabase = QVBoxLayout( )
        self.hboxDatabase.addLayout( self.vboxDatabase )
        
        params = [   [ 'save_waveform' , {'value' :'save filtered waveform' , 'label' : 'Save waveform in database',
                                                                    'possible' : ['save filtered waveform','do not save' ,  'save natural waveform' ] }],
                            [ 'spiketrain_mode' , {'value' :'standalone' , 'label' : 'SpikeTrain mode (container = spike table, standalone = more efficient)',
                                                                    'possible' : ['standalone','container' ] }],
                            
                        ]
        self.databaseOptions =  ParamWidget(params,
                                    applicationdict = self.globalApplicationDict,
                                    keyformemory = 'spikesorting/databaseoptions'  ,
                                    title = 'database options',
                                    )
        self.vboxDatabase.addWidget( self.databaseOptions )
        
        
        #~ v.addStretch(0)
    
    
    def computeFiltering(self) :
        m = self.widgetMultimethods['Filtering'].get_method()()
        kargs = self.widgetMultimethods['Filtering'].get_dict()
        
        self.anaSigFilteredList = [ ]
        for i in range( len(self.anaSigList) ):
            l = [ ]
            for j in range(self.trodness):
                l.append( m.compute( self.anaSigList[i][j] , **kargs) )
            self.anaSigFilteredList.append( l )
    

    def computeDetection(self) :
        m = self.widgetMultimethods['Detection'].get_method()()
        kargs = self.widgetMultimethods['Detection'].get_dict()
        
        self.spikeSign = kargs['sign']
        self.left_sweep = kargs['left_sweep']
        self.right_sweep = kargs['right_sweep']
        
        self.spikePosistionList = [ ]
        t_start = 0.
        sr = self.anaSigList[0][0].sampling_rate
        self.spikeTimes = zeros((0), dtype='f')
        
        for i in range( len(self.anaSigList) ):
            spikePosition = m.compute(self.anaSigFilteredList[i], **kargs)
            self.spikePosistionList.append(  spikePosition  )
            self.spikeTimes = concatenate( (self.spikeTimes , spikePosition/sr + t_start) , axis = 0)
            t_start += self.anaSigList[i][0].signal.size/sr
            
        self.sorted = zeros(self.spikeTimes.size, dtype = 'i')
        
        
    def computeExtraction(self) :
        m = self.widgetMultimethods['Extraction'].get_method()()
        kargs = self.widgetMultimethods['Extraction'].get_dict()
        
        self.waveforms = None
        #~ p = 0
        for i in range( len(self.anaSigList) ):
            #~ pos = self.spikePosistionList[i]
            wf = m.compute(self.anaSigFilteredList[i], self.spikePosistionList[i],self.spikeSign, left_sweep = self.left_sweep , right_sweep = self.right_sweep, **kargs)
            if self.waveforms is None:
                self.waveforms = wf
            else:
                self.waveforms = concatenate( ( self.waveforms , wf) , axis = 0 )
            #~ p += pos.size
        

    def computeFeatures(self) :
        m = self.widgetMultimethods['Features'].get_method()()
        kargs = self.widgetMultimethods['Features'].get_dict()
        
        self.projected = m.compute( self.waveforms, self.sampling_rate, **kargs)
    
    
    def computeClustering(self) :
        m = self.widgetMultimethods['Clustering'].get_method()()
        kargs = self.widgetMultimethods['Clustering'].get_dict()
        
        self.sorted = m.compute( self.projected , self.spikeTimes , **kargs )
    
    
    def recomputeAllSteps(self) :
        self.computeFiltering()
        self.computeDetection()
        self.computeExtraction()
        self.computeFeatures()
        self.computeClustering()



    def deleteOneNeuron(self, num):
        
        ind = self.sorted != num
        
        if self.mode == 'all_step_mode':
            p = 0 # position in sorted
            for i,seg in enumerate(self.block._segments) :
                pos = self.spikePosistionList[i]
                ind2 = ind[p:p+pos.size]
                self.spikePosistionList[i] = self.spikePosistionList[i][ind2]
                p += pos.size
        elif self.mode == 'reclustering_mode':
            self.id_segments= self.id_segments[ind]
        
        self.projected= self.projected[ind]
        self.waveforms= self.waveforms[ind]
        self.spikeTimes= self.spikeTimes[ind]
        self.sorted= self.sorted[ind]


    def save_to_db(self) :
        
        n_neurons = unique(self.sorted).size
        
        # delete old spiketrain
        id_neurons = [ ]
        for rp in self.recordingPointList:
            for sptr in self.session.query( SpikeTrain ).filter( SpikeTrain.id_recordingpoint == rp.id ).all():
                id_neurons.append( sptr.id_neuron )
                self.session.delete(sptr)
        for id_neuron in unique(id_neurons):
            if id_neuron is None : continue
            neu = self.session.query( Neuron ).filter(Neuron.id == int(id_neuron) ).one( )
            self.session.delete(neu)
        self.session.commit()
        
        
        #~ self.databaseOptions['spiketrain_mode'] == 'standalone'
        
        
        # create new neuron and spiketrain
        if self.mode == 'all_step_mode':
            
            if self.databaseOptions['save_waveform']=='save natural waveform':
                # re-extract waveform on non filtered AnalogSignal
                m = self.widgetMultimethods['Extraction'].get_method()()
                self.waveformsNatural = None
                for i in range( len(self.anaSigList) ):
                    wf = m.compute(self.anaSigList[i], self.spikePosistionList[i],self.spikeSign, left_sweep = self.left_sweep , right_sweep = self.right_sweep ,alignment='on threshold'  )
                    if self.waveformsNatural is None:
                        self.waveformsNatural = wf
                    else:
                        self.waveformsNatural = concatenate( ( self.waveformsNatural , wf) , axis = 0 )                         
            
            
            for c in unique(self.sorted):
                neu = Neuron(  id_block = self.recordingPoint.id_block,
                                        name = 'Neuron %d of recPoint %d' % (c, self.recordingPoint.channel),
                                        )
                #~ print neu.id, neu.id_block, neu.name
                
                self.session.add( neu )
                self.session.commit()
                #~ self.block._neurons.append( neu)
                self.session.commit()
                
                
                p = 0 # position in waveform.shape[0] and sorted
                for i,seg in enumerate(self.block._segments) :
                    
                    pos = self.spikePosistionList[i]
                    
                    sorted2 = self.sorted[p:p+pos.size]
                    ind, = where(sorted2 == c)
                    _spike_times = self.anaSigList[i][0].t()[pos[ind]]
                    if self.databaseOptions['save_waveform']=='save filtered waveform':
                        _waveforms = self.waveforms[p+ind,:,:]
                    elif self.databaseOptions['save_waveform']=='do not save':
                        _waveforms = None
                    elif self.databaseOptions['save_waveform']=='save natural waveform':
                        _waveforms = self.waveformsNatural[p+ind,:,:]

                    
                    if self.databaseOptions['spiketrain_mode'] == 'standalone':
                        spike_times = _spike_times
                        waveforms = _waveforms
                    elif self.databaseOptions['spiketrain_mode'] == 'container':
                        spike_times = None
                        waveforms = None
                    
                    sptr = SpikeTrain( id_neuron = neu.id,
                                                id_recordingpoint = self.recordingPoint.id,
                                                id_segment = seg.id, 
                                                name = 'Neuron.id %d Segment.id %d' %( neu.id,  seg.id ) ,
                                                t_start = float(self.anaSigList[i][0].t_start),
                                                t_stop = float(self.anaSigList[i][0].t()[-1]),
                                                sampling_rate =  float(self.sampling_rate),
                                                left_sweep = float(self.left_sweep),
                                                right_sweep = float(self.right_sweep),
                                                channel = self.recordingPoint.channel,
                                                _spike_times = spike_times,
                                                _waveforms = waveforms,
                                                )
                    
                    self.session.add( sptr )
                    #~ self.neu._spiketrains.append( sptr )
                    self.session.commit()
                    
                    if self.databaseOptions['spiketrain_mode'] == 'container':
                        for j in range(_spike_times.size):
                            if _waveforms is None:
                                waveform = None
                            else:
                                waveform = _waveforms[j]
                            spike = Spike( id_spiketrain = sptr.id,
                                                    time = float(_spike_times[j]),
                                                    waveform = waveform,
                                                    sampling_rate =  float(self.sampling_rate),
                                                )
                            self.session.add( spike )
                        self.session.commit()
                    
                    p += pos.size
                    

        if self.mode == 'reclustering_mode':
            
            for c in unique(self.sorted):
                neu = Neuron(  id_block = self.recordingPoint.id_block,
                                        name = 'Neuron %d of recPoint %d' % (c, self.recordingPoint.channel),
                                        )
                #~ print neu.id, neu.id_block, neu.name
                self.session.add( neu )
                self.session.commit()
                for i,seg in enumerate(self.block._segments) :
                    

                    ind, = where( (self.sorted == c) & ( seg.id == self.id_segments) )
                    _spike_times = self.spikeTimes[ind]
                    
                    
                    if self.databaseOptions['save_waveform']=='save filtered waveform':
                        _waveforms = self.waveforms[ind,:,:]
                    elif self.databaseOptions['save_waveform']=='do not save':
                        _waveforms = None
                    elif self.databaseOptions['save_waveform']=='save natural waveform':
                        _waveforms = self.waveformsNatural[ind,:,:]
                    
                    if self.databaseOptions['spiketrain_mode'] == 'standalone':
                        spike_times = _spike_times
                        waveforms = _waveforms
                    elif self.databaseOptions['spiketrain_mode'] == 'container':
                        spike_times = None
                        waveforms = None
                    
                    sptr = SpikeTrain( id_neuron = neu.id,
                                                id_recordingpoint = self.recordingPoint.id,
                                                id_segment = seg.id, 
                                                name = 'Neuron.id %d Segment.id %d' %( neu.id,  seg.id ) ,
                                                
                                                t_start = 0.,
                                                t_stop = None,
                                                sampling_rate =  float(self.sampling_rate),
                                                left_sweep = self.left_sweep,
                                                right_sweep = self.right_sweep,
                                                channel = self.recordingPoint.channel,
                                                _spike_times = spike_times,
                                                _waveforms = waveforms,
                                                
                                                )
                    self.session.add( sptr )
                    self.session.commit()
                    
                    
                    if self.databaseOptions['spiketrain_mode'] == 'container':
                        for j in range(ind.size):
                            if _waveforms is None:
                                waveform = None
                            else:
                                waveform = _waveforms[j]
                            spike = Spike( id_spiketrain = sptr.id,
                                                    time = _spike_times[j],
                                                    waveform = waveform,
                                                    sampling_rate =  self.sampling_rate,
                                                )
                            self.session.add( spike )
                        self.session.commit()                    
                    





class SpikeSorting(QDialog) :
    """
    Scroll area resazible for stacking matplotlib canvas
    
    several modes :
                                - spikedetection/spikesorting on recording point (and its group)
                                - spikesorting on a list spiketrain
                                - 
    
    
    
    """
    def __init__(self  , parent = None ,
                            metadata =None,
                            session = None,
                            Session = None,
                            globalApplicationDict = None,

                            mode = None,
                            tablename = None,
                            id_recordingpoint = None,
                            
                            
                            ):
        QDialog.__init__(self, parent)
        self.metadata = metadata
        self.globalApplicationDict = globalApplicationDict

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.tab = TabSpikeSorting(metadata = self.metadata,
                                                                    Session = Session,
                                                                    session = session,
                                                                    globalApplicationDict= self.globalApplicationDict,
                                                                    
                                                                    mode = mode,
                                                                    
                                                                    id_recordingpoint = id_recordingpoint,

                                                                    )
        
        mainLayout.addWidget(self.tab)
        
        self.plotWidgets = { }
        for name, module, plotWidget in steps:
            
            v = self.tab.vboxes[name]
            but = QPushButton('Compute %s'%name)
            v.addWidget(but)
            #~ self.connect(but , SIGNAL('clicked()') , getattr(self , 'compute%s'%name) )
            self.connect(but , SIGNAL('clicked()') , self.computeAStep)

            if self.tab.mode =='reclustering_mode' and (name == 'Filtering' or name =='Detection' or name =='Extraction'):
                but.setEnabled(False)


            if self.tab.mode =='reclustering_mode' and (name == 'Filtering' or name =='Detection'):
                self.plotWidgets[name] = None
                
            else:
                h = self.tab.hboxes[name]
                self.plotWidgets[name] = plotWidget(parent = self)
                h.addWidget(self.plotWidgets[name], 3)
            
        
        # database panel
        
        but = QPushButton(QIcon(':/document-save.png'), 'Save Neurons, SpikeTrain and Spike in database')
        self.connect(but, SIGNAL('clicked( )') , self.tab.save_to_db)
        self.tab.vboxDatabase.addWidget(but)
        self.tab.vboxDatabase.addSpacing(20)

        #~ but = QPushButton(QIcon(':/view-refresh.png'), 'Refresh info')
        #~ self.connect(but, SIGNAL('clicked( )') , self.refreshDataBasePanel)
        #~ self.tab.vboxDatabase.addWidget(but)
        
        self.textInfo = QTextEdit( )
        self.tab.vboxDatabase.addWidget(self.textInfo)
        self.textInfo.setReadOnly(True)
        self.tab.vboxDatabase.addStretch(1)
        
        self.tableDB = QTableWidget()
        self.tab.hboxDatabase.addWidget( self.tableDB )

        self.tabNeedRefresh = { }
        self.connect(self.tab, SIGNAL('currentChanged ( int  )'), self.refreshVisibleTab)
        self.refreshAllPlots()

        #~ self.hboxes = { }
        #~ self. = { }
        #~ self.widgetMultimethods = { }
            
        

    def computeAStep(self, ):
        name = self.sender().text()
        name = str(name.replace('Compute ', ''))
        print 'compute', name
        
        # launch computation
        import time
        t1 = time.time()
        getattr(self.tab , 'compute%s'%name)( )
        t2  = time.time()
        print 'compute', name, t2-t1
        
        self.refreshAllPlots()

    
    def refreshAllPlots(self):
        self.colors = { }
        if self.tab.sorted is not None:
            cmap = get_cmap('jet' , unique(self.tab.sorted).size+3)
            for i , c in enumerate(unique(self.tab.sorted)):
                self.colors[c] = cmap(i+2)
        self.colors[-1] = 'k' #trash
        
        
        # plot only the visible one
        ind = self.tab.currentIndex()
        if ind < len(steps):
            name, module, plotWidget = steps[ind]
            if self.plotWidgets[name] is not None:
                self.plotWidgets[name].refresh()
            visiblename = name
            self.tabNeedRefresh[visiblename] = False
        else:
            visiblename = None
        
        for name, module, plotWidget in steps:
            if visiblename == name: continue
            if self.plotWidgets[name] is  None: 
                self.tabNeedRefresh[name] = False
                continue
            self.tabNeedRefresh[name] = True

        self.refreshDataBasePanel()
        



    
    def refreshVisibleTab(self, ind):
        
        if ind == len(steps) : return
        name, module, plotWidget = steps[ind]
        if self.tabNeedRefresh[name]:
            if self.plotWidgets[name] is not None:
                self.tabNeedRefresh[name] = False
                import time
                t1 = time.time()
                self.plotWidgets[name].refresh()
                t2  = time.time()
                print 'refresh plot', name, t2-t1                
            



    
    def refreshDataBasePanel(self):
        
        
        
        # table
        self.tableDB.clear()
        if self.tab.sorted is  None: return
        n_neurons = len( unique(self.tab.sorted) )
        n_segments = len(self.tab.block._segments)
        
        self.tableDB.setRowCount(n_neurons)
        self.tableDB.setColumnCount(n_segments)
        
        for i, seg in enumerate(self.tab.block._segments) :
            item = QTableWidgetItem('Seg %d'%seg.id)
            self.tableDB.setHorizontalHeaderItem( i, item)
        
        for j,c  in enumerate(unique(self.tab.sorted)):
            item = QTableWidgetItem('Neuron %d'%c )
            self.tableDB.setVerticalHeaderItem( j, item)
        
        
        if self.tab.mode == 'all_step_mode':
            
            p = 0 
            for i, seg in enumerate(self.tab.block._segments) :
                pos = self.tab.spikePosistionList[i]
                for j,c  in enumerate(unique(self.tab.sorted)):
                    sorted2 = self.tab.sorted[p:p+pos.size]
                    ind, = where(sorted2 == c)
                    
                    pix = QPixmap(10,10 )
                    
                    r,g,b = ColorConverter().to_rgb(self.colors[c])
                    pix.fill(QColor( r*255,g*255,b*255  ))
                    icon = QIcon(pix)
                    item = QTableWidgetItem(icon, 'Nb spikes %d'% ind.size)
                    self.tableDB.setItem(j, i , item )
                
                #~ pos += c
        
        elif self.tab.mode =='reclustering_mode':
            for i, seg in enumerate(self.tab.block._segments) :
                for j,c  in enumerate(unique(self.tab.sorted)):
                    ind, = where( (self.tab.sorted == c) & ( seg.id == self.tab.id_segments) )
                    
                    pix = QPixmap(10,10 )
                    r,g,b = ColorConverter().to_rgb(self.colors[c])
                    pix.fill(QColor(r*255,g*255,b*255  ))
                    icon = QIcon(pix)
                    item = QTableWidgetItem(icon, 'Nb spikes %d'% ind.size)
                    self.tableDB.setItem(j, i , item )
                    
                
                
        
    
        # info
        text1 = """
    Block id : %d
    Blck name : %s
    RecordingPoint id: %d
    Trodness : %d               (1= standart    4=tetrode)
    Nb of segments : %d

        """ % (self.tab.block.id,
                self.tab.block.name,
                self.tab.recordingPoint.id,
                self.tab.trodness,
                len(self.tab.block._segments),
                
                )
        
        if self.tab.sorted is not None:
            text2 ="""
    Total nb of neurons : %d
    Total nb of spike : %d
                """ %(
                len( unique(self.tab.sorted) ),
                len( self.tab.spikeTimes),
                
                )
        else:
            text2 =""
    
    
        self.textInfo.setPlainText(text1+text2)
    








