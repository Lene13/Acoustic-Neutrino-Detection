# -*- coding: utf-8 -*-

import math
import copy
import time
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import sys
import os
import os.path
import numpy as np
import configparser


sys.path.append("/project/antares/lrootsel/montecarlo")
sys.path.append("/project/antares/lrootsel/montecarlo/Thoth")


# Import Functions
import HClasses
import HHydrophones
import HNoiseGen
import HNuPulse
import HToolbox
import HEvent_Numba
import HEventMerger
import HData
import HNeutrinoCounter
import HEventToFile



'This code is written with the aim to investigate the efficiency and false alarm rates of an array of hydrophones. We use both these as input parameters for this simulation.'
'This code uses a predetermined arrangement of Hydrophones.'

#--- HPP 1.1 ---#

# Code Timing 
st = time.time()
    


##################----------- Input Parameters -----------###########################################################################################################################################################################################################################
    


# timeslices     
runs = 10000                                                                              # number of timeslices
Hitsrange = [0,4]                                                                         # size of timeslice

# physical constants & parameters
Vsound = 1.5e3                                                                            # Sound velocity in water in m/s

# Read Config File 
config = configparser.RawConfigParser()
configFilePath = sys.argv[1] 
config.read(configFilePath)



##################--------- Hydrophone Locations ---------###########################################################################################################################################################################################################################

print('Pylos NMin=4')

# choose the configuration of the hydrophones
LocID = 2                                                                                   # [0 = Random, 1 = Random X,Y, Evenly Spaced in Z, 2 = Evenly Spaced + Clusters, 3 = Hexagonal Shape, 4 = Cylindrical Shape]
print(f"LocID is: {LocID}")

# choose the number of hydrophones in each of the dimensions (only in square configuration)
Nx = [13]                                                                                   # [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]#np.ones(200,dtype=int)#[4]             # Same length as Nyi, Nzi
Ny = [13]                                                                                   # [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]#np.ones(200,dtype=int)#[4]             # Same length as Nxi, Nzi
Nz = [10]                                                                                   # Amount of Hydrophones in z-direction, sqrt(N/Nz) needs to be an integer!! (e.g. 100,4) or needs to be 25
    
# calculate the total number of hydrophones in the xy-plane per slice
Nxy = np.multiply(Nx, Ny)

# change the lay out of the detector
Cluster_Size = 1                                                                            # Amount of Hydrophones at a z-location
Z_Spacing = 1                                                                               # Spacing in Cluster in [m], only relevant if Cluster_Size > 1
  
# define the number of dimensions (x, y, z)
D = 3

# define the size of the detector in each of the dimensions
xrange = [-1000,1000]                                                                       # XLoc range in meters      
yrange = [-1000,1000]                                                                       # YLoc range in meters
zrange = [-500,500]                                                                         # ZLoc range in meters
    
# define the number of hydrophones again after the set-up
Ni = int(np.multiply(Nxy, Nz) * Cluster_Size)                                               # Total amount of Hydrophones

# different Ni when using the hexagonal shape
if LocID == 3:
    Ni = [HHydrophones.HLocationAlg(xrange, yrange, zrange, Z_Spacing, Cluster_Size, LocID, Nx[0], Ny[0], Nz[0], Ni, D)[1]]
    Ni = Ni[0]
    print(Ni)

# different Ni when using the cylindrical shape
if LocID == 4:
    Ni = [HHydrophones.HLocationAlg(xrange, yrange, zrange, Z_Spacing, Cluster_Size, LocID, Nx[0], Ny[0], Nz[0], Ni, D)[1]]
    Ni = Ni[0] 
    print(Ni)



##################----------- Neutrino Pulses -----------###########################################################################################################################################################################################################################



# False Hits + Amplitudes 
Noise_Rate_Start = config.getfloat("Physics", "RCan")
Noise_Rate_End = config.getfloat("Physics", "RCan")
Noise_Rate_Steps = int(round(((Noise_Rate_End - Noise_Rate_Start) / 0.1), 2) + 1)           # Always steps of 0.1
Noise_Rate_Init = np.linspace(Noise_Rate_Start, Noise_Rate_End, Noise_Rate_Steps)           # [1,2,3]#[1,2,3,4,5,6,7,8,9,10,12,16,20]#11,12,13,14,15,16,17,18,19,20]#[5,10,20,30,40,60,80,100,120,160]   # 5 per 10 seconds
Noise_Rate_Init = [round(Noise_Rate_Init[i], 2) for i in range(len(Noise_Rate_Init))]       # Fixing annoying rounding error
Amprange = [0, 1]                                                                           # dB range of hits (Check whether assumed values are correct!!)
Source_Amp = 20                                                                             # Amplitude of Source

# Source Location
NuPulse = True
Time_Nu = 0
Energy_Nu = 1                                                                               # Placeholder Value
RCan = 15000                                                                                # int(config.getfloat("Physics", "RCan"))
Source_X_Range = [-RCan, RCan]
Source_Y_Range = [-RCan, RCan]
Source_Z_Range = [-500, 3500]
AzimuthRange = [0, 360]                                                                     # Incoming angle neutrino range in degrees! [0,360]
ZenithRange = [0, 90]                                                                       # Incoming angle neutrino range in degrees!  [0,90]


# Pancake Size and Nmin Value for Event + Clique
PanDepth = 100                                                                              # Depth of Pancake in m
PanSearchDepth = 100                                                                        # Depth of Pancake in m for HEvent Algorithm
TravelSearchDist = 720                                                                      # Value for search Algorithm
Nmini = [4]                                                                                 # Nmin value for Clique Algorithm
Max_Dist_Match = 720                                                                        # 720  #[TravelSearchDist]    # Check This!!   # Max_Dist_Match/2 is max distance travelled in both directions  [9,9,9] = 608.25 m [10,10,10] = 596.225 m
NuCountCut = 6
#print(f"NuCountCut = {NuCountCut}")                                                                             # Amount of Neutrino Hits in Event to be counted as correctly identified as neutrino Event

# Scanning Angles
AzimuthVals = [0]                                                                           # np.arange(0, 360, 10)
ZenithVals = [0]                                                                            # np.linspace(0, 90, 10)

# Physical Constants & Parameters
Vsound = 1.5e3                                                                              # Sound velocity in water in m/s

# Determine the FHR in Hz
Noise_Rate_Init = [0]


# Output File Name
NumRun = int(config.getfloat("Physics", "NumRun"))
LocEff = "/project/antares/lrootsel/data"
#LocEvent = "/data/antares/users/koers/output/Events/13x13x10/Events_FHR/"
OutName = "LocID=" + str(LocID) + "_runs=" + str(runs) + "_NMin=" + str(Nmini[0]) + "_RCan=" + str(RCan) + "_FHS =" + str(Noise_Rate_Init[0]) + "_lines" + str(Nx[0]) + "_floors" + str(Nz[0])


######################################################################################################################################


       
##################----------- Running -----------#####################################################################################



######################################################################################################################################



# initialize lists to store the results
Events_Detected = np.zeros([len(Nmini),runs])
Average_Events_Detected = np.zeros([len(Noise_Rate_Init), len(Nmini)])
Average_Hits_Per_Run_Event = np.zeros([len(Noise_Rate_Init), len(Nmini), runs])
Average_Hits_Event = np.zeros([len(Noise_Rate_Init), len(Nmini)])
Time_Store = np.zeros([len(Noise_Rate_Init), len(Nmini)]) 
Correct_Percentage = np.zeros([len(Noise_Rate_Init), len(Nmini)]) 



for i in range(len(Noise_Rate_Init)):                                                      # First Loop over amount of Hydrophones
    
    Noise_Rate = Noise_Rate_Init[i]                                                        # False Hit Rate in Hz
    Locs = np.zeros([Ni,D])
    Locs = HHydrophones.HLocationAlg(xrange, yrange, zrange, Z_Spacing, Cluster_Size, LocID, Nx[0], Ny[0], Nz[0], Ni, D)[0]
    
    for p in range(len(Nmini)):                                                            # Loop over amount of False Hits
        Nmin = Nmini[p]
        Correct_Count = 0
        for run in range(runs):                                                            # Loop over amount of timeslices
            # Correct_Pulses = np.zeros(runs)
            #print("run " + str(run))

            # Veff parameters that need to be defined
            # define the range of energies you want to sample in logarithmic scale
            log_min_energy = 18                                                                         # Logarithm (base 10) of the minimum energy
            log_max_energy = 24                                                                         # Logarithm (base 10) of the maximum energy

            # Generate random samples from a uniform distribution in log space
            log_energies = np.random.uniform(log_min_energy, log_max_energy, 1)

            # Transform the sampled energies back to linear scale
            energy = 10**log_energies                                                                   # in eV
            print(energy)

            # Define a detection threshold in mPa
            threshold = 5                                                                               # in mPa

            # Pressure at 1000 m Perkin
            Pressure_1000m = 0.25 * 21.15 * 10**(-18) * energy                                          # in mPa
            radius_pancake = 1000 + (Pressure_1000m / threshold)                                        # in m
            
            # Set a maximum radius for the pancake at x km as there it is relatively straight still
            # For Tanganyika x = 17.5 km and for Pylos x = 15 km
            if radius_pancake > 15000:
                radius_pancake = 15000

            # The TravelDist can be seen as the radius of the pancake and is energy dependent
            TravelDist = radius_pancake                                                                 # Maximum detectable Distance from Source


            # Creating Hydrophone Locations & Dict
            Source_X = np.random.uniform(Source_X_Range[0],Source_X_Range[1])
            Source_Y = np.random.uniform(Source_Y_Range[0],Source_Y_Range[1])
            Source_Z = np.random.uniform(Source_Z_Range[0],Source_Z_Range[1])
            Source_Azimuth = np.random.uniform(AzimuthRange[0], AzimuthRange[1])
            Source_Zenith = np.random.uniform(ZenithRange[0], ZenithRange[1])
            print(Source_Azimuth)
            print(Source_Zenith)

            Source_Loc = [Source_X, Source_Y, Source_Z]
            print(Source_Loc)
            Sources_Storage = [HClasses.Source(Source_X, Source_Y, Source_Z, Source_Azimuth, Source_Zenith, Time_Nu, Energy_Nu)]  # For now only one(1) source loc
            Sources = copy.deepcopy(Sources_Storage)
            
            Hydrophones_Storage = HHydrophones.HHydrophoneCreator(Locs, Ni)
            Hydrophones = copy.deepcopy(Hydrophones_Storage)
            Hits = HNoiseGen.HHitAppender(Hitsrange, Noise_Rate, Hydrophones, Amprange, Ni)
        
            # Adding Neutrino Pulses to Hydrophones 
            if NuPulse == True:
                # Now Rotate the system to align the z-axis with the incoming vertex #
                Hydrophones = HToolbox.HRotateAll(Hydrophones, np.radians(Sources[0].Azimuth), np.radians(Sources[0].Zenith))
                Sources = HToolbox.HRotateAll(Sources, np.radians(Sources[0].Azimuth), np.radians(Sources[0].Zenith))
               
                # Append the neutrino hits #
                Hits, Appended_Phones, Appended_Pulses = HNuPulse.HPulseAppender(Hydrophones, Hydrophones_Storage, Hits, Ni, Sources, PanDepth, Vsound, TravelDist, Time_Nu)

                # Now Rotate the system back #
                Hydrophones = copy.deepcopy(Hydrophones_Storage) #HToolbox.HRotateAllBack(Hydrophones, np.radians(Sources[0].Azimuth), np.radians(Sources[0].Zenith))
                Sources = copy.deepcopy(Sources_Storage) #HToolbox.HRotateAllBack(Sources, np.radians(Sources[0].Azimuth), np.radians(Sources[0].Zenith))
                
                
            # Nmin = int(len(Appended_Phones))
            # Can add more neutrino pulses (For now only at same Loc and Angle!
            # Hits, Appended_Phonesx2, Appended_Pulses2 = HPulseAppender(Hydrophones, Hits, Sources, PanDepth, 0.5)
            
            # Sorting of Hits #
            DebugHits = copy.deepcopy(Hits)
            Hits, Temp_Hits = HToolbox.HHitSorter(Hits)

            # Pancake + Causality Algorithm #
            Time_Event_S = time.time()
                    
            Event_Log = []
            #HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, ID = HEvent_Numba.HPreNumba(Hits)
            HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type = HEvent_Numba.HPreNumba(Hits)
            
            Event_Log, Len_Buffer = HEvent_Numba.HNumbaEvent2(Event_Log, Hits, Hydrophones_Storage, HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, Nmin, PanSearchDepth, Vsound, Max_Dist_Match, TravelSearchDist)

            Debug_Event_Log = copy.deepcopy(Event_Log)
            Event_Log = HEventMerger.HSortEventLog(Event_Log)
                   
            Time_Event_E = time.time()
            Time_Event_T = Time_Event_E - Time_Event_S
                    
            # Merger Algorithm # !! Check whether correctly applied !!
            Time_Merge_S = time.time()
                   
            Event_Log_Buffer = copy.deepcopy(Event_Log)
                   
            if len(Event_Log_Buffer) != 0:
                Event_Log_Buffer = HEventMerger.HEventMerger2(Event_Log_Buffer)

            NuCount, HitsCount, Correct_Count, Event_Log_Buffer_Keep = HNeutrinoCounter.HNeutrinoCounter2(NuPulse, NuCountCut, Correct_Count, Event_Log_Buffer)
          
            Time_Merge_E = time.time()
            Time_Merge_T = Time_Merge_E - Time_Merge_S

            Events_Detected[p,run] = len(Event_Log_Buffer)        
            Hits_Per_Event = []

            if len(Event_Log_Buffer) == 0:
                print('0')

            if len(Event_Log_Buffer) != 0:
                for ilog in range(len(Event_Log_Buffer)):
                    Hits_Per_Event.append(len(Event_Log_Buffer[ilog].Hits))
                
                Average_Hits_Per_Run_Event[i,p,run] = sum(Hits_Per_Event)/len(Event_Log_Buffer)

                print('1')
                        
        print('Done With NMin Value of ' + str(Nmin))       

        Correct_Percentage[i,p] = Correct_Count/runs
        Average_Hits_Event[i,p] = sum(Average_Hits_Per_Run_Event[i,p])/runs
        Average_Events_Detected[i,p] = sum(Events_Detected[p])/runs

        et = time.time()
        time_elapsed = et - st
        Time_Store[i,p] = time_elapsed/runs
    print('Done with Value of FHR of ' + str(Noise_Rate) + ' Hz')
    print('Elapsed time ' + str(time_elapsed)) 

    
# Write Relevant Data to .txt File #
Average_Events_Detected_Hz = Average_Events_Detected / Hitsrange[1]
HData.HDataWriter(OutName, Noise_Rate_Init, Nmini, Average_Events_Detected_Hz, LocEff, Correct_Percentage, NuCountCut)                          # Average_Events_Detected_Hz)