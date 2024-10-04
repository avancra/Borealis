# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 09:48:49 2023

When in its repository, launched using : ipython -i dummy_spectrometer.py

@author: renebes
"""

import sys
from pathlib import Path

sys.path.append((Path(__file__).absolute().parent.parent).as_posix())

import math

from borealis.controller.controller_base import DummyCtrl
from borealis.detector.detector_base import DummyDet
from borealis.motor import Motor
from borealis.pseudo_motor import PseudoMotor

##################################
### INITIALIZATION OF DETECTOR ###
##################################
det = DummyDet()

####################################
### INITIALIZATION OF CONTROLLER ###
####################################
_ctrl = DummyCtrl()

###############################
### INITIALIZATION OF MOTOR ###
###############################

mono = Motor('mono', '1', -3, _ctrl)

######################################
### INITIALIZATION OF PSEUDO-MOTOR ###
######################################

def theta_to_mono(angle):
    """
    Convert Bragg angle into monochromator position

    """
    position = 90 - angle
    return position

def theta_pos_law(motor_list):
    angle = motor_list[0].user_position
    position = angle + 90
    return position

theta = PseudoMotor('theta', [mono], [theta_to_mono],
                      position_law= theta_pos_law, detector=det)

# Si(12 8 4) has a d_hkl of 0.362834 Å
d_hkl = 0.362834

def theta_to_energy(angle, d_hkl = d_hkl):
    """
    Convert Bragg angle into energy following Bragg's law.

    Parameters
    ----------
    angle : float
        Bragg angle, in degrees.

    Returns
    -------
    energy : float
        Energy diffracted by the analyzer, in keV.

    """
    energy = 12.39842 / (2 * d_hkl * math.sin(angle * math.pi / 180))
    return energy

def energy_to_theta(energy, d_hkl = d_hkl):
    """
    Convert energy to Bragg angle following Bragg's law.

    Parameters
    ----------
    energy : Float
        Energy diffracted by the analyzer, in keV.

    Returns
    -------
    angle : float
        Bragg angle, in degrees.

    """
    angle = math.asin(12.39842 / (2 * d_hkl * energy)) * 180 / math.pi
    return angle

def energy_pos_law(motor_list):
    angle = motor_list[0].user_position
    return theta_to_energy(angle)


energy = PseudoMotor('energy', [theta], [energy_to_theta],
                      position_law= energy_pos_law, detector=det)

energy_nodet = PseudoMotor('energy (no detector)', [theta], [energy_to_theta],
                           position_law=energy_pos_law)
