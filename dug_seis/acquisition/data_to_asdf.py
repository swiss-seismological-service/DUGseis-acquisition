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
# import time
import logging
import os
import io

from ctypes import c_int32

from math import floor
from obspy.core import Stream, Trace

import pyasdf
import numpy as np

from dug_seis.acquisition.time_stamps import TimeStamps

logger = logging.getLogger('dug-seis')


class DataToASDF:

    def __init__(self, param):
        self.folder = param['General']['acquisition_folder']
        if self.folder[len(self.folder) - 1] != "/":
            self.folder += "/"
        self.folder_tmp = self.folder + "tmp/"
        self.compression = param['Acquisition']['asdf_settings']['compression']
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
        self._input_range = param['Acquisition']['hardware_settings']['input_range']

        _nr_of_data_points = floor(c_int32(param['Acquisition']['bytes_per_transfer']).value / 16 / 2)  # nr of channels & 16 bit = 2 bytes
        self.file_length_in_samples = int(param['Acquisition']['asdf_settings']['file_length_sec'] * self._sampling_rate)
        if self.file_length_in_samples < _nr_of_data_points:
            logger.error('file_length_sec cannot be shorter than one buffer transfer: {} seconds'
                         .format(_nr_of_data_points/self._sampling_rate))
            self.error = True
        else:
            self.error = False
        self._file_handle = None
        self._last_used_file_name = None

        self._last_used_julian_day_folder = ""
        self._data_points_in_this_file = 0

        self.time_stamps = TimeStamps(param)

    def set_starttime_now(self):
        self.time_stamps.set_starttime_now()

    def _check_if_folders_exist_create_if_needed(self):
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
            logger.info("creating folder: {}".format(self.folder))

        if not os.path.isdir(self.folder_tmp):
            os.makedirs(self.folder_tmp)
            logger.info("creating folder_tmp: {}".format(self.folder_tmp))

    def _creat_new_julian_day_folder_if_needed(self):
        if self.time_stamps.is_julian_day_still_the_same():
            pass
        else:
            self.time_stamps.set_current_julian_day()
            self._last_used_julian_day_folder = self.folder + self.time_stamps.julian_day_str() + '/'
            if os.path.isdir(self._last_used_julian_day_folder):
                logger.info("julianday folder: {} already exists, no need to create it.".format(self._last_used_julian_day_folder))
            else:
                logger.info("creating julianday folder: {}".format(self._last_used_julian_day_folder))
                os.makedirs(self._last_used_julian_day_folder)

    def _create_new_file(self):
        """Creates a new file.
        With parameters of the DataToAsdf class. Sets the age of the file to time.time()."""

        file_name = "{0}__{1}__{2}.h5".format(
            self.time_stamps.starttime_str(),
            self.time_stamps.endtime_str(),
            self.stats['station'].zfill(2))
        folder_file_name = "{0}{1}".format(self.folder_tmp, file_name)
        logger.info("_create_new_file with folder_file_name = {0}".format(folder_file_name))

        # logger.info("self.compression = {}, type = {}".format(self.compression, type(self.compression)))
        if self.compression == 'None':
            # logger.info("if self.compression = None: -> true")
            self._file_handle = pyasdf.ASDFDataSet(folder_file_name, compression=None)
        else:
            self._file_handle = pyasdf.ASDFDataSet(folder_file_name, compression=self.compression)

        if self._last_used_file_name is not None:
            self._creat_new_julian_day_folder_if_needed()
            os.rename(self.folder_tmp + self._last_used_file_name, self._last_used_julian_day_folder + self._last_used_file_name)
        self._last_used_file_name = file_name

        self._add_all_auxiliary_data(self._file_handle)

    def _add_all_auxiliary_data(self, ds):
        # pyasdf.ASDFDataSet.add_auxiliary_data
        # stuff that is not in self.stats
        ds.add_auxiliary_data(data=np.array([True]), data_type="hardware_settings", path="various",
                              parameters={"exampleValue": 5})
        ds.add_auxiliary_data(data=np.array(self._input_range), data_type="hardware_settings", path="input_range",
                              parameters={})

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

        if self._file_handle is None:
            # logger.info("no file found creating new file.\n")
            self._check_if_folders_exist_create_if_needed()
            self._create_new_file()

        # logger.info("data_points_to_file1: {}".format(data_points_to_file1))
        if data_points_to_file1 > 0:
            stream = self._add_samples_to_file(np_data_list, 0, data_points_to_file1)
            logger.info("start time of stream = {0}".format(self.time_stamps.starttime_str()))
            self._file_handle.append_waveforms(stream, tag="raw_recording")
            del stream

        # starttime for next segment
        self.time_stamps.set_starttime_next_segment( int(data_points_to_file1) )

        if data_points_to_file2 != 0:
            # logger.info("data_points_to_file2: {}".format(data_points_to_file2))
            self._create_new_file()
            self._data_points_in_this_file = data_points_to_file2
            stream = self._add_samples_to_file(np_data_list, data_points_to_file1, int(np_data_list[0].size / 16))
            self._file_handle.append_waveforms(stream, tag="raw_recording")
            del stream
            self.time_stamps.set_starttime_next_segment( int(self._data_points_in_this_file ))
