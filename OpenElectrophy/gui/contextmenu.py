# -*- coding: utf-8 -*-


"""
This modules is for context menu in a treeview

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
from guiutil.paramwidget import *
from guiutil.multiparamwidget import WidgetMultiMethodsParam


from OpenElectrophy.classes import *

from oscillationdetection import OscillationDetection
from respirationcycle import RespirationCycleEdition



class EditFields(QWidget):
    def __init__(self  , parent = None ,
                            metadata = None,
                            session = None,
                            id = None,
                            tablename=None,
                            ):
        QWidget.__init__(self, parent)
        self.metadata = metadata
        self.session = session
        

        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        OEclass = self.metadata.dictMappedClasses[tablename]
        self.OEinstance = self.session.query(OEclass).filter_by(id=id).one()
        
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle('Edit fields for %s : %d'%(tablename , id))
        
        params = [ ]
        for fieldname, t in self.OEinstance.fields :
            if t != numpy.ndarray:
                d = { 'value' :  self.OEinstance[fieldname]   }
                if self.OEinstance[fieldname] is None:
                    d['type']= str
                params += [ (fieldname ,    d) ]
        self.params = ParamWidget(params)
        self.mainLayout.addWidget( self.params )
 
        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        #~ self.connect( buttonBox , SIGNAL('accepted()') , self, SLOT('accept()') )
        self.connect( buttonBox , SIGNAL('accepted()') , self.saveAndClose )
        self.connect( buttonBox , SIGNAL('rejected()') , self.close )

    def saveAndClose(self):
        #~ self.OEinstance.__dict__.update(self.params.get_dict())
        for k,v in self.params.get_dict().iteritems():
            self.OEinstance[k] = v
        
        # ????
        #~ self.session.add(self.OEinstance)
        self.session.commit()
        
        self.close()

def editFieldsSelection(parent=None,
                                    id =None, 
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                    tablename =  None,
                                    ):
    w = EditFields(parent = parent ,
                    metadata = metadata,
                    session = session,
                    id = id,
                    tablename = tablename,
                    )
    w.show()    





def editOscillation(    parent=None,
                                    id =None, 
                                    tablename = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                        ):
    w= OscillationDetection(parent = parent,
                            metadata =metadata,
                            Session = Session,
                            globalApplicationDict = globalApplicationDict,
                            id_analogsignal = id,
                            tablename = tablename,
                            mode = 'all signal')
    w.show()





#~ def spikeSorting_all_step_mode( parent=None,
                                    #~ id =None, 
                                    #~ tablename = None,
                                    #~ metadata = None, 
                                    #~ Session = None,
                                    #~ session = None,
                                    #~ globalApplicationDict = None,
                                        #~ ):
    #~ w = SpikeSorting(   parent = parent ,
                                #~ metadata = metadata,
                                #~ tablename = tablename,
                                #~ session = session,
                                #~ Session = Session,
                                #~ globalApplicationDict= globalApplicationDict,
                                #~ mode ='all_step_mode',
                                #~ id_recordingpoint = id,
                                #~ )
    #~ w.show()

#~ def spikeSorting_reclustering_mode( parent=None,
                                    #~ id =None, 
                                    #~ tablename = None,
                                    #~ metadata = None, 
                                    #~ Session = None,
                                    #~ session = None,
                                    #~ globalApplicationDict = None,
                                        
                                        #~ ):
    #~ w = SpikeSorting(   parent = parent ,
                                #~ metadata = metadata,
                                #~ tablename = tablename,
                                #~ session = session,
                                #~ Session = Session,
                                #~ globalApplicationDict= globalApplicationDict,
                                #~ mode ='reclustering_mode',
                                #~ id_recordingpoint = id,
                                #~ )
    #~ w.show()


def newSpikeSorting_from_full_band_signal( parent=None,
                                    id =None, 
                                    tablename = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                        ):

    #DEBUG
    mainw = parent
    while True:
        p = mainw.parent()
        if p is None: break
        mainw = p
    #~ print mainw
    if not(hasattr(mainw, 'listSpikeSortingWindows')):
        mainw.listSpikeSortingWindows = [ ]
    print mainw.listSpikeSortingWindows
    #~ for w in mainw.listSpikeSortingWindows:
        #~ print w, w.isVisible()
        
            
    # END DEBUG
    
    mainw.listSpikeSortingWindows = [ ]
    

    from spikesorting import SpikeSorting
    w = SpikeSorting(             parent = None ,
                                            metadata = metadata,
                                            Session = Session,
                                            session=session,
                                            globalApplicationDict= globalApplicationDict,
                                            mode ='from_full_band_signal',
                                            id_recordingpoint = id,
                                            )
    w.setAttribute(Qt.WA_DeleteOnClose)
    w.show()
    
    mainw.listSpikeSortingWindows.append(w)
    
    


def newSpikeSorting_from_filtered_signal( parent=None,
                                    id =None, 
                                    tablename = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                        ):
    from spikesorting import SpikeSorting
    w = SpikeSorting(             parent = parent ,
                                            metadata = metadata,
                                            Session = Session,
                                            globalApplicationDict= globalApplicationDict,
                                            mode ='from_filtered_signal',
                                            id_recordingpoint = id,
                                            )
    w.show()    

def newSpikeSorting_from_detected_spike( parent=None,
                                    id =None, 
                                    tablename = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                        ):
    from spikesorting import SpikeSorting
    w = SpikeSorting(             parent = parent ,
                                            metadata = metadata,
                                            Session = Session,
                                            globalApplicationDict= globalApplicationDict,
                                            mode ='from_detected_spike',
                                            id_recordingpoint = id,
                                            )
    w.show()  





def detect_respiratory_cycles( parent=None,
                                    id =None, 
                                    tablename = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                        
                                        ):
    w = RespirationCycleEdition(   parent = parent ,
                                metadata = metadata,
                                Session = Session,
                                session = session,
                                globalApplicationDict= globalApplicationDict,
                                id_respirationsignal = id,
                                )
    w.show()




def deleteSelection(parent=None,
                                    ids =None, 
                                    tablenames = None,
                                    metadata = None,
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                    ):
    
    for warn in  [  'Do you want to delete this and all of its descendants?',
                            'Are you sure?',
                            'Are you really sure?',
                            ]:
        mb = QMessageBox.warning(parent,parent.tr('delete'),parent.tr(warn), 
                QMessageBox.Ok ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                QMessageBox.NoButton)
        if mb == QMessageBox.Cancel : return
    
    
    
    for id, tablename in zip(ids, tablenames) :
        OEclass = metadata.dictMappedClasses[tablename]
        
        # this do not work in cascade because it is directly SQL
        #~ session.query(OEclass).filter_by(id=id).delete()
        
        # this works but slow
        q = session.query(OEclass).filter(OEclass.id==id)
        OEinstance = q.one()
        session.delete(OEinstance)
    
    session.commit()
    explorer =  parent.parent().parent().parent()
    explorer.refresh()
    

def drawSelection(parent=None,
                                    ids =None,
                                    tablenames = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                    ):
    mainWindow = parent
    while mainWindow.parent() is not None :
        mainWindow = mainWindow.parent()
    mainWindow.figureTools.drawSelection()    



def saveAsFile(parent=None,
                                    ids =None,
                                    tablenames = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None, ):
    # mode homogeneous
    tablename = tablenames[0]
    
    session = Session()
    
    OEclass = metadata.dictMappedClasses[tablename]
    
    from ..io.io import all_format
    
    list_formats = [ ]
    formats ={ }
    for name, d in all_format:
        
        wo = [ o.__name__.lower() for o in d['class'].writeable_objects ]
        if tablename in wo:
            class F:
                pass
            f = F()
            f.name = name
            f.params = d['class'].write_params[ OEclass ]
            list_formats.append( f )
            formats[name] = d['class']
    
    dia = QDialog()
    dia.setWindowFlags(Qt.Dialog)
    v = QVBoxLayout()
    dia.setLayout(v)
    
    mwp = WidgetMultiMethodsParam( parent = parent ,
                        list_method = list_formats,
                        method_name = 'Export selected '+tablename,
                        globalApplicationDict = globalApplicationDict,
                        )
    v.addWidget( mwp )
    
    params = [
                        [ 'dir' , { 'value' : '' , 'widgettype' : ChooseDirWidget  , 'label' : 'Select path to write files' }],
                    ]
    place = ParamWidget(
                                params,
                                applicationdict = globalApplicationDict,
                                title = None,
                                )
    v.addWidget( place )

    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
    v.addWidget(buttonBox)
    dia.connect(buttonBox, SIGNAL('accepted()'), dia, SLOT('accept()'));

    if dia.exec_():
        name =  mwp.get_name()
        options =  mwp.get_dict()
        dir = place['dir']
        for id in ids:
            OEinstance = session.query(OEclass).filter_by(id=id).one()
            IOinstance = formats[name](filename = os.path.join( dir, OEinstance.name+'.'+formats[name].extensions[0] ) )
            if OEclass ==Segment:
                IOinstance.write_segment( OEinstance, **options)
            elif OEclass ==Block:
                IOinstance.write_block( OEinstance, **options)


def changeParent(parent=None,
                                    ids =None,
                                    tablenames = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None, ):
    # mode homogeneous
    tablename = tablenames[0]
    possible_parents = metadata.dictMappedClasses[tablename].parents
    if len(possible_parents)==0: return


    dia = QDialog()
    dia.setWindowFlags(Qt.Dialog)
    v = QVBoxLayout()
    dia.setLayout(v)
    
    params = [
                        [ 'parentname' , { 'value' : possible_parents[0] , 'possible' : possible_parents  , 'label' : 'Wich parent to change' }],
                        [ 'id' , { 'value' : '' , 'type' : int  , 'label' : 'Id of new parent' }],
                    ]
    which = ParamWidget(
                                params,
                                applicationdict = globalApplicationDict,
                                title = None,
                                )
    v.addWidget( which )

    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
    v.addWidget(buttonBox)
    dia.connect(buttonBox, SIGNAL('accepted()'), dia, SLOT('accept()'));

    if dia.exec_():
        # test if correct
        try:
            parentname = which['parentname']
            id_parent = which['id']
        except:
            return
        
        # verify that parent exists
        OEclass = metadata.dictMappedClasses[parentname]
        if session.query(OEclass).filter_by(id=id_parent).count()>0:
            OEclass = metadata.dictMappedClasses[tablename]
            for id in ids:
                OEinstance = session.query(OEclass).filter(OEclass.id==id).one()
                OEinstance['id_'+parentname] = id_parent
            session.commit()
            parent.refresh()
        
        
        if 'block' == which['parentname'] and tablenames[0] == 'segment':
            warn = """You have changed a Segment to another Block. You should apply fix recordingpoints to this block and understand why..."""
            mb = QMessageBox.warning(parent,parent.tr('delete'),parent.tr(warn), 
                    QMessageBox.Ok ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                    QMessageBox.NoButton)



        #~ else:
            #~ print 'do not exists'
        

def addATopElement(parent=None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None, 
                                    topHierarchyTable = None,
                                    ):
    oeinstance = metadata.dictMappedClasses[topHierarchyTable]()
    session.add(oeinstance)
    session.commit()
    parent.refresh()


def fixRecordingPoints( parent=None,
                                    id =None, 
                                    tablename = None,
                                    metadata = None, 
                                    Session = None,
                                    session = None,
                                    globalApplicationDict = None,
                                        
                                        ):
        warn = """All SpikeTrain.channel and AnalogSignal.channel that are not coherent with recordingpoint.channel will be moved to the good recording point
                    """
        
        mb = QMessageBox.warning(parent,parent.tr('delete'),parent.tr(warn), 
                QMessageBox.Ok ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                QMessageBox.NoButton)
        if mb == QMessageBox.Cancel : return
        bl  = session.query(Block).filter_by(id=id).one()
        bl.fix_recordingpoints()
        session.commit()
        parent.refresh()
        




# name  callback    icon    mode (unique or many or homogeneous)

context_menu = {

                            'alltable' : [ 
                                            ['Delete' , deleteSelection , ':/user-trash.png' , 'homogeneous'],
                                            ['Draw' , drawSelection , ':/office-chart-line.png' , 'all'],
                                            ['Edit' , editFieldsSelection , ':/view-form.png' , 'unique'],
                                            
                                            ['Change parent' , changeParent , ':/view-process-all-tree.png' , 'homogeneous'],
                                            
                                            ['Create empty top hierachical element' , addATopElement , ':/list-add.png' , 'empty'],
                                            
                                            
                                        ],

                            'block' : [ 
                                                #~ ['Save as file' , saveAsFile , ':/document-save.png' , 'homogeneous'],
                                                
                                                ['fix recordingpoints', fixRecordingPoints , ':/block.png'  , 'unique'],
                                                
                                            
                                                
                                            ],
                            'segment': [
                                                    ['Save as file' , saveAsFile , ':/document-save.png' , 'homogeneous'],
                                            ],
                            'analogsignal': [ 
                                                ['edit oscillations', editOscillation , ':/oscillation.png'  , 'unique'],
                                            ],
                            'recordingpoint': [
                                                #~ ['Spike Sorting all mode (Filtering+Detection+Projection+Clustering)', spikeSorting_all_step_mode , ':/spike.png'  , 'unique'],
                                                #~ ['Spike Sorting reclustering mode (Projection+Clustering)', spikeSorting_reclustering_mode , ':/spike.png' , 'unique'],
                                                
                                                ['Spike Sorting (mode = from full band signal)', newSpikeSorting_from_full_band_signal , ':/spike.png' , 'unique'],
                                                ['Spike Sorting (mode = from filtered signal)', newSpikeSorting_from_filtered_signal , ':/spike.png' , 'unique'],
                                                ['Spike Sorting (mode = from detected spikes)', newSpikeSorting_from_detected_spike , ':/spike.png' , 'unique'],
                                            ],
                            
                            'respirationsignal' :  [
                                                ['Detect respiratory cycles', detect_respiratory_cycles , ':/repiration.png'  , 'unique'],
                                                
                                            ],
                            
                            


                            }
