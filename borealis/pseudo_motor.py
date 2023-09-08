import logging
from functools import partial
from typing import Union
import time

import numpy as np

from borealis.motor import Motor
from borealis.detector import Detector
from borealis.geometries import theta

LOGGER = logging.getLogger(__name__)


class PseudoMotor:
    """Class for a basic pseudo-motor, meaning a collection of Motor objects plus 0 or 1 detector."""

    def __init__(self, motors: list[Motor], geometries: list, detector: Union[Detector, None] = None) -> None:
        """

        Parameters
        ----------
        motors : list[Motor]
            List of Motor objects.
        geometries : list[fct]
            List of conversion functions (e.g. lambda (x,y): x), one for each motor. 
        detector
            Instance of Detector.
        """
        try:
            assert len(motors) == len(geometries)
        except AssertionError:
            LOGGER.error('Length of motor list (%d) does not match the length of geometry list (%d)',
                         len(motors), len(geometries))
            raise ValueError(f"Length of motor list ({len(motors)}) does not match the length of "
                             f"geometry list ({len(geometries)})")
        self._motors = motors
        self._conversion_laws = geometries
        self._detector = detector

    @property
    def is_ready(self):
        return all(motor.is_ready for motor in self._motors)

    def _check_is_ready(self):
        # TODO: change to MotorNotReady error once available
        if self.is_ready is False:
            LOGGER.error("Command interrupted due to all motors not ready yet (i.e. not idle).")
            raise RuntimeError(f"Command interrupted due to all motors not ready yet (i.e. not idle).")

    def amove(self, pos):
        self._check_is_ready()

        for idx, motor in enumerate(self._motors):
            motor_pos = self._conversion_laws[idx](pos)
            motor.amove(motor_pos)

    def scan(self, start, stop, step, acq_time):
        self._check_is_ready()

        spectra = []
        for position in np.arange(start, stop, step, dtype=np.float32):
            try:
                self.amove(position)
            except RuntimeError:  # TODO: change to MotorNotReady error once available
                LOGGER.error(
                    "Scan interrupted at position %f due to motor not being ready yet (i.e. not idle).",
                    position)
                raise RuntimeError(f"Scan interrupted at position {position} "
                                   f"due to motor not being ready yet (i.e. not idle).")

            if self._detector is not None:
                assert acq_time is not None
                spectrum = self._detector.acquisition(acq_time)
                spectra.append(spectrum)
            elif acq_time is not None:
                time.sleep(acq_time)

        return np.array(spectra)


    @classmethod
    def theta(cls, tube_x, tube_y, tube_rot, mono_x, mono_y, det, radius):
        motors = [tube_x, tube_y, tube_rot, mono_x, mono_y]
        conversion_laws = [partial(theta.geo_tubex, radius),
                           partial(theta.geo_tubey, radius),
                           partial(theta.geo_tuber, radius),
                           partial(theta.geo_monox, radius),
                           partial(theta.geo_monor, radius)]

        return cls(motors, conversion_laws, det)
