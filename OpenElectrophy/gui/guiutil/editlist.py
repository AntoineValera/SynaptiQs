# -*- coding: utf-8 -*-



from PyQt4.QtCore import *
from PyQt4.QtGui import *


"""
Author:	Samuel Garcia
Laboratoire de Neurosciences Sensorielles, Comportement, Cognition.
CNRS - UMR5020 - Universite Claude Bernard LYON 1
Equipe logistique et technique
50, avenue Tony Garnier
69366 LYON Cedex 07
FRANCE
sgarcia@olfac.univ-lyon1.fr

License: CeCILL v2 (GPL v2 compatible)

"""


import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

if __name__ == '__main__' :
	app = QApplication(sys.argv)
	
from paramwidget import ParamDialog
from icons import icons

#------------------------------------------------------------------------------
class EditListAndProperties(QWidget) :
	#------------------------------------------------------------------------------
	def __init__(self, parent = None,
				edit_list = [ ],
				params = [ ],
				) :
		QWidget.__init__(self, parent)
		
		self.edit_list = edit_list
		self.params = [( 'name' , { 'value' :  'new'   }   ), ] + params
		
		mainLayout = QVBoxLayout()
		
		self.listview = QListWidget()
		self.listview.setSelectionMode( QAbstractItemView.SingleSelection )
		mainLayout.addWidget(self.listview)
		self.refresh_listview()
		
		h = QHBoxLayout()
		mainLayout.addLayout(h)
		
		but = QPushButton(QIcon(':/list-add.png') , 'Add')
		h.addWidget(but)
		self.connect(but,SIGNAL('clicked()'),self.add)

		but = QPushButton(QIcon(':/list-remove.png') ,'Del')
		h.addWidget(but)
		self.connect(but,SIGNAL('clicked()'),self.delete)
		
		but = QPushButton(QIcon(':/document-properties.png') , 'Edit')
		h.addWidget(but)
		self.connect(but,SIGNAL('clicked()'),self.edit)
		
		self.setLayout(mainLayout)
	
	
	#------------------------------------------------------------------------------
	def refresh_listview(self):
		self.listview.clear()
		
		for name, dict in self.edit_list:
			self.listview.addItem(name)
	
	#------------------------------------------------------------------------------
	def delete(self):
		sel = self.listview.selectedIndexes()
		if len(sel) == 0 : 
			pass
		else :
			r = sel[0].row()
			del self.edit_list[r]
			self.refresh_listview()
	
	#------------------------------------------------------------------------------
	def edit_or_add(self,  row = None):
		
			
		dialog = ParamDialog(self.params , parent = self)
		
		if row is None :
			self.edit_list += [	(  'new' , dialog.param_widget.get_dict()	) 	]
			row = len(self.edit_list) - 1
		
		name, dict = self.edit_list[row]
		dict['name'] = name
		dialog.param_widget.update( dict )

		ok = dialog.exec_()
		if  ok ==  QDialog.Accepted:
			pw = dialog.param_widget
			d = pw.get_dict()
			self.edit_list[row] =  d['name'], d
			
		self.refresh_listview()
		
	#------------------------------------------------------------------------------
	def add(self):
		self.edit_or_add()

	
	#------------------------------------------------------------------------------
	def edit(self):
		sel = self.listview.selectedIndexes()
		if len(sel) == 0 : 
			pass
		else :
			r = sel[0].row()
			self.edit_or_add(row = r)


	#------------------------------------------------------------------------------
	def get_list(self):
		return self.edit_list




		


#------------------------------------------------------------------------------
def test1():
	
	
	edit_list = [	('animal' , {  'editable' : True ,  'autoincrement' : False} ),
				('session' , {  'editable' : True ,  'autoincrement' : False} ),
				('run' , {  'editable' : True ,  'autoincrement' : True} ),
			]
	
	params = [	
				( 'editable' , { 'value' :  False   }   ),
				( 'autoincrement' , { 'value' :  False   }   ),
				
			]

	w = EditListAndProperties(edit_list = edit_list , params=params)
	w.show()
	
	
	sys.exit(app.exec_())


#------------------------------------------------------------------------------
if __name__ == '__main__' :
	test1()

