from __future__ import annotations

import logging
from typing import Union
import time

import numpy as np

from borealis.motor import Motor
from borealis.detector.detector_base import Detector

LOGGER = logging.getLogger(__name__)


class PseudoMotor:
    """Class for a basic pseudo-motor, meaning a collection of Motor objects plus 0 or 1 detector."""

    def __init__(self, alias: str, motors: list[Motor, PseudoMotor], geometries: list, detector: Union[Detector, None] = None) -> None:
        """

        Parameters
        ----------
        alias : str
            Name of the pseudo-motor
        motors : list[Motor, PseudoMotor]
            List of Motor or PseudoMotor objects.
        geometries : list[fct]
            List of conversion functions (e.g. lambda (x,y): x), one for each motor.
        detector
            Instance of Detector.
        """
        # TODO: change list to tuple to avoid changing the motor order by mistake ? same for geometries
        try:
            assert len(motors) == len(geometries)
        except AssertionError:
            LOGGER.error('Length of motor list (%d) does not match the length of geometry list (%d)',
                         len(motors), len(geometries))
            raise ValueError(f"Length of motor list ({len(motors)}) does not match the length of "
                             f"geometry list ({len(geometries)})")
        self._motor_name = alias
        self._motors = motors
        self._conversion_laws = geometries
        self._detector = detector
        self._position_law = lambda x: x[0].user_position

        LOGGER.info("PseudoMotor %s created.", self._motor_name)

    @property
    def position(self):
        return self._position_law(self._motors)

    @property
    def is_ready(self):
        return all(motor.is_ready for motor in self._motors)

    def _check_is_ready(self):
        # TODO: change to MotorNotReady error once available
        if self.is_ready is False:
            LOGGER.error("Command interrupted due to all motors not ready yet (i.e. not idle).")
            raise RuntimeError("Command interrupted due to all motors not ready yet (i.e. not idle).")

    def where(self):
        """
        Print pseudo-motor position.

        Returns
        -------
        str

        """
        print('{} at : {:6.2f} (user)'.format(self._motor_name, self.position))

    def where_all(self):
        """
        Print individual motor dial / user positions.

        Returns
        -------
        str

        """
        for motor in self._motors:
            motor.where()

    def check_soft_limits(self, dial: float) -> None:
        """
        Check if dial value is within the limits (inclusive).

        Parameters
        ----------
        dial : float
            Target position in dial unit.

        Raises
        ------
        SoftLimitError when dial is outside the allowed range.
        """
        LOGGER.debug("Checking all (pseudo)motor soft limits before amove...")
        for idx, motor in enumerate(self._motors):
            motor_pos = self._conversion_laws[idx](dial)
            motor.check_soft_limits(motor_pos)
            LOGGER.debug("Valid dial %.2f for (pseudo)motor %s", motor_pos, motor.motor_name)

    def amove(self, pos):
        self._check_is_ready()
        self.check_soft_limits(pos)

        for idx, motor in enumerate(self._motors):
            motor_pos = self._conversion_laws[idx](pos)
            motor.amove(motor_pos)

    def scan(self, start, stop, step, acq_time):
        self._check_is_ready()
        start_time = time.time()

        LOGGER.info("Scan starts...\n")
        idx_col_width = 5
        pos_col_width = 8
        time_col_width = 7
        count_col_width = 10
        LOGGER.info(f"| {'#':>{idx_col_width}} | {'pos':>{pos_col_width}} | {'time':>{time_col_width}} "
                    f"| {'count tot.':>{count_col_width}} |")
        LOGGER.info(f"| {'-'*idx_col_width} | {'-'*pos_col_width} | {'-'*time_col_width} | {'-'*count_col_width} |")
        spectra = []
        for (idx, position) in enumerate(np.arange(start, stop, step, dtype=np.float32)):
            try:
                self.amove(position)
            except RuntimeError:  # TODO: change to MotorNotReady error once available
                LOGGER.error(
                    "Scan interrupted at position %f due to motor not being ready yet (i.e. not idle).",
                    position)
                raise RuntimeError(f"Scan interrupted at position {position} "
                                   f"due to motor not being ready yet (i.e. not idle).")
            counts = np.nan
            if self._detector is not None:
                assert acq_time is not None
                spectrum = self._detector.acquisition(acq_time)
                counts = spectrum.counts.sum()
                spectra.append(spectrum)
            elif acq_time is not None:
                time.sleep(acq_time)
            LOGGER.info(f"| {idx:{idx_col_width}.0f} | {position:{pos_col_width}.3f} "
                        f"| {acq_time:{time_col_width}.2f} | {counts:{count_col_width}.0f} |")
        LOGGER.info(f"\n   Scan ended succesfully. Total duration was: {time.time()-start_time:.2f} s\n")
        return np.array(spectra)

# class Theta(ABC):
#
#     def __init__(self, radius, spectro_cmpt):
#         """Provide pseudo motor to perform angle."""
#         self.radius = radius
#         self._det_y = spectro_cmpt['det_y'] if 'det_y' in spectro_cmpt else None
#         self._src_y = spectro_cmpt['src_y'] if 'src_y' in spectro_cmpt else None
#         ...
#
#     def mvabs(pos):
#         if self._det_y is not None:
#             self.det_y.move(self.get_src_x(pos))
#         if self._src_x is not None:
#             self.det_y.move(self.get_src_x(pos))
#         ...
#
#     def scan(start, stop, step):
#         for pos in range(start, stop, step):
#             self.mvabs(pos)
#
#     def get_src_x(pos):
#         return 0
#
#     @staticmethod
#     def torad(theta):
#         return pi*theta/180
