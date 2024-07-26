# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 15:31:59 2022

@author: oerskqpv
"""
import numpy as np
import itertools
import HClasses
import copy

def HSortEventLog(Event_Log):
    # This function sorts all the data according to ascending order of the hits
    for isort in range(len(Event_Log)):
        Temp_Hits = np.zeros(len(Event_Log[isort].Hits), dtype = np.float64)
        for jsort in range(len(Event_Log[isort].Hits)):
            Temp_Hits[jsort] = Event_Log[isort].Hits[jsort].Time
            
        TempHitsInd = Temp_Hits.argsort()
        Temp_Hits = Temp_Hits[TempHitsInd[::1]]
        Event_Log[isort].Hits = [Event_Log[isort].Hits[i] for i in TempHitsInd]
        
    return Event_Log


def HSortAngleMerg(Event_Log):
    tb = np.zeros(len(Event_Log), dtype = np.float64)
    for isort in range(len(Event_Log)):
        tb[isort] = Event_Log[isort].Hits[0].Time
    
    tbind = tb.argsort()
    Event_Log = [Event_Log[i] for i in tbind]
    
    return Event_Log


def HEventMerger(Event_Log, Azimuth, Zenith, Hits):
    tb = []
    te = []
    Event_Log_Done = copy.deepcopy(Event_Log)
    if len(Event_Log) > 1:
        
        for ifill in range(len(Event_Log)-1):
            tb.append(Event_Log[ifill+1].Hits[0].Time)
            te.append(Event_Log[ifill].Hits[-1].Time)
    
        # @numba.jit(nopython=True)
        for icheck in range(len(te)-1):
            if te[icheck] > te[icheck+1] and tb[icheck] <= te[icheck]:   # tb is from event 1 and te from event 0 by default
                te[icheck+1] = te[icheck]
    
        tf = (np.asarray(tb) + 1000) / (np.asarray(te) + 1000)       # Offset needed to mitigate tb = 0 s error
        tf[tf > 1] = 0   # Overlap condition, if no overlap = 0
        tf_zero = -1
        tf_zero = np.append(tf_zero, np.where(tf == 0)[0])
        tf_zero = np.append(tf_zero, len(Event_Log)-1)
    
        Event_Log_Merge = []
        for i in range(len(Event_Log)):
            Event_Log_Merge.append(Event_Log[i].Hits)
            
        # Add if statement to check length of tf_zero, This One Takes Most Time, Speed Up!
        Event_Log_Done = []
        Merge_Counter = np.zeros(len(tf_zero)-1)
        for imerge in range(len(tf_zero)-1):
            Event_Log_Done.append(list(itertools.chain.from_iterable(Event_Log_Merge[tf_zero[imerge]+1:tf_zero[imerge+1]+1])))
            Merge_Counter[imerge] = tf_zero[imerge+1] - (tf_zero[imerge] + 1) + Event_Log[tf_zero[imerge]+1].MergeCounter
    
        for idone in range(len(Event_Log_Done)):
            Event_Log_Done[idone] = HClasses.Event(Event_Log_Done[idone], Azimuth, Zenith, int(Merge_Counter[idone]))
    
        Event_Log_Buffer_Keep = []
        for j0 in range(len(Event_Log_Done)):
            TempHits = []
            TempID = []
            for j1 in range(len(Event_Log_Done[j0].Hits)):
                TempHits.append(Event_Log_Done[j0].Hits[j1])
                TempID.append(Event_Log_Done[j0].Hits[j1].ID)
                
            UniqueID = np.unique(TempID)
         
            Hits_Temp = []
            for j3 in range(len(Hits)):
                    if Hits[j3].ID in UniqueID:
                            Hits_Temp.append(Hits[j3])
            
            Event_Log_Buffer_Keep.append(HClasses.Event(Hits_Temp, Azimuth, Zenith, Event_Log_Done[j0].MergeCounter)) 
            
        return Event_Log_Buffer_Keep
        
    else:
        return Event_Log

def HEventMerger2(Event_Log):
    tb = []
    te = []
    for ifill in range(len(Event_Log)-1):
        tb.append(Event_Log[ifill+1].Hits[0].Time)
        te.append(Event_Log[ifill].Hits[-1].Time)

    # @numba.jit(nopython=True)
    for icheck in range(len(te)-1):
        if te[icheck] > te[icheck+1] and tb[icheck] <= te[icheck]:   # tb is from event 1 and te from event 0 by default
            te[icheck+1] = te[icheck]

    tf = np.asarray(tb) / np.asarray(te)
    tf[tf > 1] = 0   # Overlap condition, if no overlap = 0
    tf_zero = -1
    tf_zero = np.append(tf_zero, np.where(tf == 0)[0])
    tf_zero = np.append(tf_zero, len(Event_Log)-1)

    Event_Log_Merge = []
    for i in range(len(Event_Log)):
        Event_Log_Merge.append(Event_Log[i].Hits)

    # Add if statement to check length of tf_zero, This One Takes Most Time, Speed Up!
    Event_Log_Done = []
    for imerge in range(len(tf_zero)-1):
        Event_Log_Done.append(list(itertools.chain.from_iterable(Event_Log_Merge[tf_zero[imerge]+1:tf_zero[imerge+1]+1])))

    for idone in range(len(Event_Log_Done)):
        Event_Log_Done[idone] = HClasses.Event(Event_Log_Done[idone])

    return Event_Log_Done
    

def main():
    pass
    
if __name__ == "__main__":
    main()
