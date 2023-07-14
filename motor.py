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
        Get motor dial / user positions from controller.

        Returns
        -------
        str

        """
        logger.info("%s at %f (dial) \t %f (user). ",
                    self.motor_name, self.dial_position, self.user_position)
        return self.dial_position, self.user_position

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
        # ??? should we use below the is_ready property instead
        if self.ctrl.is_axis_ready(self.motor_id) is False:
            # TODO: Add the fact that command/movement is aborted when axis not ready.
            logger.warning("%s not ready yet (i.e. not idle).", self.motor_name)
            return

        self.ctrl.move_axis(self.motor_id, dial)
        self.ctrl.is_in_position(self.motor_id, dial)
        logger.info("%s moved to %f.", self.motor_name, self.user_position)

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
        # ??? should we use below the is_ready property instead
        if self.ctrl.is_axis_ready(self.motor_id) is False:
            # TODO: Add the fact that command/movement is aborted when axis not ready.
            logger.warning("%s not ready yet (i.e. not idle).", self.motor_name)
            return

        self.ctrl.move_axis(self.motor_id, dial)
        self.ctrl.is_in_position(self.motor_id, dial)
        logger.info("%s moved to %f.", self.motor_name, self.user_position)

    # TODO: rename to set_home/set_zero
    def set_to_zero(self):
        """Set motor current position to 0."""
        self.ctrl.set_axis_to_zero(self.motor_id)
        logger.warning("Dial position of %s reset to 0.\n"
                       "Initial dial value was %f.",
                       self.motor_name, self.dial_position)

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
        for position in np.arange(start, stop, step, dtype=np.float32):
            self.amove(position)
            if det is not None:
                assert acq_time is not None
                spectrum = det.acquisition(acq_time)
                spectra.append(spectrum)
            elif acq_time is not None:
                time.sleep(acq_time)

        return np.array(spectra)
