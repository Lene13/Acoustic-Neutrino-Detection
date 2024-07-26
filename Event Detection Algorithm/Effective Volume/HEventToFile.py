# -*- coding: utf-8 -*-
"""
Created on Wed May 24 11:06:04 2023

@author: oerskqpv
"""

"This Function provides the tools to convert an Event to an output file, which can, for example, be used for Reconstruction."

import sys
import numpy as np


def HEventToFile(Name, Event_Log, Source):
    "Convert Events and their contents to output files"
    
    if len(Event_Log) == 0:
        
        Names = Name + 'Event'
        
        f = open(Names + ".txt", "w")
        
        # Make Headers I guess? #
        f.write('# Event Output File #')
        f.write('\n')
        # Time of nu event, Location of nu event, Energy of Event, Theta of nu event, Phi of nu event, in here I guess?
        f.write('# Energy: ' + str(Source[0].Energy))
        f.write('\n')
        f.write('# Time: ' + str(Source[0].Time))
        f.write('\n')
        f.write('# X: ' + str(Source[0].X))
        f.write('\n')
        f.write('# Y: ' + str(Source[0].Y))
        f.write('\n')
        f.write('# Z: ' + str(Source[0].Z))
        f.write('\n')
        f.write('# Azimuth: ' + str(Source[0].Azimuth))
        f.write('\n')
        f.write('# Zenith: ' + str(Source[0].Zenith))
        f.write('\n')
        f.write('Amplitude Time X Y Z Type')
        f.write('\n')
        
        f.close()
        return
    
    for ievl in range(len(Event_Log)):
        # Think of good naming convention #
        Names = Name + 'Event' + str(ievl+1) 
        
        f = open(Names + ".txt", "w")
        
        # Make Headers I guess? #
        f.write('# Event Output File #')
        f.write('\n')
        # Time of nu event, Location of nu event, Energy of Event, Theta of nu event, Phi of nu event, in here I guess?
        f.write('# Energy: ' + str(Source[0].Energy))
        f.write('\n')
        f.write('# Time: ' + str(Source[0].Time))
        f.write('\n')
        f.write('# X: ' + str(Source[0].X))
        f.write('\n')
        f.write('# Y: ' + str(Source[0].Y))
        f.write('\n')
        f.write('# Z: ' + str(Source[0].Z))
        f.write('\n')
        f.write('# Azimuth: ' + str(Source[0].Azimuth))
        f.write('\n')
        f.write('# Zenith: ' + str(Source[0].Zenith))
        f.write('\n')
        f.write('Amplitude Time X Y Z Type')
        f.write('\n')
        
        # Read Event contents #
        for ihits in range(len(Event_Log[ievl].Hits)):
            # Need Amplitude, Time of hit, X, Y, Z of Hydrophone, Type (e.g. noise or nu).
            # Amplitude of Hit on Hydrophone
            f.write(str(Event_Log[ievl].Hits[ihits].Amplitude))
            f.write(' ')
            # Time of Hit on Hydrophone
            f.write(str(Event_Log[ievl].Hits[ihits].Time))
            f.write(' ')
            # X Location of Hydrophone
            f.write(str(Event_Log[ievl].Hits[ihits].Hydrophone.X))
            f.write(' ')
            # Y Location of Hydrophone
            f.write(str(Event_Log[ievl].Hits[ihits].Hydrophone.Y))
            f.write(' ')
            # Z Location of Hydrophone
            f.write(str(Event_Log[ievl].Hits[ihits].Hydrophone.Z))
            f.write(' ')
            # Type of Hit on Hydrophone
            f.write(str(Event_Log[ievl].Hits[ihits].Type))
            f.write(' ')
            # End Line, write next Hit on new Line #
            f.write('\n')
            
    f.close()  
