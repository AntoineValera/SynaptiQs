# -*- coding: utf-8 -*-


"""
widget for managing several matplotlib figure
"""


import matplotlib
#~ matplotlib.rcParams['path.simplify']=False

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2
from matplotlib.figure import Figure


class SimpleCanvas(FigureCanvas):
    """
    A simple standart canvas from matplotlib
    """
    def __init__(self, parent=None, ):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                    QSizePolicy.Expanding,
                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        color = self.palette().color(QPalette.Background).getRgb()
        color = [ c/255. for c in color[:3] ]
        self.fig.set_facecolor(color)



class SimpleNavigationToolbar(NavigationToolbar2) :
    def __init__(self , parent , canvas , orientation = Qt.Vertical,
                            close_button = False) :
        """
        A simple matplotlib navigation toolbar that can be vertical
        Qt.Vertical or Qt.Horizontal
        """
        NavigationToolbar2.__init__( self, canvas,parent )
        self.setOrientation(orientation)
        if close_button:
            self.addSeparator()
            self.actionClose = self.addAction(QIcon(':/window-close.png'), 'Close')
            
    def set_message( self, s ):
        pass



class SimpleCanvasAndTool(QWidget):
    def __init__(self  , parent = None , orientation = Qt.Horizontal , close_button = False):
        QWidget.__init__(self, parent)
        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        if orientation == Qt.Horizontal:
            self.mainLayout = QVBoxLayout()
        else:
            self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.toolbar = SimpleNavigationToolbar(self , self.canvas , orientation = orientation, close_button = close_button)
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.canvas)
        
        if close_button:
            self.connect(self.toolbar.actionClose , SIGNAL("triggered()") , self.askClose)
            
    def askClose(self):
        self.emit(SIGNAL('want_to_be_closed'))
        
        
        
    def draw(self):
        self.canvas.draw()
        