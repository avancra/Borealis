# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""
import time
import logging
from math import inf

import numpy as np

from borealis.controller import Controller
from borealis.detector import Detector

LOGGER = logging.getLogger(__name__)


class Motor:
    """Motor generic class."""

    def __init__(self, alias: str, motor_id: str, motor_offset: float, controller: Controller,
                 positive_direction: bool = True, soft_limit_pos:  float = inf, soft_limit_neg: float = -inf):
        self.motor_name = alias
        self.motor_id = motor_id
        self.offset = motor_offset
        self._direction_coeff = -1 if positive_direction is False else 1
        self._limit_pos = soft_limit_pos
        self._limit_neg = soft_limit_neg
        self._controller = controller
        self._dial_position = self._controller.get_axis_position(self.motor_id)
        self._user_position = self.dial_position + self.offset
        self._is_ready = self._controller.is_axis_ready(self.motor_id)

    @property
    def dial_position(self):
        # TODO: add logging ?? is it necessary?
        return self._controller.get_axis_position(self.motor_id)

    @property
    def user_position(self):
        # TODO: add logging ?? is it necessary?
        return self.dial_position * self._direction_coeff + self.offset

    @property
    def is_ready(self):
        return self._controller.is_axis_ready(self.motor_id)

    @property
    def movement_direction(self):
        return "Pos(+)" if self._direction_coeff == 1 else "Neg(-)"

    def where(self):
        """
        Print motor dial / user positions from controller.

        Returns
        -------
        str

        """
        print('{} at : {:6.2f} (dial) | {:6.2f} (user)'.format(self.motor_name, self.dial_position, self.user_position))

    def _check_is_ready(self):
        # TODO: change to MotorNotReady error once available
        if self.is_ready is False:
            LOGGER.exception('Command interrupted due to motor not ready yet (i.e. not idle).')
            raise RuntimeError('Command interrupted due to motor not ready yet (i.e. not idle).')

    def _check_soft_limits(self, dial):
        try:
            assert self._limit_neg <= dial <= self._limit_pos
        except AssertionError as exc:
            LOGGER.exception(
                'SOFT LIMIT ERROR: the dial position %f is outside the available soft limit range',dial)
            raise RuntimeError(f'SOFT LIMIT ERROR: the dial position {dial} is outside the available soft limit range') from None

    def amove(self, user_position: float):
        """
        Move the motor to a new position (user) in absolute scale.

        Parameters
        ----------
        user_position : float
            New position (user) to move the motor to.

        Returns
        -------
        None.

        """
        self._check_is_ready()

        dial = (user_position - self.offset) / self._direction_coeff
        self._check_soft_limits(dial)

        self._controller.move_axis(self.motor_id, dial)
        self._controller.wait_motion_end(self.motor_id, dial)
        LOGGER.debug("%s moved to %f.", self.motor_name, self.user_position)


    def rmove(self, rel_position: float):
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

        dial = self.dial_position + rel_position * self._direction_coeff
        self._check_soft_limits(dial)

        self._controller.move_axis(self.motor_id, dial)
        self._controller.wait_motion_end(self.motor_id, dial)
        LOGGER.debug("%s moved to %f.", self.motor_name, self.user_position)

    def scan(self, start: float, stop: float, step: int, det: Detector = None, acq_time: float = None):
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
            except RuntimeError as exc:  # TODO: check separately MotorNotReady and SoftLimitError errors once available
                LOGGER.exception("Scan interrupted at position %f", position)
                raise RuntimeError(f"Scan interrupted at position {position}") from exc

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
        LOGGER.warning("Dial position of %s reset to 0.\n"
                       "Initial dial value was %f.",
                       self.motor_name, self.dial_position)
