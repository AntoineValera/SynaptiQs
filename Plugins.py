# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:31:19 2013

@author: Antoine Valera
"""


import __builtin__
import os,sys,traceback
from PyQt4 import QtCore, QtGui, Qsci



class Plugins(object):
    """
    Plugins contains your User defined Script
    
    You can call your user defined function with Plugins.<script_name>.<User_Function>(self) Every script name is a new class
    
    print Plugins.Plugin_List sort the script list
    Plugins._Info('name') sort the avaible fonction in the 'name' script
    """
    
    def __init__(self):
        self.__name__="Plugins"

        newpath = str(Main.userpath)+"/.SynaptiQs/"
        if not os.path.exists(newpath): os.makedirs(newpath)
        sys.path.append(newpath)
        
        dirList=[]
        
        for f in os.listdir(newpath):
            if os.path.splitext(f)[1] == ".py":
                dirList.append(f)   
                
       
        for i in range(len(dirList)):
            dirList[i]=dirList[i].replace(".py","")
        Main.Plugins_Menu.addAction('Reload All',self.Reload,'CTRL+R')
        Main.Plugins_Menu.addAction('New Script',self.Write_Script_Plugin,'CTRL+N')
        Main.Plugins_Menu.addAction('Force Load',self.Force_Load)
        Main.Plugins_Menu.addSeparator() 

           
        self.Plugin_List=[]
        

        for plugin in dirList:
            if plugin.find('$') == -1 and plugin.find('#') == -1 and plugin.find('__') == -1: #not checked
                try:
                    setattr(sys.modules[__name__],plugin,__import__(plugin))
                    Main.Plugins_Menu.addAction(str(plugin),lambda plugin=plugin: self.Load(plugin))
                    self.Plugin_List.append(plugin) 
                except NameError:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    While trying to load <b>%s.py plugin</b> an error occured
                    <p>Don't forget that plugin code must be stored in functions, and NOT directly on script root, except if you want the script to be executed at SynaptiQs launch
                    <p>This script was not loaded, and set as inactive ($)
                    <p>You can use 'Force Load' function to correct the error                   
                    """ %(plugin))     
                    os.rename(str(Main.userpath)+"/.SynaptiQs/"+"%s.py" %(plugin),str(Main.userpath)+"/.SynaptiQs/"+"$"+"%s.py" %(plugin))
                    msgBox.exec_()  

                except SyntaxError:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    While trying to load <b>%s.py plugin</b> an error occured
                    <p>This script may contain a Non-ASCII character.
                    <p>This script was not loaded, and set as inactive ($)
                    <p>You can use 'Force Load' function to correct the error                    
                    """ %(plugin)) 
                    os.rename(str(Main.userpath)+"/.SynaptiQs/"+"%s.py" %(plugin),str(Main.userpath)+"/.SynaptiQs/"+"$"+"%s.py" %(plugin))
                    msgBox.exec_()   
                    pass
                except:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    While trying to load <b>%s.py plugin</b> an unidentified error occured
                    <p>This script was not loaded, and set as inactive ($)
                    <p>You can use 'Force Load' function to correct the error
                    """ %(plugin))                      
                    msgBox.exec_()
                    os.rename(str(Main.userpath)+"/.SynaptiQs/"+"%s.py" %(plugin),str(Main.userpath)+"/.SynaptiQs/"+"$"+"%s.py" %(plugin))
                    pass                    
                    
                    
                    
            else:
                print plugin,' was not Loaded'
    def _all(self,All=False):
        List=[]
        i=self.__name__
        for j in dir(eval(i)):
            if All==False and j[:2] == '__':
                pass
            else:
                List.append(i+'.'+j)
        for i in List:
            print i    
    def _Info(self,name):
        print 'This are the avaible methods in Plugins.%s Module : ' % name
        List=[method for method in dir(eval('Plugins.'+name)) if callable(getattr(eval('Plugins.'+name), method))]
        for i in List:
            print i              
        

    def Load(self,name=None):
        """
        This function load a .py plugin into SynaptiQs.
        'name' is the name of the plugin without extension.
        path is the folder of the plugin. If None, path is //.SynaptiQs/  (press Ctrl+P)
        """
        
        if name==None:
            name, ok = QtGui.QInputDialog.getText(Main.FilteringWidget, 'Input Dialog', 
                'Please write the name of your Plugin, without .py extension\n The Plugin must be in '+str(Main.userpath)+"/.SynaptiQs/ folder")
            if not ok:
                return

        path=str(Main.userpath)+'/.SynaptiQs/'

        source=path+name+'.py' 
        self.Reload()#  Pb because it also reload all the non-saved script, without saving... 
        self.Write_Script_Plugin(source)

        
    def Force_Load(self):
        
        path = QtGui.QFileDialog()
        path.setDirectory(str(Main.userpath)+'/.SynaptiQs/')
        path.setNameFilter("Python Script (*.py)")
        path.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        path.setFileMode(QtGui.QFileDialog.ExistingFiles)
        
        if (path.exec_()) :
            File=str(path.selectedFiles()[0])

            self.Write_Script_Plugin(File)

       
    def Reload(self):
        """
        This function actualize the Plugin Menu
        """
        print '-----------> Plugins were Reloaded'
        self.Plugin_List=[]
        

        newpath = str(Main.userpath)+"/.SynaptiQs/"
        if not os.path.exists(newpath): os.makedirs(newpath)
        sys.path.append(newpath)
        dirList=[]
        
        for f in os.listdir(newpath):
            if os.path.splitext(f)[1] == ".py":
                dirList.append(f)   
                
        for i in range(len(dirList)):
            dirList[i]=dirList[i].replace(".py","")
        Main.Plugins_Menu.clear()
        Main.Plugins_Menu.addAction('Reload All',self.Reload,'CTRL+R')
        Main.Plugins_Menu.addAction('New Script',self.Write_Script_Plugin,'CTRL+N')
        Main.Plugins_Menu.addAction('Force Load',self.Force_Load)
        Main.Plugins_Menu.addSeparator()
        
        for plugin in dirList:
            if plugin.find('$') == -1 and plugin.find('#') == -1 and plugin.find('__') == -1:
                try:
                    try: #if already loaded
                        reload(eval('sys.modules[__name__].'+plugin))
                        setattr(__builtin__,plugin,eval('sys.modules[__name__].'+plugin))
                    except AttributeError:
                        setattr(sys.modules[__name__],plugin,__import__(plugin))
                        setattr(__builtin__,plugin,eval('sys.modules[__name__].'+plugin))
                        pass
                    print plugin,' reloaded'

                    Main.Plugins_Menu.addAction(str(plugin),lambda plugin=plugin: self.Load(plugin))
                    self.Plugin_List.append(plugin) 
                except NameError:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(
                    """
                    While trying to load <b>%s.py plugin</b> an arror occured
                    <p>Don't forget that plugin code must be stored in functions, and NOT directly on script root, except if you want the script to be executed at SynaptiQs launch
                   
                    """ %(plugin))                       
                    msgBox.exec_() 
            else:
                print plugin,' not Loaded'   
                
                
                
                
    def Execute_Script(self):
        
        clicked_widget="self."+str(QtCore.QObject().sender().parent().accessibleName()+"_Window")

        try:
            self.Save_Script(clicked_widget,name='temp') #so when excuting, the Original File is not overwritten

            for plugin in self.Plugin_List:
                try:
                    reload(eval('sys.modules[__name__].'+plugin))
                    setattr(__builtin__,plugin,eval('sys.modules[__name__].'+plugin))
                except: #BUG When a immediately excutable script is created, saved, and you start a separate new script, reload doesn't work (until next restart)
                    pass
                
            execfile(str(Main.userpath)+'/.SynaptiQs/__temp.py')


        except IndentationError:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            While trying to execute the plugin, an IndentationError error occured
            <p>This is usually due to Tabulations and Whitespaces co-existance in the script.
            Please use only Tab OR Space (1 Tab ~ 4 Whitespaces)
            """)                
            msgBox.exec_()
            fichier = open(str(Main.userpath)+'/.SynaptiQs/__temp.py', "w")
            fichier.write(str(open(str(Main.userpath)+'/.SynaptiQs/__temp.py').read()).replace('    ','\t'))
            fichier.close()            
            print '2nd trial'
            
            self.Save_Script(clicked_widget,name='temp') #so execution doesn't need saving
            
            for plugin in self.Plugin_List:
                reload(eval('sys.modules[__name__].'+plugin))
                setattr(__builtin__,plugin,eval('sys.modules[__name__].'+plugin))
              
            try:
                execfile(str(Main.userpath)+'/.SynaptiQs/__temp.py')
            except IndentationError:
                message=traceback.format_exc()
                msgBox = QtGui.QMessageBox()
                msgBox.setText(message)                
                msgBox.exec_()                
                
                msgBox = QtGui.QMessageBox()
                msgBox.setText(
                """
                While trying to execute the plugin, an IndentationError error occured
                <p>This is usually due to Tabulations and Whitespaces co-existance in the script.
                Please use only Tab OR Space (1 Tab ~ 4 Whitespaces)
                It might also be due to an empty block (try; for; while; if; function etc...)
                """)                   

            #execfile(str(Main.userpath)+'/.SynaptiQs/__temp.py')
        except:
            message=traceback.format_exc()
            msgBox = QtGui.QMessageBox()
            msgBox.setText(message)                
            msgBox.exec_()
            
    def Save_As_Script(self):
        """
        Pour sauver sous forme de fichier .py le script dans HOME/USER/.SynaptiQs
        Le nom de fichier commence par $ et n'est pas chargé au lancement de SynaptiQs
        """
        #QtCore.QObject().sender().parent() is editor
        clicked_widget="self."+str(QtCore.QObject().sender().parent().accessibleName()+"_Window")


        savename, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
            "Please enter file name") 
        while "$" in savename or savename == "New_Script": #if errors occurs because of filename, add the error list here
            savename, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
            "File name cannot contain $, be empty or named New_Script, Please enter another file name") 
        ok = True
        
        self.Current_Script_Adress = str(Main.userpath)+'/.SynaptiQs/'+savename+'.py'

        if os.path.isfile(str(self.Current_Script_Adress)) == True: #if the file name already exist
            warning = QtGui.QMessageBox.warning(QtCore.QObject().sender().parent(),'File Already exist', 'Do you want to overwrite the previous script?',
                    QtGui.QMessageBox.Ok , QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                    QtGui.QMessageBox.NoButton) 
            
            if warning == 4194304:#QtGui.QMessageBox.NoButton:
                savename2, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
                    "Please give an alternative filename") 
                while "$" in savename2 or savename2 == "" or savename2 == self.Current_Script_Adress.split('/')[-1][:-3] or os.path.isfile(str(str(Main.userpath)+'/.SynaptiQs/'+savename2+'.py')) == True or savename2 == "New_Script": #if errors occurs because of filename, add the error list here
                    savename2, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
                    "File name cannot contain $, be empty, be named New_Script or have a name already in use , Please enter another file name") 
                ok = True
                self.Current_Script_Adress = str(Main.userpath)+'/.SynaptiQs/'+savename2+'.py'     
                savename=savename2






        savename=str(savename).replace(' ','_')
        warning = QtGui.QMessageBox.warning(QtCore.QObject().sender().parent(),'Saving options', 'Do you want the script to be immediately excutable? ',
                QtGui.QMessageBox.Ok , QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                QtGui.QMessageBox.NoButton) 

        if warning == 4194304:#QtGui.QMessageBox.NoButton:
            fichier = open(str(Main.userpath)+'/.SynaptiQs/'+'$'+savename+'.py', "w")
            #fichier = open(str(Main.userpath)+'/.SynaptiQs/'+'$'+savename+'.py', "w")
            fichier.write(eval(clicked_widget.replace("$","")).editor.text())            
            fichier.close()            
        else:
            fichier = open(str(Main.userpath)+'/.SynaptiQs/'+savename+'.py', "w")   
            #fichier = open(str(Main.userpath)+'/.SynaptiQs/'+savename+'.py', "w")
            fichier.write(eval(clicked_widget.replace("$","")).editor.text())            
            fichier.close()    
            QtCore.QObject().sender().parent().close()
            self.Write_Script_Plugin(str(Main.userpath)+'/.SynaptiQs/'+savename+'.py')
            Main.Plugins_Menu.addAction(savename,lambda plugin=savename: self.Load(plugin))
            self.Plugin_List.append(savename)             
        
    def Save_Script(self,clicked_widget=None,name=None):
        """
        Pour sauver sous forme de fichier .py le script dans HOME/USER/.SynaptiQs
        Le nom de fichier commence par $ et n'est pas chargé au lancement de SynaptiQs
        
        """
        NewCreatedFile = False
        try:
            if clicked_widget == None:
                clicked_widget="self."+str(QtCore.QObject().sender().parent().accessibleName()+"_Window")
                

            #File has to be named. Filepath ends in self.Current_Script_Adress
            if name != 'temp' or name == "New_Script": #If unnamed window
                if self.Current_Script_Adress == None:
                    NewCreatedFile = True
                    savename, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
                        "It's a new function, Please enter file name") 
                    while "$" in savename or savename == "New_Script": #if errors occurs because of filename, add the error list here
                        savename, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
                        "File name cannot contain $, be empty or named New_Script, Please enter another file name") 
                    ok = True
                    
                    self.Current_Script_Adress = str(Main.userpath)+'/.SynaptiQs/'+savename+'.py'
                    
                    
                    if os.path.isfile(str(self.Current_Script_Adress)) == True: #if the file name already exist
                        warning = QtGui.QMessageBox.warning(QtCore.QObject().sender().parent(),'File Already exist', 'Do you want to overwrite the previous script?',
                                QtGui.QMessageBox.Ok , QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                                QtGui.QMessageBox.NoButton) 
                        
                        if warning == 4194304:#QtGui.QMessageBox.NoButton:
                            savename2, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
                                "Please give an alternative filename") 
                            while "$" in savename2 or savename2 == "" or savename2 == self.Current_Script_Adress.split('/')[-1][:-3] or os.path.isfile(str(str(Main.userpath)+'/.SynaptiQs/'+savename2+'.py')) == True or savename2 == "New_Script": #if errors occurs because of filename, add the error list here
                                savename2, ok = QtGui.QInputDialog.getText(QtCore.QObject().sender().parent(), 'Input Dialog', 
                                "File name cannot contain $, be empty, be named New_Script or have a name already in use , Please enter another file name") 
                            ok = True
                            self.Current_Script_Adress = str(Main.userpath)+'/.SynaptiQs/'+savename2+'.py'                
                            savename=savename2
                else:
                    self.Current_Script_Adress=str(Main.userpath)+'/.SynaptiQs/'+str(QtCore.QObject().sender().parent().accessibleName())+'.py'
                    ok = True
                    
            elif name == 'temp':  #when executed without saving
                self.Current_Script_Adress = str(Main.userpath)+'/.SynaptiQs/__temp.py'
                ok = True
            else:
                return
               
            #Once filename is chosen
            if ok: 
                if NewCreatedFile:
                    savename=str(savename).replace(' ','_')
                    warning = QtGui.QMessageBox.warning(QtCore.QObject().sender().parent(),'Saving options', 'Do you want the script to be immediately excutable? ',
                            QtGui.QMessageBox.Ok , QtGui.QMessageBox.Cancel  | QtGui.QMessageBox.Default  | QtGui.QMessageBox.Escape,
                            QtGui.QMessageBox.NoButton) 
                            
                    if warning == 4194304: #QtGui.QMessageBox.NoButton:
                        fichier = open(str(Main.userpath)+'/.SynaptiQs/'+'$'+savename+'.py', "w")
                        #fichier = open(str(Main.userpath)+'/.SynaptiQs/'+'$'+savename+'.py', "w")
                        fichier.write(eval(clicked_widget.replace("$","")).editor.text().replace('\r\n','\n'))            
                        fichier.close()            
                    else:
                        fichier = open(str(Main.userpath)+'/.SynaptiQs/'+savename+'.py', "w")   
                        #fichier = open(str(Main.userpath)+'/.SynaptiQs/'+savename+'.py', "w")
                        fichier.write(eval(clicked_widget.replace("$","")).editor.text().replace('\r\n','\n'))            
                        fichier.close()    
                        QtCore.QObject().sender().parent().close()
                        self.Write_Script_Plugin(str(Main.userpath)+'/.SynaptiQs/'+savename+'.py')
                        Main.Plugins_Menu.addAction(savename,lambda plugin=savename: self.Load(plugin))
                        self.Plugin_List.append(savename) 
    
                else:
       
                    fichier = open(str(self.Current_Script_Adress), "w")
                    fichier.write(eval(clicked_widget).editor.text().replace('\r\n','\n'))
                    fichier.close()                    
    
            else:
                'Saving Aborted'    
        except:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            Script error, check your script
            """)              
            msgBox.exec_()              
            return

    def Write_Script_Plugin(self,source=None,name=None):
        
        self.Current_Script_Adress=source
        
        try:
            self.Current_Script_Name=source.replace('.py','').split('/')[-1]

#                setattr(sys.modules[__name__],plugin,__import__(plugin))
#                setattr(__builtin__,plugin,eval('sys.modules[__name__].'+plugin))            
        except AttributeError:
            self.Current_Script_Name='New_Script'
            
        name=self.Current_Script_Name+"_Window"
        if "$" in self.Current_Script_Name:
            #plugin=source.replace('.py','').split('/')[-1].replace("$", "")
            setattr(self,name.replace("$", ""),QtGui.QWidget())  
        else:
            setattr(self,name,QtGui.QWidget()) #Widget name is scriptname + _Window
        
        name="self."+name.replace("$", "")
        
        try:
            eval(name).setMinimumSize(800,600)
            eval(name).setWindowTitle(self.Current_Script_Name)
            eval(name).setAccessibleName(self.Current_Script_Name)
            eval(name).editor=self.Script_Editor(self.Current_Script_Adress,name)
        except SyntaxError:
            print 'Problem with window name, and probably with function name'
        

        self.Ok_script = QtGui.QPushButton(eval(name))
        self.Ok_script.setText("Execute (from __temp.py file)")
        self.Ok_script.setShortcut('F5')
        
        self.Save_As_Script_Button = QtGui.QPushButton(eval(name))
        self.Save_As_Script_Button.setText("Save As")

        self.Save_Script_Button = QtGui.QPushButton(eval(name))
        self.Save_Script_Button.setText("Save")
        
        self.vbox = QtGui.QVBoxLayout()

        self.vbox.addWidget(eval(name).editor)
        
        self.hbox = QtGui.QVBoxLayout()
        
        self.hbox.addWidget(self.Ok_script)
        self.hbox.addWidget(self.Save_Script_Button)
        self.hbox.addWidget(self.Save_As_Script_Button)
        self.vbox.addLayout(self.hbox)
        
        eval(name).setLayout(self.vbox)
        
        QtCore.QObject.connect(self.Ok_script, QtCore.SIGNAL("clicked()"),self.Execute_Script)
        QtCore.QObject.connect(self.Save_As_Script_Button, QtCore.SIGNAL("clicked()"),self.Save_As_Script)
        QtCore.QObject.connect(self.Save_Script_Button, QtCore.SIGNAL("clicked()"),self.Save_Script)
        
        eval(name).show()    


        
    def Script_Editor(self,source,name):
     
     
        editor = Qsci.QsciScintilla(eval(name))
        
        ## define the font to use
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(10)
        
        # the font metrics here will help
        # building the margin width later
        fm = QtGui.QFontMetrics(font)
        
        ## set the default font of the editor
        ## and take the same font for line numbers
        editor.setFont(font)
        editor.setMarginsFont(font)
        #TODO : Adjust based on operating system
        editor.convertEols(Qsci.QsciScintilla.EolUnix)
        editor.setEolMode(Qsci.QsciScintilla.EolUnix) # Was EolUnix
        #editor.setEolVisibility(True)
        
        ## Line numbers
        # conventionnaly, margin 0 is for line numbers
        editor.setMarginWidth(0, fm.width( "00000" ))
        editor.setMarginLineNumbers(0, True)
        
        ## Edge Mode shows a red vetical bar at 80 chars
        editor.setEdgeMode(Qsci.QsciScintilla.EdgeLine)
        editor.setEdgeColumn(80)
        editor.setTabIndents(False)
        editor.setEdgeColor(QtGui.QColor("#FF0000"))
        editor.setTabWidth(4)
        
        ## Folding visual : we will use boxes
        editor.setFolding(Qsci.QsciScintilla.BoxedTreeFoldStyle)
        
        ## Braces matching
        editor.setBraceMatching(Qsci.QsciScintilla.SloppyBraceMatch)
        
        ## Editing line color
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(QtGui.QColor("#caeee0"))
        
        ## Margins colors
        # line numbers margin
        editor.setMarginsBackgroundColor(QtGui.QColor("#333333"))
        editor.setMarginsForegroundColor(QtGui.QColor("#CCCCCC"))
        
        # folding margin colors (foreground,background)
        editor.setFoldMarginColors(QtGui.QColor("#bfe4ea"),QtGui.QColor("#66bfcd"))
        
        ## Choose a lexer
        lexer = Qsci.QsciLexerPython()
        lexer.setDefaultFont(font)
        editor.setLexer(lexer)
        #editor.SendScintilla(Qsci.QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')
        
        
        text="""print '///////////////Script Execution Started//////////////////////'\n# Write Your Script here\n\n\n\n\n\n\n\n\n\n\n\n# Uncomment this and add variable to display the figure\n#from matplotlib import pyplot\n#fig=pyplot.figure()\n#pyplot.plot(variable)\n#pyplot.show()\nprint '///////////////Script Execution Ended//////////////////////'"""
    
        
        #encapsulated search function
        def Search(text=text,search_text=None):
            print 'searching :', search_text
            if text == None:
                return
            #editor.setIndicatorOutlineColor(QtGui.QColor("#FFE11F"))
            editor.findFirst(search_text,False,True,False,True)
            
        def Search_next():
            #editor.setIndicatorOutlineColor(QtGui.QColor("#FFE11F"))
            editor.findNext()

                                
        def Open_Search(text=text):
            value, ok = QtGui.QInputDialog.getText(editor, 'Search', 
                'Text to search')
            Search(text=text,search_text=str(value))
            
        def Open_Replace(text=text):
            def ShowFirstOccurence():
                editor.findFirst(inline.text(),False,True,False,True)
            def OK():
                Replace('text',search_text=inline.text(),newtext=outline.text())
            def Cancel():
                self.wid.close()
                
            self.wid = QtGui.QWidget()
            Vert=QtGui.QVBoxLayout(self.wid)
            inline= QtGui.QLineEdit()
            outline= QtGui.QLineEdit()
            
            Vert.addWidget(inline)
            Vert.addWidget(outline)
            Hor=QtGui.QHBoxLayout()
            ok = QtGui.QPushButton('OK')
            cancel = QtGui.QPushButton('Cancel')
            Hor.addWidget(ok)
            Hor.addWidget(cancel)
            Vert.addLayout(Hor)    
            
            self.wid.show()
            QtCore.QObject.connect(inline, QtCore.SIGNAL('textEdited(QString)'), ShowFirstOccurence)
            QtCore.QObject.connect(ok, QtCore.SIGNAL("clicked()"), OK)
            QtCore.QObject.connect(cancel, QtCore.SIGNAL("clicked()"), Cancel)
        

        def Replace(text=text,search_text=None,newtext=None):
            editor.findFirst(search_text,False,True,False,True)
            editor.replace(newtext)
           
            
        shcut1 = QtGui.QShortcut(editor)
        shcut1.setKey("CTRL+F")
        QtCore.QObject.connect(shcut1, QtCore.SIGNAL("activated()"), Open_Search)
   
        shcut1 = QtGui.QShortcut(editor)
        shcut1.setKey("CTRL+G")
        QtCore.QObject.connect(shcut1, QtCore.SIGNAL("activated()"), Search_next)
  
        shcut1 = QtGui.QShortcut(editor)
        shcut1.setKey("CTRL+H")
        QtCore.QObject.connect(shcut1, QtCore.SIGNAL("activated()"), Open_Replace)   
        
        try:
            text=str(open(self.Current_Script_Adress).read())
            #text=str(open(self.Current_Script_Adress).read()).replace('    ','   ')
            editor.setText(text)
            return editor
        except TypeError:
            text="""print '///////////////Script Execution Started//////////////////////'\n# Write Your Script here\n\n\n\n\n\n\n\n\n\n\n\n# Uncomment this and add variable to display the figure\n#from matplotlib import pyplot\n#fig=pyplot.figure()\n#pyplot.plot(variable)\n#pyplot.show()\nprint '///////////////Script Execution Ended//////////////////////'"""
            editor.setText(text)
            return editor
        except IOError:            
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
             """
            SynaptiQs was unable to open <b>%s plugin</b>
            <p>Destination file was maybe renamed or deleted
            <p>Do not put spaces or special caracters in files names...
            """ %(source))                     
            msgBox.exec_()  
            return
        
