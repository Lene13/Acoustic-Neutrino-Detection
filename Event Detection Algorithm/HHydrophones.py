import numpy as np
import HClasses
import math
import matplotlib.pyplot as plt

def HLocationAlg(xrange, yrange, zrange, Z_Spacing, Cluster_Size, LocID, Nx, Ny, Nz, N, D):
    # This function creates the Hydrophone locations

    # random configuration for the detector          
    if LocID == 0:# and Cluster_Size == 0:   # !! Is the == 0 necessary? !! 
        N = Nx * Ny * Nz
        Locs = np.zeros([N,D])
        Locs[:,0] = np.random.randint(xrange[0],xrange[1],N)   # X Locations
        Locs[:,1] = np.random.randint(yrange[0],yrange[1],N)   # np.zeros(N)   # Y Locations
        Locs[:,2] = np.random.randint(zrange[0],zrange[1],N)   # Z Locations

        return Locs, N

    # random configuration in x and y but randomized z value     
    if LocID == 1:
        Locs_Initx = np.random.randint(xrange[0], xrange[1], Nx*Ny)
        Locs_Inity = np.random.randint(yrange[0], yrange[1], Ny*Nx)
        Locs_Initz = np.linspace(zrange[0], zrange[1], Nz)
        Fill_Count = 0
        for i in range(Nx*Ny):
                
            for k in range(Nz):
                    
                for l in range(Cluster_Size):
                    Locs[Fill_Count ,0] = Locs_Initx[i]
                    Locs[Fill_Count ,1] = Locs_Inity[i]
                    Locs[Fill_Count ,2] = Locs_Initz[k] + l * Z_Spacing
                    Fill_Count += 1

        return Locs, N
    
    # square detector
    Locs = np.zeros([N,D])
    if LocID == 2:
        Locs_Initx = np.linspace(xrange[0], xrange[1], Nx)
        Locs_Inity = np.linspace(yrange[0], yrange[1], Ny)
        Locs_Initz = np.linspace(zrange[0], zrange[1], Nz)
        Fill_Count = 0
        for i in range(Nx):
            
            for j in range(Ny):
                
                for k in range(Nz):
                    
                    for l in range(Cluster_Size):
                        Locs[Fill_Count, 0] = Locs_Initx[i]
                        Locs[Fill_Count, 1] = Locs_Inity[j]
                        Locs[Fill_Count, 2] = Locs_Initz[k] + l * Z_Spacing
                        Fill_Count += 1
                        
        return Locs, N
    
    if LocID == 3:
        # Define the distance between the two layers in z
        Z_Inititally = np.linspace(zrange[0], zrange[1], Nz)
        Z_Layers = Z_Inititally[1] - Z_Inititally[0]

        # Initialize an array to store hydrophone locations
        Locs = np.empty((0, 3), float)
        Fill_Count = 0
        Number_of_Slots = 0

        for k in range(Nz): 
            for l in range(Cluster_Size):
                z = zrange[0] + k * Z_Layers + l * Z_Spacing
                diagonal_hydrophones = 10
                hexagonal_layers = 6
                buffer = 0

                for n in range(hexagonal_layers):
                    x = n * (625/hexagonal_layers) * 2 

                    for i in range(diagonal_hydrophones):
                        
                        y = yrange[0] + n * buffer + i * ((((2 * yrange[1] * 1.25) - (2 * n * buffer)) / (diagonal_hydrophones - 1)))
                        
                        if i==1 and x==0:
                            save = y - yrange[0]
                        
                        row = np.array([x, y, z]).reshape(1, -1)  
                        Locs = np.vstack((Locs, row))
                        Number_of_Slots += 1

                        if Fill_Count != 0:
                            row = np.array([-x, y, z]).reshape(1, -1)  
                            Locs = np.vstack((Locs, row))
                            Number_of_Slots += 1

                        Fill_Count += 1
                    
                    buffer = (1/2) * save
                    
                    if diagonal_hydrophones >= 5: 
                        diagonal_hydrophones -= 1

        Locs[:,1] = Locs[:,1] - 250 

        return Locs, Number_of_Slots


    # cylindrical shaped detector
    if LocID ==4:
        # Define the distance between two hydrophones in z in a cluster
        Z_Inititally = np.linspace(zrange[0], zrange[1], Nz)
        Z_Layers = Z_Inititally[1] - Z_Inititally[0]

        # Define the number of circles in the detector
        number_of_circles = 7
        
        # Initialize the array containing the hydrophone locations wit the hydrophone at the origin
        Locs = np.zeros([1, 3])

        # Keep track of the number of hydrophones you have created
        N = 0 

        for k in range(Nz):
            for l in range(Cluster_Size):
                z = zrange[0] + k * Z_Layers + l * Z_Spacing

                for n in range(0, number_of_circles + 1):
                    radius = ((yrange[1]) / number_of_circles) * n
                    # Define the number of hydrophones in each layer
                    num_hydrophones = 2 * np.pi * radius / (54 * np.pi)
                    num_hydrophones_round = round(num_hydrophones)
                    
                    if num_hydrophones_round == 0:
                        num_hydrophones_round == 1

                    for i in range(num_hydrophones_round):
                        angle = 2 * math.pi * i / num_hydrophones_round
                        x = radius * math.cos(angle)
                        y = radius * math.sin(angle)
                        
                        row = np.array([x, y, z]).reshape(1, -1)  
                        Locs = np.vstack((Locs, row))
                        N += 1

        return Locs, N
    
def HHydrophoneCreator(Locs, N):
    # This function creates a dict entry for each Hydrophone with name, location, hits, amplitude
    Hydrophones = []
    for Hnum in range(N):
        ID = Hnum+1
        Name = "X" + str(Locs[Hnum,0]) + "Y" + str(Locs[Hnum,1]) + "Z" + str(Locs[Hnum,2])
        Hydrophones.append(HClasses.Hydrophone(ID,Name, Locs[Hnum,0], Locs[Hnum,1], Locs[Hnum,2]))
    
    return Hydrophones


def main():
    pass
    
if __name__ == "__main__":
    main()