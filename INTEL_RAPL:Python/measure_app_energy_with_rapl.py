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
import subprocess
import time


def measure_app_energy_with_rapl(app_command, max_energy_range, analysis, number_of_reps):
    # Read RAPL counter 'cat /sys/class/powercap/intel-rapl/intel-rapl\:0/energy_uj';
    pause_time = 0.5
    measurement_domain = analysis['rapl']['measurement_domain']
    normalization_factor = analysis['rapl']['normalization_factor']
    # Measure Load

    # Perform application
    start_load = subprocess.getoutput(f'cat {measurement_domain}energy_uj')
    start_time = time.time()
    time.sleep(pause_time)
    subprocess.run(app_command, shell=True)
    time.sleep(pause_time)
    time_end = time.time() - start_time
    end_load = subprocess.getoutput(f'cat {measurement_domain}energy_uj')

    app_time = time_end - 2 * pause_time

    # Measure Idle
    start_idle = subprocess.getoutput(f'cat {measurement_domain}energy_uj')
    time.sleep(app_time + 2 * pause_time)
    end_idle = subprocess.getoutput(f'cat {measurement_domain}energy_uj')

    # Calculation
    energy_load = (float(end_load) - float(start_load)) / normalization_factor
    energy_idle = (float(end_idle) - float(start_idle)) / normalization_factor

    if energy_load < 0:
        energy_load += max_energy_range

    if energy_idle < 0:
        energy_idle += max_energy_range
    return energy_load, energy_idle, app_time