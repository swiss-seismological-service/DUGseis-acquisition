# DUG-Seis
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#
"""Timestamp creation.
"""
# import time
import logging

from math import floor
from obspy.core import UTCDateTime

logger = logging.getLogger('dug-seis')


class TimeStamps:

    def __init__(self, param):

        self._starttime_ns = None
        self._last_used_julian_day = -1

        self._delta = 1/param['Acquisition']['hardware_settings']['sampling_frequency']
        self._file_length_in_samples = int(param['Acquisition']['asdf_settings']['file_length_sec'] *
            param['Acquisition']['hardware_settings']['sampling_frequency'])

    def set_starttime_now(self):
        """Sets the start of the acquisition to the current PC time. Subtracts the pre-trigger."""
        starttime_now = UTCDateTime().ns
        # samples pre-trigger from start time in seconds
        self._starttime_ns = round(starttime_now, -9) - int((4 * self._delta * 10**9))  # balance 4

        logger.info("Data starttime set to: {}".format(UTCDateTime(ns=self._starttime_ns)))
        logger.info("System time: {} sys/data time difference: {}".format(
            UTCDateTime(ns=starttime_now), UTCDateTime(ns=starttime_now)-UTCDateTime(ns=self._starttime_ns)))

    def is_julian_day_still_the_same(self):
        """Check if julian day changed."""
        if UTCDateTime(ns=self._starttime_ns).julday == self._last_used_julian_day:
            return True
        return False

    def set_current_julian_day(self):
        """"""
        self._last_used_julian_day = UTCDateTime(ns=self._starttime_ns).julday

    def julian_day_str(self):
        return str(self._last_used_julian_day)

    def starttime_UTCDateTime(self):
        """Read the start time as UTCDateTime."""
        return UTCDateTime(ns=self._starttime_ns)

    def starttime_str(self):
        """The start time as string."""
        _st = str(UTCDateTime(ns=self._starttime_ns))
        _st = _st.replace(":", "_")
        _st = _st.replace("-", "_")
        return _st

    def endtime_str(self):
        """The end time as string."""
        _et = str(UTCDateTime(ns=self._starttime_ns + int((self._file_length_in_samples-1) * (self._delta * 10**9))))
        _et = _et.replace(":", "_")
        _et = _et.replace("-", "_")
        return _et

    def set_starttime_next_segment(self, nr_of_datapoints):
        """Add time to the start time depending on the nr of datapoints measured.

        Args:
            nr_of_datapoints: The nr of datapoints define how much time to add to the start time.
            """
        self._starttime_ns = self._starttime_ns + int(nr_of_datapoints * (self._delta * 10 ** 9))
        # logger.info("time delta between files in ns = {0}".format(int(nr_of_datapoints * (self._delta * 10 ** 9))))
