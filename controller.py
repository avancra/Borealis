# -*- coding: utf-8 -*-
"""
Created on Thu February 9 14:48:59 2023.

@author: A. Vancraeyenest
"""
from abc import ABC, abstractmethod, abstractproperty


class Controller(ABC):
    """
    Abstract base class for Controller classes.

    Defines the public API of any motor controller class.
    All new controller class must override all public methods and properties.

    """

    @abstractmethod
    def initialise(self):
        """ABC method for controller initialisation. (derived must override)."""

    #@abstractmethod
    #def close_connection(self):
    #    """ABC method for closing the connection to the controller. (derived must override)."""

    @abstractmethod
    def move_axis(self, axis_id, position=0):
        """
        ABC method for moving a single axis (derived must override).

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

    @abstractmethod
    def get_axis_status(self, axis_id):
        """
        ABC method to get the axis status (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        None

        """

    # @property
    # @abstractproperty
    # def alias(self):
    #     """ABC property for alias (derived must override)."""

    # @alias.setter
    # @abstractproperty
    # def alias(self, new_value):
    #     """ABC property for alias (derived must override)."""
