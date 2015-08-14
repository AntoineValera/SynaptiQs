# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from numpy import zeros, unique, dot, random, asarray, sqrt, nonzero, equal, amin, array, where, argmin, sum, empty
from numpy import random , linspace, newaxis, any, isnan,  matrix, mean

from numpy import linalg

from matplotlib.pyplot import get_cmap
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Circle
from matplotlib.widgets import Lasso
from matplotlib.path import Path as points_inside_poly
from matplotlib.cm import get_cmap

from enhancedmatplotlib import SimpleCanvasAndTool,  SimpleCanvas
from guiutil.paramwidget import *



plotParamDefault =  [
                        #~ [ 'plotColorbar' , {'value' : True }],
                        [ 'autoscale' , {'value' : True }],
                        [ 'xlim' , {'value' : [-4.,4.] , 'widgettype' : LimitWidget }],
                        [ 'ylim' , {'value' : [-4.,4.] , 'widgettype' : LimitWidget }],
                        
                        [ 'force_orthonormality' , {'value' : True , }],
                        
                        [ 'interval' , {'value' : 100 , 'label' : 'Refresh interval tour (ms)'  }],
                        [ 'nsteps' , {'value' : 20 , 'label' : 'Nb of steps for tour'  }],
                        
                        [ 'display_circle' , {'value' : True , }],
                    ]



class NDViewer(QWidget):
    def __init__(self , parent=None ,
                                globalApplicationDict = None,
                                show_tour = True,
                                show_select_tools = False,
                                plotParams = None,
                                
                                ):
        self.globalApplicationDict = globalApplicationDict
        self.plotParams = plotParams
        if self.plotParams is None:
            self.plotParams = ParamWidget(plotParamDefault).get_dict()
        self.show_tour = show_tour
        self.show_select_tools = show_select_tools
                                
        QWidget.__init__(self,parent )
        self.spikeSortingWin = self.parent()
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        
        self.widgetProjection = QWidget()
        
        v = QVBoxLayout()
        h.addLayout(v)
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        #~ self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #~ self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidget(  self.widgetProjection ) 
        self.scrollArea.setMinimumWidth(180)
        v.addWidget( self.scrollArea )
        
        
        if show_tour:
            self.randButton = QPushButton( QIcon(':/roll.png') , 'Random')
            v.addWidget(self.randButton)
            self.connect(self.randButton, SIGNAL('clicked()') , self.randomPosition)
            
            
            self.startRandTourButton = QPushButton( QIcon(':/helicoper_and_roll.png') , 'Random tour')
            self.startRandTourButton.setCheckable(True)
            v.addWidget(self.startRandTourButton)
            self.connect(self.startRandTourButton, SIGNAL('clicked()') , self.startStopTour)
            self.timerRandTour = QTimer()
            self.timerRandTour.setInterval(self.plotParams['interval'])
            self.connect(self.timerRandTour, SIGNAL('timeout()') , self.stepRandTour)
            
            self.startOptimizedTourButton = QPushButton( QIcon(':/helicoper_and_magic.png') , 'Optimized tour')
            self.startOptimizedTourButton.setCheckable(True)
            v.addWidget(self.startOptimizedTourButton)
            self.connect(self.startOptimizedTourButton, SIGNAL('clicked()') , self.startStopTour)
            self.timerOptimizedTour = QTimer()
            self.timerOptimizedTour.setInterval(self.plotParams['interval'])
            self.connect(self.timerOptimizedTour, SIGNAL('timeout()') , self.stepOptimizedTour)



            
        
        but = QPushButton( QIcon(':/configure.png') , 'Configure')
        v.addWidget(but)
        self.connect(but, SIGNAL('clicked()') , self.openConfigure)
        
        if show_select_tools:
            h2 = QHBoxLayout()
            
            
            groupbox = QGroupBox( 'Selection mode')
            groupbox.setLayout(h2)
            v.addWidget(groupbox)
            
            icons = [
                            ['pickone' , ':/color-picker.png'],
                            ['lasso' , ':/lasso.png'],
                            ['contour' , ':/polygon-editor.png'],
                        ]
            self.selectButton = { }
            for name, icon in icons:
                but = QPushButton(QIcon(icon),'')
                h2.addWidget(but)
                but.setAutoExclusive(True)
                but.setCheckable(True)
                self.connect(but, SIGNAL('clicked()') , self.changeSelectMode)
                self.selectButton[name] = but
            
            #~ self.selectButton['pickone'].setChecked(True)
            
            self.clearSelectBut = QPushButton(QIcon(':/view-refresh.png'),'Clear selection')
            v.addWidget(self.clearSelectBut)
            self.connect(self.clearSelectBut, SIGNAL('clicked()') , self.clearSelection)
        
        
        self.canvas = SimpleCanvas()
        #~ self.ax = self.canvas.fig.add_subplot(1,1,1)
        self.ax = self.canvas.fig.add_axes([0.02, 0.02, .96, .96])
        h.addWidget(self.canvas,2)
        self.canvas.setMinimumWidth(180)
        
        self.ax_circle = None
        self.create_axe_circle()
        
        self.tour_running = False
        
        # internal attribute
        self.dim = 0 #
        self.spins = [ ] # spin widget list
        
        self.toBeDisconnected = [ ] # manage mpl_connect and disconnect
        self.selectMode =  None # actual mode
        self.epsilon = 4. # for pickle event
        self.poly = None # for contour
        
        self.selectionLine = None
        
        self.actualSelection = array([ ] , dtype='i')
        
        self.connect(self, SIGNAL('selectionChanged') , self.redrawSelection )
    
    
    ## draw and redraw ##
    def change_dim(self, ndim):
        
        self.projection = zeros( (ndim, 2))
        self.projection[0,0] = 1
        self.projection[1,1] = 1
        
        #spinwidgets
        self.widgetProjection = QWidget()
        self.widgetProjection.updateGeometry()
        g = QGridLayout()
        self.widgetProjection.setLayout(g)
        self.spins = [ ]
        for i in range(ndim):
            d1 = QDoubleSpinBox()
            d1.setValue(self.projection[i,0])
            d2 = QDoubleSpinBox()
            d2.setValue(self.projection[i,1])
            g.addWidget( QLabel('dim %d'%i), i, 0 )
            g.addWidget( d1, i, 1 )
            g.addWidget( d2, i, 2 )
            self.connect(d1, SIGNAL('valueChanged( double  )'), self.spinsChanged)
            self.connect(d2, SIGNAL('valueChanged( double  )'), self.spinsChanged)
            d1.setSingleStep(0.05)
            d2.setSingleStep(0.05)
            #~ d1.setRange(0.,1.)
            #~ d2.setRange(0.,1.)
            d1.setRange(-1.,1.)
            d2.setRange(-1.,1.)            
            self.spins.append( [d1, d2] )
        
        self.scrollArea.setWidget(  self.widgetProjection )
        self.scrollArea.update()
        self.dim = ndim
        
        # speed vector for tour
        #~ self.tourSpeed = (random.rand( self.projection.shape[0], 2)-.5)/100.
        
        
    
    
    def change_point(self, data, dataLabels = None, colors = None, subset = None):
        """
        data =       dim 0 elements
                        dim 1 dimension
        dataLabels = vector of cluster for colors
        """
        
        if data.shape[1] != self.dim :
            self.change_dim(data.shape[1])
        self.data = data
        
        if dataLabels is None:
            dataLabels = zeros( data.shape[0], dtype = 'i')
        self.dataLabels = dataLabels
        self.allLabels = unique(self.dataLabels)
        
        if colors is None:
            colors =  [ 'c' , 'g' , 'r' , 'b' , 'k' , 'm' , 'y']*100
        self.colors = colors
        
        if subset is None:
            subset = { }
            for c in self.allLabels:
                ind = self.dataLabels ==c
                subset[c] = ind
        self.subset = subset
        
        self.fullRedraw()
        self.refreshSpins()
        
    def fullRedraw(self):
        self.ax.clear()
        #~ proj = dot( self.data, self.projection ) 
        for c in self.allLabels:
            #~ ind = self.dataLabels ==c
            ind = self.subset[c]
            proj = dot( self.data[ind,:], self.projection ) 
            self.ax.plot( proj[:,0], proj[:,1], #proj[ind,0] , proj[ind,1],
                                                linestyle = 'None',
                                                marker = '.', 
                                                color = self.colors[c],
                                                picker=self.epsilon)
        self.redraw()
        
    def redraw(self):
        if not(self.plotParams['autoscale']):
            self.ax.set_xlim( self.plotParams['xlim'] )
            self.ax.set_ylim( self.plotParams['ylim'] )
        
        self.canvas.draw()

    def spinsChanged(self,value):
        for i in range(self.projection.shape[0]):
            self.projection[i,0] =self.spins[i][0].value()
            self.projection[i,1] =self.spins[i][1].value()

        if self.plotParams['force_orthonormality']:
            m = sqrt(sum(self.projection**2, axis=0))
            m = m[newaxis, :]
            self.projection /= m
            self.refreshSpins()


            
        self.fullRedraw()
    
    def refreshSpins(self):
        for i in range(self.projection.shape[0]):
            d1, d2 = self.spins[i]

            self.disconnect(d1, SIGNAL('valueChanged( double  )'), self.spinsChanged)
            self.disconnect(d2, SIGNAL('valueChanged( double  )'), self.spinsChanged)
            #~ d1.disconnect(SIGNAL('valueChanged( double  )'))
            #~ d2.disconnect(SIGNAL('valueChanged( double  )'))
            d1.setValue(self.projection[i,0])
            d2.setValue(self.projection[i,1])
            
            self.connect(d1, SIGNAL('valueChanged( double  )'), self.spinsChanged)
            self.connect(d2, SIGNAL('valueChanged( double  )'), self.spinsChanged)
        
        
        if self.plotParams['display_circle']:
            self.refreshCircleRadius()
        
    
    def refreshCircleRadius(self):
        for l in self.radiusLines:
            self.ax_circle.lines.remove(l)
        
        self.radiusLines = [ ]
        for i in range(self.projection.shape[0]):
            l, = self.ax_circle.plot([0,self.projection[i,0]] , [0 , self.projection[i,1]]  , color = 'g')
            self.radiusLines.append(l)
        self.canvas.draw()
    
    def create_axe_circle(self):
        if self.plotParams['display_circle']:
            if self.ax_circle is None:
                ax= self.canvas.fig.add_axes([0.04, 0.04, .1, .1])
            else:
                ax = self.ax_circle
            ax.clear()
            ax.set_xticks([ ])
            ax.set_yticks([ ])
            circle = Circle((0,0) , radius = 1. , facecolor = 'w')
            ax.add_patch(circle)
            ax.set_xlim([-1.02,1.02])
            ax.set_ylim([-1.02,1.02])
            
            
            # Fixme
            #~ ax.xaxis.set_visible(False)
            #~ ax.yaxis.set_visible(False)
            
            self.ax_circle = ax
            self.canvas.draw()
            self.radiusLines = [ ]
        else:
            if self.ax_circle is not None:
                self.canvas.fig.delaxes(self.ax_circle)
                self.ax_circle = None
            #~ else:
                #~ print 'oulala'
                
    
    ## config ##
    def openConfigure(self):

        dia = ParamDialog(plotParamDefault , 
                    keyformemory = 'ndviewer/options' ,
                    applicationdict = self.globalApplicationDict,
                    title = 'Plot parameters',
                    )
        dia.param_widget.update( self.plotParams )
        
        if  dia.exec_():
            self.plotParams = dia.param_widget.get_dict()
            self.timerRandTour.setInterval(self.plotParams['interval'])
            self.timerOptimizedTour.setInterval(self.plotParams['interval'])
            self.create_axe_circle()
            self.fullRedraw()
            
            
    
    ## random and tour tour ##
    def randomPosition(self):
        ndim = self.projection.shape[0]
        self.projection = random.rand(ndim,2)*2-1.
        if self.plotParams['force_orthonormality']:
            m = sqrt(sum(self.projection**2, axis=0))
            self.projection /= m
        self.refreshSpins( )
        self.fullRedraw( )    
    
    def startStopTour(self):
        if self.sender() == self.startRandTourButton:
            but = self.startRandTourButton
            mode = 'rand'
            self.startOptimizedTourButton.setChecked(False)
            
        elif self.sender() == self.startOptimizedTourButton:
            but = self.startOptimizedTourButton
            mode = 'optimized'
            self.startRandTourButton.setChecked(False)
        
        start = but.isChecked()
        
        if start:
            if self.show_select_tools:
                for name, but in self.selectButton.iteritems():
                    but.setChecked(False)
                    but.setEnabled(False)
                self.clearSelectBut.setEnabled(False)
                self.selectMode =  None
                self.clearSelection()
            
            if mode == 'rand':
                self.timerOptimizedTour.stop()
                self.timerRandTour.start()
                self.actualStep = self.plotParams['nsteps'] +1
            elif mode == 'optimized':
                self.timerRandTour.stop()
                self.timerOptimizedTour.start()
                
                self.tour_running = True
        else:
            if self.show_select_tools:
                for name, but in self.selectButton.iteritems():
                    but.setEnabled(True)
                self.clearSelectBut.setEnabled(True)
                self.changeSelectMode()
            
            self.timerRandTour.stop()
            self.timerOptimizedTour.stop()
            self.tour_running = False
        
        self.refreshSpins( )
        self.fullRedraw( )
        
        
    
    def stepRandTour(self):
        #~ print 'stepRandTour'
        nsteps = self.plotParams['nsteps']
        ndim = self.projection.shape[0]
        
        if self.actualStep >= nsteps:
            # random for next etap
            nextEtap = random.rand(ndim,2)*2-1.
            self.allSteps = empty( (ndim , 2 ,  nsteps))
            for i in range(ndim):
                for j in range(2):
                    self.allSteps[i,j , : ] = linspace(self.projection[i,j] , nextEtap[i,j] , nsteps)
                
            if self.plotParams['force_orthonormality']:
                m = sqrt(sum(self.allSteps**2, axis=0))
                m = m[newaxis, : ,  :]
                self.allSteps /= m
                    
            self.actualStep = 0
            
        self.projection = self.allSteps[:,: ,  self.actualStep] 
        self.actualStep += 1
        self.refreshSpins( )
        self.fullRedraw( )
    


    def stepOptimizedTour(self):
        #~ print 'stepOptimizedTour'
        actual_lda =  ComputeIndexLda(self.projection, self.data, self.dataLabels)
        
        nloop = 1
        ndim = self.projection.shape[0]        
        for i in range(nloop):
            delta = (random.rand(ndim, 2)*2-1)/20.
            new_proj = self.projection + delta
            # normalize orthonormality
            m = sqrt(sum(new_proj**2, axis=0))
            m = m[newaxis, :]
            new_proj /= m
            
            new_lda = ComputeIndexLda(new_proj, self.data, self.dataLabels)
            if new_lda >=actual_lda:
                actual_lda = new_lda
                self.projection = new_proj
        self.refreshSpins()
        self.fullRedraw()


    ## selections ##
    def changeSelection(self, ind):
        
        self.actualSelection = array(ind, dtype='i')
        if not self.tour_running:
            self.redrawSelection()
    
    def changeSelectMode(self):
        self.selectMode = None
        for name, but in self.selectButton.iteritems():
            if but.isChecked():
                self.selectMode = name
        for e in self.toBeDisconnected:
            self.canvas.mpl_disconnect(e)
        self.toBeDisconnected = [ ]
        
        self.clearSelection()
    
    def clearSelection(self):
        self.clearArtistSelection()
        
        if self.selectMode =='pickone':
            cid = self.canvas.mpl_connect('pick_event', self.onPick)
            self.toBeDisconnected.append(cid)
            
        elif self.selectMode =='contour':
            cid1 = self.canvas.mpl_connect('button_press_event', self.pressContour)
            cid2 = self.canvas.mpl_connect('button_release_event', self.releaseContour)
            cid3 = self.canvas.mpl_connect('motion_notify_event', self.motionContour)
            self.toBeDisconnected += [cid1, cid2, cid3 ]
            self.poly =None
            self._ind = None
        
        elif self.selectMode =='lasso':
            cid = self.canvas.mpl_connect('button_press_event', self.startLasso)
            self.toBeDisconnected.append(cid)
        
        self.actualSelection = array([ ] , dtype='i')
        self.emit(SIGNAL('selectionChanged'))
        
        
    
    def clearArtistSelection(self):
        if self.poly is not None:
            self.ax.lines.remove(self.line)
            self.ax.patches.remove(self.poly)
            self.poly = None
            self.line = None
            #~ self.canvas.draw()
            self.redraw()
        
        # should not:
        if hasattr(self,'lasso'):
            #~ print 'del lasso in clearArtistSelection', self.canvas.widgetlock.locked()
            self.canvas.widgetlock.release(self.lasso)
            del self.lasso            
        
    def onPick(self , event):
        if isinstance(event.artist, Line2D):
            xdata, ydata = event.artist.get_data()
            x,y = xdata[event.ind[0]], ydata[event.ind[0]]
            self.actualSelection = array([argmin( sum( (dot( self.data, self.projection )-array([[ x,y ]]) )**2 , axis=1)) ] , dtype='i')
        else:
            self.actualSelection = array([ ] , dtype='i')
        
        self.emit(SIGNAL('selectionChanged'))

    
    def startLasso(self, event):
        if event.button != 1: return
        
        
        #~ print 'startLasso', self.canvas.widgetlock.locked()
        if self.canvas.widgetlock.locked():
            # sometimes there is a bug lassostop is not intercepted!!!
            # so to avoid 2 start
            #~ print 'in lasso bug'
            self.clearArtistSelection()
            return
        if event.inaxes is None: return
        #~ for e in self.toBeDisconnected:
            #~ self.canvas.mpl_disconnect(e)


        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.stopLasso)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
        
    def stopLasso(self, verts):
        #~ print 'stopLasso', self.canvas.widgetlock.locked()
        self.actualSelection,  = where(points_inside_poly(dot( self.data, self.projection ), verts))
        #~ self.canvas.draw()
        self.canvas.widgetlock.release(self.lasso)
        #~ print self.canvas.artists
        del self.lasso
        #~ print 'lasso deleted'
        #~ self.redraw()
        
        self.emit(SIGNAL('selectionChanged'))
    
    def pressContour(self, event):
        if event.inaxes==None: return
        if event.button != 1: return
        
        # new contour
        if self.poly is None:
            self.poly = Polygon( [[event.xdata , event.ydata]] , animated=False , alpha = .3 , color = 'g')
            self.ax.add_patch(self.poly)
            self.line, = self.ax.plot([event.xdata] , [event.ydata] , 
                                    color = 'g',
                                    linewidth = 2 ,
                                    marker = 'o' ,
                                    markerfacecolor='g', 
                                    animated=False)
            #~ self.canvas.draw()
            self.redraw()
            return
        
        
        # event near a point
        xy = asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = nonzero(equal(d, amin(d)))[0]
        self._ind = indseq[0]
        if d[self._ind]>=self.epsilon:
            self._ind = None

        
        # new point
        if self._ind is None:
            self.poly.xy = array( list(self.poly.xy) +  [[event.xdata , event.ydata]])
            self.line.set_xdata( array(list(self.line.get_xdata()) + [ event.xdata]) )
            self.line.set_ydata( array(list(self.line.get_ydata()) + [ event.ydata]) )
            #~ self.canvas.draw()
            self.redraw()
        
        self.actualSelection, = where(points_inside_poly(dot( self.data, self.projection ), self.poly.xy))
        self.emit(SIGNAL('selectionChanged'))
    
    
    def releaseContour(self , event):
        if event.button != 1: return
        self._ind = None

    def motionContour(self , event):
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x,y
        self.line.set_data(zip(*self.poly.xy))
        #~ self.canvas.draw()
        self.redraw()
        
        self.actualSelection, = where(points_inside_poly(dot( self.data, self.projection ), self.poly.xy))
        self.emit(SIGNAL('selectionChanged'))
    
    def redrawSelection(self):
        if self.selectionLine is not None:
            if self.selectionLine in self.ax.lines:
                self.ax.lines.remove(self.selectionLine)
        proj = dot( self.data, self.projection )
        self.selectionLine, = self.ax.plot(proj[self.actualSelection,0] , proj[self.actualSelection,1],
                                                                linestyle = 'None',
                                                                markersize = 10,
                                                                marker = 'o' ,
                                                                markerfacecolor='m',
                                                                markeredgecolor='k',
                                                                alpha = .6,
                                                                )
        #~ self.canvas.draw()
        self.redraw()







def ComputeIndexLda(proj, data, dataLabels): 
# takken from page 31 of book on GGOBI
# diane cook "integrative and dynamic graphics for data analysis
    ndim = proj.shape[0]

    A = matrix(proj)
    B = matrix(zeros((ndim, ndim)))
    W = matrix(zeros((ndim, ndim)))
    grand_mean = mean(data , axis = 0).astype(matrix)
    for c in unique(dataLabels):
        ind = dataLabels ==c
        group_mean = mean(data[ind, :], axis = 0).astype(matrix)
        d = group_mean - grand_mean
        B += ind[ind].size*dot(d[:,newaxis], d[newaxis, :])
        
        # find better:
        d = data[ind, :] - group_mean
        for j in range(data[ind, :].shape[0]):
            W+=dot(d[j,:, newaxis], d[j,newaxis,:])
        
    #~ print 'A', A, A.size
    #~ print 'B', B, B.size
    #~ print 'W', W, W.size

    lda = 1 -  linalg.det(A.T*W*A) / linalg.det(A.T*(W+B)*A)
    return lda
