# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""
import time

import numpy as np


class Motor():
    """Motor generic class."""

    def __init__(self, motor_name, motor_id, motor_offset, controller):
        self.motor_name = motor_name
        self.motor_id = motor_id
        self.offset = motor_offset
        self.ctrl = controller
        self._dial_position = self.ctrl.get_axis_position(self.motor_id)
        self._user_position = self.dial_position + self.offset
        self._is_ready = False
        #TODO! self.limits =

    @property
    def dial_position(self):
        # TODO: add logging
        return self.ctrl.get_axis_position(self.motor_id)

    @property
    def user_position(self):
        # TODO: add logging
        return self.dial_position + self.offset

    @property
    def is_ready(self):
        return self.ctrl.is_axis_ready(self.motor_id)

    def position(self):
        """
        Get motor dial position from controller.

        Returns
        -------
        str

        """
        return (f'{self.motor_name} at: \n'
                f'\t dial:  {self.dial_position} \n'
                f'\t user: {self.user_position}')

    def amove(self, user_position):
        """
        Move the motor to a new position (user) in absolute scale.

        Parameters
        ----------
        new_position : float
            New position (user) to move the motor to.

        Returns
        -------
        None.

        """
        dial = user_position - self.offset

        if self.ctrl.is_axis_ready(self.motor_id) is False:
            # TODO: Tranform into logging
            print(f'{self.motor_name} not ready yet (i.e. not idle).')
            return

        self.ctrl.move_axis(self.motor_id, dial)
        self.ctrl.is_in_position(self.motor_id, dial)

    def rmove(self, rel_position):
        """
        Move the motor by a relative position.

        Parameters
        ----------
        rel_position : float
            Relative value to move the motor by.

        Returns
        -------
        None.

        """
        dial = self.dial_position + rel_position
        if self.ctrl.is_axis_ready(self.motor_id) is False:
            # TODO: Tranform into
            print(f'{self.motor_name} not ready yet (i.e. not idle).')
            return

        self.ctrl.move_axis(self.motor_id, dial)
        self.ctrl.is_in_position(self.motor_id, dial)

    # TODO: rename to set_home/set_zero
    def set_to_zero(self):
        """Set motor current position to 0."""
        self.ctrl.set_axis_to_zero(self.motor_id)
        print(f'{self.motor_name} position set to 0. \n'
              f'Initial value was {self.dial_position}.')

    def scan(self, start, stop, step, det=None, acq_time=None):
        """
        Scan, with or without acquisition. Acquisition requires det and acq_time.

        Parameters
        ----------
        start : float
        stop : float
        step : float
        det : borealis.Detector
            if not None, acquisition is done at each motor position.
        acq_time : float
            if not None, btu det is None, will sleep for this time.

        Returns
        -------
        spectra : ndarray
        """
        spectra = []
        for position in np.arange(start, stop, step):
            self.amove(position)
            if det is not None:
                assert acq_time is not None
                spectrum = det.acquisition(acq_time)
                spectra.append(spectrum)
            elif acq_time is not None:
                time.sleep(acq_time)

        return np.array(spectra)
