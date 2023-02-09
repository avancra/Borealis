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

    def move(self, motor_id, position=0):
        """Send instruction to move a motor."""
        self._socket._write(f'goto{motor_id}:{position}')

    def get_motor_position(self, motor_id):
        """Get motor position."""
        self._socket._write(f'?p{motor_id}')
        self._read()


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
