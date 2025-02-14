# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 12:43:14 2022

@author: oerskqpv
"""
import numpy as np
import math
import HClasses

def HDistSource(Hydrophones, Sources, Vsound, N):
    # This function calculates the distance and time to the source from a Hydrophone
    Dist = np.zeros(N)
    Time_Pulse = np.zeros(N)
    for i in range(N):
        Dist[i] = math.sqrt((Hydrophones[i].X - Sources[0].X)**2 + \
                            (Hydrophones[i].Y - Sources[0].Y)**2 + \
                            (Hydrophones[i].Z - Sources[0].Z)**2)
        Time_Pulse[i] =  Dist[i] / Vsound
        
    return Dist, Time_Pulse

def HPulseAppender(Hydrophones, Hydrophones_Storage, Hits, N, Sources, PanDepth, Vsound, TravelDist, Offset):
    # This function adds the time of the pulse to the Hits of the Hydrophone dict
    Appended_Phones = []
    Appended_Pulses = []
    Distance = []
    Time = []
    Distance, Time = HDistSource(Hydrophones, Sources, Vsound, N)
    Time = Time + Offset
    Amplitudes = 1 / Distance    # 1/r dependence, Fix exact amplitudes later on (For now this is fine :) )
    ID = 0
    for i in range(N):
        if Hydrophones[i].Z <= Sources[0].Z + PanDepth/2 and Hydrophones[i].Z >= Sources[0].Z - PanDepth/2 and Distance[i] <= TravelDist:
            ID += 1
            Hits.append(HClasses.Hit(Hydrophones[i], Time[i], Amplitudes[i], 14))
            Appended_Phones = np.append(Appended_Phones,i)
            Appended_Pulses = np.append(Appended_Pulses, Time[i])
    return Hits, Appended_Phones, Appended_Pulses

def main():
    pass
    
if __name__ == "__main__":
    main()
