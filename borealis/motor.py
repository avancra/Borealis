# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""
import time
import logging

import numpy as np

logger = logging.getLogger(__name__)

class Motor():
    """Motor generic class."""

    def __init__(self, alias, motor_id, motor_offset, controller):
        self.motor_name = alias
        self.motor_id = motor_id
        self.offset = motor_offset
        self._controller = controller
        self._dial_position = self._controller.get_axis_position(self.motor_id)
        self._user_position = self.dial_position + self.offset
        self._is_ready = self._controller.is_axis_ready(self.motor_id)
        #TODO! self.limits =

    @property
    def dial_position(self):
        # TODO: add logging
        return self._controller.get_axis_position(self.motor_id)

    @property
    def user_position(self):
        # TODO: add logging
        return self.dial_position + self.offset

    @property
    def is_ready(self):
        return self._controller.is_axis_ready(self.motor_id)

    def position(self):
        """
        Get motor dial / user positions from controller.

        Returns
        -------
        str

        """
        logger.info("%s at %f (dial) \t %f (user). ",
                    self.motor_name, self.dial_position, self.user_position)
        return self.dial_position, self.user_position

    def _check_is_ready(self):
        # TODO: change to MotorNotReady error once available
        if self.is_ready is False:
            logger.error("Command interrupted due to motor not ready yet (i.e. not idle).")
            raise RuntimeError(f"Command interrupted due to motor not ready yet (i.e. not idle).")

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
        self._check_is_ready()

        dial = user_position - self.offset

        self._controller.move_axis(self.motor_id, dial)
        self._controller.is_in_position(self.motor_id, dial)
        logger.debug("%s moved to %f.", self.motor_name, self.user_position)

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
        self._check_is_ready()

        dial = self.dial_position + rel_position

        self._controller.move_axis(self.motor_id, dial)
        self._controller.is_in_position(self.motor_id, dial)
        logger.debug("%s moved to %f.", self.motor_name, self.user_position)

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
        self._check_is_ready()

        mcas = []
        for position in np.arange(start, stop, step, dtype=np.float32):
            try:
                self.amove(position)
            except RuntimeError:  # TODO: change to MotorNotReady error once available
                logger.error("Scan interrupted at position %f due to motor not being ready yet (i.e. not idle).", position)
                raise RuntimeError(f"Scan interrupted at position {position} due to motor not being ready yet (i.e. not idle).")

            if det is not None:
                assert acq_time is not None
                spectrum = det.acquisition(acq_time)
                mcas.append(spectrum)
            elif acq_time is not None:
                time.sleep(acq_time)

        return np.array(mcas)

    # TODO: rename to set_home/set_zero
    def set_to_zero(self):
        """Set motor current position to 0."""
        self._controller.set_axis_to_zero(self.motor_id)
        logger.warning("Dial position of %s reset to 0.\n"
                       "Initial dial value was %f.",
                       self.motor_name, self.dial_position)