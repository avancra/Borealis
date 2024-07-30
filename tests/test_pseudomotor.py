# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 10:18:23 2024

@author: renebes
"""
import math

import pytest

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
    position_law = lambda x: x[0].user_position
    PseudoMotor('DummyPseudoMotor', [mot1, mot2], [geo1, geo2], position_law)


def test_pseudomotor_move():
    """
    Check  the move method.

    The tested pseudomotor is composed of one pseudomotor and two motors.
    The first motor position is checked.
    The second motor position is checked to be
    Pseudomotor position in the console output is  (user).

    """
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', -1, ctrl)
    mot1.amove(3)
    assert mot1.dial_position == 4
    assert mot1.user_position == 3

    mot2 = Motor('DummyMotor2', '2', 2, ctrl)
    mot2.amove(2)
    assert mot2.dial_position == 0
    assert mot2.user_position == 2

    geo1 = lambda x: x
    geo2 = lambda x: 10 * x
    position_law = lambda x: x[0].user_position
    pseudo1 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo1, geo2], position_law)
    pseudo1.amove(10)

    assert mot1.user_position == 10
    assert mot1.dial_position == 11
    assert mot2.user_position == 100
    assert mot2.dial_position == 98

    geo3 = lambda x: x
    pseudo2 = PseudoMotor('DummyPseudoMotor2', [pseudo1], [geo3], position_law)
    pseudo2.amove(42)
    assert pseudo1.user_position == 42
    assert pseudo2.user_position == 42
    assert mot1.user_position == 42
    assert mot1.dial_position == 43
    assert mot2.user_position == 420
    assert mot2.dial_position == 418


def test_postion_law_conversion():
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 0, ctrl)
    mot2 = Motor('DummyMotor2', '2', 0, ctrl)
    geo1 = lambda x: x * math.cos(math.pi / 3)  # PM(user) -> M(user)
    geo2 = lambda x: x * math.sin(math.pi / 3)
    pos_law = lambda x: math.sqrt(x[0].user_position ** 2 + x[1].user_position ** 2)
    pseudo = PseudoMotor("pseudo", [mot1, mot2], [geo1, geo2], position_law=pos_law)

    pseudo.amove(1)
    assert mot1.user_position == pytest.approx(0.5)
    assert mot2.user_position == pytest.approx(math.sqrt(3) / 2)
    assert pseudo.user_position == pytest.approx(1)

    # Simulate Theta and Energy pseudo-motors for Si999 crystal
    geo1 = lambda x: math.cos(x * math.pi / 180)
    geo2 = lambda x: math.sin(x * math.pi / 180)
    pos_law = lambda x: math.acos(x[0].user_position) * 180 / math.pi
    pm_theta = PseudoMotor("pseudo", [mot1, mot2], [geo1, geo2], position_law=pos_law)

    pm_theta.amove(45)
    assert mot1.user_position == pytest.approx(math.sqrt(2) / 2)
    assert mot2.user_position == pytest.approx(math.sqrt(2) / 2)
    assert pm_theta.user_position == pytest.approx(45)

    d_si999 = 0.34836
    theta_to_energy = lambda x: 12.39842 / (2 * d_si999 * math.sin(x[0].user_position * math.pi / 180))
    energy_to_theta = lambda x: math.asin(12.39842 / (2 * d_si999 * x)) * 180 / math.pi

    pm_energy = PseudoMotor('energy', [pm_theta], [energy_to_theta],
                            position_law=theta_to_energy)
    pm_energy.amove(18.42)
    assert pm_theta.user_position == pytest.approx(75.0368)
    assert pm_energy.user_position == pytest.approx(18.42)

    pm_energy.scan(18.4, 18.5, 0.01, acq_time=0.1)


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
    position_law = lambda x: x[0].user_position
    pseudo = PseudoMotor('DummyPseudoMotor', [mot1, mot2], [geo1, geo2], position_law)
    assert pseudo.user_position == 42
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
    position_law = lambda x: x[0].user_position
    pseudo1 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo, geo],position_law)
    pseudo2 = PseudoMotor('DummyPseudoMotor2', [pseudo1, mot1, mot2], [geo, geo, geo], position_law)
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
    geo2 = lambda x: 2 * x
    position_law = lambda x: x[0].user_position
    pseudo1 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo1, geo2], position_law)
    pseudo1.scan(2, 5, .5, acq_time=.1)

    det = DummyDet()
    pseudo2 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo1, geo2], position_law, detector=det)
    pseudo2.scan(0, 5, 1, acq_time=.5)
