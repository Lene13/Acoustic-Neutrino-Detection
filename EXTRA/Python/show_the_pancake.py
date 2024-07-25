pip uninstall vtk

pip install vtk==9.2

import math
import scipy
from math import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import rayleigh
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from mayavi import mlab
from tvtk.tools import visual


# Find the power of 2 that is greater than the number you give it
def nextPowerOf2(i):
    n = 1
    while n < i: n *= 2
    return n

def alpha_Thorp(f):
    # EJB: shameless copy from MAA
    # absorption formula from Thorp
    # f = frequency(kHz)
    # output in dB/km 

    # Boron relaxation frequency
    F1 = 1.0

    # Magnesium relaxation frequency
    F2 = sqrt(4100.)

    A1 = 0.1/0.9144*((f**2)/(f**2 + F1**2))
    A2 = (40/0.9144)*((f**2)/(f**2 + F2**2))
    A3 = 2.75e-4* f**2
    A3 = A3/0.9144

    return A1+A2+A3

# The following function provides a comprehensive assessment of high-frequency wind-induced noise levels in underwater environments
def NL_wind_highfreq(freqs, v_wind, depth):
    # APL from Ainslie (2010)
    dT = 1                                                                               # Time difference parameter, typically set to 1    
    deltaT = 0.26*(dT-1)**2                                                              # Temporal coherence parameter for wind-induced noise
    
    # Represents the contribution of wind speed to the noise spectral density
    # Describes how wind speed affects noise level at different frequencies
    Kwind = 10**(4.12)*v_wind**(2.24) / ((freqs/1000)**(1.59)*10**(0.1*deltaT))          # Wind-induced noise spectral density coefficient

    # from Ward et al. 2011                                              
    beta = alpha_Thorp(freqs/1000)/4343                                                  # Coefficient related to Thorp's attenuation coefficient
    
    # Accounts for the attenuation of noise with depth underwater
    # Reflects the decrease in noise level with increasing water depth
    depth_correction = -alpha_Thorp(freqs/1000) * (depth/1000) - 10*np.log10(1+beta*depth/2)    # Correction term accounting for water depth
    
    
    # Represents the combined effect of wind-induced noise and depth-related 
    # attenuation on the noise level at different frequencies underwater.
    return 10*np.log10(Kwind) + depth_correction                                            # spectral density [dB re 1 muPa^2/Hz]

def NL_wind_highfreq(freqs, v_wind, depth):
    return 1


def correct_offaxis_neutrino(theta, freq):
    d = 2
    wl = 1500./freq
    I_0 = 1.
    if theta == 0:
        return I_0
    else:
        return I_0 * pow(sin((pi*d/wl)*sin(theta))/((pi*d/wl)*sin(theta)), 2)

# Neutrino propegation
def get_neutrino_sourcewaveform():
    """
    Generates a bipolar pulse with appropriate amp and period. 
    The function runs as bipolar_pulse(amp, pulse_width) where amp is in uPa, pulse_width is in seconds. 
    """
    
    fs = 500e3                          # sampling rate
    t = np.arange(0, 100e-5, 1/fs)      # time range to generate the pulse over 
    t = t-np.mean(t)
    p_norm = 0.06                       # Pa
    Pa2uPa = 1e6                        # conversion factor to micropascal
    amp = p_norm*Pa2uPa                 # Pa
    pulse_width = 1e-4                  # seconds
    
    y = -1 * amp * (t / (0.1*pulse_width)) * np.exp(-((t/(0.1*pulse_width))**2 - 1) / 2)
    
    # SPL (Sound Pressure Level): SPL is a measure of the sound pressure level in decibels (dB) relative to the reference 
    # sound pressure of 1 microPascal (µPa). It is calculated as the logarithm of the ratio of the root mean square (RMS) 
    # pressure of the waveform to the reference pressure, multiplied by 20. In the code, SPL is calculated using the formula 
    # (y represents the waveform):
    SPL = 20 * log10(sqrt(np.mean(y**2)))
    
    # E_t represents the energy level of the waveform and is also expressed in decibels (dB). It is calculated as the 
    # logarithm of the total energy of the waveform over its duration, normalized to one second, and then multiplied by 10. 
    # In the code, E_t is calculated using the formula:
    E_t = 10 * log10(np.sum(y**2)/fs)

    print(f'SPL = {SPL} dB re 1uPa and SEL = {E_t} dB re 1uPa')
    
    # returns the time array, the waveform, and the sampling frequency
    return t, y, fs

t, y, fs = get_neutrino_sourcewaveform()

plt.plot(t, y)
plt.show()

def get_neutrino_sourcewaveform_second():
    """
    Generates a bipolar pulse with appropriate amp and period. 
    The function runs as bipolar_pulse(amp, pulse_width) where amp is in uPa, pulse_width is in seconds. 
    """
        
    fs = 500e3                          # sampling rate
    t = np.arange(0, 60e-6, 1/fs)       # time range to generate the pulse over
    
    sigma = 9e-6
    # tau = 100
    
    # Calculate the probability density function (PDF) using the Rayleigh distribution
    p_t_neg = rayleigh.pdf(t, scale=sigma)
    p_t_pos = rayleigh.pdf(t, scale=sigma)
    
    p_norm = 0.06                       # Pa
    Pa2uPa = 1e6                        # conversion factor to micropascal

    # Calculate the source level (p_t)
    p_t = Pa2uPa * p_norm / np.max(p_t_neg) * (np.flip(p_t_neg) - p_t_pos) * (1000. / 1)

    SPL = 20 * np.log10(np.sqrt(np.mean(np.power(p_t, 2))))
    E_t = 10 * np.log10(np.sum(np.power(p_t, 2)) / fs)

    print(f'SPL = {SPL} dB re 1uPa and SEL = {E_t} dB re 1uPa')
    
    # Make a time array in which the wave can be plotted around the 0 point
    ttt = np.concatenate((-np.flipud(t), t[1:])) + t[-1]
    
    return ttt, p_t, fs, t

ttt, p_t, fs, t = get_neutrino_sourcewaveform_second()

plt.plot(t, p_t)
plt.show()

def propagate_neutrino():
    """
    Generates a bipolar pulse with appropriate amp and period. 
    The function runs as bipolar_pulse(amp, pulse_width) where amp is in uPa, pulse_width is in seconds. 
    """


    ttt, p_t, fs = get_neutrino_sourcewaveform()
    
    # The code calculates the next power of 2 for the length of the waveform 
    nfft = nextPowerOf2(len(ttt))
    
    # Pad the waveform with zeros for FFT calculations
    p_t_e = np.pad(p_t, (0, nfft - len(p_t)), mode='constant')

    
    # Apply fft to the padded waveform to obtain the frequency domain representation
    X_f = np.fft.fft(p_t_e)
    
    # Calculate frequency resolution
    df = fs / nfft 
    
    # Generate frequency array corresponding to the FFT output
    freqs = np.arange(0, fs/2, df)

    # Slice the FFT output to keep only positive frequencies
    X_f = X_f[:len(freqs)]

    # Calculate the normalized power spectral density
    X_f2 = abs(X_f)**2 * (2 / (nfft * fs))
   
    # The calculated ESL represents the average energy level of the waveform over its entire duration
    ESL = 10*log10(sum(p_t**2)/fs)   # in dB broadband energy source level
    
    # The calculated EPSDL represents the energy level distribution across different frequency components of the signal
    EPSDL = 10*np.log10(X_f2)        # in dB source energy spectral density level
    
    plt.plot(EPSDL)
    plt.title('EPSDL')
    plt.ylabel('PSD')
    plt.show()
    plt.clf()

    # Wind speed
    v_wind = 9                       # m/s 0 = SS0; 2 = SS2; 3.5 = SS3; 6-9 = SS 4; 
    depth = 1000                     # receiver depth

    NLwind = NL_wind_highfreq(freqs, v_wind, depth) + 10*log10(1e-4)
 
    range_neutrino = 1000            # m

    
    # Neutrinos: average over frequencies
    thetas = np.linspace(-90, 90, 360)
    f_arr = np.linspace(5000, 50000, 100)
    I_theta = np.zeros(len(thetas))

    for freq in f_arr:
        I_theta += np.asarray(list(map(correct_offaxis_neutrino, np.radians(thetas), [freq]*len(thetas))))

    I_theta_mean = np.asarray(I_theta) / len(f_arr)
    SL_thetas = np.log10(I_theta_mean)
    SL_thetas -= np.max(SL_thetas)

    xxx= np.linspace(0, 10000, 100)
    yyy= np.linspace(0, 10000, 100)
    zzz= np.linspace(0, 2000, 10)
    
    x_arr, y_arr, z_arr = np.meshgrid(xxx,yyy,zzz)
    
    z_src = 800
    x_src = 2000
    y_src = 5000

    # neutrino ####
    r_arr = np.sqrt((x_arr - x_src)**2 + (y_arr - y_src)**2 + (z_arr - z_src)**2)
    angle_r = np.arctan2(z_src-z_arr, np.sqrt((x_arr - x_src)**2 + (y_arr - y_src)**2))

    #    SL_corr = interp1(theta, 10*np.log10(I_theta_mean), angle_r)
    set_interp = interp1d(thetas, 10*np.log10(I_theta_mean), kind='linear')
    SL_corr = set_interp(angle_r)
    
    print(SL_corr.shape)
    print(x_arr.shape)
    print(y_arr.shape)
    print(z_arr.shape)
    
    sel_rec = 10*log10(np.sum(10**((EPSDL)/10)*df)) + \
              SL_corr - \
              20*np.log10(r_arr) - \
              10*log10(np.mean(10**(alpha_Thorp(freqs/1000)/10)))*r_arr/1000

    fig = mlab.figure(figure='testje', size=(700, 700), bgcolor=(0.16, 0.28, 0.46))# bgcolor=(0, .3, 1.0))
    mlab.view(85, -17, 15, [3.5, -0.3, -0.8])

    mlab.contour3d(x_arr, y_arr, z_arr, SL_corr, contours=10)
    mlab.draw()

propagate_neutrino()
