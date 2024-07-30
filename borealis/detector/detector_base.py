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
        """ABC method for stopping detector. (derived must override)."""

    def get_det_info(self):
        """Return the detector info as dictionary (stored in the MCA metadata)."""
        return {'serial_number': self.serial_number,
                'alias': self.alias,
                'type': self.DET_TYPE}

    def log(self, level, msg, *args, **kwargs):
        """Log a message with prepending the device's alias in front of the message."""
        kwargs['stacklevel'] = 2
        LOGGER.log(level, f'{self.alias}: {msg}', *args, **kwargs)


class DummyDet(Detector):
    """When in need for a detector but no access to a real device."""

    DET_TYPE = "Dummy"

    def __init__(self, alias: str = "DummyDet"):
        super().__init__(alias)
        LOGGER.info('%s detector initialised.', self.alias)

    def acquisition(self, acquisition_time: float) -> mca.MCA:
        # this message logs the alais
        self.log(logging.DEBUG, 'Log from Dummies! %s %.3f', 'Hi!', 0.225662455)
        # This message doesn't add the alias
        LOGGER.debug('Another log from Dummy :)')

        return mca.MCA(np.arange(10), mca.MCAMetadata.dummy())

    def stop(self):
        LOGGER.info('%s controller closed', self.alias)

    def get_det_info(self):
        """Return the detector info as dictionary (stored in the MCA metadata)."""
        return {'serial_number': self.serial_number,
                'alias': self.alias,
                'type': self.DET_TYPE}
