# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:48:59 2022.

@author: A. Vancraeyenest
"""
import logging
import time
from abc import ABCMeta, abstractmethod

import numpy as np

from borealis.component import SensorComponent
from borealis.data_structures import H5DataSchemas, SchemaCollection
from borealis.data_templates import MCA, DataTemplate

LOGGER = logging.getLogger(__name__)


class Detector(SensorComponent, metaclass=ABCMeta):
    """
    Abstract base class for Detector classes.

    Defines the public API of any detector class.

    """

    @abstractmethod
    def __init__(self, alias: str = "") -> None:
        """
        ABC method for detector initialisation. (derived must override).

        Inherited class must call super().__init__(alias=<new_alias>) in their __init__()
        or otherwise populate the alias and serial_number attributes themselves in the sub_class __init__ method.

        """
        self.alias = alias if alias != "" else "Undefined"
        self.serial_number = 'Unknown'
        self.raw_data = None
        super().__init__()

    @abstractmethod
    def acquisition(self, acquisition_time: float) -> DataTemplate:
        """
        ABC method for acquisition (derived must override).

        Parameters
        ----------
        acquisition_time : float
            Acquisition time in seconds.

        Returns
        -------
        data

        """

    @abstractmethod
    def stop(self) -> None:
        """ABC method for stopping detector. (derived must override)."""

    @abstractmethod
    def get_datasets_schemas(self) -> SchemaCollection:
        """ABC method for getting raw data HDF5 schema. (derived must override)."""

    def get_det_info(self):
        """Return the detector info as dictionary (stored in the MCA metadata)."""
        return {'serial_number': self.serial_number,
                'alias': self.alias,
                'type': self.__class__.__name__}

    def get_h5_data_schema(self) -> H5DataSchemas:
        attrs = self.get_det_info()
        dataset_schemas = self.get_datasets_schemas()

        return H5DataSchemas(alias=self.alias, attributes=attrs, datasets=dataset_schemas)

    def log(self, level, msg, *args, **kwargs) -> None:
        """
        Log a message with prepending the device's alias in front of the message.

        DO NOT OVERWRITE THIS METHOD

        """
        kwargs['stacklevel'] = 2
        LOGGER.log(level, f'{self.alias}: {msg}', *args, **kwargs)

    def __str__(self):
        """Custom __str__ method for Detector class. DO NOT OVERWRITE THIS METHOD"""
        return f'{self.__class__.__name__}(alias={self.alias})'

    def receive(self, message, **kwargs) -> None:
        match message:
            case 'measure':
                mca = self.acquisition(kwargs['acquisition_time'])
                kwargs['mca'] = mca
                self.send('DataPoint', message='mca', **kwargs)


class DummyDet(Detector):
    """When in need for a detector but no access to a real device."""

    def __init__(self, alias: str = "DummyDet"):
        self.mca_size = 2048
        super().__init__(alias=alias)

        LOGGER.info("Detector %s successfully initialised", self)

    def acquisition(self, acquisition_time: float) -> MCA:
        self.log(logging.DEBUG, "this message logs the alias")
        LOGGER.debug('This message does not add the alias')

        time.sleep(float(acquisition_time))

        data = MCA(self.mca_size)
        data.runtime.value = acquisition_time
        data.mca.value = np.arange(2048) * acquisition_time

        return data

    def stop(self) -> None:
        LOGGER.info('%s controller closed', self.alias)

    def get_datasets_schemas(self) -> SchemaCollection:

        return MCA(self.mca_size).get_schemas()
