# DUG-Seis
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#
"""File and directory handling for the asdf file.
Auxilliary data is kind of experimental and probably needs to be moved out of here in a later stage.
"""

import logging
import os
import pyasdf

import numpy as np

from dug_seis.acquisition.time_stamps import TimeStamps

logger = logging.getLogger('dug-seis')

class FileHandling:

    def __init__(self, param):
        self.compression = param['Acquisition']['asdf_settings']['compression']
        self.folder = param['General']['acquisition_folder']
        self.station = param['General']['stats']['daq_unit']
        if self.folder[len(self.folder) - 1] != "/":
            self.folder += "/"
        self.folder_tmp = self.folder + "tmp/"
        self._file_handle = None
        self._last_used_file_name = None
        self._last_used_julian_day_folder = ""

        self._input_range_sorted = param['Acquisition']['hardware_settings']['input_range_sorted']

    def _check_if_folders_exist_create_if_needed(self):
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
            logger.info("creating folder: {}".format(self.folder))

        if not os.path.isdir(self.folder_tmp):
            os.makedirs(self.folder_tmp)
            logger.info("creating folder_tmp: {}".format(self.folder_tmp))

    def _creat_new_julian_day_folder_if_needed(self, time_stamps):
        if time_stamps.is_julian_day_still_the_same():
            pass
        else:
            time_stamps.set_current_julian_day()
            self._last_used_julian_day_folder = self.folder + time_stamps.julian_day_str() + '/'
            if os.path.isdir(self._last_used_julian_day_folder):
                logger.info("julianday folder: {} already exists, no need to create it.".format(self._last_used_julian_day_folder))
            else:
                logger.info("creating julianday folder: {}".format(self._last_used_julian_day_folder))
                os.makedirs(self._last_used_julian_day_folder)

    def create_new_file(self, time_stamps):
        """Creates a new file.
        With parameters of the DataToAsdf class. Sets the age of the file to time.time()."""

        file_name = "{0}__{1}__{2}.h5".format(
            time_stamps.starttime_str(),
            time_stamps.endtime_str(),
            self.station.zfill(2))
        folder_file_name = "{0}{1}".format(self.folder_tmp, file_name)
        logger.info("create_new_file with folder_file_name = {0}".format(folder_file_name))

        # logger.info("self.compression = {}, type = {}".format(self.compression, type(self.compression)))
        if self.compression == 'None':
            # logger.info("if self.compression = None: -> true")
            self._file_handle = pyasdf.ASDFDataSet(folder_file_name, compression=None)
        else:
            self._file_handle = pyasdf.ASDFDataSet(folder_file_name, compression=self.compression)

        if self._last_used_file_name is not None:
            self._creat_new_julian_day_folder_if_needed(time_stamps)
            os.rename(self.folder_tmp + self._last_used_file_name, self._last_used_julian_day_folder + self._last_used_file_name)
        self._last_used_file_name = file_name

        self._add_all_auxiliary_data(self._file_handle)

    def _add_all_auxiliary_data(self, ds):
        # pyasdf.ASDFDataSet.add_auxiliary_data
        # stuff that is not in self.stats
        # ds.add_auxiliary_data(data=np.array([True]), data_type="hardware_settings", path="various",
        #                      parameters={"exampleValue": 5})
        ds.add_auxiliary_data(data=np.array(self._input_range_sorted), data_type="hardware_settings", path="input_range_sorted",
                              parameters={})

    def append_waveform_to_file(self, time_stamps, stream):
        if self._file_handle is None:
            # logger.info("no file found creating new file. (probably first run)\n")
            self._check_if_folders_exist_create_if_needed()
            self.create_new_file(time_stamps)

        self._file_handle.append_waveforms(stream, tag="raw_recording")
