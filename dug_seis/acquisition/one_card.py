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
import time

import numpy as np
import os.path

import dug_seis.acquisition.hardware_driver.regs as regs
import dug_seis.acquisition.hardware_driver.spcerr as err

from math import floor
from ctypes import byref, c_int32, POINTER, c_int16, cast, addressof

if os.path.isfile("c:\\windows\\system32\\spcm_win64.dll") or os.path.isfile("c:\\windows\\system32\\spcm_win32.dll") or os.name == 'posix':
    from dug_seis.acquisition.one_card_std_init import init_card as sdt_init_card
    from dug_seis.acquisition.hardware_driver.pyspcm import spcm_dwSetParam_i32, spcm_dwGetParam_i32, spcm_vClose
else:
    pass
    # logging at import messes with the later logging settings, no logging needed here
    # logger.warning('one_card.py: problems loading the hardware driver. simulation still available.')

logger = logging.getLogger('dug-seis')

class Card:

    def __init__(self, param, card_nr):

        # l_notify_size = c_int32(regs.KILO_B(2 * 1024))
        self.l_notify_size = c_int32(param['Acquisition']['bytes_per_transfer'])
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
        selected_range = c_int32(0)
        spcm_dwGetParam_i32(self.h_card, regs.SPC_AMP0, byref(selected_range))
        logger.info("selectedRange: +- {0:.3f} mV\n".format(selected_range.value))

    def wait_for_data(self):
        """Wait for a data package(l_notify_size) to be ready.
        Timeout after SPC_TIMEOUT, if data in not ready. (defined in one_card_sdt_init.py)"""

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

        if regs.M2STAT_EXTRA_OVERRUN >> 0x4 & l_status.value:
            logger.error("overrun or underrun detected: M2STAT_EXTRA_OVERRUN")
        return l_status.value

    def trigger_received(self):
        if self.read_status() & regs.M2STAT_CARD_TRIGGER:  # The first trigger has been detected.
            return True
        return False

    def read_xio(self):
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
        # cast to pointer to 16bit integer
        nr_of_datapoints = int(bytes_per_transfer / 16 / 2)
        x = cast(addressof(self._pv_buffer) + self.read_buffer_position() + bytes_offset, POINTER(c_int16))
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
