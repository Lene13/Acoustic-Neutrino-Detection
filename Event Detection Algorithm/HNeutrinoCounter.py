# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 10:18:06 2023

@author: oerskqpv
"""

"This Function is used to count the amount of Neutrino hits and Total Hits in an event"
import numpy as np
import HClasses
import copy

def HNeutrinoCounter1(NuPulse, NuCountCut, Correct_Count, Event_Log_Buffer, Azimuth, Zenith):
    NuCount = np.zeros(len(Event_Log_Buffer))
    HitsCount = np.zeros(len(Event_Log_Buffer))
    Event_Log_Buffer_Keep = copy.deepcopy(Event_Log_Buffer)
    if NuPulse == True:
        Event_Log_Buffer_Keep = []
        if len(Event_Log_Buffer) != 0:
            for j0 in range(len(Event_Log_Buffer)):
                Duplicate_Log = np.zeros(len(Event_Log_Buffer[j0].Hits))
                for j1 in range(len(Event_Log_Buffer[j0].Hits)):
                    for j2 in range(j1+1, len(Event_Log_Buffer[j0].Hits)):
                        if Event_Log_Buffer[j0].Hits[j1].ID == Event_Log_Buffer[j0].Hits[j2].ID:
                            Duplicate_Log[j2] +=1
             
                Hits_Temp = []
                for j3 in range(len(Duplicate_Log)):
                        if Duplicate_Log[j3] == 0:
                                Hits_Temp.append(Event_Log_Buffer[j0].Hits[j3])
                
                Event_Log_Buffer_Keep.append(HClasses.Event(Hits_Temp, Azimuth, Zenith, Event_Log_Buffer[j0].MergeCounter))
        
            for itype0 in range(len(Event_Log_Buffer_Keep)):
                for itype1 in range(len(Event_Log_Buffer_Keep[itype0].Hits)):
                    if Event_Log_Buffer_Keep[itype0].Hits[itype1].Type == 14:
                        NuCount[itype0] += 1
                HitsCount[itype0] = len(Event_Log_Buffer_Keep[itype0].Hits)
            
            for icount in range(len(NuCount)):
                if NuCount[icount] > NuCountCut:   # Motivate and check this arbitrary cut value!!
                    Correct_Count += 1
                    break        # Only need to know whether one Event has correctly identified the neutrino pulse, might check if useful to know how many events are correct or wrong!!
                
    return NuCount, HitsCount, Correct_Count, Event_Log_Buffer_Keep


def HNeutrinoCounter2(NuPulse, NuCountCut, Correct_Count, Event_Log_Buffer, Azimuth, Zenith):
    NuCount = np.zeros(len(Event_Log_Buffer))
    HitsCount = np.zeros(len(Event_Log_Buffer))
    Event_Log_Buffer_Keep = copy.deepcopy(Event_Log_Buffer)
    if NuPulse == True:
        Event_Log_Buffer_Keep = []
        if len(Event_Log_Buffer) != 0:
            for j0 in range(len(Event_Log_Buffer)):
                # Duplicate_Log = np.zeros(len(Event_Log_Buffer[j0].Hits))
                IDCheck = np.ones([len(Event_Log_Buffer[j0].Hits), len(Event_Log_Buffer[j0].Hits)])
                IDTemp = []
                for j1 in range(len(Event_Log_Buffer[j0].Hits)):
                    IDTemp.append(Event_Log_Buffer[j0].Hits[j1].Type)
                
                IDTemp = np.array(IDTemp)    
                for j2 in range(len(Event_Log_Buffer[j0].Hits)):
                    IDCheck[j2,j2:] = IDTemp[j2:] - IDTemp[j2]
                        
                        # if Event_Log_Buffer[j0].Hits[j1].Hydrophone.ID == Event_Log_Buffer[j0].Hits[j2].Hydrophone.ID and Event_Log_Buffer[j0].Hits[j1].Time == Event_Log_Buffer[j0].Hits[j2].Time:
                            # Duplicate_Log[j2] +=1
                IDCheck = np.fill_diagonal(IDCheck, 1)
                IDZero = np.where(IDCheck == 0)
                IDZero = np.unique(IDZero[1])
                # Left of Here #
                # Need to extract non-dupe Hits using the non-zeros or zeros of this IDZero Matrix
                # Use np.unique, and only check either rows or columns, whichever you prefer, should not matter lol
                Hits_Temp = []
                for j3 in range(len(Event_Log_Buffer[j0].Hits)):
                        if j3 in IDZero:
                            continue
                        Hits_Temp.append(Event_Log_Buffer[j0].Hits[j3])
                
                Event_Log_Buffer_Keep.append(HClasses.Event(Hits_Temp, Azimuth, Zenith, Event_Log_Buffer[j0].MergeCounter))
        
            for itype0 in range(len(Event_Log_Buffer_Keep)):
                for itype1 in range(len(Event_Log_Buffer_Keep[itype0].Hits)):
                    if Event_Log_Buffer_Keep[itype0].Hits[itype1].Type == 14:
                        NuCount[itype0] += 1
                HitsCount[itype0] = len(Event_Log_Buffer_Keep[itype0].Hits)
            
            for icount in range(len(NuCount)):
                if NuCount[icount] > NuCountCut:   # Motivate and check this arbitrary cut value!!
                    Correct_Count += 1
                    break        # Only need to know whether one Event has correctly identified the neutrino pulse, might check if useful to know how many events are correct or wrong!!
                
    return NuCount, HitsCount, Correct_Count, Event_Log_Buffer_Keep


def HNeutrinoCounter(NuPulse, NuCountCut, Correct_Count, Event_Log_Buffer, Azimuth, Zenith):
    NuCount = np.zeros(len(Event_Log_Buffer))
    HitsCount = np.zeros(len(Event_Log_Buffer))
    # Event_Log_Buffer_Keep = copy.deepcopy(Event_Log_Buffer)
    #print(f"NuPulse is: {NuPulse}")
    if NuPulse == True:
        
        #print(f"Event_Log_Buffer is: {Event_Log_Buffer}")        
        for itype0 in range(len(Event_Log_Buffer)):
            for itype1 in range(len(Event_Log_Buffer[itype0].Hits)):
                if Event_Log_Buffer[itype0].Hits[itype1].Type == 14:
                    NuCount[itype0] += 1
            HitsCount[itype0] = len(Event_Log_Buffer[itype0].Hits)
        
        #print(f"NuCount is: {NuCount}")    
        for icount in range(len(NuCount)):
            if NuCount[icount] > NuCountCut:   # Motivate and check this arbitrary cut value!!
                Correct_Count += 1
                break                          # Only need to know whether one Event has correctly identified the neutrino pulse, might check if useful to know how many events are correct or wrong!!
                
    return NuCount, HitsCount, Correct_Count, Event_Log_Buffer

def HNeutrinoCounter2(NuPulse, NuCountCut, Correct_Count, Event_Log_Buffer):
    NuCount = np.zeros(len(Event_Log_Buffer))
    HitsCount = np.zeros(len(Event_Log_Buffer))
    # Event_Log_Buffer_Keep = copy.deepcopy(Event_Log_Buffer)
    #print(f"NuPulse is: {NuPulse}")
    if NuPulse == True:
        
        #print(f"Event_Log_Buffer is: {Event_Log_Buffer}")        
        for itype0 in range(len(Event_Log_Buffer)):
            for itype1 in range(len(Event_Log_Buffer[itype0].Hits)):
                if Event_Log_Buffer[itype0].Hits[itype1].Type == 14:
                    NuCount[itype0] += 1
            HitsCount[itype0] = len(Event_Log_Buffer[itype0].Hits)
        
        #print(f"NuCount is: {NuCount}")    
        for icount in range(len(NuCount)):
            if NuCount[icount] > NuCountCut:   # Motivate and check this arbitrary cut value!!
                Correct_Count += 1
                break                          # Only need to know whether one Event has correctly identified the neutrino pulse, might check if useful to know how many events are correct or wrong!!
                
    return NuCount, HitsCount, Correct_Count, Event_Log_Buffer

def main():
    pass
    
if __name__ == "__main__":
    main()
