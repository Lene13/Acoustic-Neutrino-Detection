# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 14:28:08 2023

@author: oerskqpv
"""

import numpy as np
import math
import HClasses
import numba

@numba.jit(nopython=True)
def HTimeDiff(LocX1, LocX2, LocY1, LocY2, LocZ1, LocZ2, Vsound):
    # Dist = np.zeros(1,dtype = np.float64)
    # DT = np.zeros(1,dtype = np.float64)
    Dist = math.sqrt((LocX1 - LocX2)**2 + \
                        (LocY1 - LocY2)**2 + \
                            (LocZ1 - LocZ2)**2)
    DT = Dist / Vsound
    
    return DT, Dist


def HMatch1(Hit1, Hit2, Vsound, TravelDist, PanDepth):
    "Function which takes two Hits and outputs a True/False depending on whether they are a match."
    Dt = abs(Hit1.Time - Hit2.Time)
    Time_Diff, Dist = HTimeDiff(Hit1, Hit2, Vsound)
    TMargin = 1e-3      # 1 ms, ! maybe find a better way to implement this & value !
    
    if Hit1.Hydrophone.Z >= Hit2.Hydrophone.Z + PanDepth or Hit1.Hydrophone.Z <= Hit2.Hydrophone.Z - PanDepth:
        return False
        
    if Dist <= TravelDist:
        Time_DiffMax = Time_Diff   
        return Dt <= Time_DiffMax + TMargin
    elif Dist <= 2*TravelDist:
        Time_DiffMax = (TravelDist-(Dist-TravelDist))/Vsound
        return Dt <= Time_DiffMax + TMargin
    
    return False

@numba.jit(nopython=True)
def HMatch(Hit1, Hit2, Amp1, Amp2, LocX1, LocX2, LocY1, LocY2, LocZ1, LocZ2, Vsound, TravelSearchDist, PanDepth):
    "Function which takes two Hits and outputs a True/False depending on whether they are a match."
    Dt = abs(Hit1 - Hit2)
    DtAmp = Hit1 - Hit2
    Time_Diff, Dist = HTimeDiff(LocX1, LocX2, LocY1, LocY2, LocZ1, LocZ2, Vsound)
    TMargin = 1e-3
    
    if LocZ1 >= LocZ2 + PanDepth or LocZ1 <= LocZ2 - PanDepth:
        return False
    
    AmpRatio = (Amp1 / Amp2) ** np.sign(DtAmp)    # np.sign(0) = 0 --> is this a problem? --> Check!!
    
    if AmpRatio > 1:
        return False
    
    if Dist <= TravelSearchDist:
        Time_DiffMax = Time_Diff   
        return Dt <= Time_DiffMax + TMargin
    elif Dist <= 2*TravelSearchDist:
        Time_DiffMax = (TravelSearchDist-(Dist-TravelSearchDist))/Vsound
        return Dt <= Time_DiffMax + TMargin
    
    return False

@numba.jit(nopython=True)
def HClique(Hits, LocX, LocY, LocZ, LocH, Amp, Type, ID, Nmin, Vsound, TravelSearchDist, PanDepth):
    Count = np.ones(len(Hits))   # Assume match with self
    # Look for Causal Hits & add to Counter #
    for i in range(len(Hits)-1):
        for j in range(i+1, len(Hits)):
            if HMatch(Hits[i], Hits[j], Amp[i], Amp[j], LocX[i], LocX[j], LocY[i], LocY[j], LocZ[i], LocZ[j], Vsound, TravelSearchDist, PanDepth):
                Count[i] += 1
                Count[j] += 1
                
    # Now run Clique algorithm to remove hits with least amount of correlated hits
    
    # Structure infinitely running loop, 
    p = 1
    while p>0:
        j = 0
        # M = 0
        n = len(Hits)
        for i in range(n):
            if Count[i] < Count[j]:
                j = i
            # if Count[i] >= Nmin:
            #     M += 1
            
        if Count[j] == n:     # number of associated hits is equal to the number of (remaining) hits
            return Hits, Count, LocX, LocY, LocZ, LocH, Amp, Type, ID
    
       # if M < Nmin:         # maximal number of associated hits is less than the specified minimum
        #    return Hits, Count, LocX, LocY, LocZ, LocH
    
    # Swap selected Hit to end
        Hits[j], Hits[n-1] = Hits[n-1], Hits[j]
        Count[j], Count[n-1] = Count[n-1], Count[j]
        LocX[j], LocX[n-1] = LocX[n-1], LocX[j]
        LocY[j], LocY[n-1] = LocY[n-1], LocY[j]
        LocZ[j], LocZ[n-1] = LocZ[n-1], LocZ[j]
        LocH[j], LocH[n-1] = LocH[n-1], LocH[j]
        # LocHID[j], LocHID[n-1] = LocHID[n-1], LocHID[j]
        Amp[j], Amp[n-1] = Amp[n-1], Amp[j]
        Type[j], Type[n-1] = Type[n-1], Type[j]
        ID[j], ID[n-1] = ID[n-1], ID[j]
  
    # Decrease number of associated hits for each associated hits
        for i in range(n-1):
            if HMatch(Hits[i], Hits[n-1], Amp[i], Amp[n-1], LocX[i], LocX[n-1], LocY[i], LocY[n-1], LocZ[i], LocZ[n-1], Vsound, TravelSearchDist, PanDepth):
                Count[i] -=1
                Count[n-1] -=1
                
            if Count[n-1] == 1:
                Hits = np.delete(Hits,n-1)
                # Hits = np.delete(Hits, n-1)
                Count = np.delete(Count, n-1)    # This is not really needed!
                break

@numba.jit(nopython=True)
def HEvent(Hits, LocX, LocY, LocZ, LocH, Amp, Type, ID, Nmin, PanDepth, Vsound, Max_Dist_Match, TravelSearchDist, pan1, Buffer, BufferX, BufferY, BufferZ, BufferH, BufferA, BufferT, BufferID):
    # This function checks whether a hit has enough correlated hits within its pancake,
    # if this is the case, the Clique algorithm is employed, then if enough correlated
    # hits remain an event is created in the Event_Log with these hits.
    Event_Write = False
    for pan2 in range(pan1+1, len(Hits)):
        Dist = HTimeDiff(LocX[pan1], LocX[pan2], LocY[pan1], LocY[pan2], LocZ[pan1], LocZ[pan2], Vsound)[1]
        if Dist <= Max_Dist_Match:
            if HMatch(Hits[pan1], Hits[pan2], Amp[pan1], Amp[pan2], LocX[pan1], LocX[pan2], LocY[pan1], LocY[pan2], LocZ[pan1], LocZ[pan2], Vsound, TravelSearchDist, PanDepth):
                Buffer = np.append(Buffer, Hits[pan2])
                BufferX = np.append(BufferX, LocX[pan2])
                BufferY = np.append(BufferY, LocY[pan2])
                BufferZ = np.append(BufferZ, LocZ[pan2])
                BufferH = np.append(BufferH, LocH[pan2])
                # BufferIDLoc = np.append(BufferIDLoc, LocHID[pan2])
                BufferA = np.append(BufferA, Amp[pan2])
                BufferT = np.append(BufferT, Type[pan2])
                BufferID = np.append(BufferID, ID[pan2])

    Len_Buffer_PreClique = len(Buffer)-1
    if len(Buffer) >= Nmin+1:
        Buffer = np.delete(Buffer,1)
        BufferX = np.delete(BufferX,1)
        BufferY = np.delete(BufferY,1)
        BufferZ = np.delete(BufferZ,1)
        BufferH = np.delete(BufferH,1)
        # BufferIDLoc = np.delete(BufferIDLoc,1)
        BufferA = np.delete(BufferA,1)
        BufferT = np.delete(BufferT,1)
        BufferID = np.delete(BufferID,1)
        
        Buffer, BufferC, BufferX, BufferY, BufferZ, BufferH, BufferA, BufferT, BufferID = HClique(Buffer, BufferX, BufferY, BufferZ, BufferH, BufferA, BufferT, BufferID, Nmin, Vsound, TravelSearchDist, PanDepth)
        if len(Buffer) >= Nmin:
            Event_Write = True
    
    #print(Event_Write)

                
    return Buffer, BufferX, BufferY, BufferZ, BufferH, BufferA, BufferT, BufferID, Event_Write, Len_Buffer_PreClique


def HPreNumba(Hits):
    HitTimes = []
    LocX = []
    LocY = []
    LocZ = []
    Hydrophone = []
    Amp = []
    Type = []
    ID = []
    for iget in range(len(Hits)):
        HitTimes.append(Hits[iget].Time)
        LocX.append(Hits[iget].Hydrophone.X)
        LocY.append(Hits[iget].Hydrophone.Y)
        LocZ.append(Hits[iget].Hydrophone.Z)
        Hydrophone.append(Hits[iget].Hydrophone.ID)
        Amp.append(Hits[iget].Amplitude)
        Type.append(Hits[iget].Type)
        ID.append(Hits[iget].ID)
        
    HitTimes = np.asarray(HitTimes)
    LocX = np.asarray(LocX).astype(np.float64)    # Needed because of Sympy rotations!
    LocY = np.asarray(LocY).astype(np.float64)    # Needed because of Sympy rotations!
    LocZ = np.asarray(LocZ).astype(np.float64)    # Needed because of Sympy rotations!
    Hydrophone = np.asarray(Hydrophone)
    Amp = np.asarray(Amp)
    Type = np.asarray(Type)
    ID = np.asarray(ID)
    
    return HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, ID

def HNumbaEvent(Event_Log, Hits, Hydrophones_Storage, HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, ID, Nmin, PanSearchDepth, Vsound, Max_Dist_Match, TravelSearchDist, Azimuth, Zenith):
    Len_Buffer = []
    Len_Buffer_PreClique_Out = []
    for inumba in range(len(Hits)-1):
        Buffer = np.asarray([HitTimes[inumba],0])
        BufferX = np.asarray([LocX[inumba],0])
        BufferY = np.asarray([LocY[inumba],0])
        BufferZ = np.asarray([LocZ[inumba],0])
        BufferH = np.asarray([Hydrophone[inumba],0])
        # BufferIDLoc = np.asarray([Hydrophone[inumba],0])
        BufferA = np.asarray([Amp[inumba],0])
        BufferT = np.asarray([Type[inumba],0])
        BufferID = np.asarray([ID[inumba],0])

        #print(f"HitTimes = {HitTimes}")
        #print(f"LocX = {LocX}")
        #print(f"LocY = {LocY}")
        #print(f"LocZ = {LocZ}")
        #print(f"Hydrophone = {Hydrophone}")
        #print(f"Amp = {Amp}")
        #print(f"Type = {Type}")
        #print(f"ID = {ID}")
        #print(f"Nmin = {Nmin}")
        #print(f"PanSearchDepth = {PanSearchDepth}")
        #print(f"Vsound = {Vsound}")
        #print(f"Max_Dist_Match = {Max_Dist_Match}")
        #print(f"TravelSearchDist = {TravelSearchDist}")
        #print(f"inumba = {inumba}")
        #print(f"Buffer = {Buffer}")
        #print(f"BufferX = {BufferX}")
        #print(f"BufferY = {BufferY}")
        #print(f"BufferZ = {BufferZ}")
        #print(f"BufferH = {BufferH}")
        #print(f"BufferA = {BufferA}")
        #print(f"BufferT = {BufferT}")
        #print(f"BufferID = {BufferID}")


        Buffer, BufferX, BufferY, BufferZ, BufferH, BufferA, BufferT, BufferID, Event_Write, Len_Buffer_PreClique = HEvent(HitTimes, LocX, LocY, LocZ, Hydrophone, Amp, Type, ID, Nmin, PanSearchDepth, Vsound, Max_Dist_Match, TravelSearchDist, inumba, Buffer, BufferX, BufferY, BufferZ, BufferH, BufferA, BufferT, BufferID)
        Len_Buffer.append(len(Buffer))
        Len_Buffer_PreClique_Out.append(Len_Buffer_PreClique)
        AppendLocs = []
        if Event_Write == True:
            "Write to Event"
            HitsEv = []
            for iEvent in range(len(Buffer)):
                # HitsEv.append(HClasses.Hit(HClasses.Hydrophone(BufferH[iEvent], Hydrophones[BufferH[iEvent]-1].IDLoc, BufferX[iEvent], BufferY[iEvent], BufferZ[iEvent]), Buffer[iEvent], BufferA[iEvent], BufferT[iEvent], BufferID[iEvent]))
                HitsEv.append(HClasses.Hit(Hydrophones_Storage[BufferH[iEvent]-1], Buffer[iEvent], BufferA[iEvent], BufferT[iEvent], BufferID[iEvent]))
            Event_Log.append(HClasses.Event(HitsEv, Azimuth, Zenith, int(0)))
            AppendLocs.append(len(Event_Log)-1)

    return Event_Log, Len_Buffer, Len_Buffer_PreClique_Out


def main():
    pass
    
if __name__ == "__main__":
    main()