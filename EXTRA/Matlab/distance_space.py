# make sure you can run the octave script from within the python code
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors  

# define the range of rpos and zpos values you want to loop through
rpos_values = [i for i in range(100, 2001, 200)]
zpos_values = [i for i in range(1, 15, 2)]

#energy_values = [1e13, 1e14, 1e15, 1e16, 1e17, 1e18, 1e19, 1e20, 1e21, 1e22, 1e23, 1e24]
energy_values = [1e19, 1e20, 1e21]

# determine a common range for color scaling
#common_vmin = 1e0    # minimum value for color scaling
#common_vmax = 4e9    # maximum value for color scaling

# create a custom colormap normalization based on the common range
#norm = colors.Normalize(vmin=common_vmin, vmax=common_vmax)
#cmap = plt.get_cmap('turbo')

# create a custom colormap normalization based on the common range
#norm = colors.LogNorm(vmin=common_vmin, vmax=common_vmax)
#cmap = plt.get_cmap('turbo')

for i in range(len(energy_values)):
    Eo = energy_values[i]
    
    # initialize a list to store the results
    results = []

    output = "output.dat"

    # define a matrix with all the amplitudes in it
    amplitudes = np.zeros((len(zpos_values), len(rpos_values)))

    # keep track of which count of rpos and zpos you use
    track_r = 0
    track_z = 0

    # loop over rpos and zpos values
    for rpos in rpos_values:
        for zpos in zpos_values:
            octave_script_command = [
                "octave",
                "one_pulse.m",
                str(zpos),
                str(rpos),
                output,
                str(Eo)
            ]
        
            # run the octave script
            subprocess.run(octave_script_command)
        
            # capture the results from the Octave script
            result = subprocess.run(octave_script_command, stdout=subprocess.PIPE, text=True)
        
            # split the stdout into lines and parse the data as needed
            output_lines = result.stdout.strip().split('\n')
            # make sure that the z=... and r=... are not printed as they are unnecessary
            output_lines_1 = output_lines[3:]
        
            # make floats of the values
            data = [float(line) for line in output_lines_1]
        
            # append the data to the results matrix
            results.append(data)
        
            # find the highest value for p to get out the amplitude of the pulse
            largest = max(data)
        
            # save the biggest amplitude to the matrix
            amplitudes[track_z, track_r] = largest
        
            # switch to the next point
            track_z = track_z + 1
        
        # switch to the next point
        track_r = track_r + 1

        # reset the z tracker so that you will move to the next row
        track_z = 0
    

    plt.figure(figsize=(10, 6))
    # create a colored grid (heatmap)
    plt.imshow(amplitudes, cmap='turbo', interpolation='nearest')
    cbar = plt.colorbar()
    cbar.set_label('mPa')

    plt.title('Amplitude for Different rpos and zpos Values')
    plt.xlabel('rpos')
    plt.ylabel('zpos')

    # set custom tick positions and labels
    plt.xticks(np.arange(len(rpos_values)), rpos_values)
    plt.yticks(np.arange(len(zpos_values)), zpos_values)

    plt.savefig(f'Heatmap_Amplitudes_{Eo}.png')
    plt.close()
