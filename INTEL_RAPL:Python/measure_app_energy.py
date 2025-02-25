####################################################
# University of Bristol, School of Computer Science
# Xinyi Wang (xinyi.wang@bristol.ac.uk)
# Angeliki Katsenou
# Daniel Schien (Daniel.Schien@bristol.ac.uk)

# Translated from the Matlab scripts authored by:
# Matthias Kraenzler   (matthias.kraenzler@fau.de)
# Christian Herglotz   (Christian.herglotz@b-tu.de)
# 02-2025
####################################################
import os
import subprocess
import numpy as np
from scipy.stats import t
from measure_app_energy_with_rapl import measure_app_energy_with_rapl


def measure_app_energy(app_command, instance_name, cfg):
    if not os.path.exists(cfg['rapl']['output_folder']):
        os.makedirs(cfg['rapl']['output_folder'])

    # Check if RAPL parameter is specified correctly
    result = subprocess.run(['cat', cfg['rapl']['measurement_domain'] + 'energy_uj'], capture_output=True, text=True)
    try:
        float(result.stdout.strip())
    except ValueError:
        raise ValueError('RAPL is not specified correctly! Please check variable cfg["rapl"]["measurement_domain"]')

    result = subprocess.run(['cat', cfg['rapl']['measurement_domain'] + 'max_energy_range_uj'], capture_output=True, text=True)# Important to solve RAPL counter overflow
    max_energy_range = float(result.stdout.strip()) / cfg['rapl']['normalization_factor']

    measurement_energy_folder = cfg['rapl']['output_folder']
    conf_prob = cfg['rapl']['conf_alpha']
    interval_part = cfg['rapl']['conf_beta']
    progress = len([f for f in os.listdir(measurement_energy_folder) if f.startswith('measurement_')])

    # Check on previous measurements
    measurement_file = os.path.join(measurement_energy_folder, f"{instance_name}.{cfg['rapl']['measurement_file_ending']}")

    if not os.path.isfile(measurement_file):
        # Initialize measurement variables
        energy_load = [] # Energy demand during decoding
        energy_idle = [] # Energy demand during idle
        app_time = [] # Time of decoding process

        print('==============')
        print(f'Performing measurement for {instance_name}')
        # Derive processing time for multiple executions and change
        number_of_reps = 1
        if cfg['rapl']['minimum_measurement_time'] > 0:
            timeout_duration = cfg['rapl']['minimum_measurement_time'] + 1
            result = subprocess.run(['timeout', '11', 'bash', '-c', f'time {app_command}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            sys_answer = result.stdout
            print('sys_answer:\n', sys_answer)

            try:
                sys_time_start = sys_answer.find('real\t')
                sys_time_stop = sys_answer.find('user\t')
                duration_str = sys_answer[sys_time_start + 5:sys_time_stop].strip()
                duration = float(duration_str[2:-1])
                number_of_reps = int(np.ceil(cfg['rapl']['minimum_measurement_time'] / duration))
                print(f'Processing Time: {duration} sec.')
                print(f'Repetitions: {number_of_reps}')
                print('==============')
            except (IndexError, ValueError):
                pass
        subprocess.run(["sleep", "0.5"])
        if number_of_reps > 1:
            app_command = f'for ((n=0;n<{number_of_reps};n++)); do {app_command}; done'

        # Use initialization measurements for stabilization of
        # measurement process
        if cfg['rapl']['initialization_measurement']:
            print('Initialization: ')
            energy_load_init, energy_idle_init, app_time_init = measure_app_energy_with_rapl(app_command, max_energy_range, cfg, number_of_reps)
            energy_load_init /= number_of_reps # Normalization for multiple decodings
            energy_idle_init /= number_of_reps
            app_time_init /= number_of_reps
            energy_app_init = energy_load_init - energy_idle_init
            print(f'App Energy: {energy_app_init} J')

        meas_nr = 1
        while len(energy_load) < cfg['rapl']['max_measurements']:
            # Read values with decoding
            print(f'Iteration {meas_nr}')
            load, idle, time = measure_app_energy_with_rapl(app_command, max_energy_range, cfg, number_of_reps)
            energy_load.append(load / number_of_reps)
            energy_idle.append(idle / number_of_reps)
            app_time.append(time / number_of_reps)
            print(f'App Energy: {energy_load[-1] - energy_idle[-1]} J')

            # Check if measurement is statistically accurate enough
            if len(energy_load) > 4: # Make sure that a minimum number of measurements has been performed
                test_now = np.array(energy_load) - np.array(energy_idle)
                conf = np.std(test_now) / np.sqrt(len(test_now)) * t.ppf(conf_prob, len(test_now) - 1)
                threshold = interval_part * np.mean(test_now)
                print('\n')
                print(f' Confidence Interval:  {conf}')
                print(f' Threshold: {threshold}')

                if conf < threshold: # Measurement series is within confindence interval boundaries
                    print(f' E_mean: {np.mean(test_now)} J')
                    # App energies for package, CPU, and non-CPU
                    energy_app = test_now
                    energy_app_mean = np.mean(test_now)
                    data_name = instance_name
                    n_measurements = len(test_now)
                    progress += 1
                    with open(os.path.join(measurement_energy_folder, f'measurement_{instance_name}'), 'w') as f:
                        f.write(str({
                            'energyAppMean': energy_app_mean,
                            'energyApp': list(energy_app),
                            'energyLoad': energy_load,
                            'energyIdle': energy_idle,
                            'nMeasurements': n_measurements,
                            'appCommand': app_command,
                            'dataName': data_name,
                            'conf': conf,
                            'threshold': threshold,
                            'appTime': app_time
                        }))
                    break

                if conf > threshold and len(energy_load) > 9: # Discard all measurements that are out of bounds from 0.75*median to 1.25*median
                    upper_bound = 1.25 * np.median(test_now)
                    lower_bound = 0.75 * np.median(test_now)
                    mask = (test_now > lower_bound) & (test_now < upper_bound)
                    energy_load = list(np.array(energy_load)[mask])
                    energy_idle = list(np.array(energy_idle)[mask])
                    app_time = list(np.array(app_time)[mask])
                    test_now = test_now[mask]
                    meas_nr = len(test_now)
                    print('after mask:')
                    print('energy_load:', energy_load)
                    print('energy_idle:', energy_idle)
                    print('app_time:', app_time)
                    print('test_now:', test_now)
                    print('meas_nr:', meas_nr)

            print('')
            meas_nr += 1
