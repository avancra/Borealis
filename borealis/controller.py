# -*- coding: utf-8 -*-
"""
Created on Thu February 9 14:48:59 2023.

@author: A. Vancraeyenest
"""
from abc import ABC, abstractmethod, abstractproperty
import time

import pytest


class Controller(ABC):
    """
    Abstract base class for Controller classes.

    Defines the public API of any motor controller class.
    All new controller class must override all public methods and properties.

    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """ABC method for controller initialisation. (derived must override)."""

    #@abstractmethod
    #def close(self):
    #    """ABC method for closing the connection to the controller. (derived must override)."""

    @abstractmethod
    def move_axis(self, axis_id, target=0):
        """
        ABC method for moving a single axis (derived must override).

        This method should move the axis and wait that the axis had reached the target
        by calling self.is_in_position(axis_id, target)

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the controller.
        position : float
            Target position. Default to 0.

        Returns
        -------
        None

        """
        raise NotImplementedError

    @abstractmethod
    def get_axis_position(self, axis_id):
        """
        ABC method to retrieve position of a single axis (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        position : float
            Current position (dial) of the axis.

        """
        raise NotImplementedError

    @abstractmethod
    def is_axis_ready(self, axis_id):
        """
        ABC method to check that a given axis is ready, i.e. idle (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        position : bool
            True if axis is idle, False is busy or in error state.

        """
        raise NotImplementedError

    @abstractmethod
    def is_limit_switch_activated(self, axis_id):
        """
        ABC method to check if the limit switch is active (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        bool

        """
        raise NotImplementedError

    @abstractmethod
    def set_axis_to_zero(self, axis_id):
        """
        ABC method to set the axis position to zero (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        None

        """
        raise NotImplementedError

    # TODO: rename due to misleading is_in_position make think that one expects a bool as return, like is_axis_ready
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

            if self.is_limit_switch_activated(axis_id):
                raise RuntimeError(
                    f"Limit switch activated, move aborted)")

            if (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Axis never reached target position. Stopped at {current})")

            time.sleep(sleep_for)


    # @abstractmethod
    # def get_axis_status(self, axis_id):
    #     """
    #     ABC method to get the axis status (derived must override).

    #     Parameters
    #     ----------
    #     axis_id : int
    #         Axis ID as used by the comtroller.

    #     Returns
    #     -------
    #     None

    #     """

    # @property
    # @abstractproperty
    # def alias(self):
    #     """ABC property for alias (derived must override)."""

    # @alias.setter
    # @abstractproperty
    # def alias(self, new_value):
    #     """ABC property for alias (derived must override)."""
