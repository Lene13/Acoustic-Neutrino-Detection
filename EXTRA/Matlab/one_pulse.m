# the below line specifies the interpreter to be used
#!/usr/bin/octave -qf

# define the path where other functions to be used can be found
addpath("/home/lene/code/functions");

# args is an array containing the command-line arguments
args = argv;

# name the output files the following
filename = strcat(args{3}, "_", args{1}, "_", args{2}, "_", args{4}, ".dat");

# represent the position parameters
zpos = str2num(args{1})
rpos = str2num(args{2})
Eo = str2num(args{4})

#---------------------------------------------------------------------------------------------

rsc=[.5:9.5 15:10:105];             % radial bin centres (cm)
zsc=10:20:2000;                     % longitudinal Bin Centres (cm)
#Eo=1e14;                           % primary Energy
Do=[rpos 0 zpos];                   % position of observer 
fs=1e6;                             % sampling frequency


%t_axis=(-512:511)/fs;              % time axis for plot (default 1024 points)
t_axis=(-1024:1023)/fs;             % if you redefine it her, also in other scripts...

atten=1;                            % learned's attenuation
nmc=1e6;                            % number of MC points

#---------------------------------------------------------------------------------------------

# calls a function shown in another file
tsmc=ShowerParm(rsc,zsc,Eo,'Sloan');

% as the 10-100cm bins are 10x wider need to scale by a factor of 10 
tsmc=tsmc*diag(kron([1 10],ones(1,10)));

% generate MC points. Note bin EDGES need to be provided 
pointsc=MCGEn(tsmc,[0 zsc+10],[0 rsc+[0.5*ones(1,10) 5*ones(1,10)]],nmc);

% convert to cartesian
[x,y,z]=pol2cart(rand(nmc,1)*2*pi,pointsc(:,2),pointsc(:,1));

% convert fom cm to m 
points=[x y z]*1e-2;

# calculate the kernelfunction with the obtained parameters
p=kernelfr2(points,Do,log10(Eo),atten,10);

# define the path where you want the data files to be saved
folder = "/home/lene/code/simulations";

% Save the current working directory
current_dir = pwd;

% Change the working directory to the desired folder
cd(folder);

% save the data 
% filename = args{2}
tp = [t_axis' p];                         % check this weird construction of the transpose columns

# uncommand to save the files
#save(filename, 'tp');

# plot the energy deposition
x = t_axis'; 
y = p;

% Create and customize the plot
figure;                                   % Create a new figure
plot(x, y, 'r--', 'LineWidth', 2);        % Plot with red dashed line and thicker line width
title('Acoustic Neutrino Pulse');         % Set the title
xlabel('t');                              % Label the x-axis
ylabel('p');                              % Label the y-axis
grid on;                                  % Enable the grid

# uncommand to save the files
#print([args{3} ' Neutrino Pulse.png'], '-dpng', '-r300'); % Save plot as a PNG file with 300 DPI

# display so that it can be used in a python script
disp(p)

% change back to the original working directory
cd(current_dir);
