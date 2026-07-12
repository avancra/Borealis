import logging
from datetime import datetime
from pathlib import Path
from typing import Union

import h5py

from borealis.component import DataComponent
from borealis.data_structures import ScalarDatasetSchema, VectorDatasetSchema, MatrixDatasetSchema

LOGGER = logging.getLogger(__name__)


class DataCollector(DataComponent):
    """Data collector with HDF5 file handler."""

    def __init__(self):
        """
        DataCollector constructor.

        """
        super().__init__()
        self.h5file = None
        self.current_scan = None
        self.data_dir = Path.cwd() / 'data'
        self.filename_base = 'borealis_datafile_'
        self.current_sample = 'Unknown sample'
        self.instrument = 'Unknown instrument'
        self.experiment_id = 'Unknown ID'

    def __str__(self):
        """Custom __str__ method for DataCollector class."""
        return f'{self.__class__.__name__}'

    def receive(self, message, **kwargs):
        LOGGER.debug('Receiving message: %s', message)
        match message:
            case 'new_scan':
                self.add_scan(**kwargs)
            case 'new_scan_point':
                self.add_scan_point(**kwargs)
            case 'close_scan':
                self.close_scan()

    def create_h5file(self, experiment_id: str = '', add_date=True):
        if self.h5file is not None:
            LOGGER.debug("Closing h5file...")
            self.h5file.close()

        self.data_dir.mkdir(parents=False, exist_ok=True)
        if add_date is True:
            h5_filename = self.data_dir / f'{self.filename_base}{datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}.h5'
        else:
            h5_filename = self.data_dir / f'{self.filename_base}.h5'

        if experiment_id != '':
            self.experiment_id = experiment_id

        LOGGER.info(f'Creating h5file {h5_filename}')
        self.h5file = h5py.File(h5_filename, 'w', libver='latest')
        self.h5file.swmr_mode = True
        self.h5file["/"].attrs["Instrument"] = self.instrument
        self.h5file["/"].attrs["Experiment ID"] = self.experiment_id
        self.h5file["/"].attrs["Date created"] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    def add_scan(self, **kwargs):
        if self.h5file is None:
            raise UserWarning("No File exists to save data, create one with the 'new_file' command.")

        LOGGER.debug('Adding scan to H5file')
        scan_number = len(list(self.h5file.keys())) + 1
        self.current_scan = self.h5file.create_group(f"/scan{scan_number}")
        self.current_scan.attrs["start_time"] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.current_scan.attrs["Sample name"] = self.current_sample

        for h5_schema in kwargs['all_h5_data_schema']:
            group = self.current_scan.create_group(h5_schema.alias)
            for name, value in h5_schema.attributes.items():
                group.attrs[name.replace('_', ' ').capitalize()] = value
            for schema in h5_schema.datasets.raw_data:
                match schema:
                    case ScalarDatasetSchema():
                        group.create_dataset(f'{schema.name}', shape=(kwargs['scan_points'], ), dtype='f4')
                    case VectorDatasetSchema():
                        group.create_dataset(f'{schema.name}', shape=(schema.length, kwargs['scan_points']), dtype='f4')
                    case MatrixDatasetSchema():
                        group.create_dataset(f'{schema.name}', shape=(*schema.dims, kwargs['scan_points']), dtype='f4')
        # h5_scan.attrs["scan type"] = f"Type of the scan #{scan_number}, ie. function call"

        self.h5file.flush()

    def add_scan_point(self, idx: int, data: dict):
        for component_alias, component_data in data.items():
            for dataset in component_data.get_datasets().raw_data:
                match dataset.schema:
                    case ScalarDatasetSchema():
                        self.current_scan[component_alias][dataset.schema.name][idx] = dataset.value
                    case VectorDatasetSchema():
                        vector_length = dataset.schema.length
                        self.current_scan[component_alias][dataset.schema.name][0:vector_length, idx] = dataset.value
                    case MatrixDatasetSchema():
                        height, width = dataset.schema.dims
                        self.current_scan[component_alias][dataset.schema.name][0:height, 0:width, idx] = dataset.value

            self.h5file.flush()

    def close_scan(self):
        self.current_scan.attrs["end_time"] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.current_scan = None

        self.h5file.flush()
