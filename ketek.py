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

        return ret_code

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

        return ret_code

    def get_num_detectors(self):
        """Return the number of detectors currently defined in the system."""
        n_det = ct.c_uint()
        ret_code = self.HANDEL.xiaGetNumDetectors(byref(n_det))

        return ret_code, n_det.value

    def get_detectors(self):
        """Return a list of aliases of the detectors defined in the system."""
        _, n_dets = self.get_num_detectors()
        arr_type = ct.c_char_p * n_dets
        det_names = arr_type(*[b' '*self.MAXALIAS_LEN]*n_dets)
        ret_code = self.HANDEL.xiaGetDetectors(byref(det_names))

        det_names = [name.decode() for name in det_names]

        return ret_code, tuple(det_names)

    def stop_xia(self):
        """Disconnect from the hardware and clean up Handel’s internals."""
        ret_code = self.HANDEL.xiaExit()
        return ret_code

    @staticmethod
    def to_bytes(arg):
        """Return arg to bytes."""
        if isinstance(arg, bytes):
            return arg
        return arg.encode()


if __name__ == '__main__':
    dev = KetekAXASM()
    print(dev.initialise(
        (Path(__file__).parent / "examples/KETEK_DPP2_usb2.ini").as_posix()))
    print(dev.start_system())
    print(dev.get_detectors())
    print(dev.stop_xia())
