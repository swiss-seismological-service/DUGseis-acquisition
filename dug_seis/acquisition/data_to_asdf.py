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
import time
import logging
import os
import io

from ctypes import c_int32

from math import floor
from obspy.core import Stream, Trace, UTCDateTime
from obspy.core.inventory import Longitude, Latitude

import pyasdf
import numpy as np

from dug_seis.acquisition.flat_response_stationxml import get_flat_response_inventory

logger = logging.getLogger('dug-seis')


class DataToASDF:

    def __init__(self, param):
        self.folder = param['General']['acquisition_folder']
        if self.folder[len(self.folder) - 1] != "/":
            self.folder += "/"
        self.folder_tmp = self.folder + "tmp/"
        self.filename = param['General']['project_name']
        self.compression = param['Acquisition']['asdf_settings']['compression']
        self.file_length_sec = param['Acquisition']['asdf_settings']['file_length_sec']

        self.l_notify_size = c_int32(param['Acquisition']['bytes_per_transfer'])

        self.stats = {'network': param['General']['stats']['network'],
                      'station': param['General']['stats']['daq_unit'],
                      'location': '00',
                      'channel': '001',
                      'starttime': UTCDateTime().timestamp,
                      'delta': 1/param['Acquisition']['hardware_settings']['sampling_frequency'],
                      'gain': '0'
                      }

        self._sampling_rate = param['Acquisition']['hardware_settings']['sampling_frequency']
        self._input_range = param['Acquisition']['hardware_settings']['input_range']
        self._channel_count = len( param['Acquisition']['hardware_settings']['input_range'] )
        self._nr_of_data_points = floor(self.l_notify_size.value / 16 / 2)  # nr of channels & 16 bit = 2 bytes
        # self.file_length_in_samples = self._nr_of_data_points * 5  # a length that does not split transferred blocks
        self.file_length_in_samples = self.file_length_sec * 1/self.stats['delta']
        if self.file_length_in_samples < self._nr_of_data_points:
            logger.error('file_length_sec cannot be shorter than one buffer transfer: {} seconds'
                         .format(self._nr_of_data_points/self._sampling_rate))
            self.error = True
        else:
            self.error = False
        self._file_handle = None
        self._time_age_of_file = 0  # keeps track internally how old the file is
        self._last_used_file_name = None
        self._really_verbose_timing_output = False
        self._last_used_julian_day = -1
        self._last_used_julian_day_folder = ""

        self._data_points_in_this_file = 0

    def set_starttime_now(self):
        starttime_now = UTCDateTime().ns
        self.stats['starttime_ns'] = round(starttime_now, -9) - int((4 * self.stats['delta'] * 10**9))  # balance 4
        # samples pre-trigger from start time in seconds
        self.stats['starttime'] = UTCDateTime(ns=self.stats['starttime_ns'])

        logger.info("new starttime set to: {}".format(UTCDateTime(ns=self.stats['starttime_ns'])))
        logger.info("new starttime, software: {}".format(UTCDateTime(ns=starttime_now)))

    def _check_if_folders_exist_create_if_needed(self):
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
            logger.info("creating folder: {}".format(self.folder))

        if not os.path.isdir(self.folder_tmp):
            os.makedirs(self.folder_tmp)
            logger.info("creating folder_tmp: {}".format(self.folder_tmp))

    def _creat_new_julian_day_folder_if_needed(self):
        if UTCDateTime(ns=self.stats['starttime_ns']).julday != self._last_used_julian_day:
            self._last_used_julian_day = UTCDateTime(ns=self.stats['starttime_ns']).julday
            self._last_used_julian_day_folder = self.folder + str(self._last_used_julian_day) + '/'
            if os.path.isdir(self._last_used_julian_day_folder):
                logger.info("julianday folder: {} already exists, no need to create it.".format(self._last_used_julian_day_folder))
            else:
                logger.info("creating julianday folder: {}".format(self._last_used_julian_day_folder))
                os.makedirs(self._last_used_julian_day_folder)


    def _create_new_file(self):
        """Creates a new file.
        With parameters of the DataToAsdf class. Sets the age of the file to time.time()."""

        file_name = "{0}__{1}__{2}.h5".format(
            UTCDateTime(ns=self.stats['starttime_ns']),
            UTCDateTime(ns=self.stats['starttime_ns'] + int((self.file_length_in_samples-1) * (self.stats['delta'] * 10**9))),
            self.stats['station'].zfill(2))
        file_name = file_name.replace(":", "_")
        file_name = file_name.replace("-", "_")
        folder_file_name = "{0}{1}".format(self.folder_tmp, file_name)
        logger.info("samples in file = {0}".format(self.file_length_in_samples))
        logger.info("_create_new_file with folder_file_name = {0}".format(folder_file_name))


        self._time_age_of_file = time.time()
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

        # self._add_all_station_xml_s(self._file_handle)
        self._add_all_auxiliary_data(self._file_handle)

    def _add_all_auxiliary_data(self, ds):
        # pyasdf.ASDFDataSet.add_auxiliary_data
        # stuff that is not in self.stats
        ds.add_auxiliary_data(data=np.array([True]), data_type="hardware_settings", path="various",
                              parameters={"exampleValue": 5})
        ds.add_auxiliary_data(data=np.array(self._input_range), data_type="hardware_settings", path="input_range",
                              parameters={})

    def _add_all_station_xml_s(self, ds):
        for i in range(self._channel_count):
            ds.add_stationxml(self._create_station_xml(i))

    def _create_station_xml(self, channel_nr):
        inv = get_flat_response_inventory(
            sensitivity_value=self._input_range[channel_nr] * 2 / 65536,  # conversion 16bit int to mV
            sensitivity_frequency=1.0,
            input_units="M/S",  # ?
            output_units="Counts",  # ?
            creation_date=UTCDateTime(self._time_age_of_file),
            network_code=self.stats['network'],
            station_code=self.stats['station'],
            location_code=self._get_station_name(channel_nr),
            channel_code=self.stats['channel'],
            sampling_rate=self.stats['sampling_rate'],
            latitude=self.stats['origin_ch1903_north'],
            longitude=self.stats['origin_ch1903_east'],
            depth=self.stats['origin_elev'],
            elevation=0.0,
            azimuth=0.0,
            dip=0.0)

        # Test if the response makes up a valid StationXML file.
        with io.BytesIO() as buf:
            inv.write(buf, format="stationxml", validate=True)

        return inv

    def _get_station_name(self, channel_nr):
        return str(channel_nr).zfill(2)

    def _add_samples_to_file(self, np_data_list, start_sample, end_sample):
        stream = Stream()
        # self.stats['starttime'] = UTCDateTime(ns=self.stats['starttime_ns'])# adjust stats['starttime'], stream can only read UTCDateTime stamps and not nanoseconds in integer

        card_nr = 0
        for np_data in np_data_list:

            for i in range(16):
                self.stats['location'] = self._get_station_name((i + 16 * card_nr)+1)
                stream += Trace(np_data[i, start_sample:end_sample], header=self.stats)
                # logger.info("{}, {}\n".format(self.stats['station'], self.stats['starttime']))

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
            # logger.info("file handle: {}".format(self._file_handle))
            # logger.info(stream)
            # logger.info(type(self.stats['starttime']))
            # logger.info(self.stats['starttime'])
            logger.info("start time of stream = {0}".format(UTCDateTime(ns=self.stats['starttime_ns'])))
            self._file_handle.append_waveforms(stream, tag="raw_recording")
            del stream

        # logger.info("---")
        # logger.info(self.stats['starttime'])

        # vorher = self.stats['starttime']

        # starttime for next segment
        # self.stats['starttime'] = self.stats['starttime'] + self._data_points_in_this_file / self._sampling_rate
        self.stats['starttime_ns'] = self.stats['starttime_ns'] + int(data_points_to_file1 * (self.stats['delta'] * 10 ** 9))
        self.stats['starttime'] = UTCDateTime(ns=self.stats['starttime_ns'])
        logger.info("time delta between files in ns = {0}".format(int(data_points_to_file1 * (self.stats['delta'] * 10 ** 9))))
        # logger.info("data_points_in_this_file = {0}".format(self._data_points_in_this_file))
        # logger.info("seconds in this_file = {0}".format(self._data_points_in_this_file / self._sampling_rate))
        # logger.info("start_time_of next file = {0}".format(self.stats['starttime']))
        # self.stats['starttime'] = UTCDateTime(self.stats['starttime']) + data_points_to_file1 / self._sampling_rate
        # nacher = self.stats['starttime']
        # logger.info('{} {} {}'.format(vorher, nacher, vorher-nacher, type(nacher)))
        # logger.info('{}'.format(data_points_to_file1 / self._sampling_rate))

        if data_points_to_file2 != 0:
            # logger.info("data_points_to_file2: {}".format(data_points_to_file2))
            self._create_new_file()
            self._data_points_in_this_file = data_points_to_file2
            stream = self._add_samples_to_file(np_data_list, data_points_to_file1, int(np_data_list[0].size / 16))
            self._file_handle.append_waveforms(stream, tag="raw_recording")
            del stream
            # self.stats['starttime'] = UTCDateTime(self.stats['starttime']) + self._data_points_in_this_file / self._sampling_rate
            # self.stats['starttime'] = self.stats['starttime'] + self._data_points_in_this_file / self._sampling_rate
            self.stats['starttime_ns'] = self.stats['starttime_ns'] + int(self._data_points_in_this_file * (self.stats['delta'] * 10 ** 9))
            self.stats['starttime'] = UTCDateTime(ns=self.stats['starttime_ns'])
            logger.info("time delta between files in ns = {0}".format(
                int(self._data_points_in_this_file * (self.stats['delta'] * 10 ** 9))))
        # else:
            # starttime for next segment
            # self.stats['starttime'] = UTCDateTime(self.stats['starttime']) + self._nr_of_data_points / self._sampling_rate

        # logger.info("self.stats[ starttime ] = {}".format(self.stats['starttime']))
