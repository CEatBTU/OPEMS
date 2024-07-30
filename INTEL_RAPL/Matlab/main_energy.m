%% Main Function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Friedrich-Alexander-Universität Erlangen-Nürnberg        %
% Chair of Multimedia Communications and Signal Processing %
% Cauerstr. 7, 91058 Erlangen, Germany                     %
% Matthias Kraenzler   (matthias.kraenzler@fau.de)         %
% Christian Herglotz   (Christian.herglotz@b-tu.de)        %
% 08-2024                                                  %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Input Variables
% Please change settings in inputConfiguration()
[cfg] = inputConfiguration();

%% Unique identifier for the current process
instanceName = 'top_timeout_5s'
%% Full Command for process (including flags)
appcommand = 'timeout 5 top';

%% Energy Measurement
measureAppEnergy(appcommand,instanceName,cfg);    


