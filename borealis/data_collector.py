import logging
from datetime import datetime
from pathlib import Path

import h5py

from borealis.mca import MCA
from borealis.component import Component

LOGGER = logging.getLogger(__name__)


class DataCollector(Component):

    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.h5file = None
        self.current_scan = None
        self.data_dir = Path.cwd() / 'data'
        self.filename_base = 'borealis_datafile_'
        self.current_sample = 'Unknown sample'
        self.instrument = 'Unknown instrument'
        self.experiment_id = 'Unknown ID'

    def receive(self, message, **kwargs):
        LOGGER.debug('Receiving message: %s', message)
        match message:
            case 'add_scan':
                self.add_scan(**kwargs)
            case 'add_scan_pseudo_motor':
                self.add_scan_pseudo_motor(**kwargs)
            case 'add_scan_detector':
                self.add_scan_detector(**kwargs)
            case 'add_motor_datapoint':
                self.add_motor_datapoint(**kwargs)
            case 'add_datapoint_mca':
                self.add_datapoint_mca(**kwargs)

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
        self.h5file["/"].attrs["Date created"] = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))

    def add_scan(self, start_time):
        # TODO: check if h5file is not None
        LOGGER.debug('Adding scan to H5file')
        scan_number = len(list(self.h5file.keys())) + 1
        self.current_scan = self.h5file.create_group(f"/scan{scan_number}")
        self.current_scan.attrs["start_time"] = start_time.strftime("%Y-%m-%d %H-%M-%S")
        self.current_scan.attrs["Sample name"] = self.current_sample
        # h5_scan.attrs["scan type"] = f"Type of the scan #{scan_number}, ie. function call"

        self.h5file.flush()

    def close_scan(self, end_time):
        self.current_scan.attrs["end_time"] = end_time
        self.current_scan = None

        self.h5file.flush()

    def add_scan_detector(self, detector, scan_points):
        self.current_scan.create_group(detector.alias)
        self.current_scan.create_dataset(f'{detector.alias}/MCA', (4096, scan_points))
        self.current_scan.create_dataset(f'{detector.alias}/runtime', (scan_points,))
        self.current_scan.create_dataset(f'{detector.alias}/ICR', (scan_points,))
        self.current_scan.create_dataset(f'{detector.alias}/OCR', (scan_points,))
        # arr = np.arange('2023-02-01T01:00', '2023-02-01T02:39', dtype="datetime64[m]")
        # h5_detector.create_dataset(f'{h5_detector.name}/time_per_point', data=arr.astype(h5py.opaque_dtype(arr.dtype)))
        # h5_detector.attrs["id"] = "unique_id"
        # h5_detector.attrs["type"] = "class name"

        self.h5file.flush()

    def add_scan_pseudo_motor(self, pseudomotor, scan_points):
        self.current_scan.create_group(pseudomotor.motor_name)
        self.current_scan.create_dataset(f'{pseudomotor.motor_name}/user_position', (scan_points,))
        # self.current_scan.attrs["motor_list"] = "list of motor and pseudo motor constituting the pseudomotor"
        # self.current_scan.attrs["soft_limits"] = "(low, high)"
        #   would be nice to have
        # self.current_scan.attrs["conversion law"] = "conversion law of pseudo_motor in symbolic python"
        # self.current_scan.attrs["individual conversion law"] = "conversion law of pseudo_motor in symbolic python"

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
