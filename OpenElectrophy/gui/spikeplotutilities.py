# -*- coding: utf-8 -*-


"""

Set of utilities for plotting spiketrain features used for the spikesorting window

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
#~ from guiutil.globalapplicationdict import *
from guiutil.paramwidget import ParamWidget, LimitWidget, ParamDialog
from guiutil.multiparamwidget import WidgetMultiMethodsParam
#~ from enhancedmatplotlib import *


from numpy import unique, ones, mean, std, arange, where, random, unique
from enhancedmatplotlib import SimpleCanvasAndTool,  SimpleCanvas

#~ from sqlalchemy import and_, or_
from matplotlib.colors import ColorConverter
from matplotlib.cm import get_cmap



class PlotBase():
    """
    Common base for spike plotting utilities
    """
    def __init__(self,
                            plotParams = None,
                            ):
        self.plotParams = plotParams
        if self.plotParams is None:
            self.plotParams = ParamWidget(self.plotParamDefault).get_dict()        
    
    def changePlotOptions(self):
        dia = ParamDialog(self.plotParamDefault , 
                    #~ keyformemory = 'imageserieviewer/plot' ,
                    #~ applicationdict = self.globalApplicationDict,
                    title = 'Plot parameters',
                    )
        dia.param_widget.update( self.plotParams )
        ok = dia.exec_()
        if  ok ==  QDialog.Accepted:
            self.plotParams = dia.param_widget.get_dict()
        
        self.refresh()







class PlotWaveform(QWidget , PlotBase):
    """
    widget to plot waveforms
    """
    plotParamDefault =  [
                        [ 'plot_average' , {'value' : True }],
                        [ 'plot_individual' , {'value' : True }],
                        [ 'max_waveform_by_cluster' , {'value' : 10 }],
                    ]
    def __init__(self , parent=None ,
                        waveforms = None,
                        sorted = None,
                        
                        colors = None,
                        show_button = True,
                        plotParams = None,
                        
                        
                        ):
        QWidget.__init__(self,parent )
        PlotBase.__init__(self,plotParams = plotParams)
        
        self.colors = colors

        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        
        #~ self.canvas = SimpleCanvasAndTool(orientation = Qt.Horizontal )
        self.canvas = SimpleCanvas( )
        self.fig = self.canvas.fig
        mainLayout.addWidget(self.canvas)
        
        if show_button:
            #~ but = QPushButton('',parent = self.canvas.canvas)
            but = QPushButton('',self.canvas)
            but.setIcon(QIcon(':/configure.png'))
            but.setGeometry(10,10,30,30)
            self.canvas.stackUnder(but)
            self.connect(but, SIGNAL('clicked()') , self.changePlotOptions)
        
        self.trodness = None
        self.changeData(waveforms , sorted = sorted )
    
    def refresh(self):
        self.changeData(self.waveforms)
    
    def changeData(self, waveforms, sorted = None , colors = None):
        if waveforms is None : return
        self.waveforms = waveforms
        # sorted
        if sorted is not None:
            self.sorted = sorted
        if self.sorted is None:
            self.sorted = ones( waveforms.shape[0] , dtype = 'i')
        # colors
        if colors is not None:
            self.colors = colors
        if self.colors is None:
            self.colors = { }
            cmap = get_cmap('jet', unique(self.sorted).size+3)
            for i,c in enumerate(unique(self.sorted)):
                self.colors[c] = cmap(i+2)
        
        # recreate axes
        #~ if self.trodness != waveforms.shape[1]:
        if 1:
            self.trodness = waveforms.shape[1]
            self.fig.clear()
            if self.plotParams['plot_individual'] and self.plotParams['plot_average']: n = 2
            elif self.plotParams['plot_individual'] or self.plotParams['plot_average']: n = 1
            else: return
            self.ax_indi = [ ]
            j = 0
            ax = None
            if self.plotParams['plot_individual']:
                for i in range(self.trodness):
                    j+=1
                    ax = self.fig.add_subplot( n, self.trodness, j , sharex = ax, sharey = ax)
                    self.ax_indi.append( ax )
            ax = None
            self.ax_aver = [ ]
            if self.plotParams['plot_average']:
                for i in range(self.trodness):
                    j+=1
                    ax = self.fig.add_subplot( n, self.trodness, j , sharex = ax, sharey = ax)
                    self.ax_aver.append( ax )
        
        
        # plots
        for i in range(self.trodness):
            
            # individual
            if self.plotParams['plot_individual']:
                ax = self.ax_indi[i]
                ax.clear()
                for c in unique(self.sorted):
                    ind ,  = where(self.sorted ==c)
                    step = 1.*len(ind)/self.plotParams['max_waveform_by_cluster']
                    if step<=1. :
                        start = 0
                        step = 1
                    else:
                        step = int(step)
                        start = int(random.rand()*step)
                    ax.plot( waveforms[ind[start::step], i,  :].transpose(), 
                                                    color = self.colors[c],
                                                    )            
                
                # average
            if self.plotParams['plot_average']:
                ax = self.ax_aver[i]
                ax.clear()
                for c in unique(self.sorted):
                    ind = c==self.sorted
                    m  = mean(waveforms[ind,i,:], axis = 0)
                    sd = std(waveforms[ind,i,:], axis = 0)
                    ax.plot( m, 
                                        linewidth=2,
                                        color = self.colors[c],
                                        )
                    ax.fill_between(arange(m.size), m-sd, m+sd ,
                                        color = self.colors[c],
                                        alpha = .3)
    
        self.canvas.draw()




class PlotISI(QWidget , PlotBase):
    """
    widget to plot ISI (inter spike interval)
    """
    plotParamDefault =  [ 
                                [ 'plot_type' , {'value' : 'bar' , 'possible' : [ 'bar' , 'line']  }],
                                [ 'bin_width' , {'value' : 2.  , 'label' : 'bin width (ms)'}],
                                [ 'limit' , {'value' : 500.  , 'label' : 'max limit (ms)'}],
                        
                    ]
    
    def __init__(self , parent=None ,
                        
                        spike_times = None,
                        sorted = None,
                        colors = None,
                        
                        show_button = True,
                        plotParams = None,
                        
                        
                        ):
        QWidget.__init__(self,parent )
        PlotBase.__init__(self,plotParams = plotParams)

        
        self.colors = colors

        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        self.combo = QComboBox()
        mainLayout.addWidget( self.combo )
        self.connect( self.combo, SIGNAL('currentIndexChanged( int )') , self.comboChanged )
        
        self.canvas = SimpleCanvasAndTool(orientation = Qt.Horizontal )
        self.fig = self.canvas.fig
        self.ax = self.fig.add_subplot(1,1,1)
        mainLayout.addWidget(self.canvas)
        
        if show_button:
            but = QPushButton('',parent = self.canvas.canvas)
            #~ but = QPushButton('',parent = self.canvas)
            but.setIcon(QIcon(':/configure.png'))
            but.setGeometry(10,10,30,30)
            self.canvas.stackUnder(but)
            self.connect(but, SIGNAL('clicked()') , self.changePlotOptions)
        
        self.changeData(spike_times , sorted = sorted )
        
    
    def refresh(self):
        self.changeData(self.spike_times)
    
    def changeData(self, spike_times , sorted = None , colors = None):
        if spike_times is None : return
        self.spike_times = spike_times
        
        # sorted
        if sorted is not None:
            self.sorted = sorted
        if self.sorted is None:
            self.sorted = ones( waveforms.shape[0] , dtype = 'i')
        # colors
        if colors is not None:
            self.colors = colors
        if self.colors is None:
            self.colors = { }
            cmap = get_cmap('jet', unique(self.sorted).size+3)
            for i,c in enumerate(unique(self.sorted)):
                self.colors[c] = cmap(i+2)
        
        
        # combobox
        self.combo.clear()
        self.allNeurons = unique(self.sorted)
        self.combo.addItems( ['Neuron %d' %c for c in  self.allNeurons ])
        
            
        
        

    def comboChanged(self, ind):
        c = self.allNeurons[ind]
        self.ax.clear()

        width = self.plotParams['bin_width']/1000.
        limit = self.plotParams['limit']/1000.
        st = self.spike_times[c==self.sorted]
        #~ st.sort()
        y,x = numpy.histogram(numpy.diff(st), bins = numpy.arange(0,limit, width))
        
        if self.plotParams['plot_type'] == 'bar':
            self.ax.bar(x[:-1]*1000, y, width =width*1000, color = self.colors[c])
        elif self.plotParams['plot_type'] == 'line':
            self.ax.plot(x[:-1]*1000, y,  color = self.colors[c])
        
        self.ax.set_xlim(0, limit*1000.)


        
        self.canvas.draw()



class PlotCrossCorrelogram(QWidget , PlotBase):
    """
    widget to plot PlotCrossCorrelogram
    """
    plotParamDefault =  [ 
                                [ 'plot_type' , {'value' : 'line' , 'possible' : [ 'bar' , 'line']  }],
                                [ 'bin_width' , {'value' : 2.  , 'label' : 'bin width (ms)'}],
                                [ 'limit' , {'value' : 500.  , 'label' : 'max limit (ms)'}],
                                
                                [ 'exact' , {'value' :False  , 'label' : 'Compute exact crosscorrelogram'}],
                                [ 'max_spike' , {'value' :300  , 'label' : 'Otherwise bootstrap with'}],
                                
                        
                    ]
    
    def __init__(self , parent=None ,
                        
                        spike_times = None,
                        sorted = None,
                        colors = None,
                        
                        show_button = True,
                        plotParams = None,
                        
                        
                        ):
        QWidget.__init__(self,parent )
        PlotBase.__init__(self,plotParams = plotParams)

        
        self.colors = colors

        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        self.combo1 = QComboBox()
        h.addWidget( self.combo1 )
        self.connect( self.combo1, SIGNAL('currentIndexChanged( int )') , self.comboChanged )
        self.combo2 = QComboBox()
        h.addWidget( self.combo2 )
        self.connect( self.combo2, SIGNAL('currentIndexChanged( int )') , self.comboChanged )
        
        
        
        self.canvas = SimpleCanvasAndTool(orientation = Qt.Horizontal )
        self.fig = self.canvas.fig
        self.ax = self.fig.add_subplot(1,1,1)
        mainLayout.addWidget(self.canvas)
        
        if show_button:
            but = QPushButton('',self.canvas.canvas)
            #~ but = QPushButton('',parent = self.canvas)
            but.setIcon(QIcon(':/configure.png'))
            but.setGeometry(10,10,30,30)
            self.canvas.stackUnder(but)
            self.connect(but, SIGNAL('clicked()') , self.changePlotOptions)
        
        self.changeData(spike_times , sorted = sorted )
        
    
    def refresh(self):
        self.changeData(self.spike_times)
    
    def changeData(self, spike_times , sorted = None , colors = None):
        if spike_times is None : return
        self.spike_times = spike_times
        
        # sorted
        if sorted is not None:
            self.sorted = sorted
        if self.sorted is None:
            self.sorted = ones( waveforms.shape[0] , dtype = 'i')
        # colors
        if colors is not None:
            self.colors = colors
        if self.colors is None:
            self.colors = { }
            cmap = get_cmap('jet', unique(self.sorted).size+3)
            for i,c in enumerate(unique(self.sorted)):
                self.colors[c] = cmap(i+2)
        
        
        # combobox
        self.allNeurons = unique(self.sorted)
        self.combo1.clear()
        self.combo1.addItems( ['Neuron %d' %c for c in  self.allNeurons ])

        self.combo2.clear()
        self.combo2.addItems( ['Neuron %d' %c for c in  self.allNeurons ])
        
        

            
        
        

    def comboChanged(self, ind):
        c1 = self.allNeurons[self.combo1.currentIndex()]
        c2 = self.allNeurons[self.combo2.currentIndex()]
        
        self.ax.clear()

        width = self.plotParams['bin_width']/1000.
        limit = self.plotParams['limit']/1000.
        
        # corss correlogram
        
        t1 = self.spike_times[c1==self.sorted]
        t2 = self.spike_times[c2==self.sorted]
        
        if not(self.plotParams['exact']):
            
            max_spike = self.plotParams['max_spike']
            t1 = t1[unique(random.randint(0,high = t1.size, size = max_spike))]
            t2 = t2[unique(random.randint(0,high = t2.size, size = max_spike))]
        
        m1 = numpy.tile(t1[:,numpy.newaxis] , (1,t2.size) )
        m2 = numpy.tile(t2[numpy.newaxis,:] , (t1.size,1) )
        m = m2-m1
        m = m.flatten()
        #~ m = m.reshape(m.size)
        

        y,x = numpy.histogram(m, bins = numpy.arange(-limit,limit, width))
        
        if self.plotParams['plot_type'] == 'bar':
            self.ax.bar(x[:-1]*1000, y, width =width*1000)
        elif self.plotParams['plot_type'] == 'line':
            self.ax.plot(x[:-1]*1000, y )
        
        self.ax.set_xlim(-limit*1000., limit*1000.)


        
        self.canvas.draw()



