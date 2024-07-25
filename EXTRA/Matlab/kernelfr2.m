# the Kernel function
function [p,pw,Exyz]=kernelfr2(points,Do,energy,atten,nr,fs,m,c)
		% UltraFast Acoustic Integral function
                     % inputs points [x,y,z] where z is oriented along the axis of the shower,
                     % units (m) size  n x 3 where n is typically about 10^6. Note the value of n is very
                     % distance dependent. At 100m c 10^8 points are needed to give an ultra-clean pulse.
                     % At 10km c 10^4 points are sufficient.

		     % Do: is the position of the observer [x0,y0,z0]

                     % energy: is total energy of the shower 10^energy GeV. i.e. if energy = 11
                     % then the total shower energy is 10^20 eV.

	             % atten; is a flag and is passed to attenfna.

                     % nr: rotational symmetry is exploited by rotating the shower axially. a
                     % value of 100 is typical. (default 1)

                     % fs: sampling frequency (default 1MHz)

                     % m: mean distance from observer to shower. Calculated if not supplied

		% OUTPUTS
                     % p the pulse (sampling rate 1MHz default) Note: zero time is at the mean shower
                     % transit time ignoring complex attenuation

		     % pw the FFT of the pulse (sampling rate 1MHz default)

		     % Exyz is a scaled version of the Velocity Potential

                %DEFINE CONSTANDS
                     % velocity of sound in water(c),thermal Expansivity (beta), Specific heat capacity (Cp)
  
beta=2.0e-4;      Cp=3.8e3;
if nargin <5 nr=1;    end
if nargin <6 fs=1e6;  end                                     % sampling frequency
if nargin <8 c =1500; end

% t_axis=(-512:511)'/fs;f_axis=[0:512 -511:-1]'/1024*fs;      % time and frequency axes
t_axis=(-1024:1023)'/fs;f_axis=[0:1023 -1024:-1]'/2028*fs;    % time and frequency axes

% differential in Frequency Domain. The d/dt of exp(iwt) is iw exp(iwt)
% a Blackman window is used to smooth the integral and is optional
diff_filt=i*2*pi*f_axis.*fftshift(blackman(2048));

% diff_filt=i*2*pi*f_axis.*fftshift(blackman(1024));
% create Velocity potential array
% Exyz=zeros(1024,1);
Exyz=zeros(2048,1);

%---------------------------------------------------------------------------------------------------------------

% determine number of points in the integral
nmc=size(points,1);

% if rotational symmetry is being used calculates the angles
th=linspace(0,2*pi,1+nr) ;th(end)=[];

% convert the observer position to a matrix of the same size as the number of points
Do=Do(ones(1,nmc),:);

%loop through the angles
for ang=th
    % rotate using matrix rotation 
    pointsr=points*[cos(ang) sin(ang) 0;-sin(ang) cos(ang) 0;0 0 1];
    % determine the distance to each point
    d=sqrt(sum((pointsr-Do).^2,2));
    % determine the mean distance if not provided
    if nargin<7
        m=sum(d)/nmc; 
    end
    % deterime the unscaled velocity potential. (Need to divide by distance)
    his=histc(d/c,t_axis+m/c);
    Exyz=Exyz+his(:);
end

% normalise sum(Exyz) to one. 
Exyz=Exyz/length(th)/nmc;

% scale by constants and divide by distance. 
Exyzn=Exyz*beta/Cp/4/pi*10^(9+energy)*1.6e-19./(m+t_axis*c);

% do integral in the frequency domain
pw=fft(Exyzn).*diff_filt.*atten_fna(f_axis,m*1e-3,atten);

% convert back to the time domain
p=real(ifft(pw)*fs);
