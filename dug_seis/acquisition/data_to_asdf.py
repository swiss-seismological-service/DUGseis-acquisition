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
from dug_seis.acquisition.stats_handling import StatsHandling

logger = logging.getLogger('dug-seis')


class DataToASDF:

    def __init__(self, param):
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
        # self._data_points_in_this_file = 757125   # leads to 5 datapoints in next file fast (10sec filesize)
        # self._data_points_in_this_file = 854270     # big check
        self._data_points_since_start = 0
        # calculate when next datapoint needs to be deleted
        _fpga_value_should = 2**32*self._sampling_rate/20e6
        _fpga_value_is = round(_fpga_value_should)
        _one_sample_delay_in_sec = 1/(20e6*(_fpga_value_is-_fpga_value_should)/2**32)
        self._drop_point_every = self._sampling_rate * _one_sample_delay_in_sec
        # for DEGUGGING only, uncomment to see every 45 sec a dropped sample
        # self._drop_point_every = 200e3*45 # for DEGUGGING only
        self._drop_next_point_at = self._drop_point_every
        logger.info("one datapoint will be dropped every {} sample".format(self._drop_point_every))
        self._stream_leftover_data = None

        self.time_stamps = TimeStamps(param)
        self.file_handling = FileHandling(param)
        self.stats_handling = StatsHandling(param)

    def set_starttime_now(self):
        self.time_stamps.set_starttime_now()

    def _add_samples_to_stream(self, np_data_list, start_sample, end_sample):
        stream = Stream()
        self.stats_handling.set_starttime( self.time_stamps.starttime_UTCDateTime() )

        card_nr = 0
        for np_data in np_data_list:

            for i in range(16):
                self.stats_handling.set_location(card_nr, i)
                stream += Trace(np_data[i, start_sample:end_sample], header=self.stats_handling.get_stats())

            del np_data
            card_nr += 1

        return stream

    def data_to_asdf(self, np_data_list):

        nr_of_new_datapoints = int(np_data_list[0].size / 16)
        self._data_points_since_start += nr_of_new_datapoints
        if self.file_length_in_samples - self._data_points_in_this_file >= nr_of_new_datapoints:
            # logger.info("data fits in file")
            self._data_points_in_this_file += nr_of_new_datapoints
            data_points_to_file1 = nr_of_new_datapoints
        else:
            # logger.info("splitting file")
            data_points_to_file1 = self.file_length_in_samples - self._data_points_in_this_file

        data_points_to_next_file = nr_of_new_datapoints - data_points_to_file1
        if data_points_to_file1 + data_points_to_next_file != nr_of_new_datapoints:
            logger.error("error: data_points_to_file1 + data_points_to_next_file != nr_of_new_datapoints")

        # logger.info("data_points_to_file1: {}".format(data_points_to_file1))
        if data_points_to_file1 > 0:
            stream = self._add_samples_to_stream(np_data_list, 0, data_points_to_file1)
            # logger.info("start time of this buffer = {0}".format(self.time_stamps.starttime_str()))
            if self._stream_leftover_data:
                # print(stream)
                # print(self._stream_leftover_data)
                stream = self._stream_leftover_data + stream
                stream.merge()
                if len(stream.get_gaps()) != 0:
                    logger.error(".merge did not work as expected, there are gaps.")
                    # stream.print_gaps()
                # logger.info("stream {} x {}".format(len(stream), len(stream[0])))
                del self._stream_leftover_data
                self._stream_leftover_data = None
            else:
                pass
                # logger.info("no leftover")
            self.file_handling.append_waveform_to_file(self.time_stamps, stream)
            self.time_stamps.set_starttime_next_segment(data_points_to_file1)
            del stream

        if data_points_to_next_file != 0:
            logger.info("starting the next file with {} datapoints.".format(data_points_to_next_file))
            start_sample = data_points_to_file1
            self.file_handling.create_new_file(self.time_stamps)

            # drop one sample if needed, its the first sample of the new file
            if self._data_points_since_start > self._drop_next_point_at:
                logger.info("dropped one data point nr: {}".format(self._data_points_since_start))
                self._drop_next_point_at += self._drop_point_every
                start_sample += 1
                self._data_points_since_start -= 1
                data_points_to_next_file -= 1

            self._data_points_in_this_file = data_points_to_next_file
            self._stream_leftover_data = self._add_samples_to_stream(np_data_list, start_sample, nr_of_new_datapoints)
            self.time_stamps.set_starttime_next_segment(data_points_to_next_file)

