import pytest

from borealis.controller.controller_base import DummyCtrl
from borealis.exceptions import SoftLimitError
from borealis.motor import Motor


def test_motor_const():
    ctrl = DummyCtrl()
    Motor('DummyMotor', '1', 0, ctrl)


def test_motor_soft_limits():
    ctrl = DummyCtrl()

    mot = Motor('DummyMotor', '1', 0, ctrl, soft_limit_low=5, soft_limit_high=20)
    mot.amove(10)
    with pytest.raises(SoftLimitError):
        mot.amove(50)

    mot = Motor('DummyMotor', '1', 0, ctrl, soft_limit_low=5, soft_limit_high=20, positive_direction=False)
    with pytest.raises(SoftLimitError):
        mot.amove(10)

    mot.set_current_as_zero()
