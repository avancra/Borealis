# -*- coding: utf-8 -*-
"""
Hubert controller SMC.

Created on Tue Jan 10 21:17:12 2023.

@author: A. Vancraeyenest
"""
import socket

from controller import Controller


class HubertSMC(Controller):
    """Class to communicate with Hubert controller."""

    def __init__(self):
        self._socket = None

    def initialise(self, ip_adress, port=1234):
        """Initialise the connection to the device."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_adress, port))

    def _write(self, msg):
        """Write a message to the socket."""
        msg = bytes(f'{msg}\r\n', "utf-8")
        print(f'{msg=}')
        sent = self._socket.send(msg)
        print(f'{sent=}')

    def _read(self, msg_length=2048):
        """Receive message from the socket and return answer."""
        msg = self._socket.recv(msg_length)
        print(f'{msg=}')
        return msg

    def move(self, axis_id, position=0):
        """Send instruction to move an axis."""
        self._socket._write(f'goto{axis_id}:{position}')

    def get_axis_position(self, axis_id=""):
        """Get controller position."""
        self._write(f'?p{axis_id}')
        pos = self._read()
        positions = self.decode_position(pos)
        if axis_id:
            return positions[axis_id]
        else:
            #TODO! Generate the results for all motors (where_all functions)
            pass

    @staticmethod
    def decode_position(pos):
        """Decode position message."""
        positions = {}
        for item in pos.decode().strip(";\r\n").split(";"):
            axis_id, posit = item.split(":")
            positions[axis_id] = float(posit)
        return positions

    def set_zero(self, axis_id=""):
        """Set axis position to 0."""
        self._write(f'zero{axis_id}')
        #TODO! Consider log message when setting axis to 0.
        # if axis_id:
        #     print(f'Axis {axis_id} position set to 0.')
        # else:
        #     print('All axis position set to 0.')

if __name__ == "__main__":
    sock = HubertSMC()
    sock.initialise("192.168.2.2", 1234)
    sock._read()
    sock._write("?")
    sock._read()
    sock._write("?p")
    sock._read()
    sock.get_motor_position(9)
    sock.move(9, 8.42)
    sock.get_motor_position(9)
