from borealis.controller.huber import HuberSMC


def test_decode_axis_status():
    sta_msg = b'1:42:Error Message:66.6:0:0:0:0:1:0:0:0:0:0:0:0:0\r\n\r\n'
    status = HuberSMC.decode_axis_status(sta_msg)
    assert isinstance(status, dict)
    assert 'limit switch status' in status
    assert status['position'] == '66.6'
    assert status['error number'] == '42'
    assert status['error message'] == 'Error Message'
    assert status['axis ready'] == '1'


def test_decode_axis_position():
    pos_msg = b'42:66.6;\r\n'
    position = HuberSMC.decode_axis_position(pos_msg)
    assert isinstance(position, float)
    assert position == 66.6
