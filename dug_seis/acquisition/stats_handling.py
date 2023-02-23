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
        self.reorder_channels = param['Acquisition']['asdf_settings']['reorder_channels']
        self.sensor_codes = param['General']['stats']['sensor_codes']
        self.stats = {'network': '99',
                      'station': '99999',
                      'location': '',
                      'channel': '999',
                      'starttime': '',
                      'delta': 1/param['Acquisition']['hardware_settings']['sampling_frequency'],
                      'gain': '0'
                      }

    def get_stats(self):
        return self.stats

    def set_starttime(self, starttime):
        self.stats['starttime'] = starttime

    def set_sensor_code(self, card_nr, channel_nr):
        """Sets the channel number as location."""
        channel_nr_32 = channel_nr + 16 * card_nr
        re_ordered_channel_nr = self.reorder_channels[channel_nr_32]
        sensor_code = self.sensor_codes[re_ordered_channel_nr-1].split('.')
        if sensor_code[1] == 'NOT':
            # print("channel {} skipped".format(re_ordered_channel_nr))
            return False
        self.stats['network'] = sensor_code[0]
        self.stats['station'] = sensor_code[1]
        self.stats['location'] = sensor_code[2]
        self.stats['channel'] = sensor_code[3]
        # print(self.stats)
        return True
