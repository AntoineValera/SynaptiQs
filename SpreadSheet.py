# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:30:45 2013

@author: pyvan187
"""
from PyQt4 import QtCore, QtGui



class SpreadSheet(QtGui.QWidget,object):
    
    def __init__(self,parent=None,Source=[range(25)],Labels=[''],Rendering=False,MustBeClosed=False):
        self.__name__="SpreadSheet"
        QtGui.QWidget.__init__(self)
        self.setParent(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        layout = QtGui.QVBoxLayout(self)
        maxlen=[]
        
        for i in Source:
            maxlen.append(len(i))
        Max=max(maxlen)
        self.table = QtGui.QTableWidget(Max,len(Source))
        
        self.table.setWindowTitle("Table")
        
        
        for i in range(len(Source)):
            for j in range(len(Source[i])):
                self.table.setItem(j,i,QtGui.QTableWidgetItem(str(Source[i][j])))
                
            self.table.setColumnWidth(i,80) 
            try:
                self.table.setHorizontalHeaderLabels(Labels[i])
            except IndexError:
                pass
        

        self.vBar = self.table.verticalScrollBar()
        self._vBar_lastVal = self.vBar.value()
    
        #self.table.setSortingEnabled(True)
    
        layout.addWidget(self.table)

        self.shcut1 = QtGui.QShortcut(self)
        self.shcut1.setKey("CTRL+C")
        
        
        UpdateSource = lambda: self.UpdateSourceArray(Source)
        QtCore.QObject.connect(self.shcut1, QtCore.SIGNAL("activated()"), self.copytoclipboard)
        QtCore.QObject.connect(self.vBar, QtCore.SIGNAL("valueChanged()"),self.scrollbarChanged)  
        QtCore.QObject.connect(self.table, QtCore.SIGNAL("cellChanged(int, int)"),UpdateSource)
        #QtCore.QObject.connect(self.table, QtCore.SIGNAL("itemChanged()"),self.UpdateSourceArray) 
        #QtCore.QObject.connect(self.table, QtCore.SIGNAL("itemSelectionChanged()"),self.copytoclipboard) 

        if MustBeClosed == True:
            self.setWindowModality(QtCore.Qt.ApplicationModal)
        if Rendering == True:
            self.show()
            
    #def closeEvent(self,event):
    #    # Let the Exit button handle tab closing
    #    print 'Spreadsheet Closed, arrays edited'      

    def UpdateSourceArray(self,Source):
        a=self.table.currentColumn()
        b=self.table.rowCount()
        for i in range(b):
            try:
                Source[int(a)][i] = float(self.table.item(i,a).text()) 
            except ValueError :
                Source[int(a)][b-1] = None#float(self.table.item(i,a).text())

    def copytoclipboard(self):
        
        a=self.table.selectedIndexes()
        
        d={}
        l=[]
        transposed_list=[]
        columnlist=[]
        rowlist=[]
        clip=''
        
        for i in a:
            d[(i.row(),i.column())]=str(i.data())#.toString())
            l.append((i.row(),i.column()))
            columnlist.append(i.column())
            rowlist.append(i.row())
            
        l.sort()

        for i in l:
            transposed_list.append([i[0],i[1],d[i]]) #row, column, value
        
        i=0
        while i < len(list(set(rowlist))): #colonne par colonne
            for k in transposed_list:
                if k[0] == i:#si on est dans la b colonne
                    clip+=k[2]+'\t'
            clip+='\n'            
            i+=1
        
        print 'selection copied to clipboard'
        QtGui.QApplication.clipboard().setText(clip)

    
    def scrollbarChanged(self,val):
        bar = self.vBar
        minVal, maxVal = bar.minimum(), bar.maximum()
        avg = (minVal+maxVal)/2
        rowCount = self.table.rowCount()

        # scrolling down
        if val > self._vBar_lastVal and val >= avg:
            self.table.insertRow(rowCount)

        # scrolling up
        elif val < self._vBar_lastVal:
            lastRow = rowCount-1
            empty = True
            for col in xrange(self.table.columnCount()):
                item = self.table.item(lastRow, col)
                if item and item.text():
                    empty=False
                    break
            if empty:
                self.table.removeRow(lastRow)

        self._vBar_lastVal = val  