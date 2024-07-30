# Borealis

Control and acquisition software for X-ray emission and absorption spectrometers.

## Purpose

The purpose of this software is to provide the required tools to control all
components of the spectrometer (i.e. motors and their controllers, X-ray source
 and detectors) in order to perform an acquisition (i.e. scan).

## Installation

Clone the repository to get a copy of the source code:
```
git clone https://github.com/avancra/Borealis.git
cd Borealis
```
Conda environment requirements are given in env.yml file.

## How to run an experiment

The user must create a configuration file to initialize all python objects
composing the spectrometer and to establish all communication with the hardware.

An example of configuration file for a dummy spectrometer is given in
\examples\dummy_spectrometer.py.
This dummy spectrometer consists in one dummy controller, a dummy detector and
a Si(12 8 4) analyzer crystal.
A step motor theta is positionning the spectrometer at a specific Bragg angle theta.
A pseudo-motor energy moves the motor theta to the energy position in keV corresponding
to the Bragg angle obeying the Bragg law:
energy = 12.89842 / 2 * 0.362834 * sin(theta)

One starts the interactive ipython session and instantiate the dummy spectrometer with:
```
ipython -i examples/dummy_spectrometer.py

```
Within the interactive ipython session, the user can interact with the spectrometer
directly through call to object methods such as theta.amove() or energy.scan(),
or via a script. A script example for an energy scan between 17.1 keV and 17.2 keV
is given in examples\script_dummy_spectrometer.py.
This script is executed via:
```
%run -i examples/script_dummy_spectrometer.py
```
