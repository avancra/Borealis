# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""
import logging
from math import inf

import numpy as np

from borealis.controller.controller_base import Controller
from borealis.exceptions import SoftLimitError, NotReadyError
from borealis.component import ControllerComponent
from borealis.data_structures import DeviceInfo

LOGGER = logging.getLogger(__name__)


class Motor(ControllerComponent):
    """Motor generic class."""

    def __init__(self, alias: str, motor_id: str, motor_offset: float, controller: Controller,
                 positive_direction: bool = True, soft_limit_low: float = -inf, soft_limit_high: float = inf) -> None:
        self._controller = controller
        self.alias = alias

        self.motor_id = motor_id
        self.offset = motor_offset
        self._direction_coeff = -1 if positive_direction is False else 1
        self._limit_low = soft_limit_low
        self._limit_high = soft_limit_high
        self._dial_position = self._controller.get_axis_position(self.motor_id)
        self._user_position = self.dial_position + self.offset
        self._is_ready = self._controller.is_axis_ready(self.motor_id)
        super().__init__()
        LOGGER.info("Motor %s created.", self.alias)

    def log(self, level, msg, *args, **kwargs):
        """Log a message with prepending the device's alias in front of the message."""
        kwargs['stacklevel'] = 2
        LOGGER.log(level, f'{self.alias}: {msg}', *args, **kwargs)

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

    def get_device_info(self):
        attrs = {'Alias': self.alias, }
        datasets = {'user_position': 1, }
        return DeviceInfo(alias=self.alias, metadata={'attrs': attrs, 'data_sets': datasets})

    def where(self):
        """
        Print motor dial / user positions from controller.

        Returns
        -------
        str

        """
        print(f'{self.alias:20} at : {self.user_position:6.2f} (user)')


    def _check_is_ready(self):
        # TODO: change to MotorNotReady error once available
        if self.is_ready is False:
            self.log(logging.ERROR, 'Command interrupted due to motor not ready yet (i.e. not idle).')
            # LOGGER.error('Command interrupted due to motor not ready yet (i.e. not idle).')
            raise NotReadyError(self.alias)

    def check_soft_limits(self, target_user: float) -> None:
        """
        Check if dial value is within the limits (inclusive).

        Parameters
        ----------
        target_user : float
            Target position in user unit.

        Raises
        ------
        SoftLimitError when dial is outside the allowed range.
        """
        target_dial = (target_user - self.offset) / self._direction_coeff
        try:
            assert self._limit_low <= target_dial <= self._limit_high
        except AssertionError:
            self.log(logging.ERROR, 'Soft Limit Error: the dial position %.2f is outside the available soft limit range [%.2f : %.2f]', target_dial, self._limit_low, self._limit_high)
            raise SoftLimitError(target_dial, self.alias, self._limit_low, self._limit_high)

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
        self.check_soft_limits(user_position)

        dial = (user_position - self.offset) / self._direction_coeff
        self._controller.move_axis(self.motor_id, dial)
        self._controller.wait_motion_end(self.motor_id, dial)
        self.log(logging.DEBUG, "moved to %.2f.", self.user_position)

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
        self.check_soft_limits(self.user_position + rel_position)

        dial = self.dial_position + rel_position * self._direction_coeff
        self._controller.move_axis(self.motor_id, dial)
        self._controller.wait_motion_end(self.motor_id, dial)
        self.log(logging.DEBUG, "moved to %.2f.", self.user_position)

    def scan(self, start: float, stop: float, step: float, acq_time: float = 0.):
        """
        Perform a scan, if acq_time > 0 will also do an acquisition on all sensors.

        Parameters
        ----------
        start : float
            Start of interval. The interval includes this value.
        stop : float
            End of interval. The interval does not include this value.
        step : float
            Spacing between values. For any output `out`, this is the distance
            between two adjacent values, ``out[i+1] - out[i]``.
        acq_time : float

        """
        self._check_is_ready()

        scan_points = np.arange(start, stop, step, dtype=np.float32)
        acq_times = np.full_like(scan_points, acq_time)
        self.send(message='Scan', scan_points=scan_points, acq_times=acq_times)

    def set_current_as_zero(self):
        """Set motor current position as 0."""
        current_position = self.dial_position
        self._controller.set_axis_to_zero(self.motor_id)
        self.log(logging.WARNING, "Dial position reset to 0. Initial dial value was %.2f.",
                 current_position)
