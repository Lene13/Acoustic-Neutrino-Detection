# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 10:44:16 2023

@author: oerskqpv
"""

import numpy as np
import sys
import os.path


def HDataWriter(Name, TotalHitsi, Nmini, Average_Events_Detected, output_dir, Correct_Percentage, NuCountCut):
    "This function writes data to a .txt file, at the moment only supports 3 data inputs"
   
    f = open(os.path.join(output_dir, Name + ".txt"), "w")
    
    for iwrite1 in range(len(TotalHitsi)):
        for iwrite2 in range(len(Nmini)):
            f.write(str(NuCountCut))
            f.write(' ')
            f.write(str(TotalHitsi[iwrite1]))
            f.write(' ')
            f.write(str(Nmini[iwrite2]))
            f.write(' ')
            f.write(str(Average_Events_Detected[iwrite1, iwrite2]))
            f.write(' ')
            f.write(str(round(Correct_Percentage[iwrite1, iwrite2], 3)))
            f.write('\n')


def HDataWriterAngle(NuPulse, Name, TotalHitsi, Nmini, output_dir, events_detected_average, Correct_Count_average, AzimuthVals, ZenithVals):
    "This function writes data to a .txt file, at the moment only supports 3 data inputs"
   
    f = open(os.path.join(output_dir, Name + ".txt"), "w")
    
    f.write(f'Nmin: {Nmini}\n')
    f.write(f'FHR: {TotalHitsi}\n')
    f.write(f'Nupulse: {NuPulse}\n')

    for iwrite1 in range(len(AzimuthVals)):
        for iwrite2 in range(len(ZenithVals)):
            f.write(str(AzimuthVals[iwrite1]))
            f.write(' ')
            f.write(str(ZenithVals[iwrite2]))
            f.write(' ')
            f.write(str(Correct_Count_average[iwrite1, iwrite2]))
            f.write(' ')
            f.write(str(events_detected_average[iwrite1, iwrite2]))
            f.write('\n')

def HDataWriterEventPlot(OutName, LocEff, Hits, Azimuth, Zenith, Source_X, Source_Y, Source_Z, Hydrophones):
    "This function writes data to a .txt file, at the moment only supports 3 data inputs"
   
    f = open(os.path.join(LocEff, OutName + ".txt"), "w")
    
    f.write(str(Azimuth[0]))
    f.write(' ')
    f.write(str(Zenith[0]))
    f.write(' ')
    f.write(str(Source_X))
    f.write(' ')
    f.write(str(Source_Y))
    f.write(' ')
    f.write(str(Source_Z))
    f.write('\n')

    for hit in Hits:
        f.write(str(hit.Hydrophone.X))
        f.write(' ')
        f.write(str(hit.Hydrophone.Y))
        f.write(' ')
        f.write(str(hit.Hydrophone.Z))
        f.write(' ')
        f.write(str(hit.Time)) 
        f.write(' ')
        f.write(str(hit.Type))
        f.write(' ')
        f.write(str(hit.Hydrophone.ID))
        f.write('\n')

    for Hydrophone in Hydrophones:
        f.write(str(Hydrophone.X))
        f.write(' ')
        f.write(str(Hydrophone.Y))
        f.write(' ')
        f.write(str(Hydrophone.Z))
        f.write(' ')
        f.write(str(Hydrophone.ID))
        f.write('\n')

def HDataWriterEventPlotClique(OutName, LocEff, Hits, Clique_Hits, Azimuth, Zenith, Source_X, Source_Y, Source_Z, Hydrophones):
    "This function writes data to a .txt file, at the moment only supports 3 data inputs"
   
    f = open(os.path.join(LocEff, OutName + ".txt"), "w")
    
    f.write(str(Azimuth[0]))
    f.write(' ')
    f.write(str(Zenith[0]))
    f.write(' ')
    f.write(str(Source_X))
    f.write(' ')
    f.write(str(Source_Y))
    f.write(' ')
    f.write(str(Source_Z))
    f.write('\n')

    for hit in Hits:
        f.write(str(hit.Hydrophone.X))
        f.write(' ')
        f.write(str(hit.Hydrophone.Y))
        f.write(' ')
        f.write(str(hit.Hydrophone.Z))
        f.write(' ')
        f.write(str(hit.Time)) 
        f.write(' ')
        f.write(str(hit.Type))
        f.write(' ')
        f.write(str(hit.Hydrophone.ID))
        f.write('\n')
    
    for hit in Clique_Hits:
        f.write(str(hit.Hydrophone.X))
        f.write(' ')
        f.write(str(hit.Hydrophone.Y))
        f.write(' ')
        f.write(str(hit.Hydrophone.Z))
        f.write(' ')
        f.write(str(hit.Time)) 
        f.write(' ')
        f.write(str(hit.Type))
        f.write(' ')
        f.write(str(hit.Hydrophone.ID))
        f.write(' ')
        f.write('clique')
        f.write('\n')

    for Hydrophone in Hydrophones:
        f.write(str(Hydrophone.X))
        f.write(' ')
        f.write(str(Hydrophone.Y))
        f.write(' ')
        f.write(str(Hydrophone.Z))
        f.write(' ')
        f.write(str(Hydrophone.ID))
        f.write('\n')

#def HDataWriter(Name, TotalHitsi, Nmini, Average_Events_Detected):
    "This function writes data to a .txt file, at the moment only supports 3 data inputs"
   
    #f = open(Name + ".txt", "w")
    
    #for iwrite1 in range(len(TotalHitsi)):
        #for iwrite2 in range(len(Nmini)):
            #f.write(str(TotalHitsi[iwrite1]))
            #f.write(' ')
            #f.write(str(Nmini[iwrite2]))
            #f.write(' ')
            #f.write(str(Average_Events_Detected[iwrite1, iwrite2]))
            #f.write('\n')
            
    #f.close()
    
def HDataReader(Name):
    "This function reads a .txt file and outputs the data in an array"
    
    f = open(Name + ".txt", "r")
    num_lines = sum(1 for line in f)
    # Code to identify elements per line goes here
    
    data_list = []
    data_array = np.zeros([num_lines,3])    # Fix Harcoded 3 here!
    with open(Name + '.txt') as f:
        k = 0
        for line in f:
            # print(line.strip())
            data_list = line.split(' ')
            for i in range(len(data_list)):
                data_array[k,i] = float(data_list[i])
            k += 1
    
    f.close()
    
    return data_array


def main():
    pass
    
if __name__ == "__main__":
    main()