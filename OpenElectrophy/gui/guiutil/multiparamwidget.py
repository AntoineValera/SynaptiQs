# -*- coding: utf-8 -*-


"""

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from icons import icons

from paramwidget import ParamWidget, LimitWidget


class WidgetMultiMethodsParam(QFrame) :
    """
    Widget for choosing a method and its parameters.
    """
    def __init__(self,  parent = None ,
                        list_method = [ ],
                        method_name = '',
                        globalApplicationDict = None,
                        keyformemory = '',
                        ):
        QFrame.__init__(self, parent)
        
        self.list_method = list_method
        self.method_name = method_name
        self.globalApplicationDict = globalApplicationDict
        self.keyformemory = keyformemory
        
        self.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.v1 = QVBoxLayout()
        v1 = self.v1
        self.setLayout(v1)
        
        
        v1.addWidget(QLabel(self.method_name))
        self.comboBox_method = QComboBox()
        v1.addWidget(self.comboBox_method)
        self.comboBox_method.addItems([ method.name for  method in list_method ])
        
        self.connect(self.comboBox_method,SIGNAL('currentIndexChanged( int  )') , self.comboBoxChangeMethod )
        
        self.paramWidget = None
        
        
        self.comboBoxChangeMethod()
    
    def comboBoxChangeMethod(self) :
        pos = self.comboBox_method.currentIndex()
        if self.paramWidget is not None :
            self.paramWidget.setVisible(False)
            self.v1.removeWidget(self.paramWidget)
            del self.paramWidget
        method = self.list_method[pos]
        self.paramWidget = ParamWidget(method.params ,
                                                        applicationdict = self.globalApplicationDict,
                                                        keyformemory = self.keyformemory + '/%s/%s'%(self.method_name,method.name)  ,
                                                        title = method.name,
                                                        )
        self.v1.addWidget(self.paramWidget,1)
    
    def get_method(self) :
        pos = self.comboBox_method.currentIndex()
        method = self.list_method[pos]
        return method
    
    def get_name(self):
        pos = self.comboBox_method.currentIndex()
        return self.list_method[pos].name
    
    def get_dict(self) :
        return self.paramWidget.get_dict()


