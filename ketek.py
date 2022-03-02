# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 12:54:49 2022.

@author: A. Vancraeyenest
"""

import ctypes as ct
from ctypes import byref
from pathlib import Path


class KetekAXASM:
    """Class to operate KETEK detector AXAS-M."""

    HANDEL = ct.CDLL(
        (Path(__file__).parent / "lib/handel/handel.dll").as_posix())
    MAXALIAS_LEN = 80

    def __init__(self):
        self.detector = None

    def initialise(self, path):
        """
        Wrap xiaInit.

        Initializes the Handel library and loads in an .ini file.
        The functionality of this routine can be emulated by calling
        xiaInitHandel() followed by xiaLoadSystem()(“handel_ini”, iniFile).
        Either this routine or xiaInitHandel must be called prior to
        using the other Handel routines.

        """
        ret_code = self.HANDEL.xiaInit(self.to_bytes(path))

        # return ret_code

    def start_system(self):
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

        # return ret_code

    def get_num_detectors(self):
        """
        Wrap xiaGetNumDetectors.

        Return the number of detectors currently defined in the system.
        """
        n_det = ct.c_uint()
        ret_code = self.HANDEL.xiaGetNumDetectors(byref(n_det))

        return n_det.value

    def get_detectors(self):
        """
        Wrap xiaGetDetectors.

        Return a list of aliases of the detectors defined in the system.

        """
        n_dets = self.get_num_detectors()
        arr_type = ct.c_char_p * n_dets
        det_names = arr_type(*[b' '*self.MAXALIAS_LEN]*n_dets)
        ret_code = self.HANDEL.xiaGetDetectors(byref(det_names))

        det_names = [name.decode() for name in det_names]

        return tuple(det_names)

    def get_detector_nb_of_channels(self, alias):
        """Wrap xiaGetDetectorItem with name='number_of_channel'."""
        noc = ct.c_uint()
        ret_code = self.HANDEL.xiaGetDetectorItem(
            self.to_bytes(alias), b'number_of_channels', byref(noc))

        return noc.value

    def get_detector_gain(self, alias, channel=0):
        """Wrap xiaGetDetectorItem with name='channel{channel}_gain'."""
        gain = ct.c_double()
        name = f'channel{channel}_gain'
        ret_code = self.HANDEL.xiaGetDetectorItem(
            self.to_bytes(alias), self.to_bytes(name), byref(gain))

        return gain.value

    def get_detector_polarity(self, alias, channel=0):
        """Wrap xiaGetDetectorItem with name='channel{channel}_polarity'."""
        polarity = b' '*3
        name = f'channel{channel}_polarity'
        ret_code = self.HANDEL.xiaGetDetectorItem(
            self.to_bytes(alias), self.to_bytes(name), polarity)

        return polarity.decode()

    def set_acquisition_values(self, name, value, channel=None):
        """"""
        if channel is None:
            channel = -1  # All channels
        value = ct.c_double(value)
        ret_code = self.HANDEL.xiaSetAcquisitionValues(
            channel, self.to_bytes(name), value)

        return value.value

    def start_run(self, channel=None, resume=False):
        """Wrap xiaStartRun."""
        if channel is None:
            channel = -1  # All channels
        ret_code = self.HANDEL.xiaStartRun(channel, resume)

    def stop_run(self, channel=None):
        """Wrap xiaStopRun."""
        if channel is None:
            channel = -1  # All channels
        ret_code = self.HANDEL.xiaStopRun(channel)

    def get_run_livetime(self, channel):
        """"""
        livetime = ct.c_double()
        ret_code = self.HANDEL.xiaGetRunData(
            channel, b'livetime', byref(livetime))

        return livetime.value

    def get_run_runtime(self, channel):
        """"""
        runtime = ct.c_double()
        ret_code = self.HANDEL.xiaGetRunData(
            channel, b'runtime', byref(runtime))

        return runtime.value

    def stop_xia(self):
        """
        Wrap xiaExit.

        Disconnect from the hardware and clean up Handel’s internals.

        """
        ret_code = self.HANDEL.xiaExit()

    def set_logging(self, output='stdout', level='error'):
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
        ret_code = self.HANDEL.xiaSetLogOutput(self.to_bytes(output))
        ret_code = self.HANDEL.xiaSetLogLevel(log_levels[level])


    @staticmethod
    def to_bytes(arg):
        """Return arg to bytes."""
        if isinstance(arg, bytes):
            return arg
        return arg.encode()


if __name__ == '__main__':
    from time import sleep
    dev = KetekAXASM()
    print(dev.initialise(
        (Path(__file__).parent / "examples/KETEK_DPP2_usb2.ini").as_posix()))
    print(dev.set_logging('stderr', 'info'))
    print(dev.start_system())
    print(dev.get_detectors())
    print(dev.get_detector_nb_of_channels('ketek1'))
    print(dev.get_detector_gain('ketek1'))
    print(dev.get_detector_polarity('ketek1'))
    print(dev.start_run())
    sleep(10)
    print(dev.stop_run())
    print(dev.get_run_livetime(0))
    print(dev.get_run_runtime(0))
    print(dev.stop_xia())
