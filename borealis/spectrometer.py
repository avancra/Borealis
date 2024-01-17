# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:07:48 2022.

@author: A. Vancraeyenest
"""
from pathlib import Path

import yaml

from borealis.detector.ketek import KetekAXASM
from borealis.detector.amptek import AmptekCdTe123


class Spectrometer:
    """Main spectrometer class."""

    def __init__(self, config):
        self._config = config
        self._detectors = []
        self._initialise()

    def _initialise(self):
        """Initialise."""
        for detector in self._config['detectors']:
            if detector['type'] in ['KETEK-AXASM', 'Ketek' ]:
                det = KetekAXASM(detector['ini_file'])
                self._detectors.append(det)
            elif detector['type'] in ['Amptek', 'AmptekCdTe123', 'AmptekX123']:
                det = AmptekCdTe123()
                self._detectors.append(det)
            else:
                print(f'Unrecognised detector type {detector["type"]}')

        for det in self._detectors:
            det.initialise()

    def stop_all(self):
        """Close all connections to every component of the spectro."""
        for detector in self._detectors:
            detector.stop()

    def start_acquisition(self, acq_time):
        """Start an acquisition on all detectors."""
        spectra = []
        for detector in self._detectors:
            spectra.append(detector.acquisition(acq_time))
        return spectra

    @classmethod
    def from_yaml_file(cls, config_file):
        """Create spectro from a config file (.yml)."""
        with Path(config_file).open() as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError:
                print("Error while parsing the spectro config file")
                raise

        return cls(config)


if __name__ == '__main__':
    spectro = Spectrometer.from_yaml_file('../examples/spectro.yml')
    # spectro = Spectrometer({'detectors': [{'type':'Amptek'}, ]})

    spe = spectro.start_acquisition(10)

    spectro.stop_all()
