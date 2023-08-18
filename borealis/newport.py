# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 16:42:03 2023.

@author: A. Vancraeyenest
"""

import sys
sys.path.append(r"C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.3.0.0__9a267756cf640dcf")
import clr
clr.AddReference("Newport.XPS.CommandInterface")
import CommandInterfaceXPS as xps

from borealis.controller import Controller


class NewportXPS(Controller):
    """Class to communicate with Newport controller."""

    def __init__(self, ip_address, port=5001, timeout=1000):
        """Initialise the connection to the device."""
        self._xps = xps.XPS()
        ans = self._xps.OpenInstrument(ip_address, port, timeout)
        # print(f'Controller Newport {ans} successfully initialised')

    # -------------  Overiden methods ------------- #
    def close(self):
        self._xps.KillAll()  # Kill all axis
        self._xps.CloseInstrument()  # close connection to the instrument

    def move_axis(self, axis_id : str, target : float = 0.):
        """Send instruction to move an axis to a target position."""
        answer = self._xps.GroupMoveAbsolute(axis_id, [target, ], 1)
        self.is_in_position(axis_id, target)

    def get_axis_position(self, axis_id):
        """
        ABC method to retrieve position of a single axis (derived must override).

        Parameters
        ----------
        axis_id : str
            Axis ID as used by the comtroller.

        Returns
        -------
        position : float
            Current position (dial) of the axis.

        """
        answer, positions, err_str = self._xps.GroupPositionCurrentGet(axis_id, [], 1)
        positions = [pos for pos in positions]

        return positions[0]

    def is_axis_ready(self, axis_id):
        """Check that a given axis is ready (idle)."""
        return True

    def set_axis_to_zero(self, axis_id):
        """Set the axis position to zero."""
        raise NotImplementedError

    def is_limit_switch_activated(self, axis_id):
        """Check if limit switch is active."""
        return False

    # -------------  Own methods ------------- #

    def version(self):
        result, version, err_str = self._xps.FirmwareVersionGet("", "")
        print(result, version, err_str)
        # answer = self._xps.FirmwareVersionGet("", "")
        # print(f"{answer=}")
        if result == 0:
            print(f"XPS firmware version: {version}")
        else:
            print(f"Error calling the version command: {err_str}")


if __name__ == "__main__":
    ip_address = "..."
    ctrl = NewportXPS(ip_address)
    print("***")
    try:
        print("***")
        # following 2 commandes should give same output
        print(ctrl.version())
        print("***")
        print(ctrl._xps.FirmwareVersionGet())
        print("***")

        # 1-motor group
        axis_id = "tubex"
        print(ctrl._xps.GroupInitialize(axis_id))
        print("***")
        print(ctrl._xps.GroupHomeSearch(axis_id))
        print("***")
        # print(ctrl._xps.GroupPositionCurrentGet(axis_id, [], 1, ""))
        # answer, positions, err_str = ctrl._xps.GroupPositionCurrentGet(axis_id, [], 1)
        # positions = [pos for pos in positions]
        # print(f"{positions=}")
        # print("***")
        # print(ctrl._xps.GroupMoveAbsolute(axis_id, [10.0, ], 1))
        print(ctrl.move_axis(axis_id, 50.))
        print("***")
        print(ctrl.get_axis_position(axis_id))
    except Exception:
        ctrl.close()
        raise
    else:
        ctrl.close()

