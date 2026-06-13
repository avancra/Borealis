import pytest
from unittest.mock import MagicMock, call
import numpy as np

from borealis.orchestrator import Orchestrator
from borealis.data_structures import DeviceInfo


class MockSensor:
    def __init__(self, alias="S1"):
        self.alias = alias

    def get_device_info(self):
        return DeviceInfo(alias= self.alias, metadata={'data': 'test'})

    def acquisition(self, acquisition_time):
        # Fake acquisition result
        mock = MagicMock()
        mock.counts = np.array([1, 2, 3])
        return mock


class MockController:
    def __init__(self, name="motor"):
        self.alias = name
        self.user_position = 0

    def get_device_info(self):
        return DeviceInfo(alias= self.alias, metadata={'data': 'test'})

    def amove(self, pos):
        self.user_position = pos


class MockDataManager:
    def __init__(self):
        self.receive = MagicMock()


# ---------------------------------------------------------
# Tests for adding components
# ---------------------------------------------------------

def test_add_controller_component_success():
    orch = Orchestrator()
    ctrl = MockController()

    orch.add_controller_component(ctrl)

    assert ctrl in orch.controllers


def test_add_controller_component_missing_method():
    orch = Orchestrator()

    class BadComponent:
        pass

    with pytest.raises(AttributeError):
        orch.add_controller_component(BadComponent())


def test_add_sensor_component_success():
    orch = Orchestrator()
    sensor = MockSensor()

    orch.add_sensor_component(sensor)

    assert sensor in orch.sensors


def test_add_data_component():
    orch = Orchestrator()
    dm = MockDataManager()

    orch.add_data_component(dm)

    assert dm in orch.data_managers


# ---------------------------------------------------------
# notify() behavior
# ---------------------------------------------------------

def test_notify_scan_calls_scan_method(monkeypatch):
    orch = Orchestrator()
    orch.scan = MagicMock()

    orch.notify(sender="X", message="Scan", scan_points=[1, 2], acq_times=[0.1, 0.1])

    orch.scan.assert_called_once_with("X", [1, 2], [0.1, 0.1])


def test_notify_scan_missing_arguments():
    orch = Orchestrator()

    with pytest.raises(AttributeError):
        orch.notify(sender="X", message="Scan")


# ---------------------------------------------------------
# scan() behavior
# ---------------------------------------------------------

def test_scan_runs_full_cycle():
    orch = Orchestrator()

    # Components
    sensor = MockSensor(alias="S1")
    ctrl = MockController(name="motor")
    dm = MockDataManager()

    orch.add_sensor_component(sensor)
    orch.add_controller_component(ctrl)
    orch.add_data_component(dm)

    scan_points = [0.0, 1.0]
    acq_times = [1.0, 2.0]

    orch.scan(sender=ctrl, scan_points=scan_points, acq_times=acq_times)

    # Data manager should receive:
    # 1× new_scan
    # 2× new_scan_point
    # 1× close_scan
    calls = [c[0][0] for c in dm.receive.call_args_list]

    assert calls.count("new_scan") == 1
    assert calls.count("new_scan_point") == 2
    assert calls.count("close_scan") == 1


def test_scan_motor_runtime_error_propagates():
    orch = Orchestrator()

    class BadMotor(MockController):
        def amove(self, pos):
            raise RuntimeError("Motor stuck")

    bad_motor = BadMotor()
    orch.add_controller_component(bad_motor)

    with pytest.raises(RuntimeError):
        orch.scan(bad_motor, scan_points=[1, ], acq_times=[0.0, ])


def test_scan_error_length_not_matching():
    orch = Orchestrator()
    ctrl = MockController(name="motor")

    with pytest.raises(ValueError):
        orch.scan(sender=ctrl, scan_points=[1, 2, 3], acq_times=[0.1, 0.1])

# ---------------------------------------------------------
# notify_data_managers()
# ---------------------------------------------------------

def test_notify_data_managers_calls_receive():
    orch = Orchestrator()
    dm1 = MockDataManager()
    dm2 = MockDataManager()

    orch.add_data_component(dm1)
    orch.add_data_component(dm2)

    orch.notify_data_managers("event", {"x": 1})

    dm1.receive.assert_called_once_with("event", x=1)
    dm2.receive.assert_called_once_with("event", x=1)
