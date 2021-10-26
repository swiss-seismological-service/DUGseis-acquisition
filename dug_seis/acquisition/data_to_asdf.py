# DUG-Seis
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#
"""Read data from an array to a ASDF file.
Create a new file when needed.
"""
import logging

from ctypes import c_int32

from math import floor
from obspy.core import Stream, Trace

import numpy as np

from dug_seis.acquisition.time_stamps import TimeStamps
from dug_seis.acquisition.file_handling import FileHandling

logger = logging.getLogger('dug-seis')


class DataToASDF:

    def __init__(self, param):

        self.station_naming = param['Acquisition']['asdf_settings']['station_naming']

        self.l_notify_size = c_int32(param['Acquisition']['bytes_per_transfer'])

        self.stats = {'network': param['General']['stats']['network'],
                      'station': param['General']['stats']['daq_unit'],
                      'location': '00',
                      'channel': '001',
                      'starttime': '',
                      'delta': 1/param['Acquisition']['hardware_settings']['sampling_frequency'],
                      'gain': '0'
                      }

        self._sampling_rate = param['Acquisition']['hardware_settings']['sampling_frequency']

        _nr_of_data_points = floor(c_int32(param['Acquisition']['bytes_per_transfer']).value / 16 / 2)  # nr of channels & 16 bit = 2 bytes
        self.file_length_in_samples = int(param['Acquisition']['asdf_settings']['file_length_sec'] * self._sampling_rate)
        if self.file_length_in_samples < _nr_of_data_points:
            logger.error('file_length_sec cannot be shorter than one buffer transfer: {} seconds'
                         .format(_nr_of_data_points/self._sampling_rate))
            self.error = True
        else:
            self.error = False

        self._data_points_in_this_file = 0

        self.time_stamps = TimeStamps(param)
        self.file_handling = FileHandling(param)

    def set_starttime_now(self):
        self.time_stamps.set_starttime_now()

    def _get_station_name(self, channel_nr):
        return str(self.station_naming[channel_nr]).zfill(2)

    def _add_samples_to_file(self, np_data_list, start_sample, end_sample):
        stream = Stream()

        self.stats['starttime'] = self.time_stamps.starttime_UTCDateTime()

        card_nr = 0
        for np_data in np_data_list:

            for i in range(16):
                self.stats['location'] = self._get_station_name(i + 16 * card_nr)
                stream += Trace(np_data[i, start_sample:end_sample], header=self.stats)

            del np_data
            card_nr += 1

        return stream

    def data_to_asdf(self, np_data_list):

        # if self._sampling_rate * self.file_length_sec - self._data_points_in_this_file >= np_data_list[0].size / 16:
        if self.file_length_in_samples - self._data_points_in_this_file >= np_data_list[0].size / 16:

            # logger.info("data fits in file")
            self._data_points_in_this_file += np_data_list[0].size / 16
            data_points_to_file1 = int(np_data_list[0].size / 16)
            # data_points_to_file1 = 50000  # 65000 error on third file?
        else:
            # logger.info("split file")
            # data_points_to_file1 = int(self._sampling_rate * self.file_length_sec - self._data_points_in_this_file)
            data_points_to_file1 = int(self.file_length_in_samples - self._data_points_in_this_file)

        data_points_to_file2 = int(np_data_list[0].size / 16 - data_points_to_file1)
        logger.info("data_points_in_file1: {0}".format(data_points_to_file1))
        logger.info("data_points_in_file2: {0}".format(data_points_to_file2))
        if data_points_to_file1 + data_points_to_file2 != np_data_list[0].size / 16:
            logger.error("error: data_points_to_file1 + data_points_to_file2 != np_data_list[0].size / 16")

        # logger.info("data_points_to_file1: {}".format(data_points_to_file1))
        if data_points_to_file1 > 0:
            stream = self._add_samples_to_file(np_data_list, 0, data_points_to_file1)
            logger.info("start time of stream = {0}".format(self.time_stamps.starttime_str()))
            self.file_handling.append_waveform_to_file(self.time_stamps, stream)
            del stream

        # starttime for next segment
        self.time_stamps.set_starttime_next_segment( int(data_points_to_file1) )

        if data_points_to_file2 != 0:
            # logger.info("data_points_to_file2: {}".format(data_points_to_file2))
            self.file_handling.create_new_file(self.time_stamps)
            self._data_points_in_this_file = data_points_to_file2
            stream = self._add_samples_to_file(np_data_list, data_points_to_file1, int(np_data_list[0].size / 16))
            self.file_handling.append_waveform_to_file(self.time_stamps, stream)
            del stream
            self.time_stamps.set_starttime_next_segment( int(self._data_points_in_this_file ))
