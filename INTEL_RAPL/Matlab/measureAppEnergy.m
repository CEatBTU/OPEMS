%% Measure energy consumption of an app
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Friedrich-Alexander-Universität Erlangen-Nürnberg        %
% Chair of Multimedia Communications and Signal Processing %
% Cauerstr. 7, 91058 Erlangen, Germany                     %
% Matthias Kraenzler   (matthias.kraenzler@fau.de)         %
% 09-2022                                                  %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% This script works on Linux systems equipped with Intel CPUs (iX, Xeon)

function measureAppEnergy(appCommand, instanceName, cfg)

    if isfolder(cfg.rapl.outputFolder) == 0
        mkdir(cfg.rapl.outputFolder);
    end
    
    %Check if RAPL parameter is specified correctly
    [~,sysOut] = system(['cat ' cfg.rapl.measurementDomain 'energy_uj']);  
    if isnan(str2double(sysOut))
        error('RAPL is not specified correctly! Please check variable cfg.rapl.measurementDomain');
    end
    
    [~, maxEnergyRange] = system(['cat ' cfg.rapl.measurementDomain 'max_energy_range_uj']);%Important to solve RAPL counter overflow
    maxEnergyRange = str2double(maxEnergyRange) / cfg.rapl.normalizationFactor;
    
    measurementEnergyFolder = cfg.rapl.outputFolder;
    confProb = cfg.rapl.conf_alpha;
    intervalPart = cfg.rapl.conf_beta;
    progress = size(dir([measurementEnergyFolder filesep  'measurement_*']),1);

    
         %Check on previous measurements
         if ~isfile([measurementEnergyFolder filesep  instanceName '.' cfg.rapl.measurementFileEnding])
                
            
            %Initialize measurement variables
            energyLoad =[]; %Energy demand during decoding
            energyIdle = [];%Energy demand during idle
            appTime = [];%Time of decoding process

            disp('==============');
            disp(['Performing measurement for ' instanceName]);
            %Derive processing time for multiple executions and change
            numberOfReps = 1;
            if cfg.rapl.minimumMeasurementTime > 0
                timeoutDuration = cfg.rapl.minimumMeasurementTime + 1;
                [~,sysAnswer] = system(['time timeout 11 ' appCommand]);
                sysTimeStart = strfind(sysAnswer,'real	');
                sysTimeStop = strfind(sysAnswer,'user	');
                duration = str2double(sysAnswer(sysTimeStart+7:sysTimeStop-3));
                numberOfReps = ceil(cfg.rapl.minimumMeasurementTime / duration);                  
               disp(['Processing Time: ' num2str(duration) ' sec.']);
               disp(['Repetitions: ' num2str(numberOfReps) ]);
               disp('==============');
            end

            pause(0.5);
            if numberOfReps > 1
                appCommand = ['for ((n=0;n<'  num2str(numberOfReps) ';n++)); do ' appCommand '; done'];
            end

            %Use initialization measurements for stabilization of
            %measurement process
            if cfg.rapl.initializationMeasurement
                disp('Initialization: ')
                [energyLoadInit,energyIdleInit,appTimeInit] = measureAppEnergyWithRapl(appCommand,maxEnergyRange,cfg,numberOfReps);
                energyLoadInit = energyLoadInit / numberOfReps; %Normalization for multiple decodings
                energyIdleInit = energyIdleInit / numberOfReps;
                appTimeInit   = appTimeInit/numberOfReps;
                energyAppInit = energyLoadInit -energyIdleInit;
                disp(['App Energy: ' num2str(energyAppInit) ' J']);
            end

            measNr = 1;
            while size(energyLoad,1) < cfg.rapl.maxMeasurements
                % Read values with decoding
                disp(['Iteration ' num2str(measNr)])
                [energyLoad(measNr),energyIdle(measNr),appTime(measNr)] = measureAppEnergyWithRapl(appCommand,maxEnergyRange,cfg,numberOfReps); %#ok<*AGROW>

                energyLoad(measNr) = energyLoad(measNr) / numberOfReps;
                energyIdle(measNr)  = energyIdle(measNr) / numberOfReps;
                appTime(measNr)   = appTime(measNr)/numberOfReps;
                disp(['App Energy: ' num2str(energyLoad(measNr)-energyIdle(measNr)) ' J']);
                % Check if measurement is statistically accurate enough
                if size(energyLoad,2) > 4 % Make sure that a minimum number of measurements has been performed
                    testNow = energyLoad(:)-energyIdle(:);
                    conf = std(testNow)/sqrt(length(testNow))*tinv(confProb,length(testNow)-1);
                    threshold = intervalPart*mean(testNow);
                    disp(' ');
                    disp([' Confidence Interval:  ' num2str(conf)]);
                    disp([' Threshold: ' num2str(threshold)]);
                    pause(.1);
                    if (conf < threshold) %Measurement series is within confindence interval boundaries
                        disp([' E_mean: ' num2str(mean(testNow)) ' J']);
                        % App energies for package, CPU, and non-CPU
                        energyApp = testNow; %#ok<*NASGU>
                        energyAppMean = mean(testNow);
                        dataName = datasetEntries(idx).name;
                        nMeasurements = length(testNow);
                        progress = progress + 1;
                        save([measurementEnergyFolder filesep  'measurement_'  instanceName ],...
                            'energyAppMean','energyApp','energyLoad','energyIdle',...
                            'nMeasurements','appCommand','dataName',...
                            'conf','threshold','appTime','analysis');
                        break;
                    end

                    if (conf > threshold && size(energyLoad,2) > 9) % Discard all measurements that are out of bounds from 0.75*median to 1.25*median
                        upperBound = 1.25 * median(testNow);
                        lowerBound = 0.75 * median(testNow);
                        energyLoad = energyLoad((upperBound > testNow) & (testNow > lowerBound));
                        energyIdle  = energyIdle((upperBound > testNow) & (testNow > lowerBound));
                        appTime   = appTime((upperBound > testNow) & (testNow > lowerBound));
                        testNow = testNow((upperBound > testNow) & (testNow > lowerBound)) ;
                        measNr = size(testNow,1);
                    end
                end
                disp('')
                measNr = measNr + 1;
            end 
	end 
end

