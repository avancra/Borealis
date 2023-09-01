from borealis.amptek import Status


def test_status():
    raw_status = []
    status = Status(raw_status)

    assert isinstance(status.serial_number, str)
    assert status.serial_number == '022098'
    assert isinstance(status.acq_time, float)
