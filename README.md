# OPEMS
Open Power and Energy Measurement Scrips

This readme contains all information about this repo containing detailed explanations and examplary scripts to perform power and energy measurements on NVIDIA GPUs and Intel CPUs. 

Please read this document carefully to get a feeling of how to perform scientifically correct and valid measurements. 

## Overview

In general, we measure the time/power/energy consumption of a certain **application (app)** on the **device-under-test (DUT)**, which could, e.g., be a smartphone, a TV, a PC, or a component of a device such as a CPU. The power/energy is measured by the **power meter (PM)**. Furthermore, we need a **control unit (CU)** to control and automize measurements. 

Scripts for measuring power/energy on different PMs are listed in the folder ```/PMs```. 

Concerning apps, no further commands are given because the information on controlling apps is usually easily available on search engines. 

## Processing times

First of all: No, timing of a process is not a trivial thing. In fact, it is important to know what time is measured. Here is a list of the most important processing times one could measure: 
- **Elapsed time:** The real elapsed time that you would measure using your own watch (example: the linux time -p commant returning the real time)
- **CPU time**: The time a process spent on a certain (or cumulatively) on multiple CPUs. In parallel processing, this time is generally larger than the real time (example: time -p returning the user time).  
- **System time**: The time the CPUs spent on system processes not related to the target process (example: time -p returning the system time). Usually, we do not look at this in detail. 

Furthermore, is is important to know whether (1) a process is performed in real-time, e.g., video playback with just-in-time decoding for playback on a stream. Or (2) whether a process runs as fast as possible (e.g., encoding for storage in memory). These settings have an important impact on the power behavior of the process. 

Whenever you do time measurements, you should be aware of the type of time you are measuring. Especially when using further timing functions (clock() in C++, tic-toc in Matlab etc.), you should always know which time you get. 

Note that in general, these terms shown here are not standardized and not commonly used in the literature. So be careful using them. 


## Power and Energy Measurements

With the help of the time, we can now talk about energy and power measurements. For these, we usually take the elapsed time (that means the time a watch would measure). The phsyical relation between time *t* in seconds, power *P* in Watts, and energy *E* in Joules is

<img src="gfx/energy_power_time.png" width="108" height="43" />

 We can basically measure three kinds of different values that are best described by looking at a typical power consumption of a process shown below. 

<img src="gfx/powerExample.png" width="400" height="300" />

In this plot, we can see the power consumption of an arbitrary app on an arbitrary DUT. The horizontal axis corresponds to the time and the vertical axis to the instantaneous power at the corresponding time. The blue line shows the power consumption when the measured DUT is idle and the red line the power of the app to be measured. In this example, the app starts at roughly 2s and ends at roughly 6s. The power consumption before and after the app is close to the idle power. The idle power can be measured to find out about the additional power during a process. In case the overall power is desired, measuring an idle power is not needed. 

It is adviced to always record some power measurements like this to have a feeling for the power consumption properties of the DUT and the app that is running on it. 

In our research, we are mostly interested in (1) mean powers during a stationary process without a predefined beginning and end (e.g., during video streaming), or (2) in energies consumed for a full process (e.g., a decoding process for a full sequence with clear beginning and end). Both are visualized in the following. 

# Mean Power Measurement

Usually, these measurements are performed for apps that have an indefinite duration (e.g., video streaming). For these measurements, we do not care about the power consumption during the launch or the exit of an app. As a consequence, a measurement is performed as shown in the next figure. 

<img src="gfx/meanPowerExample.png" width="400" height="300" />

In principle, the execution order is 
```
start app -> start measurement -> end measurement -> end app
```
which means that we record power data during the execution of the app. From the output data, we can then calculate the mean power by averaging all power values or by dividing the energy measured in this interval by the elapsed time. 


# Energy Measurement

Usually, energy measurements are performed for apps with a fixed beginning and end (e.g., encoding of a video). This means that we include the power consumption during the launch and the exit of the app. As a consequence, a measurement is performed as shown in the next figure. 

<img src="gfx/energyExample.png" width="400" height="300" />

In principle, the execution order is 
```
start measurement -> start app  -> end app -> end measurement
```
which means that we record power data for the complete duration of the app. From the output data, we can then calculate the energy by integrating all power values over the elapsed time. Note that for fair comparisons, an idle energy must usually be subtracted to avoid errors introduced by the power consumed before and after the app. 

Note that the start and the end of the measurement could also be triggered by the starting time and the ending time of the app. However, this triggering is complicated because app execution times can vary such that also the impact of the offset power (idle) plays a more important role.  


## Statistical Validity

For statistical validity, each measurement should be repeated several times. As we are working with devices performing random processes in the background, e.g., due to the operating system, this is required to obtain statistical significance. Our standard way to ensure statistical validity is to perform a confidence interval test as follows: 

<img src="gfx/statistical_validity.png"  />

In this equation, *m* is the number of measurements, *x* the arithmetic mean of the measurements, and *&#963;* the standard deviation of the measurements. *&#945;* is the probablity, *&#946;* the relative confidence interval size, and *t_&#945;(m-1)* the critical t-value for *m* samples from Student's t-distribution. We often use *&#945;*=0.99 and *&#946;*=0.02, which for the case of energy measurements means the following: 

```
With a probability of at least 99%, the true energy is not lower than 0.99 times and not higher than 1.01 times the measured mean energy *x*.
```

An example Matlab-script for calculating such statistics is available in ```tools/statisticalAnalysis.m``` CH TODO. 

## Good Scientific Practice

For all your measurement, it is good to follow some good-scientific-practice rules: 

- Make sure that your measurements can be reproduced. 
- Before mean power or energy measurements, perform a power measurement of the process and check the power-time curve for plausibility. It is also a good idea to record such a power-time curve for the report/thesis. 
- Check all results for plausibility. 
- Crosscheck measurements which do not satisfy the statistical validity test. Try to find out why it is not statistically valid. 
- Define the system setup in detail ((state of) Internet connections, screen brightnesses, runlevel, state of background processes, OS version, ...) and find ways to set these automatically before the measurement, if possible. 



## Power Meters

Currently, scripts for the following power meters are available: 
- **Running-Average Power Limit (RAPL)**: Internal power meter of Intel CPUs (measures the energy for CPU, unCPU, and package). Only runs on Linux PCs. 
- **NVIDIA SMI**: Internal power meter for NVIDIA GPUs. Only runs on Linux PCs. 

More is to come. 

## Acknowledgment
Thanks to Matthias Kränzler, Geetha Ramasubbu, and Lena Eichermüller for providing scripts and feedback. 

## References

TODO
