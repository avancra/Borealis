# How to use Borealis



## How to run an experiment

The user must create a configuration file to initialize all python objects 
composing the spectrometer and to establish all communication with the hardware.

An example of configuration file for a dummy spectrometer is given in 
`\examples\dummy_spectrometer.py`. This dummy spectrometer consists in one 
dummy controller, a dummy detector and a Si(12 8 4) analyzer crystal. A step 
motor "mono" is positioning the monochromator, with an offset of -3 degrees. 
A pseudo-motor "theta" moves the motor "mono" in order to reach a specific 
Bragg angle theta, according to a positioning law theta_to_mono. A 
pseudo-motor "energy" moves the pseudo-motor "theta" to the energy position 
in keV corresponding to the Bragg angle obeying the Bragg law: 

$$
energy = 12.89842 / 2 * 0.362834 * sin(\theta)
$$

$\theta$ and $energy$ are both linked to a detector, allowing to perform an 
acquisition while scanning, i.e. at each point of a user-define trajectory. 
A pseudo-motor "energy_no_det" is identical to "energy", but is linked to no 
detector.

One starts the interactive ipython session and instantiate the 
dummyspectrometer with:
```
ipython -i examples/dummy_spectrometer.py

```
Within the interactive ipython session, the user can interact with the 
spectrometer directly through call to object methods such as theta.amove() 
or energy.scan(), or via a script. A script example for an energy scan 
between 17.1 keV and 17.2 keV is given in 
`examples\script_dummy_spectrometer.py`.

This script is executed via:
```
%run -i examples/script_dummy_spectrometer.py
```
