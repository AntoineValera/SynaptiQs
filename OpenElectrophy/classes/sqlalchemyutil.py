# -*- coding: utf-8 -*- 
"""

"""

import neo.core

#~ from ..sqlmapper import metadata

import sqlalchemy
import migrate.changeset

#~ from sqlalchemy.databases import mysql 
#~ from sqlalchemy.databases import sqlite


import globalvars

MAX_BINARY_SIZE = 2**30

from sqlalchemy import create_engine  , MetaData
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, Binary, Text, LargeBinary, DateTime

from sqlalchemy import orm
from sqlalchemy.orm import sessionmaker
#~ from sqlalchemy.orm import create_session
from sqlalchemy.orm import mapper , deferred, backref, clear_mappers, relationship

from sqlalchemy import Index

import numpy


def addColumnToTable(metadata, oeclass , fieldname, fieldtype):
    #~ print metadata, oeclass , fieldname, fieldtype
    table = metadata.tables[oeclass.tablename]
    names = [ col.name for col in table.columns ]
    if fieldname in names:
        print oeclass.tablename, 'add already ', fieldname
        return
        
    if fieldtype == numpy.ndarray :
        if fieldname+'_shape' not in names :
            col =  Column(fieldname+'_shape', String(128))
            col.create( table)
            col =  Column(fieldname+'_dtype', String(128))
            col.create( table)
            col =  Column(fieldname+'_blob', LargeBinary(MAX_BINARY_SIZE))
            col.create( table)
    else :
        col = Column(fieldname, fieldtype)
        col.create( table )


def removeColumnToTable(metadata, oeclass , fieldname):
    #~ print metadata, oeclass , fieldname, fieldtype
    table = metadata.tables[oeclass.tablename]
    fieldtype = dict(oeclass.fields)[fieldname]
    
    if fieldtype == numpy.ndarray :
        for suffix in [ '_shape' , '_dtype' , '_blob' ]:
            table.c[fieldname+suffix].drop()
    else :
        table.c[fieldname].drop()

def addAChildToTable(metadata, oeclass , childname):
    if childname not in metadata.tables : return
    parenttable = metadata.tables[oeclass.tablename]
    childtable = metadata.tables[childname]
    parentname = oeclass.tablename
    # FIXME (not clean):
    #~ col=  Column('id_'+parentname, Integer,  index = True , unique=False)
    #~ col.create( childtable , index_name = 'ix_'+childname+'_'+'id_'+parentname, unique = False)
    
    # better:
    col=  Column('id_'+parentname, Integer,)#  index = True , unique=False)
    col.create( childtable)
    ind = Index('ix_'+childname+'_'+'id_'+parentname, col , unique = False)
    ind.create()




def mapAll(metadata , allclasses):
    
    clear_mappers()
    
    for tablename, oeclass in allclasses.iteritems():
        table = metadata.tables[tablename]
        for parentname in oeclass.parents :
            table.c['id_'+parentname].append_foreign_key( ForeignKey(parentname+'.id') ) 
    
    
    
    for tablename, oeclass in allclasses.iteritems():
        table = metadata.tables[tablename]
        properties = { }
        for fieldname, fieldtype in oeclass.fields :
            if fieldtype == numpy.ndarray :
                properties[fieldname+'_shape'] = deferred( table.columns[fieldname+'_shape'] , group = fieldname)
                properties[fieldname+'_dtype'] = deferred( table.columns[fieldname+'_dtype'] , group = fieldname)
                properties[fieldname+'_blob'] = deferred( table.columns[fieldname+'_blob'] , group = fieldname)
        
        for child in oeclass.children :
            #~ properties['_'+child+'s'] = relationship(allclasses[child] , )
            #~ print tablename , child
            properties['_'+child+'s'] = relationship(allclasses[child] ,
                            primaryjoin = table.c.id==metadata.tables[child].c['id_'+tablename], 
                            order_by = metadata.tables[child].c['id'],
                            
                            
                            backref=backref(tablename),
                            
                            # FIXME
                            #~ cascade="all, delete, delete-orphan",
                            #~ cascade="all, delete, delete-orphan",
                            cascade="all, delete",
                            #~ cascade="all",
                            
                            #~ lazy = True,
                                        )
        
        mapper(oeclass , table , properties = properties , )
        
         #non_primary=True to create a non primary Mapper.  clear_mappers()
        
    # set numpy.ndarray field property for all classes
    for tablename, oeclass in allclasses.iteritems():
            for fieldname, fieldtype in oeclass.fields :
                if fieldtype == numpy.ndarray :
                    setattr(oeclass, fieldname, property( NumpyField(fieldname).getfield , NumpyField(fieldname).setfield) )



class NumpyField():
    """ 
    Class to manage property of numpy field in OE classes
    """
    def __init__(self, name):
        self.name = name
    
    def getfield(self , self2):
        #~ print 'self2',type(self2),self2
        #~ print 'self',type(self),self
        #~ print self2.__getattribute__(self.name+'_shape')

        if hasattr(self2, self.name+'_array') :
            return getattr(self2, self.name+'_array')

        if self2.__getattribute__(self.name+'_shape') is None or \
            self2.__getattribute__(self.name+'_dtype') is None or \
            self2.__getattribute__(self.name+'_blob') is None :
            return None
        
        
        else :
            # patch for sqlalchemy < 0.6 (ubuntu 10.4 is 0.58)
            #~ if sqlalchemy.__version__.startswith('0.5.8'):
                #~ from sqlalchemy.orm.attributes import instance_state
                #~ modified = instance_state(self2).modified
                #~ b = str(self2.__getattribute__(self.name+'_blob'))
                #~ self2.__setattr__(self.name+'_blob', b)
                #~ if not modified :
                    #~ instance_state(self2).modified = False
                    #~ self2.session.identity_map._modified.remove(self2._sa_instance_state)
            # end patch
            
           
            
            shape=[]
            for i in self2.__getattribute__(self.name+'_shape').split(',') :
                shape.append(int(i.replace('L','')))
            #shape = [ int(v) for v in self2.__getattribute__(self.name+'_shape').split(',') ]
            
            dt = numpy.dtype(str(self2.__getattribute__(self.name+'_dtype')))
            if numpy.prod(shape)==0:
                arr= numpy.empty( shape, dtype = dt )
            else:
                arr = numpy.frombuffer( self2.__getattribute__(self.name+'_blob') , dtype = dt)
                arr.flags.writeable = True
                arr = arr.reshape(shape)
            setattr(self2, self.name+'_array', arr)
            return arr


    def setfield(self, self2, value):
        if value is None:
            self2.__setattr__(self.name+'_shape',    None)
            self2.__setattr__(self.name+'_dtype', None)
            self2.__setattr__(self.name+'_blob', None)
            
            if hasattr(self2, self.name+'_array') :
                delattr(self2, self.name+'_array')
            return 
        assert (type(value) == numpy.ndarray) or (type(value) == numpy.memmap) , 'value si not numpy.array or memmap'
        shape = str(value.shape).replace('(','').replace(')','').replace(' ','')
        if shape.endswith(',') : shape = shape[:-1]
        self2.__setattr__(self.name+'_shape',    shape)
        self2.__setattr__(self.name+'_dtype', value.dtype.str)
        self2.__setattr__(self.name+'_blob', value.tostring())
        #~ self2.__setattr__(self.name+'_blob', numpy.getbuffer(value))
        self2.__setattr__(self.name+'_array', value)


def execute_sql(query ,*args,  **kargs):
    if 'metadata' in kargs :
        metadata = kargs['metadata']
        if 'session' in kargs:
            session = kargs['session']
        else:
            #~ session = create_session(bind=metadata.bind, autocommit=False, autoflush=True )
            Session = sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
            session = Session()
    else:
        metadata = globalvars.globalmetadata
        if 'session' in kargs:
            session = kargs['session']
        else:
            session = globalvars.globalSession()
        
    
    if 'column_split' in kargs :
        column_split = kargs['column_split']
    else:
        column_split = True   

    if 'Array' in kargs :
        Array = kargs['Array']
    else:
        Array = True   
    
    
    
    pres = session.execute(query, kargs)
    if pres.rowcount == 0:
        if column_split :
            
            if sqlalchemy.__version__.startswith('0.5.8'):
                if Array:
                    res = [ numpy.array([ ]) for i in pres.keys ]
                else:
                    res = [ [ ] for i in pres.keys ]
            else:
                if Array:
                    res = [ numpy.array([ ]) for i in pres.keys() ]
                else:
                    res = [ [ ] for i in pres.keys() ]
        else:
            res = [ ]
    else:
        res = pres.fetchall()
        if column_split :
            
            #debug for oursql
            if len(res) == 0:
                if Array:
                    res = [ numpy.array([ ]) for i in pres.keys() ]
                else:
                    res = [ [ ] for i in pres.keys() ]
                return res    
             #end debug


            res2 = numpy.array( res, dtype = object)
            res = [ ]
            for i in range(res2.shape[1]):
                if Array:
                    res += [ res2[:,i] ]
                else :
                    res += [ res2[:,i].tolist() ]
    
    session.close()
    return res

# alias
sql  = execute_sql

