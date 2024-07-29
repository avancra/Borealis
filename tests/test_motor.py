import pytest

from borealis.controller.controller_base import DummyCtrl
from borealis.exceptions import SoftLimitError
from borealis.motor import Motor
from borealis.detector.detector_base import DummyDet


def test_motor_const():
    ctrl = DummyCtrl()
    Motor('DummyMotor', '1', 0, ctrl)


def test_motor_soft_limits():
    ctrl = DummyCtrl()

    mot = Motor('DummyMotor', '1', 0, ctrl)
    mot.amove(10)

    mot = Motor('DummyMotor', '1', 0, ctrl, soft_limit_low=5, soft_limit_high=20)
    mot.amove(10)
    with pytest.raises(SoftLimitError):
        mot.amove(50)

    mot = Motor('DummyMotor', '1', 0, ctrl, soft_limit_low=5, soft_limit_high=20, positive_direction=False)
    with pytest.raises(SoftLimitError):
        mot.amove(10)

    mot.set_current_as_zero()

def test_motor_where():
    ctrl = DummyCtrl()
    mot = Motor('DummyMotor', '1', 0, ctrl)
    mot.amove(10)
    mot.where()

def test_motor_scan():
    ctrl = DummyCtrl()
    mot = Motor('DummyMotor', '1', 0, ctrl)
    mot.scan(1, 10, 1)
    mot.scan(2, 5, .5, acq_time=.1)
    det = DummyDet()
    mot.scan(0, 5, 1, acq_time=.5, det=det)