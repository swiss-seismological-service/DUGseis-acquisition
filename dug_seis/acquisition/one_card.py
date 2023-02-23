# DUG-Seis
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#
"""Representation of one data acquisition card. Translation between python and the spectrum hardware drive.
- making function names understandable
- translation to hardware calls
- bundling of several calls to a "higher level one"
- hiding card pointers and management
"""

import logging

import numpy as np
import os.path

import dug_seis.acquisition.hardware_driver.regs as regs
import dug_seis.acquisition.hardware_driver.spcerr as err

from ctypes import byref, c_int32, POINTER, c_int16, cast, addressof, cdll

if os.path.isfile("c:\\windows\\system32\\spcm_win64.dll") or os.path.isfile(
        "c:\\windows\\system32\\spcm_win32.dll"):
    from dug_seis.acquisition.one_card_std_init import init_card as sdt_init_card
    from dug_seis.acquisition.hardware_driver.pyspcm import spcm_dwSetParam_i32, spcm_dwGetParam_i32, spcm_vClose
else:
    pass
    # logging at import messes with the later logging settings, no logging needed here
    # logger.warning('one_card.py: problems loading the hardware driver. simulation still available.')

if os.name == 'posix':
    try:
        spcmDll = cdll.LoadLibrary("libspcm_linux.so")
        from dug_seis.acquisition.one_card_std_init import init_card as sdt_init_card
        from dug_seis.acquisition.hardware_driver.pyspcm import spcm_dwSetParam_i32, spcm_dwGetParam_i32, spcm_vClose
    except OSError as exception:
        print("linux card driver could not be loaded.")
        print(exception)

logger = logging.getLogger('dug-seis')


class Card:

    def __init__(self, param, card_nr):

        # l_notify_size = c_int32(regs.KILO_B(2 * 1024))
        self.l_notify_size = c_int32(param['Acquisition']['bytes_per_transfer'])
        self.ram_buffer_size = param['Acquisition']['hardware_settings']['ram_buffer_size']
        self.card_nr = card_nr
        self.h_card = None

        self.debug_buffer_behaviour = False

        self._pv_buffer = None
        # nr of channels & 16 bit = 2 bytes
        # self._nr_of_datapoints = floor(param['Acquisition']['bytes_per_transfer'] / 16 / 2)

        input_range_sorted = param['Acquisition']['hardware_settings']['input_range_sorted']
        if card_nr == 0:
            self.scaling_this_card = [i * 2 / 65536 for i in input_range_sorted[0:16]]   # e.g. 16 bit to +- 10'000 mV
        else:
            self.scaling_this_card = [i * 2 / 65536 for i in input_range_sorted[16:32]]

    def init_card(self, param):
        """Initialise card. Setup card parameters. Reserve buffers for DMA data transfer."""
        logger.info("init card: {}".format(self.card_nr))
        if self.card_nr == 0 or self.card_nr == 1:
            self.h_card, self._pv_buffer = sdt_init_card(param, self.card_nr)
        else:
            logger.error("card_nr needs to be 0 or 1, received:{}".format(self.card_nr))

    def print_settings(self):
        """print selected voltage range."""
        selected_range = c_int32(0)
        spcm_dwGetParam_i32(self.h_card, regs.SPC_AMP0, byref(selected_range))
        logger.info("selectedRange: +- {0:.3f} mV\n".format(selected_range.value))

    def wait_for_data(self):
        """Wait for a data package(l_notify_size) to be ready.
        Timeout after SPC_TIMEOUT, if data in not ready. (defined in one_card_sdt_init.py).
        param['Acquisition']['hardware_settings']['timeout']"""

        dw_error = spcm_dwSetParam_i32(self.h_card, regs.SPC_M2CMD, regs.M2CMD_DATA_WAITDMA)
        if dw_error != err.ERR_OK:
            if dw_error == err.ERR_TIMEOUT:
                logger.error("{0} ... Timeout".format(self.card_nr))
            else:
                logger.error("{0} ... Error: {1:d}".format(self.card_nr, dw_error))

    def read_status(self):
        """Read the status of the card. SPC_M2STATUS."""
        l_status = c_int32()
        spcm_dwGetParam_i32(self.h_card, regs.SPC_M2STATUS, byref(l_status))

        if regs.M2STAT_DATA_OVERRUN & l_status.value:
            logger.error("card {} overrun or underrun detected: M2STAT_DATA_OVERRUN".format(self.card_nr))
        return l_status.value

    def trigger_received(self):
        """Returns true once the card received the first trigger."""
        if self.read_status() & regs.M2STAT_CARD_TRIGGER:  # The first trigger has been detected.
            return True
        return False

    def read_xio(self):
        """Read the digital IO's."""
        l_data = c_int32()
        spcm_dwGetParam_i32(self.h_card, regs.SPC_XIO_DIGITALIO, byref(l_data))
        return l_data.value

    def nr_of_bytes_available(self):
        """Get amount of available data."""
        l_avail_user = c_int32()
        spcm_dwGetParam_i32(self.h_card, regs.SPC_DATA_AVAIL_USER_LEN, byref(l_avail_user))
        return l_avail_user.value

    def read_buffer_position(self):
        """Get where the buffer reader/pointer is."""
        l_pc_pos = c_int32()
        spcm_dwGetParam_i32(self.h_card, regs.SPC_DATA_AVAIL_USER_POS, byref(l_pc_pos))
        return l_pc_pos.value

    def read_data(self, bytes_per_transfer, bytes_offset):
        """Read data from the RAM buffer. Interprets a part of the RAM buffer as array.

        Args:
            bytes_per_transfer: how many bytes that are interpreted.
            bytes_offset: bytes left out from the start of the buffer.
        """
        # cast to pointer to 16bit integer
        nr_of_datapoints = int(bytes_per_transfer / 16 / 2)
        # logger.info("read_data: {} Mb".format((self.read_buffer_position() + bytes_offset)/1024/1024))
        if self.read_buffer_position() + bytes_offset >= self.ram_buffer_size:
            # logger.info("wrap around, bytes_offset % ram_buffer_size: {} Mb"
            #             .format(bytes_offset % self.ram_buffer_size/1024/1024))
            offset = (self.read_buffer_position() + bytes_offset) % self.ram_buffer_size
        else:
            offset = self.read_buffer_position() + bytes_offset
        x = cast(addressof(self._pv_buffer) + offset, POINTER(c_int16))
        np_data = np.ctypeslib.as_array(x, shape=(nr_of_datapoints, 16)).T
        return np_data

    def data_has_been_read(self):
        """Mark buffer space as available again."""
        if self.debug_buffer_behaviour is True:
            print("mark buffer as available: {0:08x}".format(self.l_notify_size.value))
        spcm_dwSetParam_i32(self.h_card, regs.SPC_DATA_AVAIL_CARD_LEN, self.l_notify_size)

    def stop_recording(self):
        """Send the stop command to the card."""
        logger.info("card {0} stopped.".format(self.card_nr))
        spcm_dwSetParam_i32(self.h_card, regs.SPC_M2CMD, regs.M2CMD_CARD_STOP | regs.M2CMD_DATA_STOPDMA)

    def close(self):
        """Close the handle to the card."""
        if self.h_card is not None:
            spcm_vClose(self.h_card)
            logger.info("card {0} closed.".format(self.card_nr))
