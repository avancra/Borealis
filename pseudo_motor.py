from abc import ABC, abstractmethod, abstractproperty
from typing import Union
import time

import numpy as np

from borealis.motor import Motor
from borealis.detector import Detector


class PseudoMotor():
    """Class for a basic pseudo-motor, meaning a collection of Motor objects plus 0 or 1 detector."""

    def __init__(self, motors: list[Motor], geometry: list, detector: Union[Detector, None] = None) -> None:
        """

        Parameters
        ----------
        motors : list[Motor]
            List of Motor objects.
        geometry : list[fct]
            List of conversion functions (e.g. lambda (x,y): x), one for each motor.
        detector
            Instance of Detector.
        """
        self._motors = motors
        self._conversion_laws = geometry
        self._detector = detector

        assert len(self._motors) == len(self._conversion_laws)

    def amove(self, pos):
        # TODO: Check if motors ready to move
        # while not all(mt.is_ready for mt in self._motors):
            # wait
            # check timeout
        for idx, motor in enumerate(self._motors):
            motor_pos = self._conversion_laws[idx](pos)
            motor.amove(motor_pos)

    def scan(self, start, stop, step, acq_time):
        spectra = []
        for position in np.arange(start, stop, step):
            self.amove(position)
            # wait all in position
            if self._detector is not None:
                assert acq_time is not None
                spectrum = self._detector.acquisition(acq_time)
                spectra.append(spectrum)
            elif acq_time is not None:
                time.sleep(acq_time)

        return np.array(spectra)


class Theta(ABC):

    def __init__(self, radius, spectro_cmpt):
        """Provide pseudo motor to perform angle."""
        self.radius = radius
        self._det_y = spectro_cmpt['det_y'] if 'det_y' in spectro_cmpt else None
        self._src_y = spectro_cmpt['src_y'] if 'src_y' in spectro_cmpt else None
        ...

    def mvabs(pos):
        if self._det_y is not None:
            self.det_y.move(self.get_src_x(pos))
        if self._src_x is not None:
            self.det_y.move(self.get_src_x(pos))
        ...

    def scan(start, stop, step):
        for pos in range(start, stop, step):
            self.mvabs(pos)

    def get_src_x(pos):
        return 0

    @staticmethod
    def torad(theta):
        return pi*theta/180
