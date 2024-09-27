# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:48:59 2022.

@author: A. Vancraeyenest
"""
import logging
from abc import ABC, abstractmethod

import numpy as np

from borealis import mca

LOGGER = logging.getLogger(__name__)


class Detector(ABC):
    """
    Abstract base class for Detector classes.

    Defines the public API of any detector class.

    """

    @abstractmethod
    def __init__(self, alias: str = ""):
        """
        ABC method for detector initialisation. (derived must override).

        Inherited class must call super().__init__(alias=<new_alias>) in their __init__()
        or otherwise populate the alias and serial_number attributes themselves in the sub_class __init__ method.

        """
        self.alias = alias if alias != "" else "Undefined"
        self.serial_number = 'Unknown'

    def __str__(self):
        """Custom __str__ method for Detector class (DO NOT OVERWRITE THIS METHOD)."""
        return f'{self.__class__.__name__}(alias={self.alias})'

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
        """ABC method for stopping detector. (derived must override)."""

    def get_det_info(self):
        """Return the detector info as dictionary (stored in the MCA metadata)."""
        return {'serial_number': self.serial_number,
                'alias': self.alias,
                'type': self.__class__.__name__}

    def log(self, level, msg, *args, **kwargs):
        """Log a message with prepending the device's alias in front of the message."""
        kwargs['stacklevel'] = 2
        LOGGER.log(level, f'{self.alias}: {msg}', *args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}(alias={self.alias})'


class DummyDet(Detector):
    """When in need for a detector but no access to a real device."""

    def __init__(self, alias: str = "DummyDet"):
        super().__init__(alias=alias)
        LOGGER.info("Detector %s successfully initialised", self)

    def acquisition(self, acquisition_time: float) -> mca.MCA:
        self.log(logging.DEBUG, "this message logs the alias")
        LOGGER.debug('This message does not add the alias')

        return mca.MCA(np.arange(10), mca.MCAMetadata.dummy())

    def stop(self):
        LOGGER.info('%s controller closed', self.alias)

