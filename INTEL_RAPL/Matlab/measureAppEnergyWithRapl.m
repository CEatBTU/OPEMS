%% Measure decoding energy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Friedrich-Alexander-Universität Erlangen-Nürnberg        %
% Chair of Multimedia Communications and Signal Processing %
% Cauerstr. 7, 91058 Erlangen, Germany                     %
% Matthias Kraenzler   (matthias.kraenzler@fau.de)         %
% Christian Herglotz   (Christian.herglotz@b-tu.de)        %
% 08-2024                                                  %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [energyLoad,energyIdle,appTime] = measureAppEnergyWithRapl(appCommand,maxEnergyRange,analysis,numberOfReps)
% Read RAPL counter 'cat /sys/class/powercap/intel-rapl/intel-rapl\:0/energy_uj';
%% MEASURE LOAD
    % Perform application
    pauseTime = 0.5;
    [~, startLoad] = system(['cat ' analysis.rapl.measurementDomain 'energy_uj']);
    tic;
    pause(pauseTime);
    [~,~] = system(appCommand);
    pause(pauseTime);
    timeEnd = toc;
    [~, endLoad] = system(['cat ' analysis.rapl.measurementDomain 'energy_uj']);

    appTime = timeEnd - 2 * pauseTime;

%% MEASURE IDLE
    % Read values without decoding
    [~, startIdle] = system(['cat ' analysis.rapl.measurementDomain 'energy_uj']);
    pause(appTime+2*pauseTime);
    [~, endIdle] = system(['cat ' analysis.rapl.measurementDomain 'energy_uj']);

%% Calculation
    % Save values
    energyLoad = (str2num(endLoad)-str2num(startLoad))/analysis.rapl.normalizationFactor; %#ok<*ST2NM>
    energyIdle = (str2num(endIdle)-str2num(startIdle))/analysis.rapl.normalizationFactor; %#ok<*ST2NM>

    if (energyLoad < 0)
        energyLoad = energyLoad + maxEnergyRange;
    end

    if (energyIdle < 0)
        energyIdle = energyIdle + maxEnergyRange;
    end

end
