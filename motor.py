# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""
from time import sleep


class Motor():
    """Motor generic class."""

    def __init__(self, motor_name, motor_id, motor_offset, controller):
        self.motor_name = motor_name
        self.motor_id = motor_id
        self.offset = motor_offset
        self.ctrl = controller
        self.current_position = self.get_motor_position()
        #TODO! self.limits =

    def get_motor_position(self):
        """
        Get motor dial position from controller.

        Returns
        -------
        Float
            Motor position (dial) as retrieved from controller.

        """
        return self.ctrl.get_axis_position(self.motor_id)

    def amove(self, new_position):
        """
        Move the motor to a new position (user) in absolute scale.

        Parameters
        ----------
        new_position : float
            New position (user) to move the motor to.

        Returns
        -------
        None.

        """
        dial = new_position - self.offset
        self.ctrl.move(self.motor_id, dial)
        self.is_in_position(dial)
        self.current_position = self.get_motor_position()

    def rmove(self, rel_position):
        """
        Move the motor by a relative position.

        Parameters
        ----------
        rel_position : float
            Relative value to move the motor by.

        Returns
        -------
        None.

        """
        dial = self.current_position + rel_position
        self.ctrl.move(self.motor_id, dial)
        self.is_in_position(dial)
        self.current_position = self.get_motor_position()

    def is_in_position(self, target, timeout=60):
        """
        Check that the motor has reached its target position.

        Parameters
        ----------
        target : float
            Position (dial) the motor must reach.
        timeout : float, optional
            Time limit for the motor movement in seconds.
            The default is 60 seconds.

        Raises
        ------
        TimeoutError
            Error when motor does not reach its target position in due time.

        Returns
        -------
        None.

        """
        waited=0
        sleep_for = 0.1  # sec
        while True:
            current = self.ctrl.get_axis_position(self.motor_id)
            if target == round(current, 3):
                print(f'Motor {self.motor_id} at {current}')
                break
            sleep(sleep_for)
            waited += sleep_for

            if waited > timeout:
                raise TimeoutError(
                    f"Motor never reached position (current is {current})")

    def where(self):
        """
        Print the current dial and user positions.

        Returns
        -------
        None.

        """
        print(f'{self.motor_name} at: \n'
              f'dial: {self.current_position} \n'
              f'user: {self.current_position + self.offset}')

    def set_position_to_zero(self):
        """Set motor current position to 0."""
        self.ctrl.set_zero(self.motor_id)
        print(f'{self.motor_name} position set to 0. \n'
              f'Initial value was {self.current_position}.')
        self.current_position = self.get_motor_position()
