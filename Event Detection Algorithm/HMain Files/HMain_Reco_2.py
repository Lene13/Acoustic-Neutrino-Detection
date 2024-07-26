import aa, ROOT
from itertools import product
from ROOT import Evt, Vec, Hit, Trk
from copy import copy
import pickle


vsound = 1500 # m/s

def EventsforPrint():
    "This function reads a .txt file and outputs the data in an array"
    
    # Read the data from the file
    with open("data.pkl", "rb") as f:
        data = pickle.load(f)
        # Now you can access the data like this:
        Energy_Source = data["Energy_Source"]
        Time_Source = data["Time_Source"]
        X_Source = data["X_Source"]
        Y_Source = data["Y_Source"] 
        Z_Source = data["Z_Source"]
        Azimuth_Source = data["Azimuth_Source"]
        Zenith_Source = data["Zenith_Source"]
    nupos = (X_Source, Y_Source, Z_Source)

    return nupos, Azimuth_Source, Zenith_Source
    
def GetEvents():
    "This function reads a .txt file and outputs the data in an array"
    
    # Read the data from the file
    with open("data.pkl", "rb") as f:
        data = pickle.load(f)

        # Now you can access the data like this:
        Energy_Source = data["Energy_Source"]
        Time_Source = data["Time_Source"]
        X_Source = data["X_Source"]
        Y_Source = data["Y_Source"] 
        Z_Source = data["Z_Source"]
        Azimuth_Source = data["Azimuth_Source"]
        Zenith_Source = data["Zenith_Source"]
        Amp_Hits = data["Amp_Hits"]
        Time_Hits = data["Time_Hits"]
        X_Hits = data["X_Hits"]
        Y_Hits = data["Y_Hits"]
        Z_Hits = data["Z_Hits"]
        Type_Hits = data["Type_Hits"]
        
    nupos = (X_Source, Y_Source, Z_Source)
    r = Evt() #km3net event
    nu = Trk()
    nu.t = Time_Source
    nu.pos.set(*nupos)

    r.mc_trks.push_back(nu)
    Hits_Locs = []
    for ilocs in range(len(X_Hits)):
        Hits_Locs.append((X_Hits[ilocs], Y_Hits[ilocs], Z_Hits[ilocs]))

    for ihits in range(len(Hits_Locs)):
        p = Vec(*Hits_Locs[ihits])
        
        h = Hit()
        h.a = Amp_Hits[ihits]
        h.t = Time_Hits[ihits]
        h.pos = p
        h.type = Type_Hits[ihits]
        r.hits.push_back(h)
        
    return r
        
        
def detector(D = 1000, N = 5):
    
    "return list of x,y,z tuples (of the hydrophones) on a grid"
    u = [D/(N-1)*i-D/2 for i in range(N)]
    return list(product(u,u,u)) 
        

def simulate (det, 
              nupos         = (80,90,100), 
              t             =1.234, 
              amplitude     = 1e3,
              time_accuracy = 10e-6, 
              noise_rate    = 0.1,         # per second
              noise_window  = [-2000/vsound,2000/vsound]):

    "Do a toy-simulation of an accoustic event. Expanding sphere with vsound"

    # how many noise hits per hydrophone, on average ? 
    mean_noise = (noise_window[1]-noise_window[0]) * noise_rate

    r = Evt() #km3net event
    nu = Trk()
    nu.t = t
    nu.pos.set(*nupos)

    r.mc_trks.push_back(nu)

    for xyz in det :
        p = Vec(*xyz)
        distance = (p - nu.pos).len()
        if distance == 0 : continue

        a = amplitude / distance; # todo: add pancake shape
        Max_Distance = 1000

        if a > 1 and p.z >= nupos[2] - 100 and p.z <= nupos[2] + 100 and distance <= Max_Distance: 
            h = Hit()
            h.a    = a
            h.t    = nu.t + distance / vsound + ROOT.gRandom.Gaus(0,time_accuracy)
            h.pos  = p 
            h.type = 14 # some neutrino
            r.hits.push_back(h)

        for i in range(ROOT.gRandom.Poisson(mean_noise)):
            h = Hit()
            h.a = 1
            h.t = ROOT.gRandom.Uniform(*noise_window) 
            h.pos = p
            h.type = -1
            r.hits.push_back(h)          

    return r


def inspect(evt, track):

    "Print a table of hits and residuals"
    T = ROOT.Table("type","x", "y", "z","distance(m)","time(s)","resi_fit(s)","resi_true(s)")
    nu = evt.mc_trks[0]

    for h in evt.hits:
        d1 = (h.pos - track.pos).len()
        r1 = h.t - track.t - d1 / vsound
        d2 = (h.pos - nu.pos).len()
        r2 = h.t - nu.t - d2 / vsound
        T.add(h.type, h.pos.x, h.pos.y, h.pos.z, d1, h.t, r1, r2)

    #print (T)
    
def inspectamp(evt, track):

    "Print a table of hits and residuals"
    T = ROOT.Table("type","x", "y", "z","distance(m)","time(s)","amplitude(Pa)","resi_fit(s)","resi_true(s)","resi_amp(Pa)")
    nu = evt.mc_trks[0]

    for h in evt.hits:
        d1 = (h.pos - track.pos).len()
        r1 = h.t - track.t - d1 / vsound
        ra1 = h.a - track.a / d1
        d2 = (h.pos - nu.pos).len()
        r2 = h.t - nu.t - d2 / vsound 
        T.add(h.type, h.pos.x, h.pos.y, h.pos.z, d1, h.t, h.a, r1, r2, ra1)

    #print (T)



def starting_point(hits, N = 5):
    "Generate a very first estimate of the neutrino position, using the amplitudes"
    hits = sorted(hits, key = lambda h: - h.a)[:N]
    #print(hits)
    start_track = Trk()
    print(hits[0])
    for h in hits :
        start_track.pos += h.pos
    start_track.pos /= N
    start_track.t = hits[0].t - (hits[0].pos - start_track.pos).len() / vsound
    start_track.a = hits[0].a * (hits[0].pos - start_track.pos).len()
    return start_track


# def select_hits( trk, evt , max_residual ):

#     "Return the hits that have a residual smaller than max_residual"
#     temphits = []
#     for h in evt.hits:
#         # d = (h.pos - trk.pos ).len()
#         temphits.append(h)

#     return filter( lambda h : h.t - trk.t - (h.pos - trk.pos ).len() / vsound < max_residual, temphits )


def select_hits(trk, evt , max_residual):
    "Return the hits that have a residual smaller than max_residual"
    sel_evt = copy(evt)
    sel_evt.hits = [elem for elem in sel_evt.hits if abs(elem.t - trk.t - (elem.pos - trk.pos ).len() / vsound) < max_residual]
    # return filter( lambda h : evt.hits.t - trk.t - (evt.hits.pos - trk.pos ).len() / vsound < max_residual, evt )
    return sel_evt

def get_aashower_fit():

    "Return a function that can fit hits using the machinery in aashowerfit"

    import rec
    from ROOT import MestShowerPdf, ShowerFit

    m_estimator_pdf = MestShowerPdf()
    showerfit = ShowerFit ("mest", m_estimator_pdf)
    showerfit.fix_vars(3,4,6) # dont fit direction and energy

    # functions to scale the hit-times so that it looks like
    # sound moves at the speed of light.

    def time_warp(obj):
        " e.g. 1500m : 1s => 6903 ns "
        obj.t *= vsound / ROOT.v_light

    def time_unwarp(obj) :
        obj.t *= ROOT.v_light / vsound


    def fit(evt):
        hits = [copy(h) for h in evt.hits] # copy since we're going to change the hits
        for h in hits : time_warp(h)
        start_track = starting_point(hits)
        track = showerfit.fit(start_track, ROOT.Det(), aa.make_vector(hits), 1)
        time_unwarp(track)
        time_unwarp(start_track)
        #print (start_track)
        #print (track)
        return track
    return fit


def get_homebrew_fit():

    "Return a function that does the fit using scipy.minimizer"

    from scipy.optimize import minimize
    import numpy as np

    def score(hits, trk):
        '''
        M-estimator score. 
        the constant determines where the quadratic behaviour becomes linear
        '''
        constant = 1e-4 # in seconds.
        power    = 0.5
        score    = 0
        for h in hits:
            d = (h.pos - trk.pos).len()
            residual = h.t - trk.t - d / vsound
            score += h.a * (constant**2 + residual**2) ** power 
        return score


    def make_fitfunc(hits):
        T = Trk()
        def fitme(pars) :
            T.pos.set(pars[0],pars[1],pars[2])
            T.t = pars[3]
            return score(hits, T)
        return fitme


    def fit(evt):
        t = starting_point(evt.hits)
        pars =  np.array([ t.pos.x, t.pos.y, t.pos.z, t.t ])
        f = make_fitfunc(evt.hits) 
        
        opts={'gtol'   : 1e-4 , 
              'eps'    : 1.4901161193847656e-08, 
              'maxiter': None, 
              'disp'   : False,
              'return_all': False}

        res = minimize(f , pars, method= "bfgs", options = opts)
        r = Trk()
        r.pos.set(res.x[0],res.x[1],res.x[2])
        r.t = res.x[3]
        r.lik = res.fun
        return r

    return fit


def get_homebrew_ampfit() :

    "Return a function that does the fit using scipy.minimizer on time + amplitude"
    # Amplitude profile used is simple for now to verify code works: f(r) = 1/r

    from scipy.optimize import minimize
    import numpy as np

    def score(hits, trk) :
  
        '''
        M-estimator score. 
        the constant determines where the quadratic behaviour becomes linear
        '''

        constant = 1e-4 # in seconds.
        power    = 0.5
        score    = 0

        for h in hits :
            d = (h.pos - trk.pos ).len()
            residual = h.t - trk.t - d / vsound
            residualamp = h.a - trk.a / d
            score += h.a * (constant**2 + (residual + residualamp)**2) ** power    # Why is h.a in here? --> Ask Aart!

        return score


    def make_fitfunc(hits) :

        T = Trk()

        def fitme(pars) :
            T.pos.set(pars[0],pars[1],pars[2])
            T.t = pars[3]
            T.a = pars[4]
            return score(hits, T)
        
        return fitme


    def fit(evt):
       
        t = starting_point(evt.hits)
        pars =  np.array([ t.pos.x, t.pos.y, t.pos.z, t.t, t.a ])   # Goes wrong here, Trk object has no attribute a!

        f = make_fitfunc(evt.hits) 
        
        opts={'gtol'   : 1e-4 , 
              'eps'    : 1.4901161193847656e-08, 
              'maxiter': None, 
              'disp'   : False,
              'return_all': False}

        res = minimize(f , pars, method= "bfgs", options = opts)

        r = Trk()
        r.pos.set( res.x[0],res.x[1],res.x[2] )
        r.t = res.x[3]
        r.a = res.x[4]
        r.lik = res.fun
        return r

    return fit

def NuCount(evt):
    NuCount = 0
    for j in evt.hits:
        if j.type == 14:
            NuCount += 1
            
    return NuCount

fit = get_aashower_fit()


Namei = "Event_NMin10RCan1000Run1SubRun1Event1"
Loc = "/project/antares/koers/Reconstruction/"
Name = Loc + Namei

evt = GetEvents()

NuCounter = NuCount(evt)


t = fit(evt)

t_loop = copy(t)
evt_loop = copy(evt)
Thresholds = [6,5,4,3,2,1.5,1]                                                      #,0.8,0.6,0.4,0.3,0.2,0.15,0.1]
for i in Thresholds:
    evt_sel = select_hits(t_loop, evt_loop, i)
    t_sel = fit(evt_sel)
    t_loop = t_sel
    evt_loop = evt_sel

NuCounter_sel = NuCount(evt_sel)

# Printing of Results
#print("table before selection")
#inspectamp(evt, t)
#inspect(evt, t)


print('Check Whether Selection Works!')
print ("event has", len(evt.hits), "hits before selection")
print("event has", len(evt_sel.hits), "hits after selection")
print ("event has", NuCounter, "neutrino hits before selection")
print ("event has", NuCounter_sel, "neutrino hits after selection")

print("Neutrino Direction from Simulation equals:")
print(f"Azimuth {EventsforPrint()[1]} and Zenith {EventsforPrint()[2]}.")

print("track reconstruction before selection")
print(t)
print("track reconstruction after selection")
print(t_sel)
print("True Neutrino Position Equals:", evt.mc_trks[0].pos, "; True Neutrino Time Equals:", evt.mc_trks[0].t)