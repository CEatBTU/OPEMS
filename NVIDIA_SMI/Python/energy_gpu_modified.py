import os
import subprocess
import time
import numpy as np
from scipy.stats import t

def measure_gpu_energy(task_command, duration, interval=0.1, B=0.05, xi=1):
    """
    Args:
        task_command (str): The shell command to execute the task.
        duration (float): Minimum runtime for the task (in seconds).
        interval (float): Sampling interval for power measurements (in seconds).
        B (float): Maximum error tolerance for the energy measurements.
        xi (float): Constant factor for calculating Nq.

    Returns:
        dict: Contains energy consumption statistics and detailed measurements.
    """
    energy_load = []
    energy_idle = []

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

    def measure_energy_with_task(task_duration, repetitions):
        """
        Runs the given task command while measuring GPU power usage.
        """
        print(f"Measuring energy consumption for {task_duration:.2f} seconds with {repetitions} repetitions...")
        total_energy = 0

        for _ in range(repetitions):
            power_readings = []
            start_time = time.time()

            # Start the task under test
            process = subprocess.Popen(task_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            while time.time() - start_time < task_duration:
                power = get_gpu_power()
                power_readings.append(power)
                time.sleep(interval)  # Sampling interval

            process.wait()  # Ensure the task completes

            total_energy += np.sum(np.array(power_readings) * interval)

        avg_energy = total_energy / repetitions
        return avg_energy, power_readings

    # Step 1: Measure Idle Energy
    print("Measuring idle energy...")
    idle_energy, _ = measure_energy_with_task(duration + 2 * interval, 5)  # Fixed repetitions for idle state
    energy_idle.append(idle_energy)

    q = 1  # Start with q = 1
    while True:  # Iterate until the condition is met
        Nq = int(np.ceil(q / xi))  # Calculate Nq = ⌊ q / ξ ⌉
        print(f"Repetitions q: {q}, Calculated samples Nq: {Nq}")

        load_energy, _ = measure_energy_with_task(duration, Nq)  # Run task under test in each iteration
        energy_load.append(load_energy)

        print(f"Iteration {q}: Energy = {load_energy:.2f} J")

        # Step 3: Evaluate condition based on the error tolerance
        if len(energy_load) > 1:  # Ensure we have enough data for statistical evaluation
            test_now = np.array(energy_load) - np.array(energy_idle)
            mean_energy = np.mean(test_now)
            confidence_interval = (
                np.std(test_now) / np.sqrt(len(test_now))
            ) * t.ppf(1 - B / 2, len(test_now) - 1)
            threshold = B * mean_energy

            print(f"Confidence Interval: {confidence_interval:.2f}")
            print(f"Threshold: {threshold:.2f}")

            if (1 - B) < ((Nq / q) * xi) < (1 + B):  # Condition from the equation
                print(f"Energy measurement stabilized: Mean = {mean_energy:.2f} J")
                return {
                    "mean_energy": mean_energy,
                    "confidence_interval": confidence_interval,
                    "energy_load": energy_load,
                    "energy_idle": energy_idle,
                    "final_q": q,
                    "final_Nq": Nq,
                }

        q += 1  # Increase the number of repetitions

        time.sleep(interval)


# Example Usage
if __name__ == "__main__":
    TASK_COMMAND = "python test.py"  # Ensure Python executes the script
    DURATION = 10  # Minimum duration for the task in seconds
    INTERVAL = 0.1  # Sampling interval in seconds (100ms)
    B = 1  # Maximum error tolerance
    XI = 1  # Constant factor for calculating Nq

    results = measure_gpu_energy(TASK_COMMAND, DURATION, INTERVAL, B, XI)
    print("Measurement Results:")
    print(results)
