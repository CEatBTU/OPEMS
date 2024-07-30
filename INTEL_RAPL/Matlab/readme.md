# Matlab Scripts for measuring the execution energy of an application

Main script: 
    ```main_energy.m```

Runs on all Linux PCs with Intel Processors (iX and Xeon), tested with generations 5+. 

Based on Intel <a href="https://dl.acm.org/doi/abs/10.1145/2425248.2425252">RAPL</a>. 


# Use

Run the main script in Matlab. 

The measurement can be configured using the file ```inputConfiguration.m```. Change the app executable to your executable with corresponding command-line flags. Using the variable 'instanceName', you can give the process a unique identifier for later analysis. 

Attention: Make sure that you have the rights to execute the application binary. 


# Example

This code measures the energy consumption of a 5-s-execution of the ```top```command. Ensure that there are no active jobs running in the background, including jobs from other active users. Othwerwise, the result will be distorted. 

When running the main script, a file is created ```measurement/measurement_instanceName.mat```, which contains detailed information on the energy consumption measurement for the process named 'instanceName'. 
