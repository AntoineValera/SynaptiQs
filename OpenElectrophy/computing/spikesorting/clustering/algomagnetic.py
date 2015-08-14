# -*- coding: utf-8 -*-

"""
draft for implementtation of superparamagnetic clustering

Attention problem de g++
voir ici
http://osdir.com/ml/debian-bugs-dist/2010-03/msg06801.html

So my solution is use this package to replace blitz++ in python-scipy:
sudo apt-get install libblitz0-dev
sudo rm -r /usr/lib/python2.6/dist-packages/scipy/weave/blitz/blitz
sudo ln -s /usr/include/blitz  /usr/lib/python2.6/dist-packages/scipy/weave/blitz


"""




from scipy import *
import scipy.weave 
from numpy.random import random_integers,random


# Note de portage
"""
variable a deduire
NP=500;                          // number of points
dim =3;                          //dimension of input data

Config;             //spin configuration

K            //number of connection


Corr   #pair correlations

fonction unutil
abstand -> sum des carre
abstand2 -> sum des carres des diff


variable a changer apres
MCS
Coord -> points

abst - > matrice distance

"""

def magn( spins , Q ) :
    """
    Calculation: Nmax = number of spins of most common spin state
    """
    nq = zeros((Q) , dtype = 'i')
    for einst in range(Q) :
        nq[einst] = where(spins == einst)[0].size
    return nq.max()

def get_cluster(clus_xh,clus_yh,npoints):

    C_Schnitt_support = """

// spanning tree  in graph given by adjaceny matrix NNN[NP][NP] 

void Schnitt(bool *NNN,int i1, int *a,int k,int points)
    {
    for( int j1=0;j1<points;j1++)
        {
        if((NNN[i1*points+j1]==1) && (a[j1]==0))  
            {
            a[j1]=k;
            // NNN[i1*points+j1]=0;
            Schnitt(NNN,j1,a,k,points);

            //  cout<<j1<<" "<<k<<endl;
            }
        }
        
    return;
    }

"""

    C_Schnitt = """

int k=1;
bool *NN;
int   *tmp_cluster;

tmp_cluster = (int*) malloc(sizeof(int) * npoints);
NN = (bool*) malloc(sizeof(bool) * npoints * npoints);
if (NN == NULL)
{
      fprintf(stderr,"Could not allocate that much memory. You should detect less events by  increasing the detection threshold for example.");
      free(tmp_cluster);
}


if (NN != NULL)
{
// initialize NN array
for(int i1=0;i1<npoints*npoints;i1++)
           NN[i1]=0;

// fill NN array with neighbours
for(int i1=0;i1<nvoisins;i1++)
    {
    NN[clus_xh(i1)*npoints+clus_yh(i1)]=1;
    NN[clus_yh(i1)*npoints+clus_xh(i1)]=1;
    }

// everybody is his own neigbour, initialization of tmp_cluster
for(int i1=0;i1<npoints;i1++)
    {
    NN[i1*npoints+i1]=1;
    tmp_cluster[i1] = 0;
    }

// check if each point is inside a cluster, otherwise use Schnitt to determine all points in his cluster
for(int i1=0;i1<npoints;i1++)
    {
    if (tmp_cluster[i1]==0)
        {
        Schnitt(NN,i1,tmp_cluster,k,npoints);
        k=k+1;
        }
    }

// replace cluster with values computed in tmp_cluster
for(int i1=0;i1<npoints;i1++)
    cluster(i1)=tmp_cluster[i1];

free(NN);
free(tmp_cluster);
}
"""
    nvoisins = clus_xh.size
    cluster = zeros((npoints),dtype='int')
    scipy.weave.inline(C_Schnitt,
            arg_names=['clus_xh','clus_yh','npoints','nvoisins','cluster'],
            support_code=C_Schnitt_support,
            compiler = 'gcc',
            type_converters=scipy.weave.converters.blitz)

    #~ # For history purpose :
    #~ # Determination des cluster en python pur avec une autre methode...
    #~ cluster = arange(npoints) # cluster_base.copy() # attribute arbitrary cluster number to each point
    #~ mask=cluster[clus_xh]!=cluster[clus_yh] # check pairs with mismatch in cluster numbers 
    #~ while any(mask) :
        #~ # correct the mismatch by attributing to both point the smallest cluster number
        #~ cluster[clus_yh[mask]]=c_[cluster[clus_xh[mask]],cluster[clus_yh[mask]]].min(1) 
        #~ cluster[clus_xh[mask]]=cluster[clus_yh[mask]] 
        #~ mask=cluster[clus_xh]!=cluster[clus_yh] # check again


    return cluster





def paramagneticclustering(
                            Coord,
                            knear=4 , #k nearest neighbours
                            radius=5.2,
                            Q = 20, #Potts spins
                            MCS=250 , #number of Monte Carlo steps 
                            threshold=0.3, # threshold
                            T = 0.01,
                            ):

    dim = Coord.shape[1]
    npoints = Coord.shape[0]
    
    # Create distance array and order neigbours by closeness
    dist = empty((npoints,npoints),dtype='f')
    ind_nearest = empty((npoints,npoints),dtype='i')
    for n in range(npoints):
        dist[n,:]=sqrt(sum((Coord - Coord[n,:])**2 , axis= 1))
        ind_nearest[n,:]=dist[n,:].argsort()

    # Keep only the k nearest neighbours and check if all points are connected
    # If not, k is increased and the check is done again
    all_connected=False            
    while not(all_connected):
        
        # initialize Vic_x,Vic_y : list of k nearest neighbours
        Vic_x=tile(arange(npoints),(1,knear+1)).flatten()
        Vic_y=ind_nearest[:,:knear+1].transpose().flatten()

        # Need to be sure that every pair is present on both direction
        Vicini = zeros((npoints,npoints),dtype='bool')
        Vicini[Vic_x,Vic_y] = True # write connected pairs in a boolean array
        Vicini = Vicini | Vicini.transpose() # make the array symetric !
        Vic_x,Vic_y, = where(Vicini) # get now all pairs in both directions

        # Keep only once, each pair (Vic_xh[i],Vic_yh[i])
        Vic_xh = Vic_x[Vic_x>Vic_y]
        Vic_yh = Vic_y[Vic_x>Vic_y]
        
        # Check if all points are connected (by making a single big cluster !)
        cluster = get_cluster(Vic_xh,Vic_yh,npoints)

        all_connected = (unique(cluster).size == 1) # only one cluster ?
        if not(all_connected):
            knear +=1
            print "Not all points connected => automatic increase of knear to : ",knear

    #~ print "All points connected with knear = ",knear
    
    # keep only required distances
    abst = dist[Vic_xh,Vic_yh]
    
    hilf = abst.sum()
    K = abst.size
    K=K/npoints
    durchabst=hilf/(K*npoints) #average distance
    #print "K = ",K
    #print "Distance moyenne = ",durchabst
    
    #~ cluster_base = zeros((npoints),dtype='i')
    #~ #print abst.mean(1).argsort().size , npoints
    #~ cluster_base[abst.mean(1).argsort()]=arange(npoints , dtype = 'i')
    
    # main
    allcluster = empty((npoints,0) , dtype = 'i')
    
    #~ ttotal=0 # time it !
    #~ tz=0 # time it !
    #~ tsame = 0 # time it !
    #~ tdeb = 0 # time it !
    #~ tconnect = 0 # time it !

        
        #~ print 'T' , T
    chi , mqu , mges = 0. , 0. ,0.
    
    spins = random_integers(0,Q-1,npoints) # Choose npoints random integers from 0 to Q-1 
    samespin=spins[Vic_xh]==spins[Vic_yh] # samespin : pairs with same spin on both points 
    Corr = samespin.astype('i') # Corr : array which compute how often two points from a pair have the same spin

    #Monte-Carlo simulation: Swendsen-Wang
    #print 'monte carlo start'

    # Weight array which say how strongly a pair is linked
    J = 1.*exp(-(abst**2)/(2*durchabst**2))/K
    p = 1. - exp((-J)/T)
    #~ print "p max : ",p.max()
    #~ print "p.min = ",p.min()

    #~ tMCS = time() # time it !

    for s in range(MCS) :
        
        #~ print "s = ",s
        
        #~ t1=time()
        
        Nmax=magn(spins,Q)
        m=(Nmax/npoints*Q-1)/(Q-1)
        mges += m
        mqu += (m*m)
        
        #~ NN = samespin.copy() # By default, all pairs (issued from Vicini !) with samespin are bonded
        # !!!! => NN is samespin and that's all !!!
        # Nearest Neighbours -> Bond
        #~ tdeb+=time()-t1
        
        #TODO optimiser
        #~ t1=time()# time it !
        ind_xh,= where(samespin) # draw only where it is needed
        z = random(ind_xh.size)
        #~ tz+=time()-t1# time it !

        #~ t1=time()# time it !
        # same spin state: disconnect with probability 1-p
        ind_mod = ind_xh[where(z>p[ind_xh])[0]]
        samespin[ind_mod] = False
        # not same spine state: do not connect (already done in NN definition)
        #~ NN[~samespin] = False
        #~ # initialise diagonal (to include a point in his own cluster) => done in get cluster if needed !
        #~ NN[arange(npoints),arange(npoints)] = True
        #~ tconnect += time()-t1# time it !

        #~ t1=time()# time it !
        # determine domains (points connected via pairs of same spin !)

        # TODO optimiser Schnitt
        clus_xh = Vic_xh[samespin] # get connected pairs
        clus_yh = Vic_yh[samespin]

        # Determination des domaines
        cluster = get_cluster(clus_xh,clus_yh,npoints)
        
        #~ print cluster[cluster.argsort()]
        NC = cluster.max()
        #~ ttotal+=time()-t1
        
        #~ tst = time()
        # domains get random spin state
        cluspi = random_integers(0,Q-1,NC+1)

        # all points in domain with equal spin state
        spins = cluspi[cluster]
        samespin=spins[Vic_xh]==spins[Vic_yh]
        Corr[samespin] += 1
        #~ tsame += time()-tst

        #Config = spins # ??? voir inverse avant
    
    #~ print "temps MCS ",time()-tMCS
    
    #print ' end'
    
    # redraw Corr as a symetric array
    #~ tmpCorr=zeros((npoints,npoints),dtype='i')
    #~ tmpCorr[Vic_xh,Vic_yh]=Corr
    #~ tmpCorr[Vic_yh,Vic_xh]=Corr
    #~ Corr = tmpCorr
    #~ Corr[range(npoints),range(npoints)]=MCS
    
    #print Corr
    #~ test = 1.0*Corr.reshape((npoints*npoints))/MCS
    #~ test = test[test>0]
    #~ pylab.figure()
    #~ pylab.hist(test)
    #~ print "test ",test.max(),test.mean()
    #~ pylab.title("Corr histogram")

    #~ pylab.figure()
    #~ pylab.imshow(abst, interpolation='nearest', origin ='lower' , aspect = 'normal')
    #~ # pylab.imshow(abs(abst**2), interpolation='nearest', origin ='lower' , aspect = 'normal')
    #~ pylab.title("Abst")
    #~ pylab.colorbar()
    
    #~ pylab.figure()
    #~ pylab.imshow(Corr, interpolation='nearest', origin ='lower' , aspect = 'normal')
    #~ pylab.title("Corr")
    #~ pylab.colorbar()
    
    #~ pylab.figure()
    #~ pylab.imshow(Vicini, interpolation='nearest', origin ='lower' , aspect = 'normal')
    #~ pylab.title("Vicini")
    #~ pylab.colorbar()
    
    # determine clusters
    #~ Nmax=magn(spins,Q)
    #~ m=(Nmax/npoints*Q-1)/(Q-1)
    #~ mges=mges+m # total magnetisation
    #~ mqu=mqu+(m*m)
    #~ chi = mqu/MCS-((mges/MCS)**2) # susceptibilty
    
    # determine clusters
    u = 1.0*Corr.astype('f')/MCS
    CCorr = u > threshold
    #print CCorr
    
    clus_xh = Vic_xh[CCorr] # get connected pairs
    clus_yh = Vic_yh[CCorr]

    ccluster = get_cluster(clus_xh,clus_yh,npoints)

    #~ # remap with small and contigu numbers => useless
    #~ map = unique(cluster)
    #~ for (k,i) in enumerate(map[map.argsort()]):
    #~ ccluster[ccluster==i]=k
            
    #~ print "Number of cluster = ",ccluster.max()
        
        #~ cmap = pylab.get_cmap('jet',unique(ccluster).size)
        #~ fig = pylab.figure()
        #~ ax = fig.add_subplot(111)
        #~ ax.set_title(str(T))
        #~ for c,cl in enumerate(unique(ccluster)) :
            #~ ind, = where(cl == ccluster)
            #~ ax.plot(Coord[ind,0] , Coord[ind,1] , ls =' ', color = cmap(c) , marker = 'o')
        
        #~ print "Schnitt time = ",ttotal
        #~ print "rand time = ",tz
        #~ print "tsame = ",tsame
        #~ print "tdeb = ",tdeb
        #~ print "tconnect = ",tconnect
        
    return ccluster


