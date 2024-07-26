# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 12:34:36 2022

@author: oerskqpv
"""
import numpy as np
import HClasses

def HHitAppender(Hitsrange, Noise_Rate, Hydrophones, Amprange, N):
    # This function adds random False Hits + Amplitudes to the Hydrophones dict
    Hits = []
    Mean_Noise = (Hitsrange[1] - Hitsrange[0]) * Noise_Rate
    ID = 1000
    for Hnum in range(N):
        Hits_Final = np.asarray([])
        Amplitudes_Final = np.asarray([])
        for itime in range(np.random.poisson( Mean_Noise )):
            Hits_Temp = []
            Amplitudes = []
            Hits_Temp = np.random.uniform(Hitsrange[0], Hitsrange[1])
            Amplitudes = np.random.uniform(Amprange[0], Amprange[1])
            Hits_Final = np.append(Hits_Final, Hits_Temp)
            Amplitudes_Final = np.append(Amplitudes_Final, Amplitudes)
            
        Hits_Final = np.sort(Hits_Final)
        
        for iHits in range(len(Hits_Final)):
            ID += 1
            Hits.append(HClasses.Hit(Hydrophones[Hnum], Hits_Final[iHits], Amplitudes_Final[iHits], -1, ID))
        
    return Hits

# def HHitAppender(Hitsrange, TotalHits, Hydrophones, Amprange, N):
#     # This function adds random False Hits + Amplitudes to the Hydrophones dict
#     Hits = []
#     for Hnum in range(N):
#         Hits_Final = np.asarray([])
#         Amplitudes_Final = np.asarray([])
#         for itime in range(Hitsrange[1]):
#             Hits_Temp = []
#             Amplitudes = []
#             Hits_Temp = np.sort(np.random.uniform(itime, itime + 1, int(TotalHits/Hitsrange[1])))
#             Amplitudes = np.random.uniform(Amprange[0], Amprange[1], int(TotalHits/Hitsrange[1]))
#             Hits_Final = np.append(Hits_Final, Hits_Temp)
#             Amplitudes_Final = np.append(Amplitudes_Final, Amplitudes)
#         for iHits in range(len(Hits_Final)):
#             Hits.append(HClasses.Hit(Hydrophones[Hnum], Hits_Final[iHits], Amplitudes_Final[iHits], -1))
        
#     return Hits

def main():
    pass
    
if __name__ == "__main__":
    main()
