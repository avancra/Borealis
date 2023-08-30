# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:48:59 2022.

@author: A. Vancraeyenest
"""
from abc import ABC, abstractmethod, abstractproperty

from borealis import mca


class Detector(ABC):
    """
    Abstract base class for Detector classes.

    Defines the public API of any detector class.

    """

    DET_TYPE = "Undefined"

    @abstractmethod
    def __init__(self, alias: str = ""):
        """
        ABC method for detector initialisation. (derived must override).

        Inherited class must call super().__init__(alias=<new_alias>) in their __init__()
        or otherwise populate the alias and serial_number attributes themselves in the sub_class __init__ method.

        """
        self.alias = alias
        self.serial_number = 'Unknown'

    @abstractmethod
    def acquisition(self, acquisition_time: float) -> mca.MCA:
        """
        ABC method for acquisition (derived must override).

        Parameters
        ----------
        acquisition_time : float
            Acquisition time in seconds.

        Returns
        -------
        mac : mca.MCA
            MCA object with spectrum counts and metadata.

        """

    @abstractmethod
    def stop(self):
        """ABC method for stoping detector. (derived must override)."""

    def get_det_info(self):
        """Return the detector info as dictionary (stored in the MCA metadata)."""
        return {'serial_number': self.serial_number,
                'alias': self.alias,
                'type': self.DET_TYPE}