# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 09:48:49 2023

Launched using : ipython -i revontuli_xas.py

@author: Revontuli_admin
"""

import sys

sys.path.append("C:\\LocalData\\renebes\\borealis")

import math as m

from borealis.controller.huber import HuberSMC
from borealis.motor import Motor
from borealis.detector.ketek import KetekAXASM
from borealis.pseudo_motor import PseudoMotor

#from spellman import Spellman_uX50P50


### CONFIG PARAMETERS ###
tubex_channel = 2
tubex_offset = -21
tubex_name = "Tube translation x"

tubey_channel = 1
tubey_offset = 38
tubey_name = "Tube translation y"

tuber_channel = 3
tuber_offset = 0
tuber_name = "Tube rotation (2theta)"

monox_channel = 4
monox_offset = 400
monox_name = "Analyzer translation x"

monor_channel = 5
monor_offset = 0
monor_name = "Analyzer rotation (theta)"

### GEOMETRY ###
def geo_monor(bragg):
    return 90-bragg
    
def geo_tuber(bragg):
    return 2*(90-bragg)
 
def geo_monox(bragg):
    pos_theo =  500 * m.sin(m.radians(bragg)) 
    return pos_theo
    
def geo_tubex(bragg):
    #correction =  -9.177849451E-03*bragg*bragg*bragg + 2.007762068E+00*bragg*bragg - 1.428034314E+02*bragg + 3.259040690E+03
    correction = 0
    pos_theo = (2 * 500 * (m.sin(m.radians(bragg)) * 
                          m.cos(m.radians(bragg)) * 
                          m.cos(m.radians(bragg))) +
                          correction )
                          
                          
    return pos_theo
    
def geo_tubey(bragg):
    correction = 0
    #correction = 1.944939468E-01*bragg*bragg - 3.256010364E+01*bragg + 1.367028138E+03
    pos_theo =  ( 2 * 500 * (m.sin(m.radians(bragg)) * 
                           m.sin(m.radians(bragg)) * 
                           m.cos(m.radians(bragg))) +
                           correction )
    return pos_theo
    
### INITIALIZATION OF MOTORS ####

_ctrler = HuberSMC("192.168.2.2", 1234)

tubex = Motor(tubex_name, tubex_channel, tubex_offset, _ctrler)
tubey = Motor(tubey_name, tubey_channel, tubey_offset, _ctrler)
tuber = Motor(tuber_name, tuber_channel, tuber_offset, _ctrler)

monox = Motor(monox_name, monox_channel, monox_offset, _ctrler)
monor = Motor(monor_name, monor_channel, monor_offset, _ctrler)

### INITIALIZATION OF DETECTORS ###

INI_FILEPATH = "C:/LocalData/renebes/borealis/examples/KETEK_DPP2_usb2.ini"
det = KetekAXASM('ketek', INI_FILEPATH)

### INITIALIZATION OF PSEUDO-MOTORS ###
mono_multiaxis = PseudoMotor([monox, monor], [geo_monox, geo_monor])
tube_multiaxis = PseudoMotor([tubex, tubey, tuber], [geo_tubex, geo_tubey, geo_tuber])
theta = PseudoMotor([tubex, tubey, tuber, monox, monor], [geo_tubex, geo_tubey, geo_tuber, geo_monox, geo_monor],det)

### INITIALIZATION OF X-RAY TUBE ###
#xsrc = Spellman_uX50P50()
#xsrc.initialise("192.168.2.3", 50001)


 

