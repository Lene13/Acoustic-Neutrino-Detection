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
import pickle


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


# Import Functions for Reconstruction
#import aa, ROOT
#from itertools import product
#from ROOT import Evt, Vec, Hit, Trk
#from copy import copy



# This code is written with the aim to investigate the efficiency and false alarm rates
# of an array of hydrophones. We use both these as input parameters for this simulation.
# This code uses a predetermined arrangement of Hydrophones
#--- HPP 1.1 ---#

# Code Timing 
st = time.time()
    


##################----------- Input Parameters -----------###########################################################################################################################################################################################################################
    


# timeslices     
runs = 1                                                                                  # number of timeslices
Hitsrange = [0,4]                                                                         # size of timeslice

# physical constants & parameters
Vsound = 1.5e3                                                                            # Sound velocity in water in m/s

# Read Config File 
config = configparser.RawConfigParser()
configFilePath = sys.argv[1] 
config.read(configFilePath)



##################--------- Hydrophone Locations ---------###########################################################################################################################################################################################################################



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
zrange = [-500,500]                                                                       # ZLoc range in meters
    
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
RCan = 1000                                                                                 # int(config.getfloat("Physics", "RCan"))
Source_X_Range = [-RCan, RCan]
Source_Y_Range = [-RCan, RCan]
Source_Z_Range = [-500, 500]
AzimuthRange = [0, 360]                                                                     # Incoming angle neutrino range in degrees! [0,360]
ZenithRange = [0, 90]                                                                       # Incoming angle neutrino range in degrees!  [0,90]

# Pancake Size and Nmin Value for Event + Clique
PanDepth = 100                                                                              # Depth of Pancake in m
PanSearchDepth = 100                                                                        # Depth of Pancake in m for HEvent Algorithm
TravelDist = 2000                                                                           # Maximum detectable Distance from Source
TravelSearchDist = 720                                                                      # Value for search Algorithm
Nmini = [int(config.getfloat("Physics", "NMin"))]                                           # Nmin value for Clique Algorithm
Max_Dist_Match = 720                                                                        # 720  #[TravelSearchDist]    # Check This!!   # Max_Dist_Match/2 is max distance travelled in both directions  [9,9,9] = 608.25 m [10,10,10] = 596.225 m
NuCountCut = 10
print(f"NuCountCut = {NuCountCut}")                                                                             # Amount of Neutrino Hits in Event to be counted as correctly identified as neutrino Event

# Scanning Angles
AzimuthVals = [0]                                                                           # np.arange(0, 360, 10)
ZenithVals = [0]                                                                            # np.linspace(0, 90, 10)

# Physical Constants & Parameters
Vsound = 1.5e3                                                                              # Sound velocity in water in m/s

# Determine the FHR in Hz
Noise_Rate_Init = [0.01]


# Output File Name
NumRun = int(config.getfloat("Physics", "NumRun"))
Loc = "/project/antares/lrootsel/data"
#LocEvent = "/data/antares/users/koers/output/Events/13x13x10/Events_FHR/"
OutName = "LocID=" + str(LocID) + "_runs=" + str(runs) + "_NMin=" + str(Nmini[0]) + "_RCan=" + str(RCan) + "FHS =" + str(Noise_Rate_Init[0]) + "_test"


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
    
    print(Locs)

    for p in range(len(Nmini)):                                                            # Loop over amount of False Hits
        Nmin = Nmini[p]
        Correct_Count = 0
        for run in range(runs):                                                            # Loop over amount of timeslices
            # Correct_Pulses = np.zeros(runs)
            print("run " + str(run))
            # Creating Hydrophone Locations & Dict
            Source_X = np.random.uniform(Source_X_Range[0],Source_X_Range[1])
            Source_Y = np.random.uniform(Source_Y_Range[0],Source_Y_Range[1])
            Source_Z = np.random.uniform(Source_Z_Range[0],Source_Z_Range[1])
            Source_Azimuth = np.random.uniform(AzimuthRange[0], AzimuthRange[1])
            Source_Zenith = np.random.uniform(ZenithRange[0], ZenithRange[1])
            
            Source_Loc = [Source_X, Source_Y, Source_Z]
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
                
                print(Hits)
                # Now Rotate the system back #
                Hydrophones = copy.deepcopy(Hydrophones_Storage) #HToolbox.HRotateAllBack(Hydrophones, np.radians(Sources[0].Azimuth), np.radians(Sources[0].Zenith))
                Sources = copy.deepcopy(Sources_Storage) #HToolbox.HRotateAllBack(Sources, np.radians(Sources[0].Azimuth), np.radians(Sources[0].Zenith))
                
                
            # Nmin = int(len(Appended_Phones))
            # Can add more neutrino pulses (For now only at same Loc and Angle!
            # Hits, Appended_Phonesx2, Appended_Pulses2 = HPulseAppender(Hydrophones, Hits, Sources, PanDepth, 0.5)
            
            # Sorting of Hits #
            DebugHits = copy.deepcopy(Hits)
            Hits, Temp_Hits = HToolbox.HHitSorter(Hits)
            Event_Log_Done = []
            Event_Log_Final = []
            
            for Azimuth in AzimuthVals:
                #print(Azimuth)
                for Zenith in ZenithVals:
                    #print(Zenith)
                    # Rotation Hydrophone Locs #
                    #Hydrophones = copy.deepcopy(Hydrophones_Storage)
                    
                    Hydrophones = HToolbox.HRotateAll(Hydrophones, np.radians(Azimuth), np.radians(Zenith))
                    
                    # Another beunfix
                    for ihits in range(len(Hits)):
                        Hits[ihits].Hydrophone.X = Hydrophones[Hits[ihits].Hydrophone.ID-1].X
                        Hits[ihits].Hydrophone.Y = Hydrophones[Hits[ihits].Hydrophone.ID-1].Y
                        Hits[ihits].Hydrophone.Z = Hydrophones[Hits[ihits].Hydrophone.ID-1].Z
                    
                    # Rotation Sources #
                    # Sources = copy.deepcopy(Sources_Storage)
                    Sources = HToolbox.HRotateAll(Sources, np.radians(Azimuth), np.radians(Zenith))
                    
                    # Pancake + Causality Algorithm #
                    Time_Event_S = time.time()
                    
                    Event_Log = []
                    HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, ID = HEvent_Numba.HPreNumba(Hits)
                    
                    Event_Log, Len_Buffer, Len_Buffer_PreClique = HEvent_Numba.HNumbaEvent(Event_Log, Hits, Hydrophones_Storage, HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, ID, Nmin, PanSearchDepth, Vsound, Max_Dist_Match, TravelSearchDist, Azimuth, Zenith)

                    Debug_Event_Log = copy.deepcopy(Event_Log)
                    Event_Log = HEventMerger.HSortEventLog(Event_Log)



                    Time_Event_E = time.time()
                    Time_Event_T = Time_Event_E - Time_Event_S
                    
                    # Merger Algorithm # !! Check whether correctly applied !!
                    Time_Merge_S = time.time()
                   
                    Event_Log_Buffer = []
                    Event_Log_Buffer = copy.deepcopy(Event_Log)
                    
                    print(f"Event_Log_Buffer is {Event_Log_Buffer}.")

                    if len(Event_Log_Buffer) != 0:
                        Event_Log_Buffer = HEventMerger.HEventMerger(Event_Log_Buffer, Azimuth, Zenith, Hits)
                        
                        # Beun Bug Fix, but works! Lack of time, I guess error due to naming in line above??
                        for o1 in range(len(Event_Log_Buffer)):
                            for o2 in range(len(Event_Log_Buffer[o1].Hits)):
                                Event_Log_Buffer[o1].Hits[o2].Hydrophone.X = Hydrophones_Storage[Event_Log_Buffer[o1].Hits[o2].Hydrophone.ID-1].X
                                Event_Log_Buffer[o1].Hits[o2].Hydrophone.Y = Hydrophones_Storage[Event_Log_Buffer[o1].Hits[o2].Hydrophone.ID-1].Y
                                Event_Log_Buffer[o1].Hits[o2].Hydrophone.Z = Hydrophones_Storage[Event_Log_Buffer[o1].Hits[o2].Hydrophone.ID-1].Z
                                                                        
                        Event_Log_Done.extend(Event_Log_Buffer)
                        print(f"Event_Log_Done is {Event_Log_Done}.")

                    # Now Rotate the system back #
                    # Hydrophones = HToolbox.HRotateAllBack(Hydrophones, np.radians(Azimuth), np.radians(Zenith))
                    Hydrophones = copy.deepcopy(Hydrophones_Storage)
                    # Sources = HToolbox.HRotateAllBack(Sources, np.radians(Azimuth), np.radians(Zenith))
                    Sources = copy.deepcopy(Sources_Storage)
                    
                    # Another beunfix
                    for ihits in range(len(Hits)):
                        Hits[ihits].Hydrophone.X = Hydrophones[Hits[ihits].Hydrophone.ID-1].X
                        Hits[ihits].Hydrophone.Y = Hydrophones[Hits[ihits].Hydrophone.ID-1].Y
                        Hits[ihits].Hydrophone.Z = Hydrophones[Hits[ihits].Hydrophone.ID-1].Z
                    
                    Time_Merge_E = time.time()
                    Time_Merge_T = Time_Merge_E - Time_Merge_S
                    
                    Hits_Per_Event = []
                    if len(Event_Log_Buffer) != 0:
                        for ilog in range(len(Event_Log_Buffer)):
                            Hits_Per_Event.append(len(Event_Log_Buffer[ilog].Hits))
                
                        Average_Hits_Per_Run_Event[i,p,run] = sum(Hits_Per_Event)/len(Event_Log_Buffer)
                        
            # Now Merge any events in the Event_Log_Done #
            if len(Event_Log_Done) != 0:
                print("yessss")
                Event_Log_Done = HEventMerger.HSortAngleMerg(Event_Log_Done)
                starting = time.time()
                Event_Log_Angle_Merge = HEventMerger.HEventMerger(Event_Log_Done, Azimuth, Zenith, Hits)
                print(f"Event Log Angle Merge is {Event_Log_Angle_Merge}.")
                
                ending = time.time()
                #print("HEventMerger Takes: " + str(ending-starting))
                NuCount, HitsCount, Correct_Count, Event_Log_Angle_Merge_Buffer = HNeutrinoCounter.HNeutrinoCounter(NuPulse, NuCountCut, Correct_Count, Event_Log_Angle_Merge, Azimuth, Zenith)
                print(f"NuCount is {NuCount}.")
                print(f"HitsCount is {HitsCount}.")
                print(f"Correct_Count is {Correct_Count}.")
                print(f"Event Log Angle Merge Buffer is {Event_Log_Angle_Merge_Buffer}.")
                
                Event_Log_Final.extend(Event_Log_Angle_Merge_Buffer) 
            
            Name = 'Event_NMin' + str(Nmin) + 'Run' + str(NumRun) + 'SubRun' + str(run+1) + 'NuCountCut' + str(NuCountCut)
            Events_Detected[p,run] = len(Event_Log_Final) 
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
#HData.HDataWriter(OutName, Noise_Rate_Init, Nmini, Average_Events_Detected_Hz, LocEff, Correct_Percentage, NuCountCut)                          # Average_Events_Detected_Hz)



######################################################################################################################################


       
##################----------- Data Writing -----------################################################################################



######################################################################################################################################



# Read Source Information First
Energy_Source = Energy_Nu
Time_Source = Time_Nu
X_Source = Source_X
Y_Source = Source_Y
Z_Source = Source_Z
Azimuth_Source = Source_Azimuth
Zenith_Source = Source_Zenith

print(Event_Log_Done)

# Read Hit Information
Amp_Hits = [hit.Amplitude for event in Event_Log_Done for hit in event.Hits]
print(f"Amp_Hits is {Amp_Hits}.")
Time_Hits = [hit.Time for event in Event_Log_Done for hit in event.Hits]
print(f"Time_Hits is {Time_Hits}.")
X_Hits = [hit.Hydrophone.X for event in Event_Log_Done for hit in event.Hits]
print(f"X_Hits is {X_Hits}.")
Y_Hits = [hit.Hydrophone.Y for event in Event_Log_Done for hit in event.Hits]
print(f"Y_Hits is {Y_Hits}.")
Z_Hits = [hit.Hydrophone.Z for event in Event_Log_Done for hit in event.Hits]
print(f"Z_Hits is {Z_Hits}.")
Type_Hits = [hit.Type for event in Event_Log_Done for hit in event.Hits]
print(f"Type_Hits is {Type_Hits}.")

# Save the data in a dictionary
data = {
    "Energy_Source": Energy_Source,
    "Time_Source": Time_Source,
    "X_Source": X_Source,
    "Y_Source": Y_Source,
    "Z_Source": Z_Source,
    "Azimuth_Source": Azimuth_Source,
    "Zenith_Source": Zenith_Source,
    "Amp_Hits": Amp_Hits,
    "Time_Hits": Time_Hits,
    "X_Hits": X_Hits,
    "Y_Hits": Y_Hits,
    "Z_Hits": Z_Hits,
    "Type_Hits": Type_Hits,
}

# Write the data to a file
with open("data.pkl", "wb") as f:
    pickle.dump(data, f)