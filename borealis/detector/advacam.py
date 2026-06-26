import contextlib
import logging
import sys

from borealis.detector.detector_base import Detector
from borealis.utils import get_lib_dir
from borealis.mca import MCAMetadata, MCA

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

        # TODO: turn into property +  enun for possible modes (cf doc)
        self.device.setOperationMode(self.pixet.PX_TPX3_OPM_EVENT_ITOT)

        # TODO:  turn into property
        self.device.setThreshold(self.pixet.PX_CHIP_ALL, 4, self.pixet.PX_THLFLG_ENERGY)

        # TODO: turn into property
        self.nb_of_frame = 1

        self.width = self.device.width()
        self.height = self.device.height()
        self.mca_size = self.width * self.height


    def stop(self):
        pypixet.exit()

    def acquisition(self, acquisition_time: float) -> 'MCA':
        rc = self.device.doSimpleAcquisition(self.nb_of_frame,
                                             acquisition_time,
                                             self.pixet.PX_FTYPE_NONE,
                                             "")
        raw_frame = self.device.lastAcqFrameRefInc()
        for sub_frame in raw_frame.subFrames():
            if sub_frame.frameName() in ("iToT", "ToT"):

                mca_metadata = MCAMetadata(raw_frame.acqTime(),
                                           None,
                                           None,
                                           self.get_det_info())
                mca = MCA(sub_frame.data(), mca_metadata)

                return mca

