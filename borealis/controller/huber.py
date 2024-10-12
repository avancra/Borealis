# -*- coding: utf-8 -*-
"""
Huber controller SMC.

Created on Tue Jan 10 21:17:12 2023.

@author: A. Vancraeyenest
"""
import logging
import socket

from borealis.controller.controller_base import Controller

LOGGER = logging.getLogger(__name__)


class HuberSMC(Controller):
    """Class to communicate with Huber controller."""

    def __init__(self, ip_address: str, port: int = 1234, alias: str = ""):
        """Initialise the connection to the device."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_address, port))
        LOGGER.debug("Opening connection on port %d at IP address %s", port, ip_address)

        ans = self._read().decode().strip('\r\n')
        alias = alias if alias !='' else f'HuberSMC {ans}'
        super().__init__(alias=alias)
        LOGGER.info("%s successfully initialised", self)

    # -------------  Overridden methods ------------- #
    def move_axis(self, axis_id: str, target: float = 0):
        """Move a single axis to a target position."""
        self._write(f'goto{axis_id}:{target}')
        self.wait_motion_end(axis_id, target)
        LOGGER.debug("%s: Moving axis %s to %f (dial).",
                     self.alias, axis_id, target)

    def get_axis_position(self, axis_id: str):
        """Get the dial position for a single axis."""
        self._write(f'?p{axis_id}')
        pos = self._read()
        return self.decode_axis_position(pos)

    def is_axis_ready(self, axis_id: str):
        """Check that a given axis is ready (idle)."""
        status = self.get_axis_status(axis_id)['axis ready']
        if status == '1':
            LOGGER.debug("%s: axis %s ready (i.e. idle).",
                         self.alias, axis_id)
        else:
            LOGGER.debug("%s: axis %s not ready yet (i.e. not idle).",
                         self.alias, axis_id)
        return status == '1'

    def is_limit_switch_activated(self, axis_id: str):
        """Check if limit switch is active for a given axis."""
        status = self.get_axis_status(axis_id)
        if status['limit switch status'] == '0':
            return False
        else:
            if status['limit switch status'] == '1':
                # print('Limit switch [-] activated')
                LOGGER.info("%s: Limit switch [-] of axis %s activated.",
                            self.alias, axis_id)
            elif status['limit switch status'] == '2':
                # print('Limit switch [+] activated')
                LOGGER.info("%s: Limit switch [+] of axis %s activated.",
                            self.alias, axis_id)
            return True

    def set_axis_to_zero(self, axis_id: str):
        """Set axis position to 0."""
        self._write(f'zero{axis_id}')
        LOGGER.debug("%s: Axis %s position set to 0 (home).",
                     self.alias, axis_id)

    # -------------  Own methods ------------- #

    def _write(self, msg):
        """Write a message to the socket."""
        msg = bytes(f'{msg}\r\n', "utf-8")
        self._socket.send(msg)

    def _read(self, msg_length: int = 2048):
        """Receive message from the socket and return answer."""
        msg = self._socket.recv(msg_length)
        return msg

    def get_axis_error(self, axis_id: str):
        """Get error message from a given axis."""
        status = self.get_axis_status(axis_id)
        self.clean_axis_error(axis_id)
        LOGGER.debug("%s: Axis %s error: %s %s",
                     self.alias, axis_id,
                     status['error number'], status['error message'])
        return status['error number'], status['error message']

    def clean_axis_error(self, axis_id: str):
        """Clean axis related errors."""
        self._write(f'cerr{axis_id}')
        LOGGER.debug("%s: Error cleared for axis %s.",
                     self.alias, axis_id)

    def get_axis_status(self, axis_id: str):
        self._write(f'?status{axis_id}')
        stat = self._read()
        status = self.decode_axis_status(stat)
        return status

    @staticmethod
    def decode_axis_position(pos_msg):
        """Decode single axis position message."""
        pos = pos_msg.decode().strip(";\r\n").split(":")
        return float(pos[1])

    @staticmethod
    def decode_axis_status(sta_msg):
        """Decode single axis status message."""
        sta = sta_msg.decode().strip("\r\n").split(":")
        status = {'error number': sta[1],
                  'error message': sta[2],
                  'position': sta[3],
                  'encoder position': sta[4],
                  'limit switch status': sta[5],
                  'home position status': sta[6],
                  'reference position status': sta[7],
                  'axis ready': sta[8]}
        return status

