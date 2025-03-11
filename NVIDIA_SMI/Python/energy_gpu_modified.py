import os
import subprocess
import time
import numpy as np
from scipy.stats import t
from math import ceil

def measure_gpu_energy(task_command, duration, interval=0.1, B=0.05, xi=1):
    """
    Args:
        task_command (str): The shell command to execute the task.
        duration (float): Target minimum total runtime for measuring energy (in seconds).
        interval (float): Sampling interval for power measurements (in seconds).
        B (float): Maximum error tolerance for the energy measurements.
        xi (float): Constant factor for calculating Nq in the stopping criterion.

    Returns:
        dict: Contains energy consumption statistics and detailed measurements.
    """

    def run_command(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode('utf-8'), stderr.decode('utf-8')

    def get_gpu_power():
        cmd = "nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits"
        output, _ = run_command(cmd)
        try:
            return float(output.strip())
        except ValueError:
            raise RuntimeError("Failed to parse power.draw from nvidia-smi.")

    # ----------------------
    # Step 0: Probe how long a single run of the task takes
    # ----------------------
    def measure_single_run_time(command):
        start_t = time.time()
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        end_t = time.time()
        return end_t - start_t

    print("Performing probe run to measure single task time...")
    single_run_time = measure_single_run_time(task_command)
    print(f"Single task time is ~{single_run_time:.2f} s")

    # If the single task is shorter than 'duration', we will aggregate multiple runs
    # so that the total measurement window is >= 'duration'
    # E.g. if single_run_time = 2s and duration=20, aggregated_runs=10
    aggregated_runs = max(1, int(ceil(duration / single_run_time)))
    print(f"Will repeat the task {aggregated_runs} time(s) per measurement batch.")

    # ----------------------
    # measure_energy_with_task:
    # Runs the test command 'aggregated_runs' times in a row *per measurement batch*.
    # For each measurement, we sample GPU power every 'interval' seconds.
    # Finally, we divide total energy by 'aggregated_runs' to get “energy per single task”.
    # ----------------------
    def measure_energy_with_task(aggregated_runs):
        # We'll measure from the moment we start the first run until the end of the last run.
        print(f"Measuring energy consumption for ~{aggregated_runs} consecutive run(s)...")
        power_readings = []
        start_time = time.time()

        for _ in range(aggregated_runs):
            proc = subprocess.Popen(task_command, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # While this instance hasn't finished, keep sampling power
            while proc.poll() is None:  # None means still running
                power = get_gpu_power()
                power_readings.append(power)
                time.sleep(interval)  # sampling interval

            # Ensure the process is fully done before starting next
            proc.wait()

        end_time = time.time()

        # The total time from first run start to last run end
        total_time_sec = end_time - start_time
        # Approximate energy by sum(power * interval)
        total_energy_joules = np.sum(np.array(power_readings) * interval)

        # Return average energy per single run
        avg_energy = total_energy_joules / aggregated_runs

        return avg_energy, total_time_sec

    # ----------------------
    # Step 1: Measure Idle Energy
    # ----------------------
    print("Measuring idle energy...")
    idle_power_readings = []
    idle_start = time.time()
    while (time.time() - idle_start) < (duration + 2 * interval):
        idle_power = get_gpu_power()
        idle_power_readings.append(idle_power)
        time.sleep(interval)

    idle_total_energy = np.sum(np.array(idle_power_readings) * interval)
    # Idle measurement is over 'idle_time' seconds
    idle_time = time.time() - idle_start
    # We'll use average idle power times the typical single_run_time
    # to estimate "idle energy" for the same time a single run takes.
    idle_average_power = idle_total_energy / idle_time
    estimated_idle_energy_per_run = idle_average_power * single_run_time
    print(f"Estimated idle energy per single run: ~{estimated_idle_energy_per_run:.2f} J")

    # We'll keep track of energy measurements (load minus idle).
    energy_load = []
    energy_idle = []
    energy_idle.append(estimated_idle_energy_per_run)

    # ----------------------
    # Step 2: Start iterative measurement until stability
    # ----------------------

    while True:
        # Nq = ⌈ q / ξ ⌉
        Nq = int(ceil(q / xi))
        print(f"\nIteration q={q}, calculating Nq={Nq}...")

        measured_energies = []
        for _ in range(Nq):
            load_energy_per_run, actual_time = measure_energy_with_task(aggregated_runs)
            measured_energies.append(load_energy_per_run)
        # The average of these is "energy per single run"
        load_energy_mean = np.mean(measured_energies)

        # Save it
        energy_load.append(load_energy_mean)
        print(f"Iteration {q}: Energy per run = {load_energy_mean:.2f} J")

        # ----------------------
        # Step 3: Evaluate condition based on the error tolerance
        if len(energy_load) > 1:
            test_now = np.maximum(np.array(energy_load) - np.array(energy_idle), 0)
            mean_energy = np.mean(test_now)
            # Confidence Interval (two-sided)
            ci = (np.std(test_now, ddof=1) / np.sqrt(len(test_now))) * t.ppf(1 - B / 2, len(test_now) - 1)
            threshold = B * mean_energy

            print(f"Confidence Interval: ±{ci:.2f} J")
            print(f"Threshold (B * mean_energy): ±{threshold:.2f} J")

            # Also check the condition (1-B) < (Nq / q) * xi < (1+B)
            ratio = (Nq / q) * xi
            print(f"(Nq / q)*xi = {ratio:.2f}")
            if (1 - B) < ratio < (1 + B):
                print(f"\nEnergy measurement stabilized. Mean load (net) = {mean_energy:.2f} J")
                return {
                    "mean_energy": mean_energy,
                    "confidence_interval": ci,
                    "energy_load": energy_load,
                    "energy_idle": energy_idle,
                    "final_q": q,
                    "final_Nq": Nq,
                    "aggregated_runs": aggregated_runs,
                }

        q += 1
        time.sleep(interval)

# ----------------------
# Example usage
# ----------------------
if __name__ == "__main__":
    TASK_COMMAND = (
        "PYTHONPATH=$(pwd)/src/pytorch-image-models/:$PYTHONPATH "
        "python3 src/submit/submit.py --mode partial_reproduce --trt"
    )
    # We'll try measuring until each iteration is at least ~20 seconds total
    # or repeated enough times to get a stable result.
    DURATION = 20       # Minimum measurement duration (seconds)
    INTERVAL = 0.1      # Sampling interval in seconds (100ms)
    B = 1               # Max error tolerance
    XI = 1              # Constant factor for calculating Nq

    results = measure_gpu_energy(TASK_COMMAND, DURATION, INTERVAL, B, XI)
    print("\nFinal Measurement Results:")
    print(results)
