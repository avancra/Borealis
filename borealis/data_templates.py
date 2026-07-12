import logging
from abc import ABCMeta, abstractmethod

from borealis.data_structures import Dataset, SchemaCollection, DatasetCollection

LOGGER = logging.getLogger(__name__)


class DataTemplate(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self):
        """ABC method for raw data objects."""

    @abstractmethod
    def get_schemas(self) -> SchemaCollection:
        """ABC method for returning a collection of schemas, one of each dataset."""

    @abstractmethod
    def get_datasets(self) -> DatasetCollection:
        """ABC method for returning a collection of all datasets."""


class MCA(DataTemplate):

    def __init__(self, mca_size):
      self.runtime = Dataset.scalar_dataset(name='runtime')
      self.icr = Dataset.scalar_dataset(name='ICR')
      self.ocr = Dataset.scalar_dataset(name='OCR')
      self.mca = Dataset.vector_dataset(name='MCA', length=mca_size)

    def get_schemas(self) -> SchemaCollection:
      raw = [ds.schema for ds in [self.runtime, self.icr, self.ocr, self.mca]]
      processed = []

      return SchemaCollection(raw, processed)

    def get_datasets(self) -> DatasetCollection:
        raw = [ds for ds in [self.runtime, self.icr, self.ocr, self.mca]]
        processed = []

        return DatasetCollection(raw, processed)


class Frame(DataTemplate):
    def __init__(self, width, height):
      self.runtime =Dataset.scalar_dataset(name='runtime')
      self.itot= Dataset.matrix_dataset(name='IToT', dims=(width, height))
      self.events = Dataset.matrix_dataset(name='Events', dims=(width, height))

    def get_schemas(self) -> SchemaCollection:
        raw = [ds.schema for ds in [self.runtime, self.itot, self.events]]
        processed =[]

        return SchemaCollection(raw, processed)

    def get_datasets(self) -> DatasetCollection:
        raw = [ds for ds in [self.runtime, self.itot, self.events]]
        processed = []

        return DatasetCollection(raw, processed)


class MoverPositions(DataTemplate):

    def __init__(self):
        self.position = Dataset.scalar_dataset(name='position')
        # self.dial = Dataset.scalar_dataset(name='dial positions')

    def get_schemas(self) -> SchemaCollection:
        raw = [ds.schema for ds in [self.position, ]]
        processed =[]

        return SchemaCollection(raw, processed)

    def get_datasets(self) -> DatasetCollection:
        raw = [ds for ds in [self.position, ]]
        processed = []

        return DatasetCollection(raw, processed)