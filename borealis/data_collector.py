import logging
from datetime import datetime
from pathlib import Path

import h5py

from borealis.mca import MCA
from borealis.component import DataComponent

LOGGER = logging.getLogger(__name__)


class DataCollector(DataComponent):
    """Data collector"""

    def __init__(self, orchestrator):
        """
        DataCollector constructor

        Parameters
        ----------
        orchestrator: Orchestrator

        """
        super().__init__(orchestrator)
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

        for alias, device_info in kwargs['all_device_info'].items():
            group = self.current_scan.create_group(alias)
            for name, value in device_info['attrs'].items():
                group.attrs[name.replace('_', ' ').capitalize()] = value
            for name, size in device_info['data_sets'].items():
                if size == 1:
                    group.create_dataset(f'{name}', (kwargs['scan_points'], ))
                else:
                    group.create_dataset(f'{name}', (size, kwargs['scan_points']))

        # h5_scan.attrs["scan type"] = f"Type of the scan #{scan_number}, ie. function call"

        self.h5file.flush()

    def close_scan(self):
        self.current_scan.attrs["end_time"] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.current_scan = None

        self.h5file.flush()

    def add_datapoint_mca(self, alias: str, idx: int, mca: MCA):
        nb_channels = len(mca.counts)
        self.current_scan[alias]['MCA'][0:nb_channels,idx] = mca.counts
        self.current_scan[alias]['runtime'][idx] = mca.metadata.runtime
        self.current_scan[alias]['ICR'][idx] = mca.metadata.input_cr
        self.current_scan[alias]['OCR'][idx] = mca.metadata.output_cr
        self.current_scan[alias]['OCR'][idx] = mca.metadata.output_cr

        self.h5file.flush()

    def add_motor_datapoint(self, alias: str, idx: int, position):
        self.current_scan[alias]['user_position'][idx] = position

        self.h5file.flush()

    def add_scan_point(self, idx, data, positions):
        for sensor_alias, sensor_data in data.items():
            self.add_datapoint_mca(sensor_alias, idx, sensor_data)
        for ctlr_alias, ctlr_position in positions.items():
            self.add_motor_datapoint(ctlr_alias, idx, ctlr_position)
