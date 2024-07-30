# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""
import time
import logging
from math import inf

import numpy as np

from borealis.controller.controller_base import Controller
from borealis.detector.detector_base import Detector
from borealis.exceptions import SoftLimitError, NotReadyError

LOGGER = logging.getLogger(__name__)


class Motor:
    """Motor generic class."""

    def __init__(self, alias: str, motor_id: str, motor_offset: float, controller: Controller,
                 positive_direction: bool = True, soft_limit_low:  float = -inf, soft_limit_high: float = inf):
        self._controller = controller
        self.motor_name = alias
        self.motor_id = motor_id
        self.offset = motor_offset
        self._direction_coeff = -1 if positive_direction is False else 1
        self._limit_low = soft_limit_low
        self._limit_high = soft_limit_high
        self._dial_position = self._controller.get_axis_position(self.motor_id)
        self._user_position = self.dial_position + self.offset
        self._is_ready = self._controller.is_axis_ready(self.motor_id)
        LOGGER.info("Motor %s created.", self.motor_name)

    def log(self, level, msg, *args, **kwargs):
        """Log a message with prepending the device's alias in front of the message."""
        kwargs['stacklevel'] = 2
        LOGGER.log(level, f'{self.motor_name}: {msg}', *args, **kwargs)

    @property
    def dial_position(self):
        return self._controller.get_axis_position(self.motor_id)

    @property
    def user_position(self):
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
            self.log(logging.ERROR, 'Command interrupted due to motor not ready yet (i.e. not idle).')
            # LOGGER.error('Command interrupted due to motor not ready yet (i.e. not idle).')
            raise NotReadyError(self.motor_name)

    def check_soft_limits(self, dial: float) -> None:
        """
        Check if dial value is within the limits (inclusive).

        Parameters
        ----------
        dial : float
            Target position in dial unit.

        Raises
        ------
        SoftLimitError when dial is outside the allowed range.
        """
        try:
            assert self._limit_low <= dial <= self._limit_high
        except AssertionError:
            self.log(logging.ERROR, 'Soft Limit Error: the dial position %.2f is outside the available soft limit range [%.2f : %.2f]', dial, self._limit_low, self._limit_high)
            raise SoftLimitError(dial, self.motor_name, self._limit_low, self._limit_high)

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
        self.check_soft_limits(dial)

        self._controller.move_axis(self.motor_id, dial)
        self._controller.wait_motion_end(self.motor_id, dial)
        self.log(logging.DEBUG, "moved to %.2f.", self.user_position)
        # LOGGER.debug("%s moved to %f.", self.motor_name, self.user_position)

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
        self.check_soft_limits(dial)

        self._controller.move_axis(self.motor_id, dial)
        self._controller.wait_motion_end(self.motor_id, dial)
        self.log(logging.DEBUG, "moved to %.2f.", self.user_position)
        # LOGGER.debug("%s moved to %f.", self.motor_name, self.user_position)

    def scan(self, start: float, stop: float, step: int, det: Detector = None, acq_time: float = 0.):
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
        start_time = time.time()

        LOGGER.info("Scan starts...\n")
        idx_col_width = 5
        pos_col_width = 8
        time_col_width = 7
        count_col_width = 10
        LOGGER.info(f"| {'#':>{idx_col_width}} | {'pos':>{pos_col_width}} | {'time':>{time_col_width}} "
                    f"| {'count tot.':>{count_col_width}} |")
        LOGGER.info(f"| {'-'*idx_col_width} | {'-'*pos_col_width} | {'-'*time_col_width} | {'-'*count_col_width} |")
        spectra = []
        for (idx, position) in enumerate(np.arange(start, stop, step, dtype=np.float32)):
            try:
                self.amove(position)
            except RuntimeError as exc:  # TODO: check separately MotorNotReady and SoftLimitError errors once available
                LOGGER.exception("Scan interrupted at position %.2f", position)
                raise RuntimeError(f"Scan interrupted at position {position}") from exc
            counts = np.nan
            if det is not None:
                assert acq_time > 0.
                spectrum = det.acquisition(acq_time)
                counts = spectrum.counts.sum()
                spectra.append(spectrum)
            elif acq_time > 0.:
                time.sleep(acq_time)
            LOGGER.info(f"| {idx:{idx_col_width}.0f} | {position:{pos_col_width}.3f} "
                        f"| {acq_time:{time_col_width}.2f} | {counts:{count_col_width}.0f} |")
        LOGGER.info(f"\n   Scan ended succesfully. Total duration was: {time.time()-start_time:.2f} s\n")
        return np.array(spectra)

    # TODO: rename to set_home/set_zero
    def set_current_as_zero(self):
        """Set motor current position to 0."""
        current_position = self.dial_position
        self._controller.set_axis_to_zero(self.motor_id)
        self.log(logging.WARNING, "Dial position reset to 0. Initial dial value was %.2f.",
                 current_position)
        # LOGGER.warning("Dial position of %s reset to 0.\n"
        #                "Initial dial value was %f.",
        #                self.motor_name, current_position)
