# -*- coding: utf-8 -*-
"""
Huber controller SMC.

Created on Tue Jan 10 21:17:12 2023.

@author: A. Vancraeyenest
"""
import socket
import pytest
import time

from borealis.controller import Controller


class HuberSMC(Controller):
    """Class to communicate with Huber controller."""

    def __init__(self):
        self._socket = None

    def initialise(self, ip_adress, port=1234):
        """Initialise the connection to the device."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_adress, port))
        msg = self._read().decode().strip('\r\n')
        print(f'Controller Huber {msg} successfully initialised')

    def _write(self, msg):
        """Write a message to the socket."""
        msg = bytes(f'{msg}\r\n', "utf-8")
        #print(f'{msg=}')
        self._socket.send(msg)

    def _read(self, msg_length=2048):
        """Receive message from the socket and return answer."""
        msg = self._socket.recv(msg_length)
        #print(f'{msg=}')
        return msg

    def move_axis(self, axis_id, target=0):
        """Send instruction to move an axis to a target position."""
        self._write(f'goto{axis_id}:{target}')
        self.is_in_position(axis_id, target)

    def get_axis_position(self, axis_id):
        """Get the axis dial position."""
        if axis_id == 0:
            self._write('?p')
            pos = self._read()
            positions = self.decode_position(pos)
            return positions
        else:
            self._write(f'?p{axis_id}')
            pos = self._read()
            positions = self.decode_position(pos)
            return positions[f'{axis_id}']

    def set_axis_to_zero(self, axis_id=""):
        """Set axis position to 0."""
        self._write(f'zero{axis_id}')
        #TODO! Consider log message when setting axis to 0.
        # if axis_id:
        #     print(f'Axis {axis_id} position set to 0.')
        # else:
        #     print('All axis position set to 0.')

    def is_in_position(self, axis_id, target, timeout=60):
        """
        Check that the axis has reached its target position.

        Parameters
        ----------
        target : float
            Position (dial) the axis must reach.
        timeout : float, optional
            Time limit for the axis movement to be done, in seconds.
            The default is 60 seconds.

        Raises
        ------
        TimeoutError
            Error when axis does not reach its target position in due time.

        Returns
        -------
        None.

        """
        sleep_for = 0.1  # sec
        start_time = time.time()
        while True:
            current = self.get_axis_position(axis_id)
            if current == pytest.approx(target, abs=5e-4):
                break

            if not self.is_limit_switch_activated(axis_id):
                break

            if (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Axis never reached target position. Stopped at {current})")

            time.sleep(sleep_for)

    def is_axis_ready(self, axis_id):
        """Check that a given axis is ready (idle)."""
        status = self.get_axis_status(axis_id)['axis ready']
        return status == '1'

    def get_axis_error(self, axis_id):
        """Get error message from a given axis."""
        status = self.get_axis_status(axis_id)
        self.clean_axis_error(axis_id)
        return (status['error number'], status['error message'])

# alternative using directky ?err command: return error number and message in one string for now
    # def get_axis_error(self, axis_id):
    #     """Get error message from a given axis"""
    #     self._write(f'err{axis_id}')
    #     error = self.decode_error(self._read())
    #     self.clean_axis_error(axis_id)
    #     return error[axis_id]


    def clean_axis_error(self, axis_id=""):
        """Clean axis related errors."""
        self._write(f'cerr{axis_id}')

    def is_limit_switch_activated(self, axis_id):
        """Check if limit switch is active for a given axis."""
        status = self.get_axis_status(axis_id)
        if status['limit switch status'] == '0':
            return False
        else:
            if status['limit switch status'] == '1':
                print('Limit switch [-] activated')
            elif status['limit switch status'] == '2':
                print('Limit switch [+] activated')
            return True

    def get_axis_status(self, axis_id=""):
        self._write(f'?status{axis_id}')
        stat = self._read()
        status = self.decode_status(stat)
        if axis_id:
            return status[axis_id]
        else:
            return status

    @staticmethod
    def decode_position(pos):
        """Decode position message."""
        positions = {}
        for item in pos.decode().strip(";\r\n").split(";"):
            axis_id, posit = item.split(":")
            positions[axis_id] = float(posit)
        return positions

    @staticmethod
    def decode_status(sta):
        """Decode status message."""
        status = {}
        for item in sta.decode().split("\r\n"):
            axis_id, st = item.split(":")
            status[axis_id] = {'error number': st[1],
                               'error message': st[2],
                               'position': st[3],
                               'encoder position': st[4],
                               'limit switch status': st[5],
                               'home position status': st[6],
                               'reference position status': st[7],
                               'axis ready': st[8] }
        return status

    # @staticmethod
    # def decode_error(err):
    #     """Decode error message"""
    #     error =  {}
    #     for item in err.decode().strip("\r\n"):
    #         axis_id, er = item.split(":")
    #         error[axis_id] = er
    #     return error


if __name__ == "__main__":
    sock = HuberSMC()
    sock.initialise("192.168.2.2", 1234)
    sock._read()
    sock._write("?")
    sock._read()
    sock._write("?p")
    sock._read()
    sock.get_motor_position(9)
    sock.move(9, 8.42)
    sock.get_motor_position(9)
