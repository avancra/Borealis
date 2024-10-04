import pickle
from pathlib import Path

import pytest

from borealis.detector.amptek import Status
from borealis.detector.detector_base import DummyDet, Detector


@pytest.fixture()
def get_raw_status():
    with (Path(__file__).parent /'status_data.pickle').open('rb') as fi:
        statuses = pickle.load(fi)
    return statuses['raw_status']


@pytest.fixture
def get_raw_spectrum_status():
    with  (Path(__file__).parent /'status_data.pickle').open('rb') as fi:
        statuses = pickle.load(fi)
    return statuses['spectrum_status']


def test_status(get_raw_status):
    raw_status = get_raw_status[6:-2]
    status = Status(raw_status)

    assert isinstance(status.serial_number, str)
    assert status.serial_number == '022098'
    assert isinstance(status.realtime, (float, int))
    assert status.realtime == pytest.approx(10, abs=0.5)
    assert isinstance(status.acq_time, (float, int))
    assert status.realtime == pytest.approx(10, abs=0.05)
    assert isinstance(status.fast_count, (float, int))
    assert isinstance(status.slow_count, (float, int))


def test_from_status_packet(get_raw_status):
    status = Status.from_status_packet(get_raw_status)
    assert isinstance(status.serial_number, str)
    assert status.serial_number == '022098'
    assert isinstance(status.realtime, (float, int))
    assert status.realtime == pytest.approx(10, abs=0.5)
    assert isinstance(status.acq_time, (float, int))
    assert status.realtime == pytest.approx(10, abs=0.05)
    assert isinstance(status.fast_count, (float, int))
    assert isinstance(status.slow_count, (float, int))


def test_from_spectrum_status_packet(get_raw_spectrum_status):
    status = Status.from_spectrum_status_packet(get_raw_spectrum_status, 2048)
    assert isinstance(status.serial_number, str)
    assert status.serial_number == '022098'
    assert isinstance(status.realtime, (float, int))
    assert status.realtime == pytest.approx(10, abs=0.5)
    assert isinstance(status.acq_time, (float, int))
    assert status.realtime == pytest.approx(10, abs=0.05)
    assert isinstance(status.fast_count, (float, int))
    assert isinstance(status.slow_count, (float, int))