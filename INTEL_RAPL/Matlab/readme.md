# Matlab Scripts for measuring the execution energy of an application

Main script: 
    ```Main_Measurement_Script.m```

Runs on all Linux PCs with Intel Processors (iX and Xeon). 

Based on Intel <a href="https://dl.acm.org/doi/abs/10.1145/2425248.2425252">RAPL</a>. 


# Use

Run the main script in Matlab. 

The measurement can be configured using the file ```inputConfiguration.m```. Change the app executable to your executable and choose a set of input data. 

Attention: Make sure that you have the rights to execute the application binary. 


# Example

This code includes a readily executable example (```app_TAppDecoderStatic```) in the ```example/``` folder. The example is based on an <a href="https://gitlab.lms.tf.fau.de/LMS/HM-XX_analyzer">HEVC bit stream analyzer</a> and produces bit stream statistics for the example video ```data_sedona.bin```. 

When running the main script, the following output is produced: 
- File ```featNum.m```: Contains statistics from the decoder analyzer (only useful to check correct functionality)
- File ```example/Energy_*.mat```: Contains summarized information from the test series with all measured energies. The wildcard '*' is replaced by the measured application. 
- File ```example/measurement_*.mat```: Contains detailed information on the energy consumption measurement for file '*' from the dataset. 
