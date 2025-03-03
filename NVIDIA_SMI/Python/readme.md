# Python Scripts for measuring the execution energy of an application

Main script:energy_gpu_modified.py

Runs on all PCs with NVIDIA SMI version 565.57.01 and CUDA 12.7. 
# NVIDIA SMI Installation

Follow the steps below to install NVIDIA SMI on your machine:

## Step 1: Install NVIDIA Drivers

1. **Update your package list** (for Ubuntu/Debian-based systems):
   ```bash
   sudo apt update
2. **Install the latest NVIDIA drivers:**
  ```bash
   sudo apt install nvidia-driver
3. **Reboot your system to ensure the driver is loaded correctly**
  ```bash
   sudo apt install nvidia-driver

I create requirement.txt file.
I recommend to build a venv and install the packages on it. then run in the machine.

# Use
For running the code you can easily write 
python energy_gpu_modified.py
I have put a simple script which its name is test.py that do a matrix multiplication in this program.
if you want to use it for your appealing python code or task you can open energy_gpu_modified then at the end of code under main
you can modified the arguments whatever that you like.

# Example
TASK_COMMAND = "python your appealing script.py"  # Ensure Python executes the script
DURATION = 10  # Minimum duration for the task in seconds
INTERVAL = 0.1  # Sampling interval in seconds (100ms)
B = 1  # Maximum error tolerance
XI = 1  # Constant factor for calculating Nq
