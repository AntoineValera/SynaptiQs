# -*- coding: utf-8 -*-


"""
viewer for image series
"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy
import os

from guiutil.icons import icons
from guiutil.globalapplicationdict import *
from guiutil.paramwidget import ParamDialog, ParamWidget, ChooseDirWidget
from enhancedmatplotlib import *

from ..classes import allclasses

import matplotlib.cm as cm



plotParamDefault =  [
                        [ 'plotColorbar' , {'value' : True }],
                        [ 'autoscale' , {'value' : True }],
                        [ 'clim1' , {'value' : 0. }],
                        [ 'clim2' , {'value' : 1. }],
                        [ 'cmap' , {'value' : 'gray' , 'possible' : [ 'gray' , 'jet']  }],
                    ]

preProcessParamDefault = [
                        ['periodF0'  , { 'value' : 0.06 , 'label' : 'period F0 (s.)' }],
                        ['deltaF_div_F0'  , { 'value' : True , 'label' :  'Apply (F-F0) / F0) '  }],
                        
                        ['max_threshold'  , { 'value' : 50. , 'label' :  'Threshold max'  }],
                        ['min_threshold'  , { 'value' : -50. , 'label' :  'Threshold min'  }],
                        ['nan_to_zeros'  , { 'value' : False , 'label' :  'Change nan to 0'  }],
                        
                        ['detrend'  , { 'value' : False , 'label' :  'linear detrend'  }],
                        
                        ['gaussian_filter'  , { 'value' : None , 'type' : float, 'label' :  'Std for gaussian filter'  }],
                        
                        
                        
                        ['f1'  , { 'value' : None , 'type' : float, 'label' :  'Low frequency filter'  }],
                        ['f2'  , { 'value' : None , 'type' : float, 'label' :  'High frequency filter'  }],


                            
                            

                ]




class ImageSerieViewer(QWidget) :
    """
    
    
    """
    def __init__(self  , parent = None ,
                            globalApplicationDict = None,
                            imageserie = None,
                            
                            showPlotOptions = True,
                            plotParams = None,
                            
                            showPreprocessOptions = True,
                            showExportOptions = True,
                            preProcessParams = None,
                            ):
        QWidget.__init__(self, parent)
        self.globalApplicationDict = globalApplicationDict
        self.plotParams = plotParams
        if self.plotParams is None:
            self.plotParams = ParamWidget(plotParamDefault).get_dict()
        self.preProcessParams = preProcessParams
        if self.preProcessParams is None:
            self.preProcessParams = ParamWidget(preProcessParamDefault).get_dict()
        
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        
        
        self.canvas = SimpleCanvas()
        self.ax = self.canvas.figure.add_subplot(1,1,1)
        self.cax = None
        self.mainLayout.addWidget(self.canvas)
        
        h = QHBoxLayout()
        
        if showPlotOptions:
            but = QPushButton(QIcon(':/colorbar.png') , '')
            h.addWidget(but)
            self.connect(but , SIGNAL('clicked()') , self.changePlotOptions)
        if showPreprocessOptions:
            but = QPushButton(QIcon(':/configure.png') , '')
            h.addWidget(but)
            self.connect(but , SIGNAL('clicked()') , self.changePreProcessOptions)
            
        
        self.mainLayout.addLayout(h)
        self.slider  = QSlider(Qt.Horizontal)
        h.addWidget(self.slider)
        self.labelTime = QLabel('')
        h.addWidget(self.labelTime)
        
        if showExportOptions:
            but = QPushButton(QIcon(':/document-save.png') , '')
            h.addWidget(but)
            self.connect(but , SIGNAL('clicked()') , self.exportImages)
        
    
    
        self.changeimageSerie(imageserie)
        self.connect(self.slider, SIGNAL('valueChanged(int)') , self.changePosition)
    
    def changeimageSerie(self , imageserie):
        self.ax.clear()
        self.imageserie = imageserie
        self.applyPreProcess()
        #~ self.slider.setInterval(1)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.imageserie.images.shape[0]-1)
        
        k = self.plotParams['cmap']
        self.cmap = { 'gray' : cm.gray , 'jet' : cm.jet }[k]
        
        self.image = self.ax.imshow(self.images[0] , 
                                cmap=self.cmap , 
                                interpolation = 'nearest',
                                #~ extent = (0,m.shape[0] , 0,m.shape[1]),
                                origin='lower',
                                #~ alpha = .2,
                                )
        
        if self.cax is None and self.plotParams['plotColorbar']:
            self.cax = self.canvas.figure.add_axes([.9,.1,.04,.8])
        if self.cax is not None and not(self.plotParams['plotColorbar']):
            self.canvas.figure.delaxes(self.cax)
            self.cax = None
        
        if self.plotParams['plotColorbar']:
            self.canvas.figure.colorbar(self.image , ax = self.ax , cax= self.cax)
        
        if not(self.plotParams['autoscale']):
            self.image.set_clim( self.plotParams['clim1'] , self.plotParams['clim2'] )
        

        self.slider.setValue(0)
        self.changePosition(0)
        
    def applyPreProcess(self ):
        self.images = self.imageserie.preProcess(**self.preProcessParams)


    def changePosition(self, num):
        self.image.set_array(self.images[num])
        self.canvas.draw()
        self.labelTime.setText('I: %03d T: %.3f'% (num , self.imageserie.t()[num]))

    
    def changePlotOptions(self):
        dia = ParamDialog(plotParamDefault , 
                    keyformemory = 'imageserieviewer/plot' ,
                    applicationdict = self.globalApplicationDict,
                    title = 'Plot parameters',
                    )
        dia.param_widget.update( self.plotParams )
        ok = dia.exec_()
        if  ok ==  QDialog.Accepted:
            self.plotParams = dia.param_widget.get_dict()
        self.changeimageSerie(self.imageserie)
        

    def changePreProcessOptions(self):
        dia = ParamDialog(preProcessParamDefault , 
                    keyformemory = 'imageserieviewer/preprocess' ,
                    applicationdict = self.globalApplicationDict,
                    title = 'Pre-process parameters',
                    )
        dia.param_widget.update( self.preProcessParams )
        ok = dia.exec_()
        if  ok ==  QDialog.Accepted:
            self.preProcessParams = dia.param_widget.get_dict()
        self.changeimageSerie(self.imageserie)
    
    def exportImages(self):
        param =  [
                            ['path'  , { 'value' : '' , 'label' : 'path to export images' , 'widgettype' : ChooseDirWidget }],
                            ['dpi'  , { 'value' : 80 , 'label' : 'DPI'  }],
                            ['width'  , { 'value' : 8. , 'label' : 'Width (inch)'  }],
                            ['height'  , { 'value' : 6. , 'label' : 'Height (inch)' } ],
                            ['force_proportions'  , { 'value' : False , 'label' : 'Force proportions' } ],
                        ]
        
        
        dia = ParamDialog(param , 
                    keyformemory = 'imageserieviewer/exportImages' ,
                    applicationdict = self.globalApplicationDict,
                    title = 'Export all images',
                    )
        dia.param_widget.update( self.preProcessParams )
        ok = dia.exec_()
        if  ok ==  QDialog.Accepted:
            d = dia.param_widget.get_dict()
            canvas = SimpleCanvas()
            
            canvas.figure.set_dpi(d['dpi'])
            if not d['force_proportions']:
                canvas.figure.set_size_inches(d['width'] , d['height'])
                dpi = d['dpi']
                
            else:
                canvas.figure.set_size_inches(self.images.shape[2]/10. , self.images.shape[1]/10.)
                dpi = 10
            canvas.figure.set_dpi(dpi)
            ax = canvas.figure.add_axes([0., 0., 1., 1.])
            ax.set_xticks([ ])
            ax.set_yticks([ ])
            cax = None
            if self.plotParams['plotColorbar']:
                cax = canvas.figure.add_axes([.9,.1,.04,.8])

            image = ax.imshow(self.images[0] , 
                                    cmap=self.cmap , 
                                    interpolation = 'nearest',
                                    origin='lower',
                                    )
            if self.plotParams['plotColorbar']:
                canvas.figure.colorbar(image , ax = ax , cax= cax)
            
            for i in range(self.imageserie.images.shape[0]):
                image.set_array(self.images[i])
                canvas.figure.savefig( os.path.join( d['path'], 'image %04d.png'%i) , dpi = dpi)



