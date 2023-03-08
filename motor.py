# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:50:29 2023.

@author: René Bes
"""

class Motor():
    """Motor generic class."""

    def __init__(self, motor_name, motor_id, motor_offset, controller):
        self.motor_name = motor_name
        self.motor_id = motor_id
        self.offset = motor_offset
        self.ctrl = controller
        self.current_position = self.ctrl.get_axis_position(self.motor_id)
        #TODO! self.limits =

    def position(self):
        """
        Get motor dial position from controller.

        Returns
        -------
        Float
            Motor position (dial) as retrieved from controller.

        """
        print(f'{self.motor_name} at: \n'
              f'dial: {self.current_position} \n'
              f'user: {self.current_position + self.offset}')
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
        self.ctrl.move_axis(self.motor_id, dial)
        self.ctrl.is_in_position(dial)
        self.current_position = self.ctrl.get_axis_position(self.motor_id)

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
        self.ctrl.move_axis(self.motor_id, dial)
        self.ctrl.is_in_position(dial)
        self.current_position = self.ctrl.get_axis_position(self.motor_id)

    def set_to_zero(self):
        """Set motor current position to 0."""
        self.ctrl.set_axis_to_zero(self.motor_id)
        print(f'{self.motor_name} position set to 0. \n'
              f'Initial value was {self.current_position}.')
        self.current_position = self.ctrl.get_axis_position(self.motor_id)
