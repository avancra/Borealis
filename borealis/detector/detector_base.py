# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:48:59 2022.

@author: A. Vancraeyenest
"""
import logging
import time
from abc import ABCMeta, abstractmethod

import numpy as np

from borealis import session_orchestrator
from borealis import mca
from borealis.component import SensorComponent

LOGGER = logging.getLogger(__name__)


class Detector(SensorComponent, metaclass=ABCMeta):
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
        self.mca_size = 4096
        super().__init__(session_orchestrator)

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
        mca : mca.MCA
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

    def get_device_info(self):
        attrs = self.get_det_info()
        data_sets = {'MCA': self.mca_size,
                     'runtime': 1,
                     'ICR': 1,
                     'OCR': 1}
        return self.alias, {'attrs': attrs, 'data_sets': data_sets }

    def log(self, level, msg, *args, **kwargs):
        """Log a message with prepending the device's alias in front of the message."""
        kwargs['stacklevel'] = 2
        LOGGER.log(level, f'{self.alias}: {msg}', *args, **kwargs)

    def receive(self, message, **kwargs):
        match message:
            case 'measure':
                mca = self.acquisition(kwargs['acquisition_time'])
                kwargs['mca'] = mca
                self.send('DataPoint', message='mca', **kwargs)


class DummyDet(Detector):
    """When in need for a detector but no access to a real device."""

    def __init__(self, alias: str = "DummyDet"):
        super().__init__(alias=alias)
        LOGGER.info("Detector %s successfully initialised", self)

    def acquisition(self, acquisition_time: float) -> mca.MCA:
        self.log(logging.DEBUG, "this message logs the alias")
        LOGGER.debug('This message does not add the alias')

        time.sleep(acquisition_time)

        return mca.MCA(np.arange(2048), mca.MCAMetadata.dummy())

    def stop(self):
        LOGGER.info('%s controller closed', self.alias)

