# make sure you can run the octave script from within the python code
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors  

# define the range of rpos and zpos values you want to loop through
rpos_values = [i for i in range(100, 2001, 200)]
zpos = 7

energy_values = [1e16, 1e17, 1e18, 1e19, 1e20, 1e21]
#energy_values = [1e21]
distance = []


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
            output,
            str(Eo),
        ]
        
        distance.append(f'{rpos}m')
        
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
        
        # create a time array based on the length of your data
        time = np.arange(len(data))
            
        # perform the FFT on the data
        fft_result = np.fft.fft(data)
        
        # calculate the sampling rate based on your data
        # in the one_pulse.m file where the Monte Carlo takes place they have a sampling frequency of 1e6
        sampling_rate = 1e6
        
        # calculate the corresponding frequency values in Hz using the sampling rate
        frequency_Hz = np.fft.fftfreq(len(data), d=1.0/sampling_rate)
        
        frequency_reshape = frequency_Hz.reshape(2048)
        result_reshape = np.abs(fft_result).reshape(2048)
        
        
        results.append(result_reshape.tolist())
        
        track_r = track_r + 1
        
        
    colours = ['red', 'orange', 'yellow', 'lime', 'cyan', 'blue', 'magenta', 'pink', 'black', 'grey']
    plt.figure(figsize=(10, 6))
    
    frequency_kHz = [i/1000 for i in frequency_reshape]
    maximum = max(results)
    
    for i in range(len(results)):
        plt.plot(frequency_kHz, results[i], color=colours[i], label=distance[i])
    
    plt.title(f'Frequency Spectrum  Eo={Eo}')
    plt.xlabel('Frequency (kHz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, 250)
    plt.gca().set_ylim(bottom=0)
    plt.legend()
     
    plt.savefig(f'Frequency Spectrum {Eo}.png')


    result = []

