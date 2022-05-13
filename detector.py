# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:48:59 2022.

@author: A. Vancraeyenest
"""
from abc import ABC, abstractmethod, abstractproperty


class Detector(ABC):
    """
    Abstract base class for Detector classes.

    Defines the public API of any detector class.

    """

    @abstractmethod
    def acquisition(self, acquisition_time):
        """
        ABC method for acquisition (derived must override).

        Parameters
        ----------
        acquisition_time : float
            Acquisition time in seconds.

        Returns
        -------
        spectrum : spectrum.Spectrum
            Spectrum object.

        """

    @abstractmethod
    def initialise(self):
        """ABC method for detector initialisation. (derived must override)."""

    # @property
    # @abstractproperty
    # def alias(self):
    #     """ABC property for alias (derived must override)."""

    # @alias.setter
    # @abstractproperty
    # def alias(self, new_value):
    #     """ABC property for alias (derived must override)."""
