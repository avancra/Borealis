import pickle
from array import array
from pathlib import Path

import pytest

from borealis.amptek import Status


@pytest.fixture()
def get_raw_status():
    with Path('status_data.pickle').open('rb') as fi:
        statuses = pickle.load(fi)
    return statuses['raw_status']


@pytest.fixture
def get_raw_spectrum_status():
    with Path('status_data.pickle').open('rb') as fi:
        statuses = pickle.load(fi)
    return statuses['spectrum_status']


def test_status(get_raw_status):
    raw_status = get_raw_status[6:-2]
    status = Status(raw_status)

    assert isinstance(status.serial_number, str)
    assert status.serial_number == '022098'
    assert isinstance(status.acq_time, (float, int))
