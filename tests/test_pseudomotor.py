# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 10:18:23 2024

@author: renebes
"""

from borealis.controller.controller_base import DummyCtrl
from borealis.motor import Motor
from borealis.pseudo_motor import PseudoMotor
from borealis.detector.detector_base import DummyDet


def test_pseudomotor_const():
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 0, ctrl)
    mot2 = Motor('DummyMotor2', '2', 0, ctrl)
    geo1 = lambda x: x
    geo2 = lambda x: -x
    PseudoMotor('DummyPseudoMotor', [mot1, mot2], [geo1, geo2])

###############################################################
### Tests below are only aimed to check the console output  ###
###############################################################

def test_pseudomotor_where():
    """
    Check the output of the where method.

    The pseudomotor is first moved to a position of 42.
    Pseudomotor position in the console output is 42 (user).

    """
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 6, ctrl)
    mot2 = Motor('DummyMotor2', '2', 0, ctrl)
    geo1 = lambda x: -x
    geo2 = lambda x: x
    mot1.amove(42)
    assert mot1.dial_position == 36
    pseudo = PseudoMotor('DummyPseudoMotor', [mot1, mot2], [geo1, geo2])
    assert pseudo.position == 42
    pseudo.where()

def test_pseudomotor_where_all():
    """
    Check the output of the where_all method.

    The tested pseudomotor is composed of one pseudomotor and two motors.
    Positions in the console output are:
    Pseudomotor position is -1.00 (user).
    Motor 1 position is 0.00 (dial) | -1.00 (user)
    Motor 2 position is 0.00 (dial) |  2.00 (user)


    """
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', -1, ctrl)
    mot2 = Motor('DummyMotor2', '2', 2, ctrl)
    geo = lambda x: x
    pseudo1 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo, geo])
    pseudo2 = PseudoMotor('DummyPseudoMotor2', [pseudo1, mot1, mot2], [geo, geo, geo])
    pseudo2.where_all()

def test_pseudomotor_scan():
    """
    Check the output of the scan method.

    Two tests are performed: (1) without and (2) with a detector.

    """
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 1, ctrl)
    mot2 = Motor('DummyMotor2', '2', 2, ctrl)
    geo1 = lambda x: x
    geo2 = lambda x: 2*x
    pseudo1 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo1, geo2])
    pseudo1.scan(2, 5, .5, acq_time=.1)

    det = DummyDet()
    pseudo2 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo1, geo2], detector=det)
    pseudo2.scan(0, 5, 1, acq_time=.5)
