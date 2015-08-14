# -*- coding: utf-8 -*-


"""

Set of wdget for spike sorting.

API is simpler all widget have:

     * SpikeSorter for entry
     * a refresh method
     * a list a step that trigger a refresh
     * a name
     *setSelection method optional
     * 2 signals (optionals)
            self.connect(w, SIGNAL('SpikeLabelsChanged'), self.spikeLabelsChanged)
            self.connect(w, SIGNAL('SpikeSelectionChanged'), self.SpikeSelectionChanged)
            self.connect(w, SIGNAL('SpikeSubsetChanged'), self.SpikeSubsetChanged)





"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy
import numpy as np

from guiutil.icons import icons
from guiutil.paramwidget import ParamWidget, LimitWidget, ParamDialog
from guiutil.multiparamwidget import WidgetMultiMethodsParam

from OpenElectrophy.classes import *

from numpy import unique, ones, mean, std, arange, where, random, unique

from enhancedmatplotlib import SimpleCanvasAndTool,  SimpleCanvas

from matplotlib.colors import ColorConverter
from matplotlib.cm import get_cmap
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D


from signalstreamer import SignalAndSpikeStreamer

from ndviewer import NDViewer


from ..computing.spikesorting.spikesorter import steps



class SpikeSortingBase():
    def __init__(self,
                            plotParams = None,
                            ):
        self.plotParams = plotParams
        if self.plotParams is None:
            self.plotParams = ParamWidget(self.plotParamDefault).get_dict()        
    
    def changePlotOptions(self):
        dia = ParamDialog(self.plotParamDefault , title = 'Plot parameters',)
        dia.param_widget.update( self.plotParams )
        ok = dia.exec_()
        if  ok ==  QDialog.Accepted:
            self.plotParams = dia.param_widget.get_dict()
        
        self.refresh()
        
    def refresh(self):
        pass

class ThreadRefresh(QThread):
    def __init__(self, parent = None,widgetToRefresh = None):
        QThread.__init__(self)
        self.widgetToRefresh = widgetToRefresh
    def run(self):
        self.widgetToRefresh.refresh_background()




class FullBandSignal(QWidget):
    name = 'Full band signal'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    icon_name = 'analogsignal.png'
    
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        
        self.spikesorter = spikesorter
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        vlimits = [ ]
        analogsignals = [ ]
        if self.spikesorter.anaSigList is not None:
            vlimit = 0
            for anaSigs in  self.spikesorter.anaSigList[:-1]:
                vlimit +=  anaSigs[0].signal.size/anaSigs[0].sampling_rate
                vlimits.append(vlimit)
        
        
            t_start = 0
            for i, anaSigs in enumerate( self.spikesorter.anaSigList ):
                analogsignals.append([ ])
                for j,ana in enumerate( anaSigs ):
                    analogsignals[-1].append(AnalogSignal( signal = ana.signal,
                                                                                    sampling_rate = ana.sampling_rate,
                                                                                    t_start = t_start,
                                                                                    )
                                                            )
                t_start += ana.signal.size/ana.sampling_rate
            
        self.streamer = SignalAndSpikeStreamer(    analogsignals = analogsignals,
                                                                            spiketrains = None,
                                                                            vlimits = vlimits,
                                                                            nplot = self.spikesorter .trodness,
                                                                            )
        mainLayout.addWidget(self.streamer)
        self.streamer.fullRefresh()
        self.refresh()

    def refresh(self, step = None):
        sps = self.spikesorter
        
        if sps.spikePosistionList is None: return
        
        spiketrains = [ ]
        p = 0
        for i, anaSigs in enumerate(self.streamer.analogsignals):
        #~ for i, anaSigs in enumerate(self.spikesorter.anaSigList):
            
            
            spiketrains.append([ ])
            pos = sps.spikePosistionList[i]
            label2 = sps.spikeLabels[p:p+pos.size]
            
            for c in sps.allLabels:
                ind, = where(label2 == c)
                ana = anaSigs[0]
                spike_times = ana.t_start + pos[ind]/ana.sampling_rate
                sptr = SpikeTrain( spike_times = spike_times,
                                                sampling_rate = ana.sampling_rate,
                                                )
                sptr.color = sps.colors[c]
                spiketrains[i].append(sptr)
            p += pos.size
            
        self.streamer.changeData(analogsignals = None,
                                                        spiketrains = spiketrains,
                                                        vlimits =  None,
                                                        )

    def setSpikeSelection(self, ind):
        if self.streamer.analogsignals is None: return
        sps = self.spikesorter
        selectedspikes = [ ]
        p = 0
        for i, anaSigs in enumerate(self.streamer.analogsignals):
            ana = anaSigs[0]
            pos = sps.spikePosistionList[i]
            ind2 = ind[(ind>=p) & (ind<p+pos.size)]
            #~ print 'ind2', i,ind2.size, p, pos.size
            spike_times = ana.t_start + pos[ind2-p]/ana.sampling_rate
            if ind.size==1 and spike_times.size==1:
                self.streamer.hspinbox.setValue(spike_times[0] - .025)
                self.streamer.hzspinbox.setValue(.05)
            
            #~ print spike_times.size
            sptr = SpikeTrain( spike_times = spike_times, sampling_rate = ana.sampling_rate,)
            selectedspikes.append(sptr)
            p+=pos.size
        self.streamer.changeSelectedSpikes( selectedspikes)



class FilteredSignal(QWidget):
    name = 'Filtered signal'
    refresh_on = ['Filtering' ,  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    icon_name = 'Detection.png'
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter

        self.spikesorter = spikesorter
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        vlimits = [ ]
        if self.spikesorter.anaSigList is not None:
            vlimit = 0
            for anaSigs in  self.spikesorter.anaSigList[:-1]:
                vlimit +=  anaSigs[0].signal.size/anaSigs[0].sampling_rate
                vlimits.append(vlimit)
        
        self.streamer = SignalAndSpikeStreamer(    analogsignals = None,
                                                                            spiketrains = None,
                                                                            vlimits = vlimits,
                                                                            nplot = self.spikesorter .trodness,
                                                                            )
        mainLayout.addWidget(self.streamer)
        self.refresh()

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.anaSigFilteredList is None: return
        
        
        if step == 'Filtering' or self.streamer.analogsignals is None:
            analogsignals = [ ]
            t_start = 0
            for i, anaSigs in enumerate( self.spikesorter.anaSigFilteredList ):
                analogsignals.append([ ])
                for j,ana in enumerate( anaSigs ):
                    analogsignals[-1].append(AnalogSignal( signal = ana.signal,
                                                                                    sampling_rate = ana.sampling_rate,
                                                                                    t_start = t_start,
                                                                                    )
                                                            )
                t_start += ana.signal.size/ana.sampling_rate
        else:
            analogsignals = None
        self.streamer.changeData(analogsignals = analogsignals)
        
        if step != 'Filtering' and  sps.spikePosistionList is not None:
        
            spiketrains = [ ]
            p = 0
            for i, anaSigs in enumerate(self.streamer.analogsignals):
                spiketrains.append([ ])
                pos = sps.spikePosistionList[i]
                label2 = sps.spikeLabels[p:p+pos.size]
                
                for c in sps.allLabels:
                    ind, = where(label2 == c)
                    ana = anaSigs[0]
                    spike_times = ana.t_start + pos[ind]/ana.sampling_rate
                    sptr = SpikeTrain( spike_times = spike_times,
                                                    sampling_rate = ana.sampling_rate,
                                                    )
                    sptr.color = sps.colors[c]
                    spiketrains[i].append(sptr)
                p += pos.size
        else:
            spiketrains = None
        self.streamer.changeData(spiketrains = spiketrains,)

    def setSpikeSelection(self, ind):
        
        if self.streamer.analogsignals is None: return
        
        sps = self.spikesorter
        selectedspikes = [ ]
        p = 0
        for i, anaSigs in enumerate(self.streamer.analogsignals):
            ana = anaSigs[0]
            pos = sps.spikePosistionList[i]
            ind2 = ind[(ind>=p) & (ind<p+pos.size)]
            #~ print 'ind2', i,ind2.size, p, pos.size
            spike_times = ana.t_start + pos[ind2-p]/ana.sampling_rate
            if ind.size==1 and spike_times.size==1:
                self.streamer.hspinbox.setValue(spike_times[0] - .025)
                self.streamer.hzspinbox.setValue(.05)
            
            #~ print spike_times.size
            sptr = SpikeTrain( spike_times = spike_times, sampling_rate = ana.sampling_rate,)
            selectedspikes.append(sptr)
            p+=pos.size
        self.streamer.changeSelectedSpikes( selectedspikes)


class SignalStatistics(QWidget):
    name = 'Signal statistics'
    refresh_on = [  'Filtering' ]
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.canvas = SimpleCanvas( )
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)
    
    def refresh(self, step = None):
        
        sps = self.spikesorter
        self.fig.clear()
        self.axs = [ ]
        for j in range(sps.trodness):
            ax = self.fig.add_subplot(sps.trodness,1,j+1)
            self.axs.append(ax)
        
        
        if sps.anaSigFilteredList is None: return
        
        # stats
        min, max = numpy.inf, -numpy.inf
        all_mean = numpy.zeros( ( len(sps.anaSigList), sps.trodness) ,dtype = 'f')
        all_std = numpy.zeros( ( len(sps.anaSigList), sps.trodness) ,dtype = 'f')
        all_median = numpy.zeros( ( len(sps.anaSigList), sps.trodness) ,dtype = 'f')
        for j in range(sps.trodness):
            for i in range(len(sps.anaSigList)):
                mi, ma = sps.anaSigFilteredList[i][j].signal.min() , sps.anaSigFilteredList[i][j].signal.max()
                if mi < min : min=mi
                if ma > max: max=ma
                all_mean[i,j] = numpy.mean(sps.anaSigFilteredList[i][j].signal) 
                all_std[i,j] =  numpy.std(sps.anaSigFilteredList[i][j].signal)
                all_median[i,j] =numpy.median(sps.anaSigFilteredList[i][j].signal)
        
        # histo
        nbins = 1000.
        bins = numpy.arange(min,max, (max-min)/nbins)
        for j in range(sps.trodness):
            ax = self.axs[j]
            ax.clear()
            ax.axhline( numpy.mean(all_mean[:,j]) , color = 'r')
            ax.axhline( numpy.mean(all_median[:,j]) , color = 'g')
            ax.axhline( numpy.mean(all_mean[:,j]) + numpy.sqrt(mean(all_std[:,j]**2)) , color = 'r' , linestyle = '--')
            ax.axhline( numpy.mean(all_mean[:,j]) - numpy.sqrt(mean(all_std[:,j]**2)) , color = 'r' , linestyle = '--')
            
            counts = numpy.zeros( (bins.shape[0]-1), dtype = 'i')
            for i in range(len(sps.anaSigList)):
                count, _ = numpy.histogram(sps.anaSigFilteredList[i][j].signal , bins = bins)
                counts += count
            ax.plot( counts, bins[:-1])



class AllWaveforms(QWidget, SpikeSortingBase):
    name = 'Waveforms'
    refresh_on = [ 'Detection' , 'Extraction' , 'Features' , 'Clustering']
    icon_name = 'plot-waveform.png'
    
    plotParamDefault =  [
                                        [ 'max_waveform_by_cluster' , {'value' : 10 }],
                                    ]

    
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        SpikeSortingBase.__init__(self,  plotParams = None)
        
        self.spikesorter = spikesorter
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        h = QHBoxLayout()
        mainLayout.addLayout(h)
        
        #self.butPlotParam = QPushButton(QIcon(':/configure.png'), '', parent  = self)
        self.butPlotParam = QPushButton(QIcon(':/configure.png'), '', self)
        h.addWidget(self.butPlotParam)
        self.butPlotParam.clicked.connect(self.changePlotOptions)
        
        h.addStretch()
        
        self.canvas = SimpleCanvas( )
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)
        
        # for selection
        self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)
        self.actualSelection = numpy.array([ ] , dtype='i')
        self.epsilon = .5
        self.selected_lines = None
        self.already_in_pick = False # to avoid multiple pick
        
        #~ self.butPlotParam = QPushButton(QIcon(':/configure.png'), '', parent = self)
        #~ self.butPlotParam.setGeometry(10,10,32,32)
        #~ self.butPlotParam.clicked.connect(self.changePlotOptions)
        
        
        # TODO :params
        #~ self.plotParams = { }
        #~ self.plotParams['max_waveform_by_cluster'] = 10
        
    def refresh(self, step = None):
        self.axs = [ ]
        sps = self.spikesorter
        self.fig.clear()
        self.selected_lines = None

        if sps.waveforms is None : return
            
        # recreate axes
        ax = None
        for i in range(sps.trodness):
            ax = self.fig.add_subplot( 1, sps.trodness, i+1 , sharex = ax, sharey = ax)
            self.axs.append( ax )
        
        # plots
        self.lines = [ ]
        for i in range(sps.trodness):
            ax = self.axs[i]
            ax.clear()
            self.lines.append([ ])
        
        self.ploted_indices =[ ]
        for c in sps.allLabels:
            ind = sps.shuffledSpikeSubset[c]
            if ind.size> self.plotParams['max_waveform_by_cluster']:
                ind = ind[:self.plotParams['max_waveform_by_cluster']]
            
            #~ ind ,  = where(sps.spikeLabels ==c)
            #~ if ind.size >= max_spike:
                #~ rand_select = unique(random.randint(0,high = ind.size, size = max_spike))
                #~ ind = ind[rand_select]
            self.ploted_indices.extend( ind )
            for i in range(sps.trodness):
                if ind.size>0: 
                    lines  = self.axs[i].plot( sps.waveforms[ind, i,  :].transpose(),
                                                color = sps.colors[c],
                                                picker=self.epsilon,
                                                )
                    self.lines[i] += lines
                else:
                    self.lines[i].append(None)
        self.ploted_indices = numpy.array(self.ploted_indices)
        self.canvas.draw()
    
    
    #cid = self.canvas.mpl_connect('pick_event', self.onPick)
    # self.canvas.mpl_disconnect(e)
    
    def refresh_selection(self):
        
        if self.selected_lines is not None:
            for i, ax in enumerate(self.axs):
                ax.lines.remove(self.selected_lines[i])
        
        
        if self.actualSelection.size>=1:
            self.selected_lines = [ ]
            for i, ax in enumerate(self.axs):
                lines  = self.axs[i].plot(self.spikesorter.waveforms[self.actualSelection[0],i,:],
                                                    color = 'm',
                                                    linewidth = 4,
                                                    alpha = .6,
                                                    )
                self.selected_lines += lines
        else:
            self.selected_lines = None
        #~ print 'self.selected_lines', self.selected_lines
        self.canvas.draw()
        
        
    
    def onPick(self , event):
        #~ print 'on pick'
        if self.already_in_pick: return
        self.canvas.mpl_disconnect(self.mpl_event_id)
        if isinstance(event.artist, Line2D):
            i =  self.axs.index(event.artist.get_axes())
            if event.artist not in self.lines[i]:
                self.actualSelection = numpy.array([ ] , dtype='i')
            else:
                num_line = self.lines[i].index(event.artist)
                self.actualSelection = self.ploted_indices[[num_line]]
        else:
            self.actualSelection = numpy.array([ ] , dtype='i')
        #~ print 'self.actualSelection', self.actualSelection
        self.refresh_selection()
        self.emit( SIGNAL('SpikeSelectionChanged') , self.actualSelection)
        self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)
        
        # this is a ugly patch to avoid multiple onPick at the same time
        self.already_in_pick = True
        #self.timer = QTimer(interval = 1000., singleShot = True)
        self.timer = QTimer( )
        self.timer.setInterval( 1000.)
        self.timer.setSingleShot( True )
        
        self.timer.timeout.connect(self.do_pick_again)
        self.timer.start()
    
    def do_pick_again(self):
        self.already_in_pick = False
    
    
    def setSpikeSelection(self, ind):
        # TO avoid larsen
        self.canvas.mpl_disconnect(self.mpl_event_id)
        self.actualSelection =  ind
        self.refresh_selection()
        self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)








class AverageWaveforms(QWidget):
    name = 'Average waveforms'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    icon_name = 'plot-waveform.png'
    
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.canvas = SimpleCanvas( )
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)


    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.waveforms is None : return
            
        # recreate axes
        self.fig.clear()
        self.axs = [ ]
        ax = None
        for i in range(sps.trodness):
            ax = self.fig.add_subplot( 1, sps.trodness, i+1 , sharex = ax, sharey = ax)
            self.axs.append( ax )
            

        # plots
        for i in range(sps.trodness):
            ax = self.axs[i]
            ax.clear()
            for c in sps.allLabels:
                ind = c==sps.spikeLabels
                m  = mean(sps.waveforms[ind,i,:], axis = 0)
                sd = std(sps.waveforms[ind,i,:], axis = 0)
                ax.plot( m, 
                                    linewidth=2,
                                    color = sps.colors[c],
                                    )
                ax.fill_between(arange(m.size), m-sd, m+sd ,
                                    color = sps.colors[c],
                                    alpha = .3)
        self.canvas.draw()


class FeaturesNDViewer(QWidget):
    name = 'Features NDViewer'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    icon_name = 'Clustering.png'
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        
        self.ndviewer = NDViewer(globalApplicationDict = globalApplicationDict,
                                                            show_tour = True,
                                                            show_select_tools = True,)
        mainLayout.addWidget(self.ndviewer)

        self.connect(self.ndviewer , SIGNAL('selectionChanged') , self.newSelectionInViewer )
        self.ndviewer.canvas.mpl_connect('button_press_event', self.rigthClickOnNDViewer)



    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.features is None : return
        self.ndviewer.change_point(sps.features, dataLabels = sps.spikeLabels, 
                                                        colors = sps.colors,
                                                        subset = sps.shuffledSpikeSubset,
                                                        )
    
    def newSelectionInViewer(self):
        self.emit( SIGNAL('SpikeSelectionChanged') , self.ndviewer.actualSelection)
        
    def setSpikeSelection(self, ind):
        # To avoid larsen
        if self.spikesorter.features is None: return
        self.disconnect(self.ndviewer , SIGNAL('selectionChanged') , self.newSelectionInViewer )
        self.ndviewer.changeSelection(ind)
        self.connect(self.ndviewer , SIGNAL('selectionChanged') , self.newSelectionInViewer )

    def rigthClickOnNDViewer(self,event):
        #~ print 'rigthClickOnNDViewer', self.ndviewer.canvas.widgetlock.locked()
        if hasattr(self.ndviewer, 'lasso'): return
        if self.ndviewer.canvas.widgetlock.locked(): return
        if event.button == 3: 
            menu = QMenu()
            act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Move selection to trash'))
            act.triggered.connect(self.moveSpikeToTrash)
            act = menu.addAction(QIcon(':/merge.png'), self.tr('Group selection in one unit'))
            act.triggered.connect(self.createNewClusterWithSpikes)
            menu.exec_(self.cursor().pos())
    
    def moveSpikeToTrash(self):
        ind = self.ndviewer.actualSelection
        self.spikesorter.spikeLabels[ ind ]= -1
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))

    def createNewClusterWithSpikes(self):
        ind = self.ndviewer.actualSelection
        self.spikesorter.spikeLabels[ ind ]= max(self.spikesorter.allLabels)+1
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))





class FeaturesParallelPlot(QWidget, SpikeSortingBase):
    name = 'Features Parallel Plot'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']

    plotParamDefault =  [
                                        [ 'max_lines' , { 'value' : 60  }],
                                    ]

    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        SpikeSortingBase.__init__(self,  plotParams = None)
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)


        self.canvas = SimpleCanvasAndTool()
        mainLayout.addWidget(self.canvas)
        self.ax = self.canvas.fig.add_subplot(1,1,1)
        mainLayout.addWidget(self.canvas)
        
        act = self.canvas.toolbar.addAction(QIcon(':/configure.png'), 'Configure')
        act.triggered.connect(self.changePlotOptions)


        #TODO
        #~ self.plotParams = { }
        #~ self.plotParams['max_lines'] = 60

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.features is None : return
            
        self.ax.clear()
        for c in sps.allLabels:
            ind = sps.shuffledSpikeSubset[c]
            if ind.size>self.plotParams['max_lines']:
                ind = ind[:self.plotParams['max_lines']]
            self.ax.plot( sps.features[ind,:].transpose() , 
                                                color = sps.colors[c],
                                                )
        self.canvas.draw()


class Features3D(QWidget, SpikeSortingBase):
    name = 'Features 3D'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    

    plotParamDefault =  [
                                        [ 'max_points_by_cluster' , {'value' : 500 }],
                                    ]
    

    
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        SpikeSortingBase.__init__(self,  plotParams = None)
        
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)


        h = QHBoxLayout()
        mainLayout.addLayout(h)

        self.butPlotParam = QPushButton(QIcon(':/configure.png'), '')
        h.addWidget(self.butPlotParam)
        self.butPlotParam.clicked.connect(self.changePlotOptions)
        h.addStretch()

        h.addWidget(QLabel('Choose dim'))
        self.combos = [ ]
        for i in range(3):
            cb = QComboBox()
            self.combos.append(cb)
            cb.activated.connect(self.change_dim)
            h.addWidget(cb)

        self.canvas = SimpleCanvas()
        self.ax = Axes3D(self.canvas.fig)
        mainLayout.addWidget( self.canvas )



        # TODO :params
        #~ self.plotParams = { }
        #~ self.plotParams['max_points_by_cluster'] = 500


    def change_dim(self, index = None):
        sps = self.spikesorter
        if sps.features is None : return
        self.ax.clear()
        vects = [ ]
        for i in range(3):
            ind = self.combos[i].currentIndex()
            vects.append( sps.features[:,ind] )
        
        for c in sps.allLabels:
            ind = sps.shuffledSpikeSubset[c]
            if ind.size>self.plotParams['max_points_by_cluster']:
                ind = ind[:self.plotParams['max_points_by_cluster']]
            if ind.size>0:
                self.ax.scatter(vects[0][ind], vects[1][ind], vects[2][ind], 
                                                color = sps.colors[c],
                                                )
        self.canvas.draw()

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.features is None : return
        
        ndim = sps.features.shape[1]
        for i in range(3):
            self.combos[i].clear()
            self.combos[i].addItems( [ str(n) for n in range(ndim) ] )
            if i<ndim:
                self.combos[i].setCurrentIndex(i)
        
        self.change_dim()


class FeaturesWilsonPlot(QWidget):
    name = 'Features Wilson Plot'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)


        self.canvas = SimpleCanvasAndTool()
        mainLayout.addWidget( self.canvas )

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.features is None : return
        
        ndim = sps.features.shape[1]
        ndim2 = min(ndim, 16)
        self.canvas.fig.clear()
        if sps.features.shape[1]>1:
            for c in sps.allLabels:
                #~ ind = c==sps.spikeLabels
                ind = sps.shuffledSpikeSubset[c]
                for i in range(ndim2):
                    for j in range(i+1, ndim2):
                        p = (j-1)*(ndim2-1)+i+1
                        ax = self.canvas.fig.add_subplot(ndim2-1, ndim2-1, p)
                        ax.plot(sps.features[ind,i], sps.features[ind,j], 
                                                        marker = '.',
                                                        linestyle = 'None',
                                                        color = sps.colors[c]
                                                        ) 
                        #ax.set_title('%d %d'%(i,j))
                        if i==0:
                            ax.set_ylabel( str(j) )
                        if j==ndim-1:
                            ax.set_xlabel( str(i) )
                        ax.set_xticks([ ])
                        ax.set_yticks([ ])
        self.canvas.draw()


class ModelSpikeList(QAbstractItemModel):
    """
    Implementation of a treemodel for a long spike list
    """
    def __init__(self, parent =None ,
                        spikesorter = None,
                        ) :
        QAbstractItemModel.__init__(self,parent)
        self.spikesorter = spikesorter
        
        self.icons = { }
        for c in self.spikesorter.allLabels:
            pix = QPixmap(10,10 )
            r,g,b = self.spikesorter.colors[c]
            pix.fill(QColor( r*255,g*255,b*255  ))
            self.icons[c] = QIcon(pix)
        
        self.icons[-1] = QIcon(':/user-trash.png')
        
    def columnCount(self , parentIndex):
        return 3
        
    def rowCount(self, parentIndex):
        if not parentIndex.isValid():
            if self.spikesorter.spikeTimes is not None:
                return self.spikesorter.spikeTimes.size
            else:
                return 0
        else :
            return 0
        
    def index(self, row, column, parentIndex):
        if not parentIndex.isValid():
            if column==0:
                childItem = row
            elif column==1:
                childItem = self.spikesorter.spikeTimes[row]
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
                return QVariant(str(self.spikesorter.spikeTimes[row]))
            elif col == 2:
                if self.spikesorter.spikeLabels is None or self.spikesorter.shuffledSpikeSubset is None:
                    return QVariant(str())
                else:
                    c = self.spikesorter.spikeLabels[row]
                    return QVariant( str(row in self.spikesorter.shuffledSpikeSubset[c]) )
            else:
                return QVariant()
        elif role == Qt.DecorationRole :
            if col == 0:
                return self.icons[self.spikesorter.spikeLabels[row]]
            else:
                return QVariant()
        else :
            return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled



class SpikeList(QWidget):
    name = 'Spike list'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter

    
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel('<b>All spikes</b>') )
        self.treeSpike = QTreeView()
        self.treeSpike.setMinimumWidth(100)
        self.treeSpike.setColumnWidth(0,80)
        self.treeSpike.setUniformRowHeights(True)
        mainLayout.addWidget(self.treeSpike)
        self.treeSpike.setSelectionMode( QAbstractItemView.ExtendedSelection)
        self.treeSpike.setSelectionBehavior(QTreeView.SelectRows)
        self.treeSpike.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.treeSpike.customContextMenuRequested.connect(self.contextMenuSpike)
    
    def refresh(self, step = None):
        self.modelSpike = ModelSpikeList( spikesorter = self.spikesorter)
        self.treeSpike.setModel(self.modelSpike)
        self.treeSpike.selectionModel().selectionChanged.connect(self.newSelectionInSpikeTree)

    def newSelectionInSpikeTree(self):
        ind = [ ]
        for index in self.treeSpike.selectedIndexes():
            if index.column() == 0: ind.append(index.row())
        ind = numpy.array(ind)
        self.emit( SIGNAL('SpikeSelectionChanged') , ind)
        

    def setSpikeSelection(self, ind):
        # TO avoid SIGNAL larsen 
        self.treeSpike.selectionModel().selectionChanged.disconnect(self.newSelectionInSpikeTree)
        
        # change selection
        self.treeSpike.selectionModel().clearSelection()
        flags = QItemSelectionModel.Select #| QItemSelectionModel.Rows
        itemsSelection = QItemSelection()
        if ind.size>10000:
            # only the first one because QT4 is able to handle with big selections
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

        self.treeSpike.selectionModel().selectionChanged.connect(self.newSelectionInSpikeTree)

    def contextMenuSpike(self, point):
        #~ pass
        menu = QMenu()
        act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Move selection to trash'))
        act.triggered.connect(self.moveSpikeToTrash)
        act = menu.addAction(QIcon(':/merge.png'), self.tr('Group selection in one unit'))
        act.triggered.connect(self.createNewClusterWithSpikes)
        menu.exec_(self.cursor().pos())
    
    def getSelection(self):
        l = [ ]
        for index in self.treeSpike.selectedIndexes():
            if index.column() !=0: continue
            l.append(index.row())
        ind = numpy.array(l)
        return ind
    
    def moveSpikeToTrash(self):
        ind = self.getSelection()
        self.spikesorter.spikeLabels[ ind ]= -1
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))

    def createNewClusterWithSpikes(self):
        ind = self.getSelection()
        self.spikesorter.spikeLabels[ ind ]= max(self.spikesorter.allLabels)+1
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))




    
    
    

class UnitList(QWidget):
    name = 'Unit list'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter
        self.globalApplicationDict = globalApplicationDict

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.treeNeuron = QTreeWidget()
        self.treeNeuron.setColumnCount(3)
        self.treeNeuron.setHeaderLabels(['Num', 'Nb sikes', 'Name', 'Sorting score' ])
        self.treeNeuron.setMinimumWidth(100)
        self.treeNeuron.setColumnWidth(0,60)
        mainLayout.addWidget(self.treeNeuron)
        self.treeNeuron.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeNeuron.customContextMenuRequested.connect(self.contextMenuNeuron)
        self.treeNeuron.setSelectionMode( QAbstractItemView.ExtendedSelection)


    def refresh(self, step = None):
        sps = self.spikesorter
        self.treeNeuron.clear()
        self.labels = [ ]
        for c in sps.allLabels:
            ind, = where(c==sps.spikeLabels)
            if c==-1:
                icon = QIcon(':/user-trash.png')
            else:
                pix = QPixmap(10,10 )
                r,g,b = sps.colors[c]
                pix.fill(QColor( r*255,g*255,b*255  ))
                icon = QIcon(pix)
            if c in sps.names: name = sps.names[c]
            else: name = ''
            if c in sps.sortingScores: sortingScore = sps.sortingScores[c]
            else: sortingScore = ''
            
            item = QTreeWidgetItem(["%s" % (c)  , str(ind.size), name, sortingScore  ] )
            item.setIcon(0,icon)
            self.treeNeuron.addTopLevelItem(item)
            self.labels.append(c)


    def contextMenuNeuron(self, point):
        
        
        menu = QMenu()
        act = menu.addAction(QIcon(':/window-close.png'), self.tr('Delete selection forever'))
        act.triggered.connect(self.deleteSelection)
        act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Move selection to trash'))
        act.triggered.connect(self.moveToTrash)
        act = menu.addAction(QIcon(':/merge.png'), self.tr('Group selection in one unit'))
        act.triggered.connect(self.groupSelection)
        act = menu.addAction(QIcon(':/color-picker.png'), self.tr('Select these spikes'))
        act.triggered.connect(self.selectSpikeFromCluster)
        act = menu.addAction(QIcon(':/go-jump.png'), self.tr('Regroup small units'))
        act.triggered.connect(self.regroupSmallUnits)
        act = menu.addAction(QIcon(':/TODO.png'), self.tr('Hide/Show on ndviewer and waveform'))
        act.triggered.connect(self.hideOrShowClusters)
        
        if len(self.treeNeuron.selectedIndexes()) ==  self.treeNeuron.columnCount():
            # one selected row only
            act = menu.addAction(QIcon(':/Clustering.png'), self.tr('Explode cluster (sub clustering)'))
            act.triggered.connect(self.subComputeCluster)
            act = menu.addAction(QIcon(':/TODO.png'), self.tr('Set name of this unit'))
            act.triggered.connect(self.setUnitNameAndScore)
        
        menu.exec_(self.cursor().pos())
    
    def deleteSelection(self):
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            self.spikesorter.deleteOneNeuron(self.labels[r])
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))
        
    
    def moveToTrash(self):
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            labels = self.spikesorter.spikeLabels
            labels[labels == self.labels[r]] = -1
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))
        
    def groupSelection(self):
        labels = self.spikesorter.spikeLabels
        n = max(self.spikesorter.allLabels) +1
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            labels[ labels == self.labels[r] ]= n
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))
        
    def selectSpikeFromCluster(self):
        labels = self.spikesorter.spikeLabels
        ind = numpy.array([ ], dtype = 'i')
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            a, = where( labels == self.labels[r] )
            ind = numpy.concatenate( ( ind, a))
        self.emit(SIGNAL('SpikeSelectionChanged'), ind)


    def subComputeCluster(self):
        #~ dia = QDialog(parent = self)
        dia = QDialog(self)
        v = QVBoxLayout()
        dia.setLayout(v)
        
        from ..computing.spikesorting.clustering import list_method
        
        wMeth = WidgetMultiMethodsParam(  list_method = list_method,
                                                            method_name = '<b>Choose method for clustering</b>:',
                                                            globalApplicationDict = self.globalApplicationDict,
                                                            keyformemory = 'spikesorting',
                                                            )
        v.addWidget(wMeth)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        v.addWidget(buttonBox)
        self.connect( buttonBox , SIGNAL('accepted()') , dia, SLOT('accept()') )
        self.connect( buttonBox , SIGNAL('rejected()') , dia, SLOT('close()') )
        if not dia.exec_(): return
        
        sps = self.spikesorter
        for index in self.treeNeuron.selectedIndexes():
            if index.column() != 0: continue
            r = index.row()
            sps.subComputeCluster( self.labels[r], wMeth.get_method(), **wMeth.get_dict())
        
        sps.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))
    
    def regroupSmallUnits(self):
        params = [  [ 'size' , { 'value' : 10 , 'label' : 'Regroup unit when size less than' }  ] , ]
        d =  ParamDialog(params,
                                    applicationdict = self.globalApplicationDict,
                                    keyformemory = 'spikesorting/regroupsmallunit'  ,
                                    title = 'Regroup small units',
                                    )
        if d.exec_():
            self.spikesorter.regroupSmallUnits( **d.get_dict() )
        
        self.spikesorter.refreshPlotUtilities()
        self.refresh()
        self.emit(SIGNAL('SpikeLabelsChanged'))
    
    def hideOrShowClusters(self):
        sps = self.spikesorter
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            c = self.labels[r]
            if c in sps.shuffledSpikeSubset and sps.shuffledSpikeSubset[c].size == 0:
                ind, = where( sps.spikeLabels ==c )
                random.shuffle(ind)
                if sps._max_size_by_cluster < ind.size:
                    ind = ind[:sps._max_size_by_cluster]
                sps.shuffledSpikeSubset[c]  = ind
            else:
                sps.shuffledSpikeSubset[c]  = numpy.array([ ], 'i')
            
        self.emit( SIGNAL('SpikeSubsetChanged') )
    
    def setUnitNameAndScore(self):
        sps = self.spikesorter
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            c = self.labels[r]
        
        if c in sps.names: name = sps.names[c]
        else: name = ''
        if c in sps.sortingScores: sortingScore = sps.sortingScores[c]
        else: sortingScore = ''
        
        
        params = [  [ 'name' , { 'value' :  name , 'label' : 'Name of unit %d'%(c) }  ] ,
                            [ 'sortingScore' , { 'value' :  sortingScore , 'label' : 'Sorting score of unit %d'%(c) }  ] ,
                            ]
        d =  ParamDialog(params,
                                    applicationdict = self.globalApplicationDict,
                                    #~ keyformemory = 'spikesorting/regroupsmallunit'  ,
                                    title = 'Name',
                                    )
        if d.exec_():
            d.get_dict()['name']
            sps.names[c] = d.get_dict()['name']
            sps.sortingScores[c] = d.get_dict()['sortingScore']
            
            
            
        self.refresh()




class PlotIsi(QWidget, SpikeSortingBase):
    name = 'Inter-Spike Interval'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    icon_name = 'plot-isi.png'


    plotParamDefault =  [
                                        [ 'bin_width' , {'value' : 5. , 'label' : 'bin width (ms)'}],
                                        [ 'limit' , {'value' : 100.,  'label' : 'limit (ms)'}],
                                        [ 'plot_type' , {'value' : 'bar', 'possible' : ['bar', 'line'] }],
                                    ]
    
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        SpikeSortingBase.__init__(self,  plotParams = None)
        
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        self.butPlotParam = QPushButton(QIcon(':/configure.png'), '')
        h.addWidget(self.butPlotParam)
        self.butPlotParam.clicked.connect(self.changePlotOptions)
        
        h.addStretch()
        
        self.combo = QComboBox()
        h.addWidget( self.combo )
        self.combo.currentIndexChanged.connect( self.comboChanged )
        
        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        self.ax = self.fig.add_subplot(1,1,1)
        mainLayout.addWidget(self.canvas)
        

        #TODO
        #~ self.plotParams = { }
        #~ self.plotParams['bin_width'] = 5.
        #~ self.plotParams['limit'] = 100.
        #~ self.plotParams['plot_type'] = 'bar'

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.spikeTimes is None : return
        self.combo.clear()
        self.combo.addItems( ['Neuron %d' %c for c in  sps.allLabels ])
        
    def comboChanged(self, ind):
        
        sps = self.spikesorter
        if sps.spikeLabels is None: return
        c = sps.allLabels[ind]
        self.ax.clear()

        width = self.plotParams['bin_width']/1000.
        limit = self.plotParams['limit']/1000.
        st = sps.spikeTimes[c== sps.spikeLabels]
        #~ st.sort()
        y,x = numpy.histogram(numpy.diff(st), bins = numpy.arange(0,limit, width))
        if self.plotParams['plot_type'] == 'bar':
            self.ax.bar(x[:-1]*1000, y, width =width*1000, color = sps.colors[c])
        elif self.plotParams['plot_type'] == 'line':
            self.ax.plot(x[:-1]*1000, y,  color = sps.colors[c])
        self.ax.set_xlim(0, limit*1000.)
        self.canvas.draw()
        
        
def correlogram(t1, t2=None, bin_width=.001, limit=.02, auto=False):
    """Return crosscorrelogram of two spike trains.
    
    Essentially, this algorithm subtracts each spike time in `t1` 
    from all of `t2` and bins the results with numpy.histogram, though
    several tweaks were made for efficiency.
    
    Arguments
    ---------
        t1 : first spiketrain, raw spike times in seconds.
        t2 : second spiketrain, raw spike times in seconds.
        bin_width : width of each bar in histogram in sec
        limit : positive and negative extent of histogram, in seconds
        auto : if True, then returns autocorrelogram of `t1` and in
            this case `t2` can be None.
    
    Returns
    -------
        (count, bins) : a tuple containing the bin edges (in seconds) and the
        count of spikes in each bin.

        `bins` is relative to `t1`. That is, if `t1` leads `t2`, then
        `count` will peak in a positive time bin.
    """
    # For auto-CCGs, make sure we use the same exact values
    # Otherwise numerical issues may arise when we compensate for zeros later
    if auto: t2 = t1

    # For efficiency, `t1` should be no longer than `t2`
    swap_args = False
    if len(t1) > len(t2):
        swap_args = True
        t1, t2 = t2, t1

    # Sort both arguments (this takes negligible time)
    t1 = np.sort(t1)
    t2 = np.sort(t2)

    # Determine the bin edges for the histogram
    # Later we will rely on the symmetry of `bins` for undoing `swap_args`
    limit = float(limit)
    bins = np.linspace(-limit, limit, num=(2 * limit/bin_width + 1))

    # This is the old way to calculate bin edges. I think it is more
    # sensitive to numerical error. The new way may slightly change the
    # way that spikes near the bin edges are assigned.
    #bins = np.arange(-limit, limit + bin_width, bin_width)

    # Determine the indexes into `t2` that are relevant for each spike in `t1`
    ii2 = numpy.searchsorted(t2, t1 - limit)
    jj2 = numpy.searchsorted(t2, t1 + limit)

    # Concatenate the recentered spike times into a big array
    # We have excluded spikes outside of the histogram range to limit
    # memory use here.
    big = np.concatenate([t2[i:j] - t for t, i, j in zip(t1, ii2, jj2)])

    # Actually do the histogram. Note that calls to numpy.histogram are
    # expensive because it does not assume sorted data.
    count, bins = np.histogram(big, bins=bins)

    if auto:
        # Compensate for the peak at time zero that results in autocorrelations
        # by subtracting the total number of spikes from that bin. Note
        # possible numerical issue here because 0.0 may fall at a bin edge.
        c_temp, bins_temp = np.histogram([0.], bins=bins)
        bin_containing_zero = numpy.nonzero(c_temp)[0][0]
        count[bin_containing_zero] -= len(t1)

    # Finally compensate for the swapping of t1 and t2
    if swap_args:
        # Here we rely on being able to simply reverse `counts`. This is only
        # possible because of the way `bins` was defined (bins = -bins[::-1])
        count = count[::-1]

    return count, bins


class PlotCrossCorrelogram(QWidget, SpikeSortingBase):
    name = 'Cross-correlogram'
    #~ refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']
    refresh_on = [  'Detection' ,   'Clustering']
    icon_name = 'plot-crosscorrelogram.png'

    plotParamDefault =  [
                                        [ 'bin_width' , {'value' : 5. , 'label' : 'bin width (ms)'}],
                                        [ 'limit' , {'value' : 100.,  'label' : 'limit (ms)'}],
                                        [ 'plot_type' , {'value' : 'bar', 'possible' : ['bar', 'line'] }],
                                    ]
    
    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        SpikeSortingBase.__init__(self,  plotParams = None)
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        
        
        #self.butPlotParam = QPushButton(QIcon(':/configure.png'), '', parent  = self)
        self.butPlotParam = QPushButton(QIcon(':/configure.png'), '',  self)
        
        h.addWidget(self.butPlotParam)
        self.butPlotParam.clicked.connect(self.changePlotOptions)
        
        h.addStretch()

        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)



        #TODO
        #~ self.plotParams = { }
        #~ self.plotParams['bin_width'] = 5.
        #~ self.plotParams['limit'] = 100.
        #~ self.plotParams['plot_type'] = 'bar'
        self.threadRefresh = None


    def refresh(self, step = None):
        self.threadRefresh = ThreadRefresh(widgetToRefresh = self)
        self.threadRefresh.start()
        
        
    def refresh_background(self):
        sps = self.spikesorter
        if sps.spikeLabels is None : return
        
        # ms to s
        bin_width = self.plotParams['bin_width']/1000.
        limit = self.plotParams['limit']/1000.
         
        n = len(sps.allLabels)
        self.canvas.fig.clear()
        for i in range(n):
            t1 = sps.spikeTimes[ sps.spikeLabels == sps.allLabels[i] ]
            for j in range(i,n):
                delta = .05
                ax = self.canvas.fig.add_axes([delta/4.+i*1./n, delta/4.+j*1./n  ,(1.-delta)/n, (1.-delta)/n])
                t2 = sps.spikeTimes[ sps.spikeLabels == sps.allLabels[j] ]
                count, bins = correlogram(t1,t2, bin_width = bin_width, limit = limit , auto = i==j)
                if i==j:
                    #~ count[count.size//2-1]=0
                    color =  sps.colors[ sps.allLabels[i] ]
                else:
                    color = 'k'

                if self.plotParams['plot_type'] == 'bar':
                    ax.bar(bins[:-1]+bin_width/2., count , width = bin_width, color = color)
                elif self.plotParams['plot_type'] == 'line':
                    ax.plot(bins[:-1]+bin_width/2., count , color = color)
                ax.set_xlim(-limit, limit)
                
                if i!=j: ax.set_xticks([])
                if i!=0: ax.set_yticks([])
                
        self.canvas.draw()




class FeaturesEvolutionInTime(QWidget, SpikeSortingBase):
    name = 'Evolution of features over time'
    refresh_on = [  'Detection' ,  'Features' , 'Clustering']
    icon_name = 'office-chart-line.png'
    
    plotParamDefault =  [
                                        [ 'plot_type' , {'value' : 'amplitude', 'possible' : [ 'amplitude' ] }],
                                    ]


    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        SpikeSortingBase.__init__(self,  plotParams = None)
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)

        #TODO
        #~ self.plotParams = { }
        #~ self.plotParams[ 'plot_type' ] = 'amplitude'



    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.spikeLabels is None : return
        if sps.waveforms is None : return
        
        if self.plotParams[ 'plot_type' ] == 'amplitude':
            if sps.spikeSign =='+':
                amplitudes = numpy.amax(sps.waveforms, axis = 2)
            elif sps.spikeSign =='-':
                amplitudes = numpy.amin(sps.waveforms, axis = 2)
            elif sps.spikeSign ==None:
                amplitudes = numpy.amax(abs(sps.waveforms), axis = 2)
        
        
        self.fig.clear()
        self.axs = [ ]
        ax = None
        for i in range(sps.trodness):
            ax = self.fig.add_subplot(  sps.trodness, 1,  i+1 , sharex = ax)
            self.axs.append( ax )
            
        # plots
        for i in range(sps.trodness):
            ax = self.axs[i]
            ax.clear()
            for c in sps.allLabels:
                ind = c==sps.spikeLabels
        
        
        for c  in sps.allLabels:
            ind =  sps.spikeLabels == c
            x = sps.spikeTimes[ind]
            
            if self.plotParams[ 'plot_type' ] == 'amplitude':
                for i in range(sps.trodness):
                    self.axs[i].plot(x, amplitudes[ind,i], color = sps.colors[c], linestyle = '--', marker = '.')
        
        self.canvas.draw()




class Summary(QWidget):
    name = 'Summary'
    refresh_on = [  'Detection' , 'Extraction' , 'Features' , 'Clustering']

    def __init__(self, parent=None ,
                        spikesorter = None,
                        globalApplicationDict= None,
                        ):
        QWidget.__init__(self,parent )
        self.spikesorter = spikesorter

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        self.label = QLabel('Block id:%d name:%s trodness:%d' % ( self.spikesorter.block.id, self.spikesorter.block.name, self.spikesorter.trodness) )
        mainLayout.addWidget( self.label )
        
        g = QGridLayout()
        mainLayout.addLayout( g )

        if self.spikesorter.mode != 'from_detected_spike':
            self.labelSignal = QLabel('AnalogSignal')
            g.addWidget( self.labelSignal, 0,0)
            self.tableSignal = QTableWidget()
            g.addWidget( self.tableSignal , 1,0)

        self.labelSipkeTrain = QLabel('SpikeTrain')
        g.addWidget( self.labelSipkeTrain, 0,1)
        self.tableSpikeTrain = QTableWidget()
        g.addWidget( self.tableSpikeTrain, 1,1 )


    def refresh(self, step = None):
        sps = self.spikesorter
        
        if sps.spikeLabels is not None:
            n_neurons = len( sps.allLabels)
        else:
            n_neurons = 0
        n_segments = len(sps.id_segments)

        # signal
        if self.spikesorter.mode != 'from_detected_spike':
            self.tableSignal.clear()
            self.tableSignal.setRowCount(len(sps.recordingPointList))
            self.tableSignal.setColumnCount(n_segments)
            #~ for i, seg in enumerate(sps.block._segments) :
            for i, id_segment in enumerate(sps.id_segments):
                item = QTableWidgetItem('Seg %d'%id_segment)
                self.tableSignal.setHorizontalHeaderItem( i, item)
            for j,rp  in enumerate(sps.recordingPointList):
                item = QTableWidgetItem('RecPt\n id:%d\n channel:%d'% (rp.id, rp.channel) )
                self.tableSignal.setVerticalHeaderItem( j, item)
            #~ for i, seg in enumerate(sps.block._segments) :
            for i, id_segment in enumerate(sps.id_segments):
                for j,rp  in enumerate(sps.recordingPointList):
                    if self.spikesorter.mode == 'from_full_band_signal':
                        ana = sps.anaSigList[i][j]
                    elif self.spikesorter.mode == 'from_filtered_signal':
                        ana = sps.anaSigFilteredList[i][j]
                    item = QTableWidgetItem(QIcon(), 'AnalogSignal\n id:%d\n size:%d\n duration:%.1fs.'% (ana.id, ana.signal.size, ana.signal.size/ana.sampling_rate) )
                    self.tableSignal.setItem(j, i , item )
        self.tableSignal.resizeColumnsToContents()
        self.tableSignal.resizeRowsToContents()


        #table neurons
        self.tableSpikeTrain.clear()
        self.tableSpikeTrain.setRowCount(n_neurons)
        self.tableSpikeTrain.setColumnCount(n_segments)
        #~ for i, seg in enumerate(sps.block._segments) :
        for i, id_segment in enumerate(sps.id_segments):
            item = QTableWidgetItem('Seg %d'%id_segment)
            self.tableSpikeTrain.setHorizontalHeaderItem( i, item)
        for j,c  in enumerate(sps.allLabels):
            #~ nb = sum(sps.spikeLabels==c)
            nb = where(sps.spikeLabels==c)[0].size
            item = QTableWidgetItem('Neuron :%d\n nb:%d\n '%(c,nb) , )
            self.tableSpikeTrain.setVerticalHeaderItem( j, item)        
        
        p=0
        pos = numpy.array([])
        #~ for i, seg in enumerate(sps.block._segments) :
        for i, id_segment in enumerate(sps.id_segments):
            for j,c  in enumerate(sps.allLabels):
                if self.spikesorter.mode == 'from_detected_spike':
                    ind, = where( (sps.spikeLabels == c) & ( seg.id == sps.id_segments) )
                    nb_spikes= ind.size
                else:
                    pos = sps.spikePosistionList[i]
                    labels = sps.spikeLabels[p:p+pos.size]
                    ind, = where(labels == c)
                    nb_spikes = ind.size
                pix = QPixmap(10,10 )
                r,g,b = sps.colors[c]
                pix.fill(QColor( r*255,g*255,b*255  ))
                icon = QIcon(pix)
                item = QTableWidgetItem(icon, 'Nb spikes %d'% nb_spikes)
                self.tableSpikeTrain.setItem(j, i , item )
            p += pos.size
        self.tableSpikeTrain.resizeColumnsToContents()
        self.tableSpikeTrain.resizeRowsToContents()


spikesortingwidgets = [ FullBandSignal , FilteredSignal , AllWaveforms, AverageWaveforms, SignalStatistics,
                                        FeaturesNDViewer, FeaturesParallelPlot, Features3D , FeaturesWilsonPlot,
                                        SpikeList, UnitList,
                                        PlotIsi,PlotCrossCorrelogram, FeaturesEvolutionInTime,
                                        Summary,
                                        ]






