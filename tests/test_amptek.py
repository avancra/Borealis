import pytest

from borealis.amptek import Status

@pytest.mark.xfail(reason="missing status test value")
def test_status():
    # TODO: get a real raw_status value
    raw_status = []
    status = Status(raw_status)

    assert isinstance(status.serial_number, str)
    assert status.serial_number == '022098'
    assert isinstance(status.acq_time, float)
