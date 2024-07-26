# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:55:13 2022

@author: oerskqpv
"""
import numpy as np
import copy
import sympy as sp
import math

def HHitSorter(Hits):
    Temp_Hits = np.zeros(len(Hits))
    for i in range(len(Hits)):
        Temp_Hits[i] = Hits[i].Time
        
    TempHitsInd = Temp_Hits.argsort()
    Temp_Hits = Temp_Hits[TempHitsInd[::1]]
    Hits = [Hits[i] for i in TempHitsInd]
    
    return Hits, Temp_Hits

def scos(x): 
    return sp.N(sp.cos(x))

def ssin(x): 
    return sp.N(sp.sin(x))

def HRotateAzimuth(Hydrophones, Azimuth):
    # This function rotates the Azimuth angle, Rotation around the z-axis
    for irx in range(len(Hydrophones)):
        Y1 = Hydrophones[irx].Y * scos(Azimuth)
        Y2 = -Hydrophones[irx].X * ssin(Azimuth)
        LocYY = Y1 + Y2    # Check These Formulas
    
        X1 = Hydrophones[irx].Y * ssin(Azimuth)
        X2 = Hydrophones[irx].X * scos(Azimuth)
        LocXX = X1 + X2
        
        Hydrophones[irx].Y = LocYY
        Hydrophones[irx].X = LocXX
    
    return Hydrophones

def HRotateZenith(Hydrophones, Zenith):
    # This function rotates the Zenith angle, Rotation around the x-axis
    for iry in range(len(Hydrophones)):
        Y1 = Hydrophones[iry].Y * scos(Zenith)
        Y2 = Hydrophones[iry].Z * ssin(Zenith)
        LocYY = Y1 + Y2
    
        Z1 = -Hydrophones[iry].Y * ssin(Zenith)
        Z2 = Hydrophones[iry].Z * scos(Zenith)
        LocZZ = Z1 + Z2
        
        Hydrophones[iry].Y = LocYY
        Hydrophones[iry].Z = LocZZ
    
    return Hydrophones

def HRotateAll(Hydrophones, Azimuth, Zenith): # New 20-07
    # Rotations
    Zenith = math.pi - Zenith
    Azimuth = - Azimuth
    for ir in range(len(Hydrophones)):
        X1 = scos(Zenith) * scos(Azimuth) * Hydrophones[ir].X - scos(Zenith) * ssin(Azimuth) * Hydrophones[ir].Y + ssin(Zenith) * Hydrophones[ir].Z
        Y1 = ssin(Azimuth) * Hydrophones[ir].X + scos(Azimuth) * Hydrophones[ir].Y
        Z1 = -ssin(Zenith) * scos(Azimuth) * Hydrophones[ir].X + ssin(Zenith) * ssin(Azimuth) * Hydrophones[ir].Y + scos(Zenith) * Hydrophones[ir].Z

        Hydrophones[ir].X = X1
        Hydrophones[ir].Y = Y1
        Hydrophones[ir].Z = Z1
        
    return Hydrophones

# Now we write a function that rotates the hits back to the original position
def HRotateAllBackHits(Hits, Azimuth, Zenith):
    # Rotate Back
    Zenith = math.pi - Zenith
    Azimuth = -Azimuth
    # Inverse Rotations
    for ir in range(len(Hits)):
        X1 = scos(Zenith) * scos(Azimuth) * Hits[ir].Hydrophone.X + ssin(Azimuth) * Hits[ir].Hydrophone.Y - ssin(Zenith) * scos(Azimuth)* Hits[ir].Hydrophone.Z
        Y1 = -scos(Zenith) * ssin(Azimuth) * Hits[ir].Hydrophone.X + scos(Azimuth) * Hits[ir].Hydrophone.Y + ssin(Zenith) * ssin(Azimuth) * Hits[ir].Hydrophone.Z
        Z1 = ssin(Zenith) * Hits[ir].Hydrophone.X + scos(Zenith) * Hits[ir].Hydrophone.Z

        Hits[ir].Hydrophone.X = X1
        Hits[ir].Hydrophone.Y = Y1
        Hits[ir].Hydrophone.Z = Z1
        
    return Hits



def HRotateAll1(Hydrophones, Azimuth, Zenith):  # Old
    # Rotations
    for ir in range(len(Hydrophones)):
        X1 = scos(Azimuth) * Hydrophones[ir].X - ssin(Azimuth) * Hydrophones[ir].Y
        Y1 = scos(Zenith) * ssin(Azimuth) * Hydrophones[ir].X + scos(Zenith) * scos(Azimuth) * Hydrophones[ir].Y - ssin(Zenith) * Hydrophones[ir].Z
        Z1 = ssin(Zenith) * ssin(Azimuth) * Hydrophones[ir].X + ssin(Zenith) * scos(Azimuth) * Hydrophones[ir].Y + scos(Zenith) * Hydrophones[ir].Z
        
        Hydrophones[ir].X = X1
        Hydrophones[ir].Y = Y1
        Hydrophones[ir].Z = Z1
        
    return Hydrophones



def HRotateAllBack(Hydrophones, Azimuth, Zenith):
    for ir in range(len(Hydrophones)):
        X1 = scos(-Azimuth) * Hydrophones[ir].X - ssin(-Azimuth) * scos(-Zenith) * Hydrophones[ir].Y + ssin(-Azimuth) * scos(-Zenith) * Hydrophones[ir].Z
        Y1 = ssin(-Azimuth) * Hydrophones[ir].X + scos(-Azimuth) * scos(-Zenith) * Hydrophones[ir].Y - scos(-Azimuth) * ssin(-Zenith) * Hydrophones[ir].Z
        Z1 = ssin(-Zenith) * Hydrophones[ir].Y + scos(-Zenith) * Hydrophones[ir].Z
        
        Hydrophones[ir].X = X1
        Hydrophones[ir].Y = Y1
        Hydrophones[ir].Z = Z1
        
    return Hydrophones

#def HRotateAllBackHits(Hits, Azimuth, Zenith):
    # Rotate Back
    #for ir in range(len(Hits)):
        #X1 = scos(-Azimuth) * Hits[ir].Hydrophone.X - ssin(-Azimuth) * scos(-Zenith) * Hits[ir].Hydrophone.Y + ssin(-Azimuth) * scos(-Zenith) * Hits[ir].Hydrophone.Z
        #Y1 = ssin(-Azimuth) * Hits[ir].Hydrophone.X + scos(-Azimuth) * scos(-Zenith) * Hits[ir].Hydrophone.Y - scos(-Azimuth) * ssin(-Zenith) * Hits[ir].Hydrophone.Z
        #Z1 = ssin(-Zenith) * Hits[ir].Hydrophone.Y + scos(-Zenith) * Hits[ir].Hydrophone.Z
        
        #Hits[ir].Hydrophone.X = X1
        #Hits[ir].Hydrophone.Y = Y1
        #Hits[ir].Hydrophone.Z = Z1
        
    #return Hits


def HRotateBackAzimuth(Hydrophones, Azimuth):
   # This function rotates the Azimuth angle in -Azimuth direction, Rotation around the z-axis
   for irx in range(len(Hydrophones)):
       Y1 = Hydrophones[irx].Y * scos(-Azimuth)
       Y2 = -Hydrophones[irx].X * ssin(-Azimuth)
       LocYY = Y1 + Y2    # Check These Formulas
   
       X1 = Hydrophones[irx].Y * ssin(-Azimuth)
       X2 = Hydrophones[irx].X * scos(-Azimuth)
       LocXX = X1 + X2
       
       Hydrophones[irx].Y = LocYY
       Hydrophones[irx].X = LocXX
   
   return Hydrophones

def HRotateBackZenith(Hydrophones, Zenith):
    # This function rotates the Zenith angle in -Zenith direction, Rotation around the x-axis
    for iry in range(len(Hydrophones)):
        Y1 = Hydrophones[iry].Y * scos(-Zenith)
        Y2 = Hydrophones[iry].Z * ssin(-Zenith)
        LocYY = Y1 + Y2
    
        Z1 = -Hydrophones[iry].Y * ssin(-Zenith)
        Z2 = Hydrophones[iry].Z * scos(-Zenith)
        LocZZ = Z1 + Z2
        
        Hydrophones[iry].Y = LocYY
        Hydrophones[iry].Z = LocZZ
    
    return Hydrophones

# definea function that can calculate the angle between the neutrino source and the hydrophone
def HCalculateAngles(neutrino_source_coords, neutrino_vertex_angles, hydrophone_coords):
    # Convert azimuth and zenith angles to radians
    azimuth_rad = np.radians(neutrino_vertex_angles[0])
    zenith_rad = np.radians(neutrino_vertex_angles[1])

    # Define unit vector in the direction of neutrino vertex
    vertex_direction = np.array([
        np.sin(zenith_rad) * np.cos(azimuth_rad),
        np.sin(zenith_rad) * np.sin(azimuth_rad),
        np.cos(zenith_rad)
    ])

    # Vector from neutrino source to other point
    source_to_point_vector = np.array(hydrophone_coords) - np.array(neutrino_source_coords)

    # Calculate the projection of source_to_point_vector onto the plane perpendicular to the vertex
    projection = source_to_point_vector - np.dot(source_to_point_vector, vertex_direction) * vertex_direction
    
    # Calculate the angle between source_to_point_vector and the plane perpendicular to the vertex
    angle_to_perpendicular_plane = np.arccos(np.dot(source_to_point_vector, projection) /
                                             (np.linalg.norm(source_to_point_vector) * np.linalg.norm(projection)))

    # Convert angle from radians to degrees
    angle_to_perpendicular_plane_deg = np.degrees(angle_to_perpendicular_plane)

    return angle_to_perpendicular_plane_deg


def main():
    pass
    
if __name__ == "__main__":
    main()
