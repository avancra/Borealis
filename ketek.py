# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 12:54:49 2022.

@author: A. Vancraeyenest
"""
import ctypes as ct
from ctypes import byref
from pathlib import Path
from time import sleep

import numpy as np

from borealis.ketek_error import check_error
from borealis.detector import Detector


class KetekAXASM(Detector):
    """Class to operate KETEK detector AXAS-M."""

    HANDEL = ct.CDLL(
        (Path(__file__).parent / "lib/handel/handel.dll").as_posix())
    MAXALIAS_LEN = 80

    def __init__(self, ini_filepath):
        """Initialise the detector."""
        self._ini_file = self._validate_ini(ini_filepath)
        self._chan_no = 0
        self._initialise(self._ini_file)
        self._start_system()
        print('Detector Ketek successfully initialised')

    def acquisition(self, acquisition_time):
        """Start an acquisition and return corresponding Spectrum object."""
        self._start_run()
        sleep(acquisition_time)
        self._stop_run()

        return self._get_spectrum()

    def stop(self):
        """
        Close the connection to the detector and free resources.

        Wrap xiaExit.
        Disconnect from the hardware and clean up Handel’s internals.

        """
        ret_code = self.HANDEL.xiaExit()
        check_error(ret_code)

    @staticmethod
    def _validate_ini(ini_filepath):
        """Check that ini_filepath is a valid and existing filepath."""
        try:
            assert Path(ini_filepath).exists()
        except TypeError:
            raise ValueError('Wrong ini file name.')
        except AssertionError:
            raise ValueError("The ini file doesn't exist.")

        return ini_filepath

    def _initialise(self, path):
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

        This routine also performs several validation steps to insure
        that all of the configuration information required to run the
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

    def _save_system(self, filename):
        """
        Wrap xiaSaveSystem.

        Saves the current system configuration to the specified file and
        with the specified format.
        """
        filename = self._to_bytes(filename)
        ret_code = self.HANDEL.xiaSaveSystem(b'handel_ini', filename)

        check_error(ret_code)

    def _load_system(self, filename):
        """
        Wrap xiaLoadSystem.

        Loads a configuration file. Since only one type is supported
        (handel_ini), it is typically more convenient to call xiaInit(),
        which both initializes the library and loads a handel_ini file,
        instead of xiaInitHandel() and xiaLoadSystem.
        """
        filename = self._to_bytes(filename)
        ret_code = self.HANDEL.xiaLoadSystem(b'handel_ini', filename)

        check_error(ret_code)

    def _get_num_detectors(self):
        """
        Wrap xiaGetNumDetectors.

        Return the number of detectors currently defined in the system.
        """
        n_det = ct.c_uint()
        ret_code = self.HANDEL.xiaGetNumDetectors(byref(n_det))

        check_error(ret_code)

        return n_det.value

    def _get_detectors(self):
        """
        Wrap xiaGetDetectors.

        Return a list of aliases of the detectors defined in the system.

        """
        n_dets = self._get_num_detectors()
        arr_type = ct.c_char_p * n_dets
        det_names = arr_type(*[b' '*self.MAXALIAS_LEN]*n_dets)
        ret_code = self.HANDEL.xiaGetDetectors(byref(det_names))

        check_error(ret_code)

        det_names = [name.decode() for name in det_names]

        return tuple(det_names)

    def _get_detector_nb_of_channels(self, alias):
        """Wrap xiaGetDetectorItem with name='number_of_channel'."""
        noc = ct.c_uint()
        ret_code = self.HANDEL.xiaGetDetectorItem(
            self._to_bytes(alias), b'number_of_channels', byref(noc))
        check_error(ret_code)

        return noc.value

    def _get_detector_gain(self, alias):
        """Wrap xiaGetDetectorItem with name='channel{channel}_gain'."""
        gain = ct.c_double()
        name = f'channel{self._chan_no}_gain'
        ret_code = self.HANDEL.xiaGetDetectorItem(
            self._to_bytes(alias), self._to_bytes(name), byref(gain))
        check_error(ret_code)

        return gain.value

    def _get_detector_polarity(self, alias):
        """Wrap xiaGetDetectorItem with name='channel{channel}_polarity'."""
        polarity = b' '*3
        name = f'channel{self._chan_no}_polarity'
        ret_code = self.HANDEL.xiaGetDetectorItem(
            self._to_bytes(alias), self._to_bytes(name), polarity)
        check_error(ret_code)

        return polarity.decode()

    def _set_acquisition_values(self, name, value, channel=None):
        """Warning: Not in used. Incomplete implementation."""
        if channel is None:
            channel = -1  # All channels
        value = ct.c_double(value)
        ret_code = self.HANDEL.xiaSetAcquisitionValues(
            channel, self._to_bytes(name), value)
        check_error(ret_code)

        return value.value

    def _start_run(self, resume=False):
        """Wrap xiaStartRun."""
        ret_code = self.HANDEL.xiaStartRun(self._chan_no, resume)
        check_error(ret_code)

    def _stop_run(self):
        """Wrap xiaStopRun."""
        ret_code = self.HANDEL.xiaStopRun(self._chan_no)
        check_error(ret_code)

    def _get_run_livetime(self):
        """Report the acquisition livetime in seconds."""
        livetime = ct.c_double()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'livetime', byref(livetime))
        check_error(ret_code)

        return livetime.value

    def _get_run_runtime(self):
        """Report the acquisition runtime in seconds."""
        runtime = ct.c_double()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'runtime', byref(runtime))
        check_error(ret_code)

        return runtime.value

    def _get_run_input_count_rate(self):
        """Wrap xiaGetRunData with input_count_rate."""
        input_cr = ct.c_double()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'input_count_rate', byref(input_cr))
        check_error(ret_code)

        return input_cr.value

    def _get_run_output_count_rate(self):
        """Wrap xiaGetRunData with output_count_rate."""
        output_cr = ct.c_double()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'output_count_rate', byref(output_cr))
        check_error(ret_code)

        return output_cr.value

    def _is_run_active(self):
        """Wrap xiaGetRunData with run_active."""
        is_active = ct.c_ushort()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'run_active', byref(is_active))
        check_error(ret_code)

        return is_active.value

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

    def _get_run_event_counts(self):
        """Wrap xiaGetRunData with events_in_run."""
        counts = ct.c_ulong()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'events_in_run', byref(counts))
        check_error(ret_code)

        return counts.value

    def _get_run_trigger_counts(self):
        """Wrap xiaGetRunData with triggers."""
        counts = ct.c_ulong()
        ret_code = self.HANDEL.xiaGetRunData(
            self._chan_no, b'triggers', byref(counts))
        check_error(ret_code)

        return counts.value

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

    def _set_logging(self, output='stdout', level='error'):
        """
        Wrap xiaSetLogOutput and xiaSetLogLevel.

        Set the logging output and level.

        Parameters
        ----------
        output : str, optional
            filename or 'stdout' or 'stderr'. The default is 'stdout'.
        level : str, optional
            level name, one of 'debug', 'info', 'warning', 'error'.
            The default is 'error'.

        Returns
        -------
        None.

        """
        log_levels = {'debug': 4,
                      'info': 3,
                      'warning': 2,
                      'error': 1}
        ret_code = self.HANDEL.xiaSetLogOutput(self._to_bytes(output))
        check_error(ret_code)
        ret_code = self.HANDEL.xiaSetLogLevel(log_levels[level])
        check_error(ret_code)

    @staticmethod
    def _to_bytes(arg):
        """Return arg to bytes."""
        if isinstance(arg, bytes):
            return arg
        return arg.encode()


if __name__ == '__main__':
    from time import sleep
    from matplotlib import pyplot as plt
    dev = KetekAXASM(
        (Path(__file__).parent / "examples/KETEK_DPP2_usb2.ini").as_posix())
    dev._set_logging('stderr', 'error')
    dev._start_system()
    print(dev._get_detectors())
    print(dev._get_detector_nb_of_channels('ketek1'))
    print(dev._get_detector_gain('ketek1'))
    print(dev._get_detector_polarity('ketek1'))
    spe = dev.acquisition(1)
    print(dev._get_all_run_stats())
    plt.plot(spe)
    dev.stop()
