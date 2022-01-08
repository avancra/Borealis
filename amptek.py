# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:54:19 2021.

@author: A. Vancraeyenest
"""
import usb.core
import usb.util
import numpy as np


class AmptekCdTe123:
    """Interface for CdTe X-123 detector from Amptek."""

    vendor_id = 0x10C4
    product_id = 0x842A

    def __init__(self):
        self.device = None
        self._config = None
        self._interface = None
        self._endpoint_in = None
        self._endpoint_out = None

    def open_device(self):
        """Open and configure device."""
        self.device = usb.core.find(idVendor=self.vendor_id,
                                    idProduct=self.product_id)
        if self.device is None:
            raise ValueError('Device not found')

        self.device.set_configuration()
        self._config = self.device.get_active_configuration()
        self._interface = self._config[(0, 0)]
        self._endpoint_out = usb.util.find_descriptor(
            self._interface,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_OUT)

        self._endpoint_in = usb.util.find_descriptor(
            self._interface,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_IN)

    def close_device(self):
        """Close connection to device and free resources."""
        usb.util.dispose_resources(self.device)

    def _write(self, msg):
        """Write a message to the device."""
        answer = self.device.write(self._endpoint_out.bEndpointAddress,
                                   bytes.fromhex(msg))
        return answer

    def _read(self, buffer_size):
        """Read message from the device and return buffer."""
        answer = self.device.read(self._endpoint_in.bEndpointAddress,
                                  buffer_size)
        return answer

    def get_status(self):
        """Send a status request and return status information."""
        self._write('F5FA01010000FE0F')
        status = Status(self._read(8000))

        return status

    def get_spectrum(self, clear=False):
        """Send a spectrum request and return spectrum."""
        if clear:
            self._write('F5FA02020000FE0D')
        else:
            self._write('F5FA02010000FE0E')

        spectrum = self._read(8000)

        return spectrum

    def get_spectrum_status(self, clear=False):
        """Send a spectrum & status request and return spectrum & status."""
        if clear:
            self._write('F5FA02040000FE0B')
        else:
            self._write('F5FA02030000FE0C')

        spectrum_status = self._read(8000)

        return spectrum_status

    def clear_spectum(self):
        """Send a clear spectrum request."""
        self._write('F5FAF0010000FD20')

    def enable_mca(self):
        """Enable MCA."""
        self._write('F5FAF0020000FD1F')

    def disable_mca(self):
        """Disable MCA."""
        self._write('F5FAF0030000FD1E')

    @staticmethod
    def from_raw_spectrun(answer, num_chan=2048):
        """Extract spectrum from response packet."""
        raw = np.array(answer[6:-2])
        raw = np.reshape(raw, (num_chan, 3))
        spectrum = raw[:, 0] + raw[:, 1]*2**8 + raw[:, 2]*2**16

        return spectrum


class Status:
    """Status packet of AmptekCdTe123."""

    def __init__(self, raw_status):
        self._raw = raw_status[6:70]
        self.status = ""
        self.serial_number = ""
        self._process_raw()

    def _process_raw(self):
        """Decode the raw status byte into a human readable output."""
        self.serial_number = '{:06}'.format((self._raw[26]
                                             + self._raw[27]*2**8
                                             + self._raw[28]*2**16
                                             + self._raw[29]*2**24))


if __name__ == '__main__':
    dev = AmptekCdTe123()
    dev.open_device()
    stat = dev.get_status()
    print(stat._raw)
    print(stat.serial_number)
    dev.close_device()
