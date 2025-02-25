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
from measure_app_energy import measure_app_energy

def input_configuration():
    # Settings to be changed by user
    cfg = {}

    # Settings RAPL
    cfg['rapl'] = {}
    cfg['rapl']['output_folder'] = 'measurements'
    if not os.path.isdir(cfg['rapl']['output_folder']):
        os.makedirs(cfg['rapl']['output_folder'])

    # Application specific settings - Do not change
    cfg['rapl']['measurement_domain'] = '/sys/class/powercap/intel-rapl/intel-rapl:0/'
    cfg['rapl']['conf_alpha'] = 0.99  # Confidence interval test
    cfg['rapl']['conf_beta'] = 0.04
    cfg['rapl']['max_measurements'] = 50
    cfg['rapl']['minimum_measurement_time'] = 2.5  # Minimum time in seconds to improve measurement quality
    cfg['rapl']['initialization_measurement'] = 1
    cfg['rapl']['normalization_factor'] = 1e6  # RAPL measures energy in uJ
    cfg['rapl']['measurement_file_ending'] = 'txt'

    return cfg


if __name__ == "__main__":
    # Input Variables
    # Please change settings in inputConfiguration()
    cfg = input_configuration()

    # Unique identifier for the current process
    instance_name = 'top_timeout_5s'

    # Full Command for process (including flags)
    app_command = 'timeout 5 top'

    # Energy Measurement
    measure_app_energy(app_command, instance_name, cfg)
