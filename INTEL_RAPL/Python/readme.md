# Python Scripts for measuring the execution energy of an application

Main script: 
    ```main_energy.py```

Runs on all Linux PCs with Intel Processors (iX and Xeon), tested with generations 5+. 

Based on Intel <a href="https://dl.acm.org/doi/abs/10.1145/2425248.2425252">RAPL</a>. 


# Use

Run the main script in Python. 

The measurement can be configured using the function ```def input_configuration()```. Change the app executable to your executable with corresponding command-line flags. Using the variable 'instance_name', you can give the process a unique identifier for later analysis. 

Attention: Make sure that you have the rights to execute the application binary. 

[//]: # (# Environment setup)

[//]: # (conda create --name energy python=3.10)

[//]: # (conda activate energy)

[//]: # (pip requirements.txt)

# Environment Setup
Follow these steps to set up the environment and run the main script:

### 1. Create a Conda Environment
```sh
conda create --name energy python=3.10
```

### 2. Activate the Environment
```sh
conda activate energy
```

### 3. Install Dependencies
Ensure you have a `requirements.txt` file in your project directory, then run:
```sh
pip install -r requirements.txt
```

### 4. Run the Script to do the experiment
```sh
python main_energy.py
```

### 5. Deactivating the Environment
```sh
conda deactivate
```

### 6. Removing the Environment (Optional)
If you want to remove the environment completely, run:
```sh
conda remove --name energy --all
```

# Example

This code measures the energy consumption of a 5-s-execution of the ```top```command. Ensure that there are no active jobs running in the background, including jobs from other active users. Othwerwise, the result will be distorted. 

When running the main script, a file is created ```measurement/instance_name.txt```, which contains detailed information on the energy consumption measurement for the process named by the variable 'instanceName'. 
