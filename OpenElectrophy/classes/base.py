# -*- coding: utf-8 -*- 
"""

"""

import neo.core

#~ from ..sqlmapper import metadata

import globalvars



#~ from sqlalchemy.orm import sessionmaker
#~ from sqlalchemy.orm import create_session
from sqlalchemy import orm


from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, Binary, Text, LargeBinary
import sqlalchemy
import migrate.changeset

import numpy


ECHO = False
#~ ECHO = True

from sqlalchemyutil import *
    
    
    
    






class OEBase(object):
    """The base OE class that makes this object suitable for SQL.
    
    OE objects inherit from this base class. They also inherit from
    the neo class for the same object. They should define the following
    attributes:
        fields : sql fields for that object, such as `name`
        parents : objects that can be parents for it
    
    OEBase provides the following
    extra functionality:
    
    __new__ : Ability to load from database
    __init__ : Stores links to sql fields and parents
    save, load : save and load from database
    childrenInTree, parentInTree : navigating sql database
    __setitem__, __getitem__ : dict-like access to attributes
    copy : return copy with same information as specified in `fields`
    """
    
    def __new__( cls, session = None,*args, **kargs):
        """
        This is buggy for the moment ...
        It load all the hierarchy ...
        
        The idea is to load an object an instanciation
        
        seg = Segment(id = 45) # this do load
        """
        if 'id' in kargs:
            return cls.test_load(id =kargs ['id'],  session = session)
        else:
            return super( OEBase,cls).__new__(cls)
            
    @orm.reconstructor
    def init_on_load(self):
        pass
        #~ print 'init on load', self.id
        

            

        #~ tag = cls.query.filter(cls.name == tag_name).first()
        #~ if not tag:
            #~ tag = cls(tag_name)
        #~ return tag


    def __init__(self, *args, **kargs):
        """Constructs OEBase object.
        
        The purpose of this is to add the fields and attributes to
        OE objects to allow them to be added to the SQL database
        and to be linked to other objects in the database.
        
        Do not pass in non-keyname arguments. 
        
        Parameters
        ----------
        id_* : If * is in self.parents, then this link will be stored.        
        metadata : sqlalchemy Metadata object, or the global metadata
        * : if * is in self.fields, then this value will be stored as an
            attribute, unless it was already set by another constructor.        
        
        All keyname arguments will be ignored. If a keyname argument
        already exists in the object (because it was defined in the neo
        constructor), then that argument will be ignored.
        """
        if 'metadata' in kargs.keys() :
            self.metadata = kargs['metadata']
        else :
            self.metadata = globalvars.globalmetadata
        
        self.dict_field_types = dict(self.fields)
        
        for k,v in kargs.iteritems():
            if k.startswith('id_') and k[3:] in self.parents and (v is not None):
                # Link to parent object
                self[k] = v
            if k in dict(self.fields).keys() and (v is not None):
                # Other attribute
                try:
                    # Does it already exist?
                    # If so it was probably set by another constructor
                    self[k]
                    
                    # But upon loading the attribute may be None, so
                    # override this. This is not the best solution because
                    # this means that the neo object cannot force an attribute
                    # to be None if the keyword arg is not None.
                    if self[k] is None:
                        self[k] = v
                except AttributeError:
                    # If not, then store
                    self[k] = v


    def __setitem__(self , key , val) :
        setattr(self, key, val)
        
    def __getitem__(self, key):
        return getattr(self, key)

    def save(self  , session = None):
        """
        Usefull to create a new field in script mode (based on globalsession and global metadata).
        
        Save the object in the database (perform a session.commit()).
        
        If self.id is None => insert
        If self.id is not None => update
        
        
        """
        if session is None:
            session = globalvars.globalSession()

        if self.id is None:
            session.add(self)
            session.commit()
        else:
            merged = session.merge(self)
            session.commit()
            id = merged.id

        if ECHO:
            print self.tablename , ' saved', self.id
        
        return self.id


    @classmethod
    def test_load(cls, id, session = None,):
        
        print 'cls', cls
        if session is None:
            session = globalvars.globalSession()
        
        query = session.query(cls).filter_by(id=id)
        if query.count()==0:
            return cls()
        return query.one()


    @classmethod
    def load(cls, id, session = None,):
        """
        Load from the database with a id.
        
        You must call methods thids way :
        
        inst = MyObject.load(id, session = None)
        
        if session is None take 
        
        ex : 
        bl = Block.load(4)
        anasig = AnalogSignal.load(id)
        """
        
        #~ if not hasattr(self, 'metadata'):
            #~ self.metadata = globalvars.globalmetadata
        
        if session is None:
            session = globalvars.globalSession()
        
        
        query = session.query(cls).filter_by(id=id)
        if query.count()==0:
            return None
        
        loaded = query.one()
        #~ loaded.metadata = self.metadata
        loaded.session = session
        return loaded
    
    

    #~ def delete(self):
        #~ pass
        #~ session.delete
    
    def copy(self):
        
        #~ inst = self.metadata.dictMappedClasses[self.tablename]()
        inst = self.__class__()
        for key,u in self.fields:
            inst[key] = self[key]
            
        return inst

    
    def addColumn(self, fieldname, fieldtype):
        """
        Usefull to create a new field in script mode (based on global metadata).
        
        Create a column if not exists.
        
        args
         fieldname: name of field
         fieldtype: type sqlalchemy like (Interger, Text, Float, ...)
        
        """
        for f,t in self.fields:
            if f == fieldname:
                return
                
        if not hasattr(self, 'metadata'):
            self.metadata = globalvars.globalmetadata
        
        addColumnToTable(self.metadata, self.__class__ , fieldname, fieldtype)
        self.__class__ .fields.append( [ fieldname, fieldtype])
        
    def parentInTree(self, dictChildren, session , dictMappedClasses):
        """
        Function for navigating in a qtsqltree. Give the parent in a tree.
        
        args
        
        dictChildren : a dict a of children for all objects.
        session : sqlalchemy session for querying
        dictMappedClasses : dict tablename -> mapped object
        
        """
        for parentname in self.parents :
            if parentname not in dictChildren.keys():continue
            if self.tablename in dictChildren[parentname] :
                return self[parentname]
        return None
    
    def childrenInTree(self, dictChildren, session):
        """
        Function for navigating in a qtsqltree. Give the children in a tree.
        
        args
        
        dictChildren : a dict a of children for all objects.
        session : sqlalchemy session for querying
        
        """
        if self.tablename not in dictChildren : return [ ]
        children = [ ]
        for childname in dictChildren[self.tablename] :
            children += getattr(self, '_'+childname+'s')
        for child in children :
            child.metadata = self.metadata
            child.session = self.session
            if child not in self.session.cache_for_all:
                self.session.cache_for_all.append(child)
            
        return children



