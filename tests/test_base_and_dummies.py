import pytest

from borealis.controller.controller_base import DummyCtrl, Controller
from borealis.detector.detector_base import DummyDet, Detector


def test_controller_base():
    """The base class can not be instantiated."""
    with pytest.raises(TypeError):
        Controller(alias='detector')


def test_dummy_controller():
    """Check basic functionality of DummyCtrl."""
    ctrl = DummyCtrl()
    ctrl = DummyCtrl(alias="Such a Dummy")

    ctrl.move_axis(axis_id=1, target=10.)
    current_pos = ctrl.get_axis_position(axis_id=1)
    assert current_pos == 10.

    # with pytest.raises(ValueError):
    ctrl.get_axis_position(axis_id=2)


def test_detector_base():
    """The base class can not be instantiated."""
    with pytest.raises(TypeError):
        Detector('detector')


def test_dummy_detector():
    """Check basic functionality of Dummy detector."""
    det = DummyDet()
    det = DummyDet('DummyAlias')
    det.acquisition(5)