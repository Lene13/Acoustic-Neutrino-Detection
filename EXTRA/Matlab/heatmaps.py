# make sure you can run the octave script from within the python code
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors  

# define the range of rpos and zpos values you want to loop through
rpos_values = [i for i in range(0, 1000, 400)]
zpos = 7

#energy_values = [1e13, 1e14, 1e15, 1e16, 1e17, 1e18, 1e19, 1e20, 1e21, 1e22, 1e23, 1e24]
energy_values = [1e21]



for i in range(len(energy_values)):
    Eo = energy_values[i]
    
    # initialize a list to store the results
    results = []
    
    output = "output.dat"
    
    # keep track of which count of rpos and zpos you use
    track_r = 0
    track_z = 0
    
    # loop over rpos and zpos values
    for rpos in rpos_values:
        octave_script_command = [
            "octave",
            "one_pulse.m",
            str(zpos),
            str(rpos),
            output]
        
        # run the octave script
        subprocess.run(octave_script_command)
        
        # capture the results from the Octave script
        result = subprocess.run(octave_script_command, stdout=subprocess.PIPE, text=True)
        
        # split the stdout into lines and parse the data as needed
        output_lines = result.stdout.strip().split('\n')
        
        # make sure that the z=... and r=... are not printed as they are unnecessary
        output_lines_1 = output_lines[2:]
        
        # make floats of the values
        data = [float(line) for line in output_lines_1]
        
        # create a time array based on the length of your data
        time = np.arange(len(data))
            
        # perform the FFT on the data
        fft_result = np.fft.fft(data)
            
        # calculate the corresponding frequency values in Hz
        frequency = np.fft.fftfreq(len(data))

        frequency_reshape = frequency.reshape(2048)
        result_reshape = np.abs(fft_result).reshape(2048)

        # plot the magnitude spectrum
        plt.figure(figsize=(10, 6))
        plt.plot(frequency_reshape, result_reshape, color='red')
        plt.title('Frequency Spectrum')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.xlim(0, 0.2)
        plt.gca().set_ylim(bottom=0)
        
        plt.savefig(f'Frequency Spectrum {Eo} at {rpos}m.png')

