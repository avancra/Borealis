# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 12:54:49 2022.

@author: A. Vancraeyenest
"""
import ctypes as ct
import logging
from ctypes import byref
from pathlib import Path
from time import sleep

import numpy as np

from borealis.detector.ketek_error import check_error
from borealis.detector.detector_base import Detector
from borealis.mca import MCA, MCAMetadata

LOGGER = logging.getLogger(__name__)


class KetekAXASM(Detector):
    """Class to operate KETEK detector AXAS-M."""
    HANDEL = ct.CDLL(
        (Path(__file__).parent.parent / "lib/handel/handel.dll").as_posix())
    MAXALIAS_LEN = 80

    def __init__(self, ini_filepath: str, alias: str = "Ketek-AXAS M"):
        """Initialise the detector."""
        super().__init__(alias)
        self._ini_file = self._validate_ini(ini_filepath)
        self._chan_no = 0
        self._initialise(self._ini_file)
        self._start_system()
        self.serial_number = self._get_serial_number()

        LOGGER.info("Detector %s successfully initialised", self)

    def acquisition(self, acquisition_time: float):
        """Start an acquisition and return corresponding Spectrum object."""
        self._start_run()
        sleep(acquisition_time)
        self._stop_run()
        mca_counts = self._get_spectrum()
        run_stat = self._get_all_run_stats()

        mca_metadata = MCAMetadata(run_stat['runtime'],
                                   run_stat['ICR'],
                                   run_stat['OCR'],
                                   self.get_det_info())
        mca = MCA(mca_counts, mca_metadata)

        return mca

    def stop(self):
        """
        Close the connection to the detector and free resources.

        Wrap xiaExit.
        Disconnect from the hardware and clean up Handel’s internals.

        """
        ret_code = self.HANDEL.xiaExit()
        check_error(ret_code)

    @staticmethod
    def _validate_ini(ini_filepath: str):
        """Check that ini_filepath is a valid and existing filepath."""
        try:
            assert Path(ini_filepath).exists()
        except TypeError:
            raise ValueError('Wrong ini file name.')
        except AssertionError:
            raise ValueError("The ini file doesn't exist.")

        return ini_filepath

    def _initialise(self, path: str):
        """
        Wrap xiaInit.

        Initializes the Handel library and loads in an .ini file.
        The functionality of this routine can be emulated by calling
        xiaInitHandel() followed by xiaLoadSystem()(“handel_ini”, iniFile).
        Either this routine or xiaInitHandel must be called prior to
        using the other Handel routines.

        """
        ret_code = self.HANDEL.xiaInit(self._to_bytes(path))
        check_error(ret_code)

    def _start_system(self):
        """
        Wrap xiaStartSystem.

        Starts the system previously defined via an .ini file.
        Connects to the hardware and downloads the firmware and
        acquisition values to all active channels in order to set the
        system up for data acquisition. This routine must be called after
        configuring the system with a configuration file
        (see Initializing Handel).

        This routine also performs several validation steps to ensure
        that all the configuration information required to run the
        system is present. Specifically, the firmware and detector
        information is validated by Handel while the module is verified
        by the Product Specific Layer. If an inconsistency is found,
        it will be reported back as an error and should be fixed before
        attempting to call xiaStartSystem() again.

        This routine may block for up to several seconds, depending on
        the size of the system and timing of firmware downloading.

        """
        ret_code = self.HANDEL.xiaStartSystem()

        check_error(ret_code)

    def _get_serial_number(self):
        serial_number = ct.create_string_buffer(16)
        self.HANDEL.xiaBoardOperation(self._chan_no, b'get_serial_number', serial_number)

        return serial_number.value

    def _start_run(self, resume: bool = False):
        """Wrap xiaStartRun."""
        ret_code = self.HANDEL.xiaStartRun(self._chan_no, resume)
        check_error(ret_code)

    def _stop_run(self):
        """Wrap xiaStopRun."""
        ret_code = self.HANDEL.xiaStopRun(self._chan_no)
        check_error(ret_code)

    def _get_spectrum_length(self):
        """Wrap xiaGetRunData with mca_length."""
        spe_length = ct.c_ulong()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'mca_length', byref(spe_length))
        check_error(ret_code)

        return spe_length.value

    def _get_spectrum(self):
        """Wrap xiaGetRunData with mca."""
        spe_length = self._get_spectrum_length()
        spectrum = np.empty(spe_length, dtype='uint32')
        spectrum_ct = spectrum.ctypes.data_as(ct.POINTER(ct.c_uint32))
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'mca', spectrum_ct)
        check_error(ret_code)

        return spectrum

    def _get_all_run_stats(self):
        """Wrap xiaGetRunData with all_statistics."""
        all_stats_ct = (ct.c_double * 6)()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'all_statistics', byref(all_stats_ct))
        check_error(ret_code)

        all_stats = {'livetime': all_stats_ct[0],
                     'runtime': all_stats_ct[1],
                     'triggers': all_stats_ct[2],
                     'events': all_stats_ct[3],
                     'ICR': all_stats_ct[4],
                     'OCR': all_stats_ct[5]}

        return all_stats

    @staticmethod
    def _to_bytes(arg):
        """Return arg to bytes."""
        if isinstance(arg, bytes):
            return arg
        return arg.encode()
