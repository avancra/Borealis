# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 16:42:03 2023.

@author: A. Vancraeyenest
"""
import logging
import sys

sys.path.append(r"C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.3.0.0__9a267756cf640dcf")

import clr
clr.AddReference("Newport.XPS.CommandInterface")
import CommandInterfaceXPS as xps

from borealis.controller.controller_base import Controller

LOGGER = logging.getLogger(__name__)


class NewportXPS(Controller):
    """Class to communicate with Newport controller."""

    def __init__(self, ip_address: str, alias: str = "", port: int = 5001, timeout: int = 1000):
        """Initialise the connection to the device."""
        self._xps = xps.XPS()
        ans = self._xps.OpenInstrument(ip_address, port, timeout)
        LOGGER.debug("Opening connection on port %d at IP address %s with timeout %d)",
                     port, ip_address, timeout)
        alias = alias if alias != '' else f'NewportXPS {ans}'
        super().__init__(alias=alias)
        LOGGER.info("%s successfully initialised", self)

    # -------------  Overridden methods ------------- #
    def close(self):
        self._xps.KillAll()  # Kill all axis
        self._xps.CloseInstrument()  # close connection to the instrument

    def move_axis(self, axis_id: str, target: float = 0.):
        """Send instruction to move an axis to a target position."""
        self._xps.GroupMoveAbsolute(axis_id, [target, ], 1)
        self.wait_motion_end(axis_id, target)

    def get_axis_position(self, axis_id: str):
        """
        ABC method to retrieve position of a single axis (derived must override).

        Parameters
        ----------
        axis_id : str
            Axis ID as used by the controller.

        Returns
        -------
        position : float
            Current position (dial) of the axis.

        """
        answer, positions, err_str = self._xps.GroupPositionCurrentGet(axis_id, [], 1)
        positions = [pos for pos in positions]

        return positions[0]

    def is_axis_ready(self, axis_id: str):
        """Check that a given axis is ready (idle)."""
        return True

    def set_axis_to_zero(self, axis_id: str):
        """Set the axis position to zero."""
        raise NotImplementedError

    def is_limit_switch_activated(self, axis_id: str):
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
    ip_add = "..."
    ctrl = NewportXPS(ip_add)
    print("***")
    try:
        print("***")
        # following 2 commands should give same output
        print(ctrl.version())
        print("***")
        print(ctrl._xps.FirmwareVersionGet())
        print("***")

        # 1-motor group
        axis = "tubex"
        print(ctrl._xps.GroupInitialize(axis))
        print("***")
        print(ctrl._xps.GroupHomeSearch(axis))
        print("***")
        # print(ctrl._xps.GroupPositionCurrentGet(axis_id, [], 1, ""))
        # answer, positions, err_str = ctrl._xps.GroupPositionCurrentGet(axis_id, [], 1)
        # positions = [pos for pos in positions]
        # print(f"{positions=}")
        # print("***")
        # print(ctrl._xps.GroupMoveAbsolute(axis_id, [10.0, ], 1))
        print(ctrl.move_axis(axis, 50.))
        print("***")
        print(ctrl.get_axis_position(axis))
    except Exception:
        ctrl.close()
        raise
    else:
        ctrl.close()
