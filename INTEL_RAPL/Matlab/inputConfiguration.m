%% Input Configuration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Friedrich-Alexander-Universität Erlangen-Nürnberg        %
% Chair of Multimedia Communications and Signal Processing %
% Cauerstr. 7, 91058 Erlangen, Germany                     %
% Matthias Kraenzler   (matthias.kraenzler@fau.de)         %
% Christian Herglotz   (Christian.herglotz@b-tu.de)        %
% 08-2024                                                  %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [cfg] = inputConfiguration()
% Settings to be changed by user
    % Settings RAPL
    cfg.rapl.outputFolder = 'measurements';
    if ~isfolder(cfg.rapl.outputFolder)
        mkdir(cfg.rapl.outputFolder);
    end
    
    % Application specific settings - Do not change
    cfg.rapl.measurementDomain = '/sys/class/powercap/intel-rapl/intel-rapl:0/';
    cfg.rapl.conf_alpha = 0.99; %description of confidence interval test: https://doi.org/10.1109/TCSVT.2016.2598705
    cfg.rapl.conf_beta = 0.04;
    cfg.rapl.maxMeasurements = 50;
    cfg.rapl.minimumMeasurementTime = 2.5; %Minimum time in seconds to improve measurement quality 
    cfg.rapl.initializationMeasurement = 1;
    cfg.rapl.normalizationFactor = 1e6; %RAPL measures energy in uJ
    cfg.rapl.measurementFileEnding = 'mat';
end
