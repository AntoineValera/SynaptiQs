# -*- coding: utf-8 -*-
"""

"""




from sqlalchemy import Column, Integer, String, Float, Text, Unicode
import numpy
from scipy import signal
from scipy import interpolate , digitize , nan , arccos , where, mean, std , ones , zeros , isnan, any, all
from scipy import ndimage
from numpy import abs

from base import OEBase
from sqlalchemy import orm



class ImageSerie( OEBase):
    """
    
    """
    parents = [ 'segment' ]
    children = [ ]
    fields = [  ['name' , Text],
                    
                    ['sampling_rate' , Float],
                    ['t_start' , Float],
                    
                    ['images' , numpy.ndarray],
                    
                ]
    tablename = 'imageserie'
    def __init__(self, *args , **kargs):
        """
        """
        for k,v in kargs.iteritems():
            if k in dict(self.fields):
                setattr(self, k, v)
        
        OEBase.__init__(self, *args, **kargs)
        
        self._t = None
        
    @orm.reconstructor
    def init_on_load(self):
        OEBase.init_on_load(self)
        self._t = None
    
    def compute_time_vector(self) :
        return numpy.arange(self.images.shape[0], dtype = 'f8')/self.sampling_rate + self.t_start

    def t(self):
        if self._t==None:
            self._t=self.compute_time_vector()
        return self._t

    plotAptitudes = [   [ 'image_average' , {  
                                                        'name' : 'average off all images',
                                                        'default_selected' :  True,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : False,
                                                        'params' :  [       
                                                                           ],
                                                    }
                                ],
                                
                                [ 'temporal_average' , {  
                                                        'name' : 'temporal average',
                                                        'default_selected' :  False,
                                                        'ax_needed' : 1,
                                                        'fig_needed' : None,
                                                        'widget_needed' : None,
                                                        'stackable' : True,
                                                        'params' :  [        [ 'color' , {'value' : 'g' }],
                                                                                    [ 'plot_std' , {'value' : True }],
                                                                           ],
                                                    }
                                ],                                
                            
                            ]


    def plot_image_average( self, **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        import matplotlib.cm as cm
        m = numpy.mean(self.images , axis = 0)
        #~ print 'm.shape' , m.shape
        im = ax.imshow(m , cmap=cm.gray , interpolation = 'nearest',
                                #~ extent = (0,m.shape[0] , 0,m.shape[1]),
                                origin='lower',
                                #~ alpha = .2,
                                )
        return im
    


    def preProcess(self,
                                    periodF0 = 0.06,
                                    deltaF_div_F0 = True,
                                    
                                    max_threshold = None,
                                    min_threshold = None,
                                    nan_to_zeros = True,
                                    
                                    detrend = False,
                                    
                                    #~ band_filter = None,
                                    
                                    gaussian_filter = None,
                                    
                                    f1 = None,
                                    f2 = None,
                                    
                                    **kargs):
        
        images = self.images
        if deltaF_div_F0:
            ind = self.t()<=self.t_start+periodF0
            m0 = mean(images[ind,:,:] , axis = 0)
            images = (images-m0)/m0*1000.
            
        if max_threshold is not None:
            #~ images[images>max_threshold] = max_threshold
            images[images>max_threshold] = nan
            

        if min_threshold is not None:
            #~ images[images<min_threshold] = min_threshold
            images[images<min_threshold] = nan
                
            
        if nan_to_zeros:
            images[isnan(images) ] = 0.

        if detrend and not nan_to_zeros:
            m = any(isnan(images) , axis = 0)
            images[isnan(images) ] = 0.
            images = signal.detrend( images , axis = 0)
            images[:,m] = nan
        elif detrend and nan_to_zeros:
            images = signal.detrend( images , axis = 0)
            
        if gaussian_filter is not None:
            images = ndimage.gaussian_filter( images , (0 , gaussian_filter , gaussian_filter))
            

        if f1 is not None or f2 is not None:
            from ..computing.filter import fft_passband_filter
            if f1 is None: f1=0.
            if f2 is None: f1=inf
            nq = self.sampling_rate/2.
            images = fft_passband_filter(images, f_low = f1/nq , f_high = f2/nq , axis = 0)
        
        return images
        


    def selectAndPreprocess(self , 
                                                        mask = None,
                                                        **kargs):
        
        images = self.preProcess(**kargs)
        
        if mask is None:
            id0 , id1 = where( ones((images.shape[1] , images.shape[2] )) )
        else:
            id0 , id1 = where( mask )
        
        allpixel =images[:,id0,id1]
        
        
        return allpixel
        
        
        
    
    def plot_temporal_average( self, 
                                                        color = 'g',
                                                        plot_std = True,
                                                        
                                                        t_start = None,
                                                        
                                                        label = None,
                                                        **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        allpixel = self.selectAndPreprocess( **kargs ) 
        

        m = mean( allpixel , axis = 1 )
        
        if t_start is None:
            t = self.t()
        else:
            t = self.t() - self.t()[0] + t_start
        
        ax.plot(t , m , color = color , linewidth = 2 , label = label)
        
        if plot_std:
            s = mean( allpixel , axis = 1 )
            ax.fill_between(t , m+s , m-s , color = color , alpha = .3 , )


    def plot_all_pixel(self , 
                                            color = 'g',
                                            
                                            max_lines = 50,
                                            
                                            **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        else:
            from matplotlib import pyplot
            fig = pyplot.figure()
            ax = fig.add_subplot(1,1,1)
        
        allpixel = self.selectAndPreprocess( **kargs )
        step = 1.*allpixel.shape[1]/max_lines
        if step<=1. : step = 1
        else: step = int(step)
        
        ax.plot(self.t() , allpixel[:,::step] , color = color )
        
        

