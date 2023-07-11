# -*- coding: utf-8 -*-
"""
Spellman High Voltage power supply.

Created on Tue May 30 15:22:12 2023.

@author: R. Bes
"""
import socket

class Spellman_uX50P50():
    """Class for Spellman uX50P50 high voltage power supply (ethernet)."""

    # Digital to analogic conversion factors (Device model specific):
    D2A_KV = 12.21
    D2A_MA = 0.4884
    D2A_FIL = 2.442

    # Analogic to digital conversion factors (Device model specific):
    A2D_KV = 12.21
    A2D_MA = 0.58608
    A2D_T = 0.07326
    A2D_FIL_A = 0.87912
    A2D_FIL_V = 0.001343
    A2D_24V = 0.10476

    # Arbitrary values. Can be changed within hardware limits (device specific):
    FIL_PREHEAT = 1.5
    FIL_LIMIT = 1.7
    FIL_RAMP_TIME = 2000

    def __init__(self):
        self._socket = None
        self.software_version = ''
        self.model_number = ''
        self.hardware_version = ''

    def initialise(self, ip_adress, port=50001):
        """Initialise the connection to the device."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_adress, port))
        self.software_version = self._send('23,')[1]
        self.hardware_version = self._send('24,')[1]
        self.model_number = self._send('26,')[1]
        # TODO: handle errors of progamming the filament ramp time, prehat and limits
        val = int(round(1000 * self.FIL_PREHEAT / self.D2A_FIL))
        self._send(f'12,{val},')
        val = int(round(1000 * self.FIL_LIMIT / self.D2A_FIL))
        self._send(f'13,{val},')
        self._send(f'47,1,{self.FIL_RAMP_TIME},')
        # TODO Logging the successful initialisation of the device
        print(f'Spellman {self.model_number} successfully initialised')

    def open_shutter(self):
        ans = self._send('99,1,')
        # TODO add error code in logging : 2 :  interlock open, high voltage disabled
        # TODO add logging when Xrays are turned on
        return ans[1]

    def close_shutter(self):
        ans = self._send('99,0,')
        # TODO add logging when Xrays are turned off
        return ans[1]

    @property
    def voltage_setpoint(self):
        """Request the accelerating voltage setpoint value, in kV. """
        ans = self._send('14,')
        return float(ans[1]) * self.A2D_KV / 1000

    @voltage_setpoint.setter
    def voltage_setpoint(self, new_value):
        """Program the accelerating voltage setpoint, in kV. """
        val = int(round(1000 * new_value / self.D2A_KV))
        cmd = f"10,{val},"
        ans = self._send(cmd)
        # TODO Raise error when ans[1]==1: "out of range"
        # TODO logging when successful ans[1]==$: "Voltage successfully set to XX kV."
        return ans[1]

    @property
    def current_setpoint(self):
        """Request the source current setpoint value, in mA """
        ans = self._send('15,')
        return float(ans[1]) * self.D2A_MA / 1000

    @current_setpoint.setter
    def current_setpoint(self, new_value):
        """Program the current setpoint, in mA. """
        val = int(round(1000 * new_value / self.D2A_MA))
        cmd = f"11,{val},"
        ans = self._send(cmd)
        # TODO Raise error when ans[1]==1: "out of range"
        # TODO logging when successful ans[1]==$: "Current successfully set to XX mA."
        return ans[1]

    @property
    def status(self):
        state = self._send('22,')
        if state[1] == '1':
            high_voltage = 'ON'
        else:
            high_voltage = 'OFF'
        if state[2] == '1':
            interlock = 'OPEN'
        else:
            interlock = 'CLOSED'
        if state[3] == '1':
            fault = 'YES'
        else:
            fault = 'NO'
        # TODO: Logging the status
        # TODO: Error raised when fault occurs, when interlock is open / HV off and a scan is asked by user
        print(f'High Voltage: {high_voltage} \n'
              f'Interlock: {interlock} \n'
              f'Fault : {fault} ')
        return state[1:4]

    def analog_readbacks(self):
        ans = self.send('20,')
        return ans[1:8]

    @property
    def temperature(self):
        """Return the Control board temperature from analog feedback. """
        return float(self.analog_readbacks()[0])* self.A2D_T

    @property
    def low_voltage(self):
        """Return the low voltage supply monitor from analog feedback. """
        return float(self.analog_readbacks()[1])* self.A2D_24V

    @property
    def voltage(self):
        """Return the accelerating voltage, in kV, from analog feedback. """
        return float(self.analog_readbacks()[2]) * self.A2D_KV / 1000

    @property
    def current(self):
        """Return the source current, in mA, from analog feedback. """
        return float(self.analog_readbacks()[3]) * self.A2D_MA / 1000

    @property
    def fil_current(self):
        """Return the filament current from analog feedback. """
        return float(self.analog_readbacks()[4]) * self.A2D_FIL_A / 1000

    @property
    def fil_voltage(self):
        """Return the filament voltage from analog feedback. """
        return float(self.analog_readbacks()[5])* self.A2D_FIL_V / 1000

    @property
    def hv_temperature(self):
        """Return the High voltage board temperature from analog feedback. """
        return float(self.analog_readbacks()[6])* self.A2D_T

    def _send(self, cmd):
        msg = f'\x02{cmd}\x03'
        self._write(bytes(msg, 'ascii'))
        ans = self.decode(self._read())
        # TODO: handle errors
        return ans

    def _write(self, msg):
        """Write a message to the socket."""
        self._socket.send(msg)

    def _read(self, msg_length=2048):
        """Receive message from the socket and return answer."""
        return self._socket.recv(msg_length)

    @staticmethod
    def decode(msg):
        ans = msg.decode().split(',')
        return ans


if __name__ == "__main__":
    sock = Spellman_uX50P50()
    sock.initialise("192.168.2.3", 50001)
    sock.voltage
    sock.current
    sock.temperature
