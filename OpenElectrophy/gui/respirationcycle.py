# -*- coding: utf-8 -*-


"""
dialog for edition of respiratory cycles

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
from guiutil.paramwidget import ParamWidget, LimitWidget, ParamDialog
import numpy

from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter

from ..classes import RespirationSignal
from ..computing.cycle import list_method
from enhancedmatplotlib import SimpleCanvasAndTool
from guiutil.multiparamwidget import WidgetMultiMethodsParam



class RespirationCycleEdition(QDialog) :
    """
    
    
    """
    def __init__(self  , parent = None ,
                            metadata =None,
                            Session = None,
                            session = None,
                            globalApplicationDict = None,
                            id_respirationsignal = None,
                            
                            ):
        QDialog.__init__(self, parent)
        self.metadata = metadata
        self.session = Session()
        self.globalApplicationDict = globalApplicationDict
        self.id_respirationsignal = id_respirationsignal
        self.respiration = self.session.query(RespirationSignal).filter_by(id=id_respirationsignal).one()
        
        #FIXME: do not work:
        self.setModal(False)
        self.setWindowModality(  Qt.NonModal )

        self.setWindowTitle(self.tr('OpenElectrophy respiration for %d'%(self.respiration.id) ))
        self.setWindowIcon(QIcon(':/respiration.png'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        h = QHBoxLayout()
        self.mainLayout.addLayout( h )
        
        c = SimpleCanvasAndTool()
        h.addWidget(c, 3)
        self.canvas = c.canvas
        self.ax = self.canvas.fig.add_subplot(1,1,1)
        
        
        v = QVBoxLayout()
        h.addLayout(v , 2)

        
        but = QPushButton(QIcon(':/TODO.txt') , 'Auto detect')
        v.addWidget(but)
        self.connect(but , SIGNAL('clicked()'), self.newDetection )
        
        v.addSpacing(20)

        
        v.addWidget(QLabel('<b>Repiratory cycles</b>') )
        self.table = QTreeWidget()
        #~ self.table.setMinimumWidth(100)
        #~ self.table.setColumnWidth(0,80)
        v.addWidget(self.table )
        
        self.table.setSelectionMode( QAbstractItemView.ExtendedSelection)
        self.connect(self.table ,SIGNAL('itemSelectionChanged()') , self.newSelectionInTable)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.table,SIGNAL('customContextMenuRequested( const QPoint &)'),self.contextMenuTable)
        
        
        
        self.mainLayout.addSpacing(20)
        
        buttonBox = QDialogButtonBox()
        
        but = QPushButton(QIcon(':/document-save.png'),'Save to DB')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        self.connect(but, SIGNAL('clicked()'), self.save_to_db)
        
        but = QPushButton(QIcon(':/reload.png'),'Reload from DB')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        self.connect(but, SIGNAL('clicked()'), self.reload_from_db)
        
        but = QPushButton(QIcon(':/window-close.png') , 'Quit')
        buttonBox.addButton(but , QDialogButtonBox.RejectRole)
        self.connect(but, SIGNAL('clicked()'), self.close)
        self.mainLayout.addWidget(buttonBox)

        
        
        
        if self.respiration.cycle_times is None:
            self.cycle_times = None
        else:
            self.cycle_times = self.respiration.cycle_times
        
        self.vlines = { }
        self.baseline = 0.
        self.refreshPlot()
        self.refreshTable()
        
        
        self.canvas.mpl_connect('pick_event', self.onPick)
        self.canvas.mpl_connect('button_release_event', self.releaseEvent)
        self.canvas.mpl_connect('motion_notify_event', self.motionEvent)
        #~ self.picked = None
        
        #~ self.lineSelection = None
        self.session.expunge_all()
    
    def refreshPlot(self, with_same_zoom = False):
        if with_same_zoom:
            if self.canvas.toolbar._views.empty(): self.canvas.toolbar.push_current()
            #~ self.canvas.toolbar.push_current()
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        
        self.ax.clear()
        t = self.respiration.t()
        sig = self.respiration.signal
        self.ax.plot(t,sig, 'b')
        
        if self.cycle_times is not None:
            self.vlines = { }
            cmap = get_cmap('jet' , self.cycle_times.shape[0])
            for i in range(self.cycle_times.shape[0]):
                for j in range(self.cycle_times.shape[1]):
                    if j==0: ls = '-'
                    else: ls = '--'
                    line = self.ax.axvline( self.cycle_times[i,j] , color = cmap(i) , linestyle = ls , picker = 3 , linewidth = 1.5)
                    self.vlines[line] = (i,j)
        self.ax.axhline( self.baseline, color = 'k', linewidth = 2)
        self.lineSelection = None
        self.picked = None
        
        if with_same_zoom:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.toolbar.push_current()
            
        
        self.canvas.draw()
    
    
    def refreshTable(self):
        self.table.clear()
        ct = self.cycle_times
        if ct is None:
            return
        
        self.table.setColumnCount( ct.shape[1])
        self.table.setHeaderLabels( [ '%d/%d'%(j,ct.shape[1]) for j in range( ct.shape[1]) ])
        
        cmap = get_cmap('jet' , self.cycle_times.shape[0])
        for i in range(ct.shape[0]):
                item = QTreeWidgetItem(["%f"%ct[i,j] for j in range( ct.shape[1]) ])
                pix = QPixmap(10,10 )
                r,g,b = ColorConverter().to_rgb(cmap(i) )
                pix.fill(QColor(r*255,g*255,b*255  ))
                icon = QIcon(pix)
                item.setIcon(0,icon)
                self.table.addTopLevelItem(item)
        
        self.table.setColumnWidth(0,100)
        
    
    def onPick(self, event):
        thisline = event.artist
        mouseevent = event.mouseevent
        if event.artist in self.vlines:
            self.picked =  event.artist
    
    
    def releaseEvent(self, event):
        if self.picked is None: return
        
        i,j = self.vlines[self.picked]
        x = self.picked.get_xdata()
        
        # fixme ???????
        if x.size>=2: x = x[0]
        
        if x == numpy.array(None):
            # out
            self.picked.set_xdata(self.cycle_times[i,j])
            self.canvas.draw()
            self.picked = None
            return
        
        
        # test if between neightbours
        ct = self.cycle_times.copy()
        ct[i,j] = x
        ct = ct.reshape(ct.size)
        ct = ct[~numpy.isnan(ct)]
        if  numpy.any(numpy.diff(ct)<0):
            self.picked.set_xdata(self.cycle_times[i,j])
        else:
            self.cycle_times[i,j] = x
        
        self.refreshTable()
        self.canvas.draw()
        self.colorSelected(i,j)
        self.picked = None
    
    def motionEvent(self, event):
        if self.picked is None: return
        self.picked.set_xdata(event.xdata)
        i,j = self.vlines[self.picked]
        
        if self.lineSelection is not None:
            self.lineSelection.set_xdata(event.xdata)
            
        self.canvas.draw()
    
    
    def colorSelected(self, i , j):
        if i is None:
            if self.lineSelection is not None:
                self.ax.lines.remove(self.lineSelection)
                self.lineSelection = None
        else:
            if self.lineSelection is None:
                self.lineSelection = self.ax.axvline( self.cycle_times[i,j] , color ='m' , alpha = .4, linewidth = 5 , picker = False)
            else:
                self.lineSelection.set_xdata(self.cycle_times[i,j])

            # change select in table
            self.disconnect(self.table ,SIGNAL('itemSelectionChanged()') , self.newSelectionInTable)
            
            flags = QItemSelectionModel.Select | QItemSelectionModel.Rows
            itemsSelection = QItemSelection()
            index = self.table.model().index(i,0,QModelIndex())
            ir = QItemSelectionRange( index )
            itemsSelection.append( ir )
            self.table.selectionModel().select( itemsSelection , flags)
            
            # set selection visible
            index = self.table.model().index(i,0,QModelIndex())
            item = self.table.itemFromIndex(index)
            self.table.scrollToItem( item )
            
            self.connect(self.table ,SIGNAL('itemSelectionChanged()') , self.newSelectionInTable)

                
        self.canvas.draw()
        
        
        

    ## highlight selection
    
    def newSelectionInTable(self):
        ind = [ ]
        for index in self.table.selectedIndexes():
            if index.column() == 0: ind.append(index.row())
        if len(ind)>=1 :
            self.colorSelected(ind[0] , 0)
        else:
            self.colorSelected(None,None)
    
    ## compute new one
    
    def newDetection(self):
        dia = QDialog()
        v = QVBoxLayout()
        dia.setLayout(v)
        self.wMeth = WidgetMultiMethodsParam(  list_method = list_method,
                                                                method_name = '<b>Choose methd for detection</b>:',
                                                                globalApplicationDict = self.globalApplicationDict,
                                                                keyformemory = 'methodRespiration',
                                                                )
        v.addWidget( self.wMeth )
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        v.addWidget(buttonBox)
        #~ self.connect( buttonBox.buttons()[1] , SIGNAL('clicked()') , self.apply )
        self.connect( buttonBox , SIGNAL('rejected()') , dia, SLOT('reject()') )
        self.connect( buttonBox , SIGNAL('accepted()') , dia, SLOT('accept()') )
        
        
        if dia.exec_():
            method =  self.wMeth.get_method()
            m = method()
            self.cycle_times =m.compute(self.respiration,  **self.wMeth.get_dict() )
            self.refreshPlot( with_same_zoom = False )
            self.refreshTable( )
        
    


    
        
    ## context menu insert and delete
    
    def contextMenuTable(self, point):
        ind = [ ]
        for index in self.table.selectedIndexes():
            if index.column() == 0: ind.append(index.row())
        
        
        menu = QMenu()
        act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Delete cycles'))
        self.connect(act,SIGNAL('triggered()') ,self.deleteSelectedCycles)
        
        if len(ind)==1:
            act = menu.addAction(QIcon(':/TODO.png'), self.tr('Insert cycle before this one'))
            self.connect(act,SIGNAL('triggered()') ,self.insertCycleBefore)
            
            act = menu.addAction(QIcon(':/TODO.png'), self.tr('Insert cycle after this one'))
            self.connect(act,SIGNAL('triggered()') ,self.insertCycleAfter)

        
        menu.exec_(self.cursor().pos())        

    
    def deleteSelectedCycles(self):
        ind = [ ]
        for index in self.table.selectedIndexes():
            if index.column() == 0: ind.append(index.row())
        
        indOK = numpy.setdiff1d(numpy.arange(self.cycle_times.shape[0]) , numpy.array(ind))
        
        if self.cycle_times.shape[0]-1 in ind and numpy.isnan(self.cycle_times[-1,-1]):
            nanlast = True
        else:
            nanlast = False
        self.cycle_times = self.cycle_times[indOK,:]
        if nanlast and self.cycle_times.shape[1] >1:
            self.cycle_times[-1,1:] = numpy.nan
        self.refreshPlot( with_same_zoom = True )
        self.refreshTable( )        
        
        
        
            
    def insertCycleBefore(self):
        i = self.table.selectedIndexes()[0].row() 
        self.insertCycle(i)
        
    
    def insertCycleAfter(self):
        i = self.table.selectedIndexes()[0].row() + 1
        self.insertCycle(i)
        
    def insertCycle(self, i):
        n = self.cycle_times.shape[1]
        ct = numpy.zeros( (self.cycle_times.shape[0]+1, n) , dtype = 'f')
        ct[:i , :] = self.cycle_times[:i,:]
        ct[i+1: , :] = self.cycle_times[i:,:]
        
        
        
        if i!=0:
            start = self.cycle_times[i-1,-1]
        else:
            start = self.cycle_times[0,0]-1.
            
        if i!=self.cycle_times.shape[0]:
            stop = self.cycle_times[i,0]
        else:
            stop = self.cycle_times[-1,-1]+1.
            if numpy.isnan(stop): return
        
        step = (stop-start)/(n+2)
        
        ct[i,:]  = numpy.arange(start+step, stop-step, step)
        
        self.cycle_times = ct

        self.refreshPlot( with_same_zoom = True )
        self.refreshTable( )        


    def save_to_db(self):
        #~ self.respiration = self.session.query(RespirationSignal).filter_by(id=self.id_respirationsignal).one()
        
        self.respiration.cycle_times = self.cycle_times
        self.session.merge(self.respiration)
        self.session.commit()
        self.session.expunge_all()
        
    def reload_from_db(self):
        #~ self.respiration = self.session.query(RespirationSignal).filter_by(id=self.id_respirationsignal).one()
        self.cycle_times = self.respiration.cycle_times
        self.refreshPlot( )
        self.refreshTable( )        
        self.session.expunge_all()
