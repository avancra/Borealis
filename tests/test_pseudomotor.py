# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 10:18:23 2024

@author: renebes
"""

from borealis.controller.controller_base import DummyCtrl
from borealis.motor import Motor
from borealis.pseudo_motor import PseudoMotor


def test_pseudomotor_const():
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 0, ctrl)
    mot2 = Motor('DummyMotor2', '2', 0, ctrl)
    geo1 = lambda x: x
    geo2 = lambda x: -x
    PseudoMotor('DummyPseudoMotor', [mot1, mot2], [geo1, geo2])

def test_pseudomotor_where():
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 0, ctrl)
    mot2 = Motor('DummyMotor2', '2', 0, ctrl)
    geo1 = lambda x: -x
    geo2 = lambda x: x
    mot1.amove(42)
    pseudo = PseudoMotor('DummyPseudoMotor', [mot1, mot2], [geo1, geo2])
    pseudo.where()

def test_pseudomotor_where_all():
    ctrl = DummyCtrl()
    mot1 = Motor('DummyMotor1', '1', 1, ctrl)
    mot2 = Motor('DummyMotor2', '2', 2, ctrl)
    geo1 = lambda x: x
    geo2 = lambda x: 2*x
    pseudo1 = PseudoMotor('DummyPseudoMotor1', [mot1, mot2], [geo1, geo2])
    geo3 = lambda x: 10*x
    pseudo2 = PseudoMotor('DummyPseudoMotor2', [pseudo1, mot1, mot2], [geo3, geo1, geo2])
    mot1.amove(-3)
    mot2.amove(4)
    pseudo2.where_all()


