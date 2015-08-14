# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:32:28 2013

@author: pyvan187
"""

from PyQt4 import QtCore, QtGui
from matplotlib import numpy,pyplot,mathtext
from scipy import stats,optimize
from lmfit import minimize, Parameters, Parameter

class Fitting(object):
    """
    Fitting Classes
    """
    
    def __init__(self):
        self.__name__="Fitting"
        
        
        self.Line=[r'$\mathrm{y = a.x + b }$',['a', 'b']]
        self.Poly2=[r'$\mathrm{y = a.x^2 + b.x + c}$'  ,['a','b','c']]    
        self.Poly3=[r'$\mathrm{y = a.x^3 + b.x^2 + c.x + d}$' ,['a','b','c','d']]
        self.Poly4=[r'$\mathrm{y = a.x^4 + b.x^3 + c.x^2 + d.x + e}$' ,['a','b','c','d','e']]
        self.Gauss=[r'$\mathrm{y = Y0 + A \exp \left[-\left(\frac{x-\mu}{width}\right)^2\right]}$' , ['Y0','A','mu','width']]
        self.Exp=[r'$\mathrm{y = Y0 + A \exp \left(\frac{-x}{\tau}\right)}$' ,['Y0','A1','tau1']]
        self.Double_exp=[r'$\mathrm{y = Y0 + A_1 \exp \left(\frac{-x}{\tau_1}\right) + A_2 \exp \left(\frac{-x}{\tau_2}\right)}$' ,['Y0','A1','tau1','A2','tau2']]
        self.Double_exp_xoffset=[r'$\mathrm{y = Y0 + A_1 \exp \left(\frac{-(x-XOffset)}{\tau_1}\right) + A_2 \exp \left(\frac{-(x-XOffset)}{\tau_2}\right)}$',['Y0','A1','tau1','A2','tau2','X_Offset']] 
        self.Sin=[r'$\mathrm{y = Y0 + A \sin (f.x+\phi)}$' , ['Y0','A','f','phi']]
        self.Hill=[r'$\mathrm{y = base + \left(\frac{(Max-base)}{1+(\frac{xhalf}{x})^r }\right)}$' ,['base','Max','xhalf','rate']]
        self.Sigmoid=[r'$\mathrm{y = base + \left(\frac{Max}{1+ \exp\left(\frac{(xhalf-x)}{rate}\right)}\right)}$', ['base','Max','xhalf','rate']]
        self.Power=[r'$\mathrm{y = Y0 + A*(x^p)}$',['Y0','A','power']]
        self.Beta=[r'$\mathrm{y = Y0 + A * \frac{\gamma(a) . \gamma(b)}{\gamma(a+b)}}$',  ['a','b','X0','width','Y0','A']]
        #self.Chi2=[r'$\mathrm{y = \chi_2}$',  ['a','A','Y0']]
        self.Lognormal=[r'$\mathrm{y = Y0 + A \exp \left[-\ln\left(\frac{x-\mu}{width}\right)^2\right]}$' , ['Y0','A','mu','width']]
        self.param_list=[1.0]*10
        self.List=["Line",
                   "Poly2",
                   "Poly3",
                   "Poly4",
                   "Gauss",
                   "Exp",
                   "Double_exp",
                   "Double_exp_xoffset",
                   "Sin",
                   "Hill",
                   "Sigmoid",
                   "Power",
                   "Beta",
                   "Lognormal"]
           
           
        self.currentWave='None'
        self.currentWaveScale='None'
        self.currentFittingFunction='line'
        self.range=[0,100,1000]
        self.display_range=[0.,1.,-1.,1.] 
        self.MinGuess=[None]*10
        self.MaxGuess=[None]*10 

           
    def line_init(self,x): 
        p=[1.0,0.]
        a, b  = p
        return (a*x + b)


    
                                       
    def line(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)
        p=p[:2]
        a, b  = p
        if y is None:
            return (a*x + b)
        return (a*x + b) - y


   
    def poly2(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)        
        p=p[:3]
        a, b, c = p
        if y is None:
            return (a*x**2 + b*x + c)
        return (a*x**2 + b*x + c) - y
        
    
    def poly3(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)        
        p=p[:4]    
        a, b, c, d = p

        if y is None:
            return (a*x**3 + b*x**2 + c*x + d)
        return (a*x**3 + b*x**2 + c*x + d) - y        

    
    def poly4(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)
        p=p[:5]    
        a, b, c, d, e = p
        if y is None:
            return (a*x**4 + b*x**3 + c*x**2 + d*x + e)
        return (a*x**4 + b*x**3 + c*x**2 + d*x + e) - y
    
    def gauss(self,param,x,y=None):
        """
        width (or Full Width at Half Maximum, or FWHM) is 2.sigma.sqrt(2.ln(2)), or about 2.35.sigma
        """
        p=[]
        for i in list(param):
            p.append(param[i].value)        
        p=p[:4]    
        Y0, A, mu, width = p
        if y is None:
            return (Y0 + A*numpy.exp(-((x-mu)/width)**2))
        return (Y0 + A*numpy.exp(-((x-mu)/width)**2)) - y        

    
    def exp(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)        
        p=p[:3]    
        Y0, A, tau = p
        return Y0 + A*numpy.exp(-x/tau)
        
    def double_exp(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:5]    
        Y0, A1, tau1, A2, tau2 = p
        if y is None:
            return (Y0 + A1*numpy.exp(-x/tau1) + A2*numpy.exp(-x/tau2))
        return (Y0 + A1*numpy.exp(-x/tau1) + A2*numpy.exp(-x/tau2)) - y        


    def double_exp_xoffset(self,param,x,y=None):
        """
        You can try this for a positive current
        200.,100. is for the decay part. it decays to 0 
        -200.,30. is for the rising part. it rise to 0
        a=numpy.arange(500)
        f=ARG.double_exp_var(a,*[0,200.,100.,-200.,30.,0.])
        pyplot.plot(f)
        pyplot.show()
        
        Y0 is the Y_Offset
        A2,A2 are the values of the exponential at X=0
        tau1 and tau2 are the corresponding time constant
        if tau1<tau2 the resulting bi-exponential is negative
        if tau1>tau2 the resulting bi-exponential is positive
        if tau1=tau2 the resulting bi-exponential is an horizontal line
        X_Offset switch the peak to right if positive, or to the left if negative
        """
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:6]    
        Y0, A1, tau1, A2, tau2, X_Offset = p
        if y is None:
            return (Y0 + A1*numpy.exp(-(x-X_Offset)/tau1) + A2*numpy.exp(-(x-X_Offset)/tau2))
        return (Y0 + A1*numpy.exp(-(x-X_Offset)/tau1) + A2*numpy.exp(-(x-X_Offset)/tau2)) - y 

    def sin(self,param,x,y=None):
        """
        Y0 is an Y Offset
        A is the amplitude of the wave
        phi is the phase/shift
        """
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:4]    
        Y0, A, f, phi = p
        if y is None:
            return (Y0 + A*numpy.sin((f*x)+phi))
        return (Y0 + A*numpy.sin((f*x)+phi)) - y

    def hill(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:4]    
        base, Max, xhalf, rate = p
        if y is None:
            return (base+(Max-base)/(1+(xhalf/x)**rate))
        return (base+(Max-base)/(1+(xhalf/x)**rate)) - y
       
    
    def sigmoid(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:4]    
        base, Max, xhalf, rate = p
        if y is None:
            return (base+(Max/(1+numpy.exp((xhalf-x)/rate))))
        return (base+(Max/(1+numpy.exp((xhalf-x)/rate)))) - y
    
    def power(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:4]    
        Y0,A,power = p
        if y is None:
            return (Y0+A*(x**power))
        return (Y0+A*(x**power)) - y
         

    def beta(self,param,x,y=None):
        """
        try p0=[4.,8.,-30.,150.,0.,100.] for negative currents
        try p0=[4.,8.,30.,150.,0.,100.] for positive currents
        a and b  must be positive
        Y0 is the Y offset
        X0 is the minimal point on Xaxis
        width is the interval of the distribution
       
        """
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:6]    
        a,b,X0,width,Y0,A = p
        dist = stats.beta(a, b, scale=width,loc=X0).pdf(x)
        if y is None:
            return (Y0+A*dist)
        return (Y0+A*dist) - y

    def lognormal(self,param,x,y=None):
        p=[]
        for i in list(param):
            p.append(param[i].value)    
        p=p[:4]    
        Y0, A, mu, width = p
        if y is None:
            return (Y0 + A*numpy.exp(-((numpy.log(x-mu)/width)**2)))
        return (Y0 + A*numpy.exp(-((numpy.log(x-mu)/width)**2))) - y
         

  
        

    def Fit(self,Source,X=None,function='line',Guess=numpy.ones(10),Show_Residuals=True,StartP=None,EndP=None,StartX=None,EndX=None,Show_Guess=False,Figure=None,Rendering=True,RAW_Data=True,Color='r',Show_Parameters=True,Number_of_points=1000.,Bounds=[[None,None]]*10,Model=False):
        """
        Source is the signal to fit
        X is the XScale
        function is the fitting function.
        Avaible functions are : line,
                                poly2,
                                poly3,
                                poly4,
                                gauss,
                                exp,
                                double_exp,
                                double_exp_xoffset,
                                sin,
                                hill,
                                sigmoid,
                                power,
                                beta
        p0 are the intitial guesses (default is a list of 1.)
        StartP and EndP are the start point and the End point of the fit (in points)
        StartX and EndX are the start point and the End point of the fit (in timescale units)
        """
        
        def find_indexes(Source,Min,Max):
        	c=abs(numpy.array(Source)-Min)
        	Min_index=list(c).index(min(c))
        	c=abs(numpy.array(Source)-Max)
        	Max_index=list(c).index(min(c))
        	return Min_index,Max_index    

        begin=X[0] #original begin and end points are stored here, so the final plot will be displayed in the original workspace
        end=X[-1]        
        if (StartP == None) and (StartX == None) :
            StartP=0
            StartX=0
        if (EndP == None) and (EndX == None) == None:
            EndP=len(Source)-1   
            EndX=len(Source)-1 
        
        if (StartP == None) or (EndP == None) :
            StartP,EndP=find_indexes(X,StartX,EndX) 
        else:
            StartX=X[StartP]
            EndX=X[EndP]


        Source=numpy.array(Source[StartP:EndP]) #if not using the whole range for the fit, truncated wave is created here
        X=numpy.array(X[StartP:EndP]) #if not using the whole range for the fit, truncated timescale is created here


    	# Data and Xscale
        Source = numpy.array(Source)
        if X==None or (len(Source) != len(X)):
            X = numpy.array(range(len(Source)))
            # create a set of Parameters

        Function=eval("self."+function) #the fitting function
        Formula=eval("self."+function.capitalize())[0] #the fitting formula
        Parameters_Names=eval("self."+function.capitalize())[1] ##list of the fitting parameters            
            



        for i,j in enumerate(Bounds):
            if Bounds[i][0] != None:
                Bounds[i][0]=numpy.float32(Bounds[i][0])
            if Bounds[i][1] != None:
                Bounds[i][1]=numpy.float32(Bounds[i][1])
        
        #print Bounds
        
        p0 = Parameters()

       
        # do fit, here with leastsq model
        if Model == False:
           
            for i,j in enumerate(Parameters_Names):
                #For each paramters, you can set value, min & max. i.e. p0.add('omega', value= 0.0, min=-numpy.pi/2., max=numpy.pi/2)
                if j != '0':
                    if Bounds[i][0] != None and Bounds[i][1]!=None:
                        p0.add(j,value=Guess[i],min=Bounds[i][0],max=Bounds[i][1])
                    elif Bounds[i][0] !=None and Bounds[i][1]==None:
                        p0.add(j,value=Guess[i],min=Bounds[i][0])     
                    elif Bounds[i][0] == None and Bounds[i][1] != None:
                        p0.add(j,value=Guess[i],max=Bounds[i][1])
                    else:
                        p0.add(j,value=Guess[i])            
            print 'Fitting in process ...'
            try:
                result = minimize(Function, p0, args=(X, Source))
                RenderingX=numpy.linspace(float(X[0]),float(X[-1]),num=Number_of_points)
                fit = Function(result.params,RenderingX) #Rendering, with Popt, the best fitting parameters
            except:
                print 'Fitting failed, try other parameters or constraints'
                return
            print 'Fitting performed between points ',StartP,' and ',EndP, ' (',len(X),' points)'
            print 'in units between: ',StartX,' and ',EndX
            print '######### FITTING RESULTS ############'
            print 'Parameters are :' 
            res=[]
            for i in list(result.params):
                print i, result.params[i].value  
                res.append(result.params[i].value)
            
        elif Model== True:
            for i,j in enumerate(Parameters_Names):
                if j != '0':
                    p0.add(j,value=Guess[i])             
            RenderingX=numpy.linspace(float(X[0]),float(X[-1]),num=Number_of_points)
            fit = Function(p0,RenderingX) #Rendering, with Popt, the best fitting parameters            

#        if Show_Parameters == True:
#            for i in range(len(popt)):
#                if List[i][0] != '0':
#                    try:
#                        pyplot.text(begin+((end-begin)/10), max(fit)-(i+1)*abs((max(fit)-min(fit))/(10)), r"%s = {%s} +/- {%s}" % ((str(List[i][0])),str(float(popt[i])),str(float((pcov[i][i])**0.5))))# .format(popt[i], (pcov[i][i])**0.5))
#                    except:
#                        pyplot.text(begin+((end-begin)/10), max(fit)-(i+1)*abs((max(fit)-min(fit))/(10)),'test')

        #if Show_Error_Bars == True: to do
            #pyplot.errorbar(X, Source, yerr = y_sigma, fmt = 'o')    

        
#        if Show_Guess == True:
#            guess=Function(X,*p0)
#            G,=pyplot.plot(X, guess, label='Test data',marker='o',color='g') 
#            if RAW_Data == True:
#                pyplot.legend([S, G, F], ["Data", "initial guess", "Fit"], loc='best',fancybox=True)
#            else:
#                pyplot.legend([G, F], ["initial guess", "Fit"], loc='best',fancybox=True)
#        else:
#            if RAW_Data == True:
#                pyplot.legend([S, F], ["Data", "Fit"], loc='best',fancybox=True)
#            else:
#                pyplot.legend([F], ["Fit"], loc='best',fancybox=True)

        if Rendering == True:
            pyplot.rc('axes',fc='white')
            if Figure == None: #Creation of the figure. If Figure is not None, the fit is integrated in pre-existing figure
                fig=pyplot.figure(facecolor='white')
            else:
                fig = Figure   
                
            pyplot.title('Fitting completed')        
            if RAW_Data == True:
                S,=pyplot.plot(X, Source,color='b')
                
            try:
                if Show_Residuals == True:
                    final = Source + result.residual
                    pyplot.plot(X, final, 'r')
            except UnboundLocalError: #Should be only in the Plugin, at first launch.
                print 'No results'
                
            F,=pyplot.plot(RenderingX, fit, linestyle='--',color=Color)
            
            pyplot.xlim([begin,end])
            pyplot.grid(True) 
            pyplot.show()
            return fit,res,fig
        else:
            return fit
           
        


   # def fit(self,Source,X=None,function='line',p0=numpy.ones(10),StartP=None,EndP=None,StartX=None,EndX=None,Show_Guess=False,Figure=None,Rendering=True,RAW_Data=True,Color='r',Show_Parameters=True):
#
#        try:
#            print'ok'
#
#        
#           
#
#        except ValueError:
#            pyplot.rc('axes',fc='#FFDDDD')
#            pyplot.title('PARAMETERS ERROR')
#            S,=pyplot.plot(X, Source,marker='-',color='b')
#            guess=Function(Source,*p0)           
#            G,=pyplot.plot(X, guess,marker='-',color='g')
#            pyplot.legend([S, G], ['Data', 'initial guess'], loc='best',fancybox=True)
#            msg = """
#            The Function form is
#            
#            %s
#            
#            Try other initial parameters""" %(Formula)
#              
#            pyplot.text(min(X),min(Source),msg)
#            pyplot.show()
#            pyplot.rc('axes',fc='white')
#            return
#            
#        except RuntimeError:
#            trial=0
#            while trial<20:
#                print 'trial # ', trial, ' Parameters were adjusted'
#                pbis=p0*numpy.random.rand(1)[0]*20-10
#                print 'New P0 parameters are : ',pbis
#                try:
#                    
#                    popt, pcov = optimize.fmin_slsqp(Function, X, Source, p0=pbis)
#                    
#                    trial=20#Fitting of the data, (function, xdata, ydata, p0)
#                except:
#                    trial+=1
#                    
#                if trial == 19:
#                    print 'FITTING ERROR, STOPING FITTING'
#                    msgBox = QtGui.QMessageBox()
#                    msgBox.setText(
#                     """
#                    <b>Fitting Error</b>
#                    <p>Fitting function was launched 100 times and didn't worked. try different initial parameters
#                    """)             
#                    msgBox.exec_()
#                    return
#                elif trial == 20:
#                    print 'fitting completed with parameters ', p0
#
#            
#        except TypeError:   
#            print "ERROR, Not enough data to fit, please set larger range or negative range error"
#            return

         




    def Helper(self):
        
        #Global Widget
        self.all = QtGui.QWidget()
        self.all.setMinimumSize(900,500)
        self.all.setWindowTitle("Fitting Tools") 

        #Fitting preview
        self.Fit_Example = MyMplWidget(parent=self.all,No_Toolbar=False)
        self.Fit_Example.setMinimumSize(600,600)
        self.Fit_Example.setWindowTitle("Display")
        plot=self.line_init(numpy.arange(1000)*0.001)
        self.Fit_Example.canvas.axes.plot(numpy.arange(1000)*0.001,plot,'r')
        
        self.hbox=QtGui.QHBoxLayout()        

        self.vbox=QtGui.QVBoxLayout()
        
        #Box1 The fitting Functions
        self.List_of_Functions = QtGui.QComboBox()
        self.List_of_Functions.setMinimumSize(600,40)
        self.List_of_Functions.addItems(self.List)
        self.vbox.addWidget(self.List_of_Functions)
        QtCore.QObject.connect(self.List_of_Functions, QtCore.SIGNAL("currentIndexChanged(int)"),self.Fitting_Parameters)
        
        #Box2 Select the DataWave & XScale
        self.ListYWaves()
        #self.ListXWaves()
        QtCore.QObject.connect(self.Data_Wave, QtCore.SIGNAL('currentIndexChanged(int)'),self.ListXWaves)#lambda sender="self.Button_1": self.Update_Graph(sender))   #just to refresh the display          
        QtCore.QObject.connect(self.Data_Wave_Axes, QtCore.SIGNAL('currentIndexChanged(int)'),self.Optimize_Range)   #just to refresh the display          
        self.vbox.addWidget(self.Data_Wave)
        self.vbox.addWidget(self.Data_Wave_Axes)

        
        RangeHbox=QtGui.QHBoxLayout()
        
        self.Range = QtGui.QWidget()
        Label2 = QtGui.QLabel(self.Range)
        Label2.setText('<b>Fitting Range (in pts)</b>')
        Label2.setGeometry(40,0, 100, 25)        
        
        for k,l in enumerate(["X_Start","X_End","Points"]):
            eval(compile("self.RangeLabel_"+str(k)+"= QtGui.QLabel(self.Range)",'<string>','exec'))
            eval(compile("self.RangeLabel_"+str(k)+".setGeometry(10,int(k*30)+30, 100, 25)",'<string>','exec'))    
            eval(compile("self.RangeLabel_"+str(k)+".setText('"+l+"')",'<string>','exec'))    
            eval(compile("self.Range_"+str(k)+"= QtGui.QLineEdit(self.Range)",'<string>','exec'))
            eval(compile("self.Range_"+str(k)+".setGeometry(50,int(k*30)+30, 100, 25)",'<string>','exec'))
            eval(compile("self.Range_"+str(k)+".setText('"+str(self.range[k])+"')",'<string>','exec'))
            current2=eval("self.Range_"+str(k))
            QtCore.QObject.connect(current2, QtCore.SIGNAL('editingFinished()'),lambda sender="self.Range_"+str(k): self.Update_Graph(sender))        
        
        RangeHbox.addWidget(self.Range)  

        self.Display_Range = QtGui.QWidget()
        Label3 = QtGui.QLabel(self.Display_Range)
        Label3.setText('<b>Display Range (in Units)</b>')
        Label3.setGeometry(40,0, 100, 25)        
        
        for k,l in enumerate(["X_Start","X_End","Y_Start","Y_End"]):
            eval(compile("self.Display_RangeLabel_"+str(k)+"= QtGui.QLabel(self.Display_Range)",'<string>','exec'))
            eval(compile("self.Display_RangeLabel_"+str(k)+".setGeometry(10,int(k*30)+30, 100, 25)",'<string>','exec'))    
            eval(compile("self.Display_RangeLabel_"+str(k)+".setText('"+l+"')",'<string>','exec'))    
            eval(compile("self.Display_Range_"+str(k)+"= QtGui.QLineEdit(self.Display_Range)",'<string>','exec'))
            eval(compile("self.Display_Range_"+str(k)+".setGeometry(50,int(k*30)+30, 100, 25)",'<string>','exec'))
            eval(compile("self.Display_Range_"+str(k)+".setText('"+str(self.display_range[k])+"')",'<string>','exec'))
            eval(compile("self.Display_Range_"+str(k)+".setEnabled(False)",'<string>','exec'))
            current3=eval("self.Display_Range_"+str(k))
            QtCore.QObject.connect(current3, QtCore.SIGNAL('editingFinished()'),lambda sender="self.Display_Range_"+str(k): self.Update_Graph(sender))        
        
        self.fixed_range=QtGui.QCheckBox(self.Display_Range)
        self.fixed_range.setText('Fixed display range')
        self.fixed_range.setGeometry(10,int((k+1)*30)+30, 150, 25)
        self.fixed_range.setCheckState(0)
        QtCore.QObject.connect(self.fixed_range, QtCore.SIGNAL('stateChanged(int)'), self.Update_Fields_State) #just to refresh the display     
        
        RangeHbox.addWidget(self.Display_Range)
        self.vbox.addLayout(RangeHbox)
        
        
        self.Fitting_Parameters()
        
        self.fit_the_data = QtGui.QPushButton()
        
        self.fit_the_data.setText('Fit !')
        QtCore.QObject.connect(self.fit_the_data, QtCore.SIGNAL('clicked()'),self.Pre_Fit)   #just to refresh the display          
        self.vbox.addWidget(self.fit_the_data)
        self.hbox.addLayout(self.vbox)
        
        self.hbox.addWidget(self.Fit_Example)

        self.all.setLayout(self.hbox)
        self.all.show()


    def ListYWaves(self):
        
        L1,L2,nop,nop2=Infos.List_All_Globals(option='numericalonly')
        self.Data_Wave = QtGui.QComboBox()
        self.Data_Wave.addItem(str('None'))
        self.Data_Wave.addItems(L1+L2)    
        
        self.Data_Wave_Axes = QtGui.QComboBox()
        self.Data_Wave_Axes.clear()
        self.Data_Wave_Axes.addItem(str('None'))
            
        self.Update_Graph("None")
        
    def ListXWaves(self):
        
        L1,L2,nop,nop2=Infos.List_All_Globals(option='numericalonly') 
        L=L1+L2

        self.Data_Wave_Axes.clear()
        self.Data_Wave_Axes.addItem(str('None'))
        if str(self.Data_Wave.currentText()) != 'None':
            length=len(eval(str(self.Data_Wave.currentText())))
            for i in L:
                try:
                    if len(eval(str(i))) == length:
                        self.Data_Wave_Axes.addItem(str(i))
                except AttributeError:
                    pass
        self.Data_Wave_Axes.setCurrentIndex(0)
        self.Optimize_Range()

    def Optimize_Range(self): 
        
        self.currentWaveScale=str(self.Data_Wave_Axes.currentText())
        
        
        try: #if there is already a defined wave, the length of this wave is set as default
            length=len(eval(str(self.Data_Wave.currentText())))
        except TypeError:
            length=1000
            
        try:
            begin=0.
            end=len(eval(str(self.Data_Wave.currentText())))
        except:
            begin=0.
            end=1.
        self.range=[begin,end,length]  
        

        try:
            Xmin=float(eval(str(self.Data_Wave_Axes.currentText()))[0])
            Xmax=float(eval(str(self.Data_Wave_Axes.currentText()))[-1])
            self.range=[Xmin,Xmax,length] 
            Ymin=float(min(eval(str(self.Data_Wave.currentText()))))
            Ymax=float(max(eval(str(self.Data_Wave.currentText()))))
            self.display_range=[Xmin,Xmax,Ymin,Ymax]
        except TypeError: #if Ywave is None, at first launch for example
            self.display_range=[0.,1.,-1.,1.]            
        except:
            Xmin=0.
            Xmax=len(eval(str(self.Data_Wave.currentText())))
            
            Ymin=float(min(eval(str(self.Data_Wave.currentText()))))
            Ymax=float(max(eval(str(self.Data_Wave.currentText()))))            
            self.display_range=[Xmin,Xmax,Ymin,Ymax]
            
        try:
            for k,l in enumerate(["X_Start","X_End","Points"]):
                eval(compile("self.Range_"+str(k)+".setText('"+str(self.range[k])+"')",'<string>','exec'))
            
            for k,l in enumerate(["X_Start","X_End","Y_Start","Y_End"]):
                eval(compile("self.Display_Range_"+str(k)+".setText('"+str(self.display_range[k])+"')",'<string>','exec'))
        except:
            pass
        
        self.Update_Graph('None')    
            
        #self.Refresh_Wave_Lists()
        
    def formula(self,formula):
        """
        This function create a png picture to render mathematical formula
        """
        parser = mathtext.MathTextParser("Bitmap")
        rgba1, depth1 = parser.to_rgba(formula,fontsize=8, dpi=200)
        fig = pyplot.figure(facecolor='white',figsize=(3,0.2))
        fig.figimage(rgba1.astype(float)/255., 0, 0)
        pyplot.savefig(Main.Script_Path+"\\formula.png")




    def Fitting_Parameters(self):
        try:
            self.Parameters.close()
        except:
            pass

        self.Parameters=QtGui.QWidget()
        self.Parameters.setMinimumSize(400,400)
        
        vbox=QtGui.QVBoxLayout()
        self.currentFittingFunction=str(self.List_of_Functions.currentText())        
        print "Function is ", self.currentFittingFunction
          
        '''  
        Nice formula
        self.formula(eval("self."+self.currentFittingFunction.capitalize())[0])
        self.Formula = QtGui.QLabel()
        self.Formula.setPixmap(QtGui.QPixmap(Main.Script_Path+"\\formula.png"))
        vbox.addWidget(self.Formula)
        '''
        
        
        ############         
        
        #Fitting parameters Widget
        self.Params = QtGui.QWidget()
        
        
        #First, the fitting parameters are collected from the definitions
        params=eval("self."+self.currentFittingFunction.capitalize())[1] #Its the parameters list, see __init__()
        params.extend(['0']*(10-len(params))) #name of the parameters (10 max), '0' means that the parameters won't be use
        
        #column 1 title
        Label1 = QtGui.QLabel(self.Params)
        Label1.setText('<b>Fit Parameters</b>')
        Label1.setGeometry(40,0, 100, 25)
        
        #parameters buttons
        for i,j in enumerate(params):
            eval(compile("self.ButtonLabel_"+str(i)+"= QtGui.QLabel(self.Params)",'<string>','exec'))
            eval(compile("self.ButtonLabel_"+str(i)+".setGeometry(10,int(i*30)+30, 100, 25)",'<string>','exec'))    
            eval(compile("self.ButtonLabel_"+str(i)+".setText('"+j+"')",'<string>','exec'))    
            eval(compile("self.Button_Guess"+str(i)+"= QtGui.QLineEdit(self.Params)",'<string>','exec'))
            eval(compile("self.Button_Guess"+str(i)+".setGeometry(50,int(i*30)+30, 100, 25)",'<string>','exec'))
            eval(compile("self.Button_Guess"+str(i)+".setText('1.0')",'<string>','exec')) 
            
            eval(compile("self.Button_Min"+str(i)+"= QtGui.QLineEdit(self.Params)",'<string>','exec'))
            eval(compile("self.Button_Min"+str(i)+".setGeometry(150,int(i*30)+30, 100, 25)",'<string>','exec'))
            eval(compile("self.Button_Min"+str(i)+".setText('None')",'<string>','exec'))
            
            eval(compile("self.Button_Max"+str(i)+"= QtGui.QLineEdit(self.Params)",'<string>','exec'))
            eval(compile("self.Button_Max"+str(i)+".setGeometry(250,int(i*30)+30, 100, 25)",'<string>','exec'))
            eval(compile("self.Button_Max"+str(i)+".setText('None')",'<string>','exec')) 
            
            if j == '0': #unneeded parameters lines are hiden
                eval(compile("self.ButtonLabel_"+str(i)+".hide()",'<string>','exec'))   
                eval(compile("self.Button_Guess"+str(i)+".hide()",'<string>','exec'))  
                eval(compile("self.Button_Min"+str(i)+".hide()",'<string>','exec'))  
                eval(compile("self.Button_Max"+str(i)+".hide()",'<string>','exec'))  
            
            current=eval("self.Button_Guess"+str(i))
            currentMin=eval("self.Button_Min"+str(i))
            currentMax=eval("self.Button_Max"+str(i))
            QtCore.QObject.connect(current, QtCore.SIGNAL('editingFinished()'),lambda sender="self.Button_Guess"+str(i): self.Update_Graph(sender))
            QtCore.QObject.connect(currentMin, QtCore.SIGNAL('editingFinished()'),lambda sender="self.Button_Min"+str(i): self.Update_Graph(sender))
            QtCore.QObject.connect(currentMax, QtCore.SIGNAL('editingFinished()'),lambda sender="self.Button_Max"+str(i): self.Update_Graph(sender))


            
        vbox.addWidget(self.Params)
        

        self.Parameters.setLayout(vbox)
        self.Parameters.show()

    def Pre_Fit(self):
        #Last computation of the data, before fitting
        Y=eval(str(self.Data_Wave.currentText()))
        
        if self.Data_Wave_Axes.currentText() == 'None':
            X=numpy.arange(len(eval(str(self.Data_Wave.currentText()))))
            timescale=1.
        else:
            X=eval(str(self.Data_Wave_Axes.currentText()))
            timescale=abs(X[1]-X[0])

        Bounds=[]
        for i in range(10):
            Bounds.append([self.MinGuess[i],self.MaxGuess[i]])
        print 'bounds',Bounds
        try:
            self.Fit(Y,X=X,function=str(self.List_of_Functions.currentText()).lower(),Guess=self.param_list,StartX=self.range[0],EndX=self.range[1],Show_Guess=False,Figure=None,Rendering=True,Color='r',Bounds=Bounds)
        except ValueError:   
            msgBox = QtGui.QMessageBox()
            msgBox.setText(
            """
            <b>Fitting Error</b>
            <p>You should try others initial parameters
            """) 
            msgBox.exec_() 

    def Update_Fields_State(self):
        if self.fixed_range.checkState() == 2:
            for k,l in enumerate(["X_Start","X_End","Y_Start","Y_End"]):
                eval(compile("self.Display_Range_"+str(k)+".setEnabled(True)",'<string>','exec'))
        else:
            for k,l in enumerate(["X_Start","X_End","Y_Start","Y_End"]):
                eval(compile("self.Display_Range_"+str(k)+".setEnabled(False)",'<string>','exec'))
                
    def Update_Graph(self,sender):
        sender=str(sender)
        
        if 'Button_Min' in sender:
            value=eval(sender).text()   
            pos=int(sender[-1])
            try:
                self.MinGuess[pos]=float(value)
            except ValueError:
                self.MinGuess[pos]=None
                pass
            
        if 'Button_Max' in sender:
            value=eval(sender).text()   
            pos=int(sender[-1])
            try:
                self.MaxGuess[pos]=float(value)
            except ValueError:
                self.MaxGuess[pos]=None
                pass   

        elif 'Button_Guess' in sender:
            value=eval(sender).text()   
            pos=int(sender[-1])
            try:
                self.param_list[pos]=float(value)
            except ValueError:
                self.param_list[pos]=None
                pass

        elif 'Display_' in sender:
            value=eval(sender).text()   
            pos=int(sender[-1])
            try:
                self.display_range[pos]=float(value)
            except ValueError:
                self.display_range[pos]=1.0
                pass  
            
        elif 'Range' in sender:
            value=eval(sender).text()   
            pos=int(sender[-1])
            try:
                self.range[pos]=float(value)
            except ValueError:
                self.range[pos]=1.0
                pass     
        else:
            pass
            
        #fitting function is set
        function=eval('self.'+str(self.List_of_Functions.currentText()).lower())
        #Graph is cleared
        self.Fit_Example.canvas.axes.clear()

        timescale=1.
        
        if str(self.Data_Wave.currentText()) != 'None':
            y=numpy.array(eval(str(self.Data_Wave.currentText())))
            if str(self.Data_Wave_Axes.currentText()) == 'None':
                x=numpy.arange(len(y))
            else:
                try:
                    x=numpy.array(eval(str(self.Data_Wave_Axes.currentText())))
                except SyntaxError: #should be corrected
                    x=numpy.arange(len(y))
            timescale=abs(x[1]-x[0])
            A,=self.Fit_Example.canvas.axes.plot(x,y,'g')
        else:
            print 'No Data Wave defined (yet)'
            return


        Bounds=[]
        for i in range(10):
            Bounds.append([self.MinGuess[i],self.MaxGuess[i]])
        fit=self.Fit(x,X=x,function=str(self.List_of_Functions.currentText()).lower(),Guess=self.param_list,StartX=self.range[0],EndX=self.range[1],Number_of_points=len(x),Rendering = False,Bounds=Bounds,Model=True)
        B,=self.Fit_Example.canvas.axes.plot(x,fit,'r') #The fitting guess
        self.Fit_Example.canvas.axes.legend([A,B], ["Data", "Model"], loc='best',fancybox=True)
        
        self.Fit_Example.canvas.axes.axvspan(self.range[0], self.range[1], -2000, 2000,color='r',alpha=0.1)

            

        if self.fixed_range.checkState()==2:
            self.Fit_Example.canvas.axes.set_xbound(self.display_range[0],self.display_range[1])
            self.Fit_Example.canvas.axes.set_ybound(self.display_range[2],self.display_range[3])
        else:
            self.Display_Range_0.setText(str(self.Fit_Example.canvas.axes.get_xbound()[0]))
            self.Display_Range_1.setText(str(self.Fit_Example.canvas.axes.get_xbound()[1]))
            self.Display_Range_2.setText(str(self.Fit_Example.canvas.axes.get_ybound()[0]))
            self.Display_Range_3.setText(str(self.Fit_Example.canvas.axes.get_ybound()[1])) 
            self.display_range[0]=self.Fit_Example.canvas.axes.get_xbound()[0]
            self.display_range[1]=self.Fit_Example.canvas.axes.get_xbound()[1]
            self.display_range[2]=self.Fit_Example.canvas.axes.get_ybound()[0]
            self.display_range[3]=self.Fit_Example.canvas.axes.get_ybound()[1]

        self.Fit_Example.canvas.draw()
        
        
    def FittingWindowInput(self):
        from matplotlib import numpy
        try:
            self.List_of_Functions.setCurrentIndex(4)
            
            index=self.Data_Wave.findText('Histogram.n')
            self.Data_Wave.setCurrentIndex(index)
            index=self.Data_Wave_Axes.findText('Histogram.bin_centres')
            self.Data_Wave_Axes.setCurrentIndex(index)            
            
            #self.Button_Guess1.setText(str(numpy.min(Histogram.n)))
            #self.Button_Guess2.setText(str(numpy.max(Histogram.n)))
            #self.Button_Guess3.setText(str(max(Histogram.bin_centres)-(max(Histogram.bin_centres)-min(Histogram.bin_centres))/2))
            #self.Button_Guess4.setText(str((max(Histogram.bin_centres)-min(Histogram.bin_centres))/10))            
        except AttributeError:
            self.Helper()
            self.List_of_Functions.setCurrentIndex(4)
            index=self.Data_Wave.findText('Histogram.n')
            self.Data_Wave.setCurrentIndex(index)
            index=self.Data_Wave_Axes.findText('Histogram.bin_centres')
            self.Data_Wave_Axes.setCurrentIndex(index)     
            #self.Button_Guess1.setText(str(numpy.min(Histogram.n)))
            #self.Button_Guess2.setText(str(numpy.max(Histogram.n)))
            #self.Button_Guess3.setText(str(max(Histogram.bin_centres)-(max(Histogram.bin_centres)-min(Histogram.bin_centres))/2))
            #self.Button_Guess4.setText(str((max(Histogram.bin_centres)-min(Histogram.bin_centres))/10))
            
        self.Update_Graph('None') 