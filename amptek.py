# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:54:19 2021.

@author: A. Vancraeyenest
"""

from operator import xor, and_

import usb.core
import usb.util
import numpy as np

from detector import Detector


class AmptekCdTe123(Detector):
    """Interface for CdTe X-123 detector from Amptek."""

    vendor_id = 0x10C4
    product_id = 0x842A
    max_allowed_acq_time = 99999999.9
    max_allowed_acq_counts = 4294967295
    min_allowed_gain = 0.750
    max_allowed_gain = 250

    def __init__(self):
        self._device = None
        self._endpoint_in = None
        self._endpoint_out = None

    def acquisition(self, acquisition_time):
        """Start an acquisition and return corresponding Spectrum object."""

    def initialise(self):
        """Initialise the detector."""
        self._device = usb.core.find(idVendor=self.vendor_id,
                                     idProduct=self.product_id)
        if self._device is None:
            raise ValueError('_device not found')

        self._device.set_configuration()
        config = self._device.get_active_configuration()
        interface = config[(0, 0)]
        self._endpoint_out = usb.util.find_descriptor(
            interface,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_OUT)

        self._endpoint_in = usb.util.find_descriptor(
            interface,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_IN)

    def stop(self):
        """Close the connection to the detector and free resources."""
        usb.util.dispose_resources(self._device)

    def _write(self, msg):
        """Write a message to the _device."""
        answer = self._device.write(self._endpoint_out.bEndpointAddress,
                                    bytes.fromhex(msg))
        print(f'{answer=}')
        return answer

    def _read(self, buffer_size):
        """Read message from the _device and return buffer."""
        answer = self._device.read(self._endpoint_in.bEndpointAddress,
                                   buffer_size)
        return answer

    def _get_status(self):
        """Send a status request and return status information."""
        self._write('F5FA01010000FE0F')
        status = Status(self._read(8000))

        return status

    def _get_spectrum(self, clear=False):
        """Send a spectrum request and return spectrum."""
        if clear:
            self._write('F5FA02020000FE0D')
        else:
            self._write('F5FA02010000FE0E')

        spectrum = self._read(8000)

        return spectrum

    def _get_spectrum_status(self, clear=False):
        """Send a spectrum & status request and return spectrum & status."""
        if clear:
            self._write('F5FA02040000FE0B')
        else:
            self._write('F5FA02030000FE0C')

        spectrum_status = self._read(8000)

        return spectrum_status

    def _clear_spectrum(self):
        """Send a clear spectrum request."""
        self._write('F5FAF0010000FD20')

    def _enable_mca(self):
        """Enable MCA."""
        self._write('F5FAF0020000FD1F')

    def _disable_mca(self):
        """Disable MCA."""
        self._write('F5FAF0030000FD1E')

    def _send_text_config(self, config_cmd, save_to_mem=True):
        """
        Send a text fonfiguration command (ASCII commands).

        Parameters
        ----------
        config_cmd : str
            Command string, e.g. 'RESC=Y;'.
        save_to_mem : bool, optional
            True to save the config to detector memory. The default is True.

        Raises
        ------
        error
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if save_to_mem:
            msg = 'F5FA2002'
        else:
            msg = 'F5FA2004'

        cmd_length = len(config_cmd)
        assert cmd_length <= 512

        msg += f'{cmd_length:04X}'
        msg += config_cmd.encode().hex().upper()

        chksum = self._calculate_checksum(msg)
        msg += chksum

        self._write(msg)
        resp = self._read(8000)

        print(resp.tobytes())
        # TODO: check response, log or raise error accordingly

    def _reset_configuration(self):
        """Reset the Configuration to defaults."""
        self._send_text_config('RESC=Y;', save_to_mem=True)

    def _set_acquisition_time(self, acq_time, save_to_mem=True):
        """
        Preset Acquisition Time, without any preset counts.

        Parameters
        ----------
        acq_time : float
            Acquisition time in second, will be rounded to 1 decimal before
            sending to the detector.
        save_to_mem : bool, optional
            True to save the config to detector memory. The default is True.

        Returns
        -------
        None.

        """
        if not 0 <= acq_time <= AmptekCdTe123.max_allowed_acq_time:
            raise ValueError('Acquisition time out of allowed range: '
                             f'{[0, AmptekCdTe123.max_allowed_acq_time]}.')

        self._send_text_config(f'PRET={acq_time:.1f};PREC=OFF;', save_to_mem)

    def _set_acquisition_counts(self, acq_counts, save_to_mem=True):
        """
        Preset Acquisition Counts, without any preset time.

        Parameters
        ----------
        acq_counts : int
        Acquisition counts aka number of events.
        save_to_mem : bool, optional
        True to save the config to detector memory. The default is True.

        Returns
        -------
        None.

        """
        if not isinstance(acq_counts, int):
            raise ValueError('Acquisition counts must be of type integer.')

        if not 0 <= acq_counts <= AmptekCdTe123.max_allowed_acq_counts:
            raise ValueError('Acquisition counts out of allowed range: '
                             f'{[0, AmptekCdTe123.max_allowed_acq_counts]}.')

        self._send_text_config(f'PRET=OFF;PREC={acq_counts};', save_to_mem)

    def _set_acquisition_time_counts(self, acq_time, acq_counts,
                                     save_to_mem=True):
        """
        Preset Acquisition Time and Counts.

        Parameters
        ----------
        acq_time : float
        Acquisition time in seconds, will be rounded to 1 decimal before
        sending to the detector.
        acq_counts : int
        Acquisition counts aka number of events.
        save_to_mem : bool, optional
        True to save the config to detector memory. The default is True.

        Returns
        -------
        None.

        """
        if not isinstance(acq_counts, int):
            raise ValueError('Acquisition counts must be of type integer.')

        if not 0 <= acq_counts <= AmptekCdTe123.max_allowed_acq_counts:
            raise ValueError('Acquisition counts out of allowed range: '
                             f'{[0, AmptekCdTe123.max_allowed_acq_counts]}.')

        if not 0 <= acq_time <= AmptekCdTe123.max_allowed_acq_time:
            raise ValueError('Acquisition time out of allowed range: '
                             f'{[0, AmptekCdTe123.max_allowed_acq_time]}.')

        self._send_text_config(f'PRET={acq_time:.1f};PREC={acq_counts};',
                              save_to_mem)

    def _set_mca_channel(self, number_of_channel):
        """Select Number of MCA Channels."""
        allowed_values = [256, 512, 1024, 2048, 4096, 8192]

        if number_of_channel not in allowed_values:
            raise ValueError('Wrong number of MCA channels.\n'
                             f'{allowed_values=}')

        self._send_text_config(f'MCAC={number_of_channel};', save_to_mem=True)

    def _set_gain(self, gain, save_to_mem=True):
        """
        Set the total gain.

        Parameters
        ----------
        gain : float
            Acquisition gain, will be rounded to 3 decimal before
            sending to the detector.
        save_to_mem : bool, optional
            True to save the config to detector memory. The default is True.

        Returns
        -------
        None.

        """
        min_gain = AmptekCdTe123.min_allowed_gain
        max_gain = AmptekCdTe123.max_allowed_gain
        if not min_gain <= gain <= max_gain:
            raise ValueError(
                f'Gain out of allowed range: {[min_gain, max_gain]}')

        self._send_text_config(f'GAIN={gain:.3f};', save_to_mem)

    @staticmethod
    def _from_raw_spectrun(answer, num_chan=2048):
        """Extract spectrum from response packet."""
        raw = np.array(answer[6:-2])
        raw = np.reshape(raw, (num_chan, 3))
        spectrum = raw[:, 0] + raw[:, 1]*2**8 + raw[:, 2]*2**16

        return spectrum

    @staticmethod
    def _calculate_checksum(packet):
        """
        Calculate checksum of a string packet.

        Parameters
        ----------
        packet : str
            Full packet message for which one calculate checksum.

        Returns
        -------
        checksum : str
            Checksum as a string

        """
        pack = bytes.fromhex(packet)
        checksum = sum(pack)
        checksum = xor(checksum, 0xFFFF) + 1
        checksum = and_(checksum, 0xFFFF)
        return f'{checksum:04X}'

    @staticmethod
    def _verify_checksum(packet):
        """
        Verify the checksum of a string message.

        Parameters
        ----------
        packet : str
            Full packet message with checksum.

        Returns
        -------
        Bool
            True if checksums match, False otherwise.

        """
        checksum = AmptekCdTe123._calculate_checksum(packet[:-4])
        return checksum == packet[-4:]


class Status:
    """Status packet of AmptekCdTe123."""

    def __init__(self, raw_status):
        self._raw = raw_status[6:70]
        self.status = raw_status[6:70].tobytes()
        self.serial_number = ""
        self._process_raw()

    def _process_raw(self):
        """Decode the raw status byte into a human readable output."""
        self.serial_number = '{:06}'.format((self._raw[26]
                                             + self._raw[27]*2**8
                                             + self._raw[28]*2**16
                                             + self._raw[29]*2**24))


if __name__ == '__main__':
    import traceback
    ACK_OK = b'\xF5\xFA\xFF\x00\x00\x00\xFD\x12'
    dev = AmptekCdTe123()
    dev.initialise()
    stat = dev._get_status()
    print(stat._raw)
    print(stat.status)
    print(stat.serial_number)

    try:
        dev._get_spectrum()
    except Exception:
        traceback.print_exc()

    try:
        dev._set_acquisition_time_counts(42, 666, save_to_mem=False)
    except Exception:
        traceback.print_exc()

    dev.stop()
