# -*- coding: utf-8 -*- 
"""

"""

import classes.globalvars

import classes
from classes import allclasses
from classes.sqlalchemyutil import *
from classes.base import  OEBase

import numpy



#~ def close_db():
    #~ classes.globalvars.globalsession.close()


def Session():
    return classes.globalvars.globalSession()


def open_db( url = '' , metadata = None, use_global_session = True):
    
    """
    url is th url sqlalchemy style
    
    If metadata is None OpenElectrophy use a global metadata in the classes.globalvars
    file. The goal is to simplify script for end user when do not known sqlalchemy.
    
    If use_global_session is True it also create a global session (bad for memory but easy to use)
    
    
    
    
    """
    clear_mappers()
    
    #~ engine = create_engine(url, echo=True)
    engine = create_engine(url, echo=False)
    if metadata is None :
        metadata = classes.globalvars.globalmetadata
        metadata.bind = engine
        if use_global_session:
            classes.globalvars.globalSession = sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
            session = classes.globalvars.globalSession()
            
            
            #~ classes.globalvars.globalsession = create_session(bind=metadata.bind, autocommit=False, autoflush=True )
            #~ session = classes.globalvars.globalsession
    else:
        metadata.bind = engine
    
    
    
    # reflect existing
    metadata.reflect()
    #~ print dir(metadata.tables['segment'].c.id_block)
    
    # verify if db table need an update
    for tablename, table in metadata.tables.iteritems() :
        #~ print tablename
        #~ print table, type(table)
        if tablename in allclasses.keys() :
            # class exist in OE
            oeclass = allclasses[tablename]
            
            # verify if new field in db and not in oe
            for col in table.columns :
                #~ print col, type(col), col.name
                fieldnames = [ n for n,t in oeclass.fields ]
                if col.name in fieldnames :
                    #~ print col.name, 'exist'
                    pass
                else :
                    if col.name == 'id' :
                        pass
                    elif col.name.startswith('id_') :
                        parentname = col.name[3:]
                        #~ print 'ici' , tablename, parentname
                        if parentname not in oeclass.parents:
                            #~ print 'yep', parentname, tablename
                            oeclass.parents.append( str(parentname) )
                        
                    elif '_blob' in col.name: 
                        arrayname = col.name.replace('_blob' , '')
                        if arrayname not in fieldnames:
                            if  ( arrayname+'_shape' in table.columns) and \
                                    ( arrayname+'_dtype' in table.columns):
                                oeclass.fields += [ [arrayname , numpy.ndarray] ]

                    elif col.name.endswith('_dtype') or \
                        col.name.endswith('_shape') :
                        pass
                    
                    else :
                        #~ print col.name, ' not exist in oe adding ...'
                        
                        oeclass.fields += [[ col.name, type(col.type)]]
                        #~ print oeclass.fields
                #~ print col
            
            # verify new field in oe and not in db
            names = [ col.name for col in table.columns ]
            for fieldname, fieldtype in oeclass.fields :
                if fieldname not in names :
                    
                    addColumnToTable(metadata, oeclass , fieldname, fieldtype)
            
            
            for parentname in oeclass.parents : 
                if 'id_'+parentname not in names:
                    
                    #~ table.append_column( Column('id_'+parentname, ForeignKey(parentname+'.id') , index = True,) )
                    #~ sqltype = Integer().dialect_impl(engine.dialect).get_col_spec()
                    #~ if type(engine.dialect) == sqlite.SQLiteDialect:
                        #~ engine.execute("ALTER TABLE %s ADD COLUMN %s INT "%(tablename , 'id_'+parentname )  )
                    #~ else :
                        #~ engine.execute("ALTER TABLE %s ADD COLUMN %s INT,  ADD INDEX (%s) "%(tablename , 'id_'+parentname , 'id_'+parentname)  )

                    #~ col = Column('id_'+parentname, ForeignKey(parentname+'.id') , index = True,)
                    #~ col.create( table)
                    
                    col=  Column('id_'+parentname, Integer,)#  index = True , unique=False)
                    col.create( table)
                    ind = Index('ix_'+tablename+'_'+'id_'+parentname, col , unique = False)
                    ind.create()
                    
                    
            
            
        else :
            # class do not exist in OE
            #~ print 'this table is a new one', tablename, table
            classname = str(tablename[0].upper() + tablename[1:])
            newclass = type(classname,(OEBase,),{})
            newclass.tablename = tablename
            newclass.parents = [ ]
            newclass.children = [ ]
            newclass.fields = [ ]
            
            for col in table.columns:
                #~ print col, col.name, col.type
                if  col.name == 'id':
                    pass
                    #~ print col.primary_key
                elif col.name.startswith('id_'):
                    newclass.parents += [ col.name[3:] ]
                elif col.name.endswith('_blob') :
                    fieldname = col.name[:-5]
                    if  ( fieldname+'_shape' in table.columns) and \
                        ( fieldname+'_dtype' in table.columns) :
                        newclass.fields += [ [fieldname , numpy.ndarray] ]
                
                elif col.name.endswith('_dtype') or \
                    col.name.endswith('_shape') :
                    pass
                else:
                    # fixme type
                    newclass.fields += [ [col.name , type(col.type)] ]
            
            #FIXME : inject this oject in global scope
            #~ setattr(classes, tablename, newclass)
            classes.allclasses[tablename] = newclass
            
            
    # create table that are not in db
    #~ print allclasses
    for tablename, oeclass in allclasses.iteritems():
        #~ print tablename
        if tablename not in metadata.tables.keys() :
            #~ print 'create table', tablename
            
            columns = [ Column('id', Integer, primary_key=True) ,]
            for parentname in oeclass.parents :
                #~ columns += [ Column('id_'+parentname, Integer , index = True) ]
                columns += [ Column('id_'+parentname, ForeignKey(parentname+'.id') , index = True) ]
            for fieldname, fieldtype in oeclass.fields :
                if fieldtype == numpy.ndarray :
                    columns += [ Column(fieldname+'_shape', String(128)) ]
                    columns += [ Column(fieldname+'_dtype', String(128)) ]
                    columns += [ Column(fieldname+'_blob', LargeBinary(MAX_BINARY_SIZE)) ]
                else :
                    columns += [ Column(fieldname, fieldtype) ]
            table =  Table(tablename, metadata, *columns  )
    
    metadata.create_all()
    #~ engine
    
    # verify children <-> parents bijectivity
    for tablename, oeclass in allclasses.iteritems():
        toremove = [ ]
        for parentname in oeclass.parents :
            if parentname not in allclasses :
                 toremove += [parentname]
            else:
                if tablename not in allclasses[parentname].children:
                    allclasses[parentname].children.append(tablename)
        for rem in toremove:
            oeclass.parents.remove(rem)
            
        toremove = [ ]
        for childname in oeclass.children :
            if childname not in allclasses :
                toremove += [childname]
            else:
                if tablename not in allclasses[childname].parents:
                    allclasses[parentname].parents.append(tablename)
        for rem in toremove:
            oeclass.children.remove(rem)
    
    mapAll(metadata , allclasses)
    
    # attach allclasses dict for convenient use
    metadata.dictMappedClasses = allclasses
    
    return  metadata



    
    







