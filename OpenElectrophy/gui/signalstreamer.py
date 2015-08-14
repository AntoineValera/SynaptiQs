# -*- coding: utf-8 -*-


"""

This module provide a widget for streaming with a slider a ver y long signal.

It is base on guiqwt.



"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
from guiutil.paramwidget import ParamWidget, LimitWidget, ParamDialog

from guiqwt.curve import CurvePlot, CurveItem
from guiqwt.styles import CurveParam
from guiqwt.builder import make


import numpy as np
from numpy import log10, zeros_like




class SignalAndSpikeStreamer(QWidget):
    """
    Use by spike sorting 
    
    """
    def __init__(self, parent=None,
                        
                        
                        
                        view_duration = 10.,
                        t_start = 0.,
                        zoom_limit = (0.001, 100),
                        
                        analogsignals = None,
                        spiketrains = None,
                        vlimits = None,
                        nplot = 1,
                        
                        
                        ):
        QWidget.__init__(self, parent)
        
        self.zoom_limit = zoom_limit
        
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.analogsignals =analogsignals
        self.spiketrains = spiketrains
        self.vlimits = vlimits
        self.nplot = nplot
        
        self.selectedspikes = [ ]
        
        self.plots = [ ]
        for i in range(nplot):
            plot = CurvePlot()
            self.mainlayout.addWidget(plot)
            self.plots.append(plot)
            plot.del_all_items(except_grid=False)
            # TODO :
            # xaxis off fo i>0
        
        self.x_min,self.x_max = 0., 60.
        self.y_min , self.y_max = -1., 1.
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        # position
        h.addWidget(QLabel('Pos'))
        self.hslider = QSlider(Qt.Horizontal)
        self.hslider.setMaximum(1000)
        h.addWidget(self.hslider,6)
        #self.hspinbox = QDoubleSpinBox(decimals=3, minimum = -np.inf, maximum =np.inf, value = 0.)
        self.hspinbox = QDoubleSpinBox()
        self.hspinbox.setDecimals(3)
        self.hspinbox.setMinimum( -np.inf)
        self.hspinbox.setMaximum( np.inf)
        self.hspinbox.setValue( 0.)
        h.addWidget(self.hspinbox,3)
        #self.popupStep = QToolButton(popupMode = QToolButton.MenuButtonPopup, toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        self.popupStep = QToolButton( )
        self.popupStep.setPopupMode( QToolButton.MenuButtonPopup )
        self.popupStep.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        self.popupStep.setText('step')
        h.addWidget(self.popupStep)
        h.addSpacing(20)
        self.hslider.valueChanged.connect(self.hsliderChanged)
        self.hspinbox.valueChanged.connect(self.refresh)
        #~ self.actPopup = [ ]
        #ag = QActionGroup(self.popupStep, exclusive = True)
        ag = QActionGroup(self.popupStep )
        ag.setExclusive( True)
        
        for s in ['60s','10s', '1s', '100ms', '5ms' ]:
            #act = QAction(s, self.popupStep, checkable = True)
            act = QAction(s, self.popupStep)
            act.setCheckable( True)
            ag.addAction(act)
            self.popupStep.addAction(act)
        ag.triggered.connect(self.changeHStep)
        
        #H zoom factor
        h.addWidget(QLabel('HZoom'))
        #self.hzslider= QSlider(Qt.Horizontal, minimum = 0, maximum = 100,)
        self.hzslider= QSlider(Qt.Horizontal)
        self.hzslider.setMinimum( 0 )
        self.hzslider.setMaximum( 100)
        h.addWidget(self.hzslider,1)
        self.hzslider.valueChanged.connect(self.hzsliderChanged)
        #self.hzspinbox = QDoubleSpinBox(decimals=5,value=1., singleStep = .1,
        #                                                minimum = self.zoom_limit[0], maximum = self.zoom_limit[1],)
        self.hzspinbox = QDoubleSpinBox( )
        
        self.hzspinbox.setDecimals(5)
        self.hzspinbox.setValue(1.)
        self.hzspinbox.setSingleStep( .1 )
        self.hzspinbox.setMinimum(self.zoom_limit[0])
        self.hzspinbox.setMaximum( self.zoom_limit[1])
        h.addWidget(self.hzspinbox) 
        self.hzspinbox.valueChanged.connect(self.hzspinboxChanged)
        self.hzspinbox.setValue(view_duration)
        self.hzspinbox.valueChanged.connect(self.refresh)
        h.addSpacing(20)
        
        # V zoom
        v = QVBoxLayout()
        h.addLayout(v)
        #self.vz2spinbox = QDoubleSpinBox(decimals=5,value=1., singleStep = .1, minimum = -np.inf, maximum =np.inf,)
        self.vz2spinbox = QDoubleSpinBox( )
        self.vz2spinbox.setDecimals(5 )
        self.vz2spinbox.setValue( 1. )
        self.vz2spinbox.setSingleStep( .1 )
        self.vz2spinbox.setMinimum( -np.inf )
        self.vz2spinbox.setMaximum( np.inf )
        
        v.addWidget(self.vz2spinbox)
        #self.vz1spinbox = QDoubleSpinBox(decimals=5,value=-1., singleStep = .1, minimum = -np.inf, maximum =np.inf,)
        self.vz1spinbox = QDoubleSpinBox( )
        self.vz1spinbox.setDecimals(5)
        self.vz1spinbox.setValue( -1. )
        self.vz1spinbox.setSingleStep( .1 )
        self.vz1spinbox.setMinimum( -np.inf)
        self.vz1spinbox.setMaximum( np.inf)
        
        v.addWidget(self.vz1spinbox)
        self.vz2spinbox.valueChanged.connect(self.vzspinboxChanged)
        self.vz1spinbox.valueChanged.connect(self.vzspinboxChanged)
        #~ self.vz2spinbox.valueChanged.connect(self.refresh)
        #~ self.vz1spinbox.valueChanged.connect(self.refresh)
        
        
        #
        self.changeData(     analogsignals = analogsignals,
                                        spiketrains = spiketrains,
                                        vlimits = vlimits,
                                        )
    
    def hsliderChanged(self, val):
        v = float(val)/1000.*(self.x_max-self.x_min) + self.x_min
        if val == 1000: v = v  - self.hzspinbox.value()/2.
        self.hspinbox.setValue(v)
        
    def hzsliderChanged(self, val):
        """
        Convert int to float with log law
        """
        min, max = self.zoom_limit
        v = 10**((val/100.)*(log10(max) - log10(min) )+log10(min))
        self.hzspinbox.valueChanged.disconnect(self.hzspinboxChanged)
        self.hzspinbox.setValue(v)
        self.hzspinbox.valueChanged.connect(self.hzspinboxChanged)
    
    def hzspinboxChanged(self, val):
        min, max = self.zoom_limit
        v = int( (log10(val)-log10(min))/(log10(max) - log10(min) )*100 )
        self.hzslider.valueChanged.disconnect(self.hzsliderChanged)
        self.hzslider.setValue(v)
        self.hzslider.valueChanged.connect(self.hzsliderChanged)
    
    def changeHStep(self, act):
        t = str(act.text())
        if t.endswith('ms'):
            v = float(t[:-2])*1e-3
        else:
            v = float(t[:-1])
        self.hspinbox.setSingleStep(v)
    
    def vzspinboxChanged(self, val):
        if self.sender() == self.vz1spinbox:
            self.y_min = float(self.vz1spinbox.value())
        if self.sender() == self.vz2spinbox:
            self.y_max = float(self.vz2spinbox.value())
        self.refresh()
    
    def fullRefresh(self):
        """
        plot refresh
        """
        for plot in self.plots:
            plot.del_all_items(except_grid=False)
        
        self.signal_curves = [ ]
        if self.analogsignals:
            for i, analist in enumerate(self.analogsignals):
                self.signal_curves.append([ ])
                for p, ana in enumerate(analist):
                    curve = make.curve([ ], [ ], color =  'b')
                    self.plots[p].add_item(curve)
                    self.signal_curves[-1].append(curve)
        
        self.spike_curves = [ ]
        self.selectedspikes_curves = [ ]
        if self.spiketrains:
            for p in range(self.nplot):
                self.spike_curves.append( [ ])
                for i, spiketrains2 in enumerate(self.spiketrains):
                    self.spike_curves[p].append([ ])
                    for j, spiketrain in enumerate(spiketrains2):
                        if type(spiketrain.color) is str:
                            color = QColor(spiketrain.color)
                        elif type(spiketrain.color) is tuple:
                            color = QColor( *tuple([c*255 for c in spiketrain.color]) )
                        else:
                            color = QColor( 'red')
                        
                        curve = make.curve([ ], [ ], markerfacecolor=  color,marker = 'o' , linestyle = '', markersize = 7)
                        self.plots[p].add_item(curve)
                        self.spike_curves[p][i].append( curve )
            
            for p in range(self.nplot):
                self.selectedspikes_curves.append([ ])
                for i in range(len(self.analogsignals)):
                    curve = make.curve([ ], [ ], markerfacecolor=  'm',marker = 'o' , linestyle = '', markersize = 8 )#, alpha = .3)
                    self.selectedspikes_curves[p].append( curve )
                    self.plots[p].add_item(curve)
        
        self.refresh()
        

    def refresh(self,):
        t_start = self.hspinbox.value()
        visible = self.hzspinbox.value()
        t_stop = t_start + visible
        
        # signals
        if self.analogsignals:
            for i, analist in enumerate(self.analogsignals):
                for p, ana in enumerate(analist):
                    curve = self.signal_curves[i][p]
                    if t_start>=ana.t_start+ana.signal.size/ana.sampling_rate:
                        curve.set_data([ ], [ ])
                    elif t_stop<ana.t_start: 
                        curve.set_data([ ], [ ])
                    else:
                        ind_start = (t_start-ana.t_start)*ana.sampling_rate
                        ind_stop = (t_stop-ana.t_start)*ana.sampling_rate
                        if ind_start<0: ind_start=0
                        if ind_stop>ana.signal.size: ind_stop=ana.signal.size
                        curve.set_data(ana.t()[ind_start:ind_stop], ana.signal[ind_start:ind_stop])
        
        # spiketrains on signal
        if self.spiketrains:
            
            for i, analist in enumerate(self.analogsignals):
                
                for j in range(len(self.spiketrains[i])):
                    
                    
                    sptr = self.spiketrains[i][j]
                    st = sptr.spike_times[(sptr.spike_times>=t_start) & (sptr.spike_times<t_stop)]
                    for p in range(self.nplot):
                        ana = self.analogsignals[i][p]
                        ind = ((st - ana.t_start)*ana.sampling_rate).astype('i')
                        
                        curve = self.spike_curves[p][i][j]
                        curve.set_data( st, ana.signal[ind])
        
        # slection of spikes
        if self.selectedspikes:
            for i, selectedspike in enumerate(self.selectedspikes):
                st = selectedspike.spike_times
                st = st[(st>=t_start) & (st<t_stop)]
                for p in range(self.nplot):
                    ana = self.analogsignals[i][p]
                    ind = ((st - ana.t_start)*ana.sampling_rate).astype('i')
                    curve = self.selectedspikes_curves[p][i]
                    #~ print 'i p', i, p, st.size
                    curve.set_data( st, ana.signal[ind])
                    
        
        for vlimit in self.vlimits:
            for p in range(self.nplot):
                if (vlimit>t_start) and (vlimit<t_stop):
                    r = make.range(vlimit, vlimit)
                    self.plots[p].add_item(r)
            
        for p in range(self.nplot):
            plot = self.plots[p]            
            xaxis, yaxis = plot.get_active_axes()
            plot.setAxisScale(xaxis, t_start, t_stop )
            
            plot.setAxisScale(yaxis, self.y_min , self.y_max )
            plot.replot()
    
    def changeData(self,analogsignals = None,
                                        spiketrains = None,
                                        vlimits = None,
                                        ):
        if analogsignals:
            self.analogsignals =analogsignals
            self.x_min, self.x_max = numpy.inf, -numpy.inf
            self.y_min , self.y_max = numpy.inf, -numpy.inf
            for anas in self.analogsignals:
                for ana in anas:
                    if ana.t_start<self.x_min : self.x_min = ana.t_start
                    if ana.t_stop>self.x_max : self.x_max = ana.t_stop
                    m =ana.signal.min()
                    if m<self.y_min: self.y_min = m
                    m =ana.signal.max()
                    if m>self.y_max: self.y_max = m
            self.fullRefresh( )
            self.vz1spinbox.setValue(self.y_min)
            self.vz2spinbox.setValue(self.y_max)
            
        if spiketrains:
            self.spiketrains = spiketrains
            self.fullRefresh( )
        if vlimits:
            self.vlimits = vlimits
            self.fullRefresh( )
        
    def changeSelectedSpikes(self, selectedspikes):
        self.selectedspikes = selectedspikes
        
        self.refresh()
        

        
        
        
        
        

