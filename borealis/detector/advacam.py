import contextlib
import logging
import sys

import mca
from borealis.detector.detector_base import Detector
from utils import get_lib_dir

pixet_dir = get_lib_dir() / 'pixet/'
sys.path.append(pixet_dir.as_posix())
import pypixet

LOGGER = logging.getLogger(__name__)


class MinipixTPX3(Detector):
    """
    Provide support for Advacam Minipix TPX3.

    Borealis currently only provides Windows libraries for Minipix TPX3.

    """

    def __init__(self):
        """Open the communication with Minipix detector"""
        with contextlib.chdir(pixet_dir):
            pypixet.start()
            self.pixet = pypixet.pixet
            # TODO: .devicesByType(pixet.PX_DEVTYPE_TPX3) only if I can get a TPX3 virtual device when none connected
            devices = self.pixet.devices()
            self.device = devices[0]

        full_name = self.device.fullName()
        super().__init__(full_name)

        dev_info = self.pixet.DevInfo()
        self.device.deviceInfo(dev_info)

        self.serial_number = dev_info.serial


    def stop(self):
        pypixet.exit()

    def acquisition(self, acquisition_time: float) -> mca.MCA:
        pass

