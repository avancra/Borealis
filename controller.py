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
    def move(self, motor_id, position=0):
        """
        ABC method for moving a single motor (derived must override).

        Parameters
        ----------
        motor_id : int
            Motor ID as used by the controller.
        position : float
            Target position. Default to 0.

        Returns
        -------
        None

        """

    @abstractmethod
    def get_motor_position(self, motor_id):
        """
        ABC method to retrieve position of a single motor (derived must override).

        Parameters
        ----------
        motor_id : int
            Motor ID as used by the comtroller.

        Returns
        -------
        position : float
            Current position of the motor.

        """



    # @property
    # @abstractproperty
    # def alias(self):
    #     """ABC property for alias (derived must override)."""

    # @alias.setter
    # @abstractproperty
    # def alias(self, new_value):
    #     """ABC property for alias (derived must override)."""