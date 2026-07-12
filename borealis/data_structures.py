from dataclasses import dataclass, field
from numbers import Number
from typing import Any

import numpy as np


@dataclass(frozen=True, kw_only=True)
class DatasetSchema:
    name: str
    shape: int | tuple = field(init=False)

    def validate_value(self, value):
        pass

@dataclass(frozen=True, kw_only=True)
class ScalarDatasetSchema(DatasetSchema):
    shape: int = field(init=False, default=1)

    def validate_value(self, value):
        if not isinstance(value, Number):
            raise ValueError("Scalar value must be numeric")


@dataclass(frozen=True, kw_only=True)
class VectorDatasetSchema(DatasetSchema):
    length: int

    def __post_init__(self):
        if not isinstance(self.length, int):
            raise ValueError("Vector length must be an integer")
        object.__setattr__(self, "shape", (self.length, ))

    def validate_value(self, value):
        value = np.array(value, dtype='f4')
        if value.shape != self.shape:
            raise ValueError("Vector shape mismatch: expected {self.shape}, got {value.shape}")


@dataclass(frozen=True, kw_only=True)
class MatrixDatasetSchema(DatasetSchema):
    dims: tuple[int, int]

    def __post_init__(self):
        if not (isinstance(self.dims, tuple) and len(self.dims) == 2):
            raise ValueError("Matrix dims must be a tuple of length 2")
        object.__setattr__(self, "shape", self.dims)

    def validate_value(self, value):
        value = np.array(value, dtype='f4')
        if value.shape != self.shape:
            raise ValueError("Matrix shape mismatch: expected {self.shape}, got {value.shape}")


@dataclass
class SchemaCollection:
    raw_data: list[DatasetSchema]
    processed_data: list[DatasetSchema]


@dataclass
class H5DataSchemas:
    alias: str
    attributes: dict
    datasets: SchemaCollection


###  DATASET  ##
class Dataset:

    def __init__(self, schema: DatasetSchema, value: Any = None):
        self.schema = schema
        self.schema.validate_value(value)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.schema.validate_value(value)
        self._value = value

    @classmethod
    def scalar_dataset(cls, name, value: Any = None):
        if value is None:
            value = np.nan
        return cls(ScalarDatasetSchema(name=name), value)

    @classmethod
    def vector_dataset(cls, name, length, value: Any = None):
        if value is None:
            value = np.full(length, np.nan)
        return cls(VectorDatasetSchema(name=name, length=length), value)

    @classmethod
    def matrix_dataset(cls, name, dims, value: Any = None):
        if value is None:
            value = np.full(dims, np.nan)
        return cls(MatrixDatasetSchema(name=name, dims=dims), value)


@dataclass
class DatasetCollection:
    raw_data: list[Dataset]
    processed_data: list[Dataset]