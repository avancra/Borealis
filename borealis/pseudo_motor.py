from __future__ import annotations

import logging
from typing import Union, Callable
import time

import numpy as np

from borealis.motor import Motor
from borealis.detector.detector_base import Detector

LOGGER = logging.getLogger(__name__)


class PseudoMotor:
    """Class for a basic pseudo-motor, meaning a collection of Motor objects plus 0 or 1 detector."""

    def __init__(self, alias: str, motors: list[Motor, PseudoMotor], geometries: list,
                 position_law: Callable[[list], float], detector: Union[Detector, None] = None) -> None:
        """

        Parameters
        ----------
        alias : str
            Name of the pseudo-motor
        motors : list[Motor, PseudoMotor]
            List of Motor or PseudoMotor objects.
        geometries : list[Callable[float, float]
            List of conversion functions (e.g. lambda (x: ax + b), one for each motor.
        position_law : Callable[[list], float]
            Function that takes as input the list of (pseudo)-motors as it was given at instantiation and returns
             a single float.
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
        self.motor_name = alias
        self._motors = motors
        self._conversion_laws = geometries
        self._detector = detector
        self._position_law = position_law

        LOGGER.info("PseudoMotor %s created.", self.motor_name)

    @property
    def user_position(self):
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
        print('{} at : {:6.2f} (user)'.format(self.motor_name, self.user_position))

    def where_all(self):
        """
        Print individual motor dial / user positions.

        Returns
        -------
        str

        """
        for motor in self._motors:
            motor.where()

    def check_soft_limits(self, target_user: float) -> None:
        """
        Check if dial value is within the limits (inclusive).

        Parameters
        ----------
        target_user : float
            Target position in user unit.

        Raises
        ------
        SoftLimitError when dial is outside the allowed range.
        """
        LOGGER.debug("Checking all (pseudo)motor soft limits before amove...")
        for idx, motor in enumerate(self._motors):
            motor_pos = self._conversion_laws[idx](target_user)
            motor.check_soft_limits(motor_pos)
            LOGGER.debug("Valid dial %.3f for (pseudo)motor %s", motor_pos, motor.motor_name)

    def amove(self, target_user):
        self._check_is_ready()
        self.check_soft_limits(target_user)

        for idx, motor in enumerate(self._motors):
            motor_pos = self._conversion_laws[idx](target_user)
            motor.amove(motor_pos)

    def scan(self, start: float, stop: float, step: float, acq_time: float = 0):
        """
        Scan, with or without acquisition.

        Parameters
        ----------
        start : float
            Start of interval.  The interval includes this value.
        stop : float
            End of interval.  The interval does not include this value.
        step : float
            Spacing between values.  For any output `out`, this is the distance
            between two adjacent values, ``out[i+1] - out[i]``.
        acq_time : float
            If a Detector is attached to the pseudo-motor, will perform an acquisition for this time.
            If no detector is defined and acq_time > 0, it will sleep for this time.

        Returns
        -------
        spectra : ndarray
            Array of MCA objects.
        """
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
            except RuntimeError as exc:  # TODO: change to MotorNotReady error once available
                LOGGER.error(
                    "Scan interrupted at position %.2f",position)
                raise RuntimeError(f"Scan interrupted at position {position}") from exc

            counts = np.nan
            if self._detector is not None:
                assert acq_time > 0.
                spectrum = self._detector.acquisition(acq_time)
                counts = spectrum.counts.sum()
                spectra.append(spectrum)
            elif acq_time > 0.:
                time.sleep(acq_time)

            LOGGER.info(f"| {idx:{idx_col_width}.0f} | {position:{pos_col_width}.3f} "
                        f"| {acq_time:{time_col_width}.2f} | {counts:{count_col_width}.0f} |")

        LOGGER.info(f"\n   Scan ended succesfully. Total duration was: {time.time()-start_time:.2f} s\n")

        return np.array(spectra)
