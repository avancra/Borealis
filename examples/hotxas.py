"""
# Launched using : ipython -i hotxas.py
"""

import sys



sys.path.append("C:\\LocalData\\HotXAS\\borealis")



import math as m



from borealis.controller.newport import NewportXPS

from borealis.motor import Motor 

#from borealis.detector.ketek import KetekAXASM

from borealis.detector.amptek import AmptekCdTe123

from borealis.pseudo_motor import PseudoMotor



### CONFIG PARAMETERS ###

tubex_channel = 'tubex'

tubex_offset = 250.2

tubex_name = "Tube translation x"

tubex_direction = False

tubex_lower_limit = -500

tubex_higher_limit = 500



tubey_channel = 'tubey'

tubey_offset = 150

tubey_name = "Tube translation y"

tubey_direction = False

tubey_lower_limit = -500

tubey_higher_limit = 500



tuber_channel = 'tuber'

tuber_offset = 0

tuber_name = "Tube rotation (2theta)"

tuber_direction = False

tuber_lower_limit = -180

tuber_higher_limit = 180



monoy_channel = 'monoy'

monoy_offset = 450

monoy_name = "Analyzer translation y"

monoy_direction = False

monoy_lower_limit = -500

monoy_higher_limit = 500



monor_channel = 'monor'

monor_offset = 0.45

monor_name = "Analyzer rotation (theta)"

monor_direction = False

monor_lower_limit = -180

monor_higher_limit = 180



revor_channel = 'revor'

revor_offset = 0

revor_name = "Crystal revolver rotation (theta)"

revor_direction = False

revor_lower_limit = -180

revor_higher_limit = 180



### INITIALIZATION OF CONTROLER ####



_ctrler = NewportXPS("192.168.2.4", 5001)





### INITIALIZATION OF MOTORS ####



tubex = Motor(tubex_name, tubex_channel, tubex_offset, _ctrler,tubex_direction,tubex_lower_limit,tubex_higher_limit)

_ctrler._xps.GroupInitialize(tubex_channel)

_ctrler._xps.GroupHomeSearch(tubex_channel)



tubey = Motor(tubey_name, tubey_channel, tubey_offset, _ctrler,tubey_direction,tubey_lower_limit,tubey_higher_limit)

_ctrler._xps.GroupInitialize(tubey_channel)

_ctrler._xps.GroupHomeSearch(tubey_channel)



tuber = Motor(tuber_name, tuber_channel, tuber_offset, _ctrler,tuber_direction,tuber_lower_limit,tuber_higher_limit)

_ctrler._xps.GroupInitialize(tuber_channel)

_ctrler._xps.GroupHomeSearch(tuber_channel)



monoy = Motor(monoy_name, monoy_channel, monoy_offset, _ctrler,monoy_direction,monoy_lower_limit,monoy_higher_limit)

_ctrler._xps.GroupInitialize(monoy_channel)

_ctrler._xps.GroupHomeSearch(monoy_channel)



monor = Motor(monor_name, monor_channel, monor_offset, _ctrler,monor_direction,monor_lower_limit,monor_higher_limit)

_ctrler._xps.GroupInitialize(monor_channel)

_ctrler._xps.GroupHomeSearch(monor_channel)



revor = Motor(revor_name, revor_channel, revor_offset, _ctrler,revor_direction,revor_lower_limit,revor_higher_limit)

_ctrler._xps.GroupInitialize(revor_channel)

_ctrler._xps.GroupHomeSearch(revor_channel)



### GEOMETRY ###

def geo_monoy(bragg):

    pos_theo =  500 * m.sin(m.radians(bragg)) 

    return pos_theo



def geo_monor(bragg):

    return 90-bragg



def geo_tubex(bragg):

    #correction = -4.295531260E-03*bragg**3 + 1.179954561E+00*bragg**2 - 1.078553012E+02*bragg + 3.280992603E+03

    correction =0

    pos_theo = (2 * 500 * (m.sin(m.radians(bragg)) * 

                          m.sin(m.radians(bragg)) * 

                          m.cos(m.radians(bragg))) +

                          correction )

                          

                          

    return pos_theo

    

def geo_tubey(bragg):

    #correction =  1.588247881E-05*bragg**5 - 5.963775618E-03*bragg**4 + 8.897755147E-01*bragg**3 - 6.596120473E+01*bragg**2 + 2.433947613E+03*bragg - 3.590774045E+04

    correction =0

    pos_theo =  ( 2 * 500 * (m.sin(m.radians(bragg)) * 

                           m.cos(m.radians(bragg)) * 

                           m.cos(m.radians(bragg))) +

                           correction )

    return pos_theo



def geo_tuber(bragg):

    return 2*(90-bragg)



### INITIALIZATION OF DETECTORS ###



#INI_FILEPATH = "C:/LocalData/HotXAS/borealis/examples/KETEK_DPP2_usb2.ini"

#det = KetekAXASM('ketek', INI_FILEPATH)

det = AmptekCdTe123('amptek')



### INITIALIZATION OF PSEUDO-MOTORS ###

mono_multiaxis = PseudoMotor([monoy, monor], [geo_monoy, geo_monor], det)

tube_multiaxis = PseudoMotor([tubex, tubey, tuber], [geo_tubex, geo_tubey, geo_tuber], det)

theta = PseudoMotor([tubex, tubey, tuber, monoy, monor], [geo_tubex, geo_tubey, geo_tuber, geo_monoy, geo_monor], det)

#theta = PseudoMotor([tubex_rev, tubey_rev, tuber, monoy, monor], [theta_to_dialX, theta_to_dialY, geo_tuber, geo_monoy, geo_monor], det)
