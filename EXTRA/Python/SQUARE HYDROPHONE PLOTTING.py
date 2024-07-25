#plotting the hydrophones

xrange = [-1000,1000]                                                                       # XLoc range in meters      
yrange = [-1000,1000]                                                                       # YLoc range in meters
zrange = [-500,500] 
D = 3

LocID = 2

import numpy as np
N = 1690

Nx = 13
Ny = 13
Nz = 10 
Cluster_Size = 1
Z_Spacing = 10


# hexaconal shape
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
                        
print(f"The density of hydrophones is {Fill_Count / ((2 * xrange[1]/1000 )**2 * 2 * (zrange[1]/1000))} hydrophones per km^3.")
print(Fill_Count)

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# plot all the Locs in a 3D graph

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(Locs[:,0], Locs[:,1], Locs[:,2],color='blue')

plt.show()