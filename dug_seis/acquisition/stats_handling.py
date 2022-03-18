# DUG-Seis
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#
"""creation of the stats structure."""
import logging

logger = logging.getLogger('dug-seis')


class StatsHandling:

    def __init__(self, param):
        self.station_naming = param['Acquisition']['asdf_settings']['station_naming']
        self.stats = {'network': param['General']['stats']['network'],
                      'station': param['General']['stats']['daq_unit'],
                      'location': '00',
                      'channel': '001',
                      'starttime': '',
                      'delta': 1/param['Acquisition']['hardware_settings']['sampling_frequency'],
                      'gain': '0'
                      }

    def get_stats(self):
        return self.stats

    def set_starttime(self, starttime):
        self.stats['starttime'] = starttime

    def set_location(self, card_nr, channel_nr):
        """Sets the channel number as location."""
        channel_nr_32 = channel_nr + 16 * card_nr
        self.stats['location'] = str(self.station_naming[channel_nr_32]).zfill(2)