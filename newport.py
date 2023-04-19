# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 16:42:03 2023.

@author: A. Vancraeyenest
"""

import sys
sys.path.append(r"C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.0.0.1__9a267756cf640dcf")
import clr
clr.AddReference("Newport.XPS.CommandInterface")
import CommandInterfaceXPS as xps

from borealis.controller import Controller


class NewportXPS(Controller):
    """Class to communicate with Newport controller."""

    def __init__(self):
        self._xps = xps.XPS()

    def initialise(self, ip_adress, port=5001, timeout=1000):
        """Initialise the connection to the device."""
        ans = self._xps.OpenInstrument("192.168.0.254", port, timeout)
        return ans

    def close(self):
        self._xps.CloseInstrument()

    def move_axis(self, axis_id, position=0):
        """

        """

    def get_axis_position(self, axis_id):
        """
        ABC method to retrieve position of a single axis (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        position : float
            Current position (dial) of the axis.

        """

    def set_axis_to_zero(self, axis_id):
        """
        ABC method to set the axis position to zero (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        None

        """

    def get_axis_status(self, axis_id):
        """
        ABC method to get the axis status (derived must override).

        Parameters
        ----------
        axis_id : int
            Axis ID as used by the comtroller.

        Returns
        -------
        None

        """

if __name__ == "__main__":
    ctrl = NewportXPS()
    print(ctrl.initialise("192.168.0.254"))
    print(ctrl.close())
