# Copyright (c) 2018 by SCCER-SoE and SED at ETHZ
#
# Version 0.0, 23.10.2018, Joseph Doetsch (doetschj)
#              23.10.2018, Thomas Haag (thaag)

"""
Acquisition module of DUG-Seis.
"""

import logging
import dug_seis.acquisition.card_manager as card_manager
import os.path
import shutil
import socket

from obspy.core import UTCDateTime

logger = logging.getLogger('dug-seis')


def acquisition_(param):
    """
    Acquisition entry point.
    Defines Buffer sizes for: DMA, Stream, and RAM.
    Checks if this script runs on a computer where the Spectrum cards are installed or if they need to be simulated.
    Defines how complex simulated data is.
    Sets the daq_unit name based on the hostname.
    Start writing to the log file and adds the configuration to it.
    Runs the card manger.

    Args:
        param: Parameters which where loaded from dug-seis.yaml when calling "dug-seis acquisition"
    """
    logger.info('Acquisition script started')
    logger.info('==========================')
    # print("logger name: " + logger.name);
    # print("logger level: " + logging.getLevelName(logger.level));

    param['Acquisition']['simulation_mode'] = False     # should be False, or no real data is recorded when True!
    param['Acquisition']['bytes_per_stream_packet'] = 1*1024*1024
    # 32 * 1024 * 1024   # in bytes (amount of data processed per python call)
    param['Acquisition']['bytes_per_transfer'] = 32*1024*1024
    # 128 * 1024 * 1024 # in bytes (computer memory reserved for data)
    param['Acquisition']['hardware_settings']['ram_buffer_size'] = 128*1024*1024
    # ms, when during this time not transfer_size data is available -> timeout
    param['Acquisition']['hardware_settings']['timeout'] = 8000
    # amount of generated data for simulation: 0...4
    # 0 = fastest, only zeroes used, will lead to high compression rate -> small files, low load
    # 4 = slow, all channels with sine, sawtooth and random data filled -> "worst cast data"
    param['Acquisition']['simulation_amount'] = 0
    param['Acquisition']['asdf_settings']['reorder_channels'] = [1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15, 8, 16,
                                               17, 25, 18, 26, 19, 27, 20, 28, 21, 29, 22, 30, 23, 31, 24, 32]

    _check_if_hardware_needs_to_be_simulated(param)

    hostname = socket.gethostname()
    if hostname == 'continuous-01-bedretto':
        param['General']['stats']['daq_unit'] = '01'.zfill(2)
    elif hostname == 'continuous-02-bedretto':
        param['General']['stats']['daq_unit'] = '02'.zfill(2)
    elif hostname == 'continuous-03-bedretto':
        param['General']['stats']['daq_unit'] = '03'.zfill(2)
    elif hostname == 'continuous-04-bedretto':
        param['General']['stats']['daq_unit'] = '04'.zfill(2)
    elif hostname == 'continuous-05-bedretto':
        param['General']['stats']['daq_unit'] = '05'.zfill(2)
    else:
        if param['Acquisition']['simulation_mode'] == True:
            param['General']['stats']['daq_unit'] = '99'.zfill(2)
            logger.info('simulation on host: {}, setting daq_unit to: {}'.format(hostname, param['General']['stats']['daq_unit']))
        else:
            # Mt Terri will probably run here
            param['General']['stats']['daq_unit'] = '98'.zfill(2)
            logger.error('host name not known')

    param['Acquisition']['hardware_settings']['input_range_sorted'] = _sorted_input_ranges(param)

    logger.info('used configuration values (from .yaml file) :')
    _write_used_param_to_log_recursive(param)
    logger.info('additional information, os.name: {0}, os.getcwd(): {1}'.format(os.name, os.getcwd()))
    _copy_config_file(param)
    card_manager.run(param)


def _check_if_hardware_needs_to_be_simulated(param):
    if param['Acquisition']['simulation_mode']:
        logger.warning('param["Acquisition"]["simulation_mode"] = True, this is for testing purposes only.'
                        ' This setting should never be pushed to Git, the real system does only record simulated'
                        ' data this way. A computer without the acquisition hardware will detect the missing hardware'
                        ' and ask to change to the simulation mode automatically.')
    else:
        if _check_if_hardware_driver_can_be_loaded():
            logger.info('Hardware driver found, running on real hardware')
        else:
            user_input = input("\nCould not load hardware driver, to simulate hardware press: enter or (y)es?")
            if user_input == 'y' or user_input == 'Y' or user_input == 'yes' or user_input == '':
                param['Acquisition']['simulation_mode'] = True
                logger.info('Could not load hardware driver, user requested simulation of hardware.')
            else:
                logger.info('Could not load hardware driver, user abort.')
                return


def _check_if_hardware_driver_can_be_loaded():
    if os.name == 'nt':
        if os.path.isfile("c:\\windows\\system32\\spcm_win64.dll") or os.path.isfile(
                "c:\\windows\\system32\\spcm_win32.dll"):
            return True
    if os.name == 'posix':
        logger.info('os.name == posix')
        if os.path.isfile('/proc/spcm_cards'):
            if os.access('/proc/spcm_cards', os.R_OK):
                logger.info('/proc/spcm_cards is accessible')
                file = open('/proc/spcm_cards', 'r')
                found_cards = 0
                for line in file:
                    # print(line.rstrip("\n"))
                    if line.__contains__('/dev/spcm0'):
                        logger.info('/dev/spcm0 found.')
                        found_cards = found_cards + 1
                    if line.__contains__('/dev/spcm1'):
                        logger.info('/dev/spcm1 found.')
                        found_cards = found_cards + 1
                file.close()
                if found_cards > 0:
                    return True
    return False


def _copy_config_file(param):
    _folder = param['General']['acquisition_folder']
    if _folder[len(_folder) - 1] != "/":
        _folder += "/"
    _folder += 'configs/'
    _time_str = str(UTCDateTime()).replace(":", "_").replace("-", "_")
    _time_str = _time_str.split('.')[0]
    _time_str += '_'
    _folder_file = _folder + _time_str + 'dug-seis.yaml'

    if not os.path.isdir(_folder):
        os.makedirs(_folder)
        logger.info("creating folder: {}".format(_folder))
    if os.path.isfile('./dug-seis.yaml'):
        logger.info("copying ./dug-seis.yaml to {}".format(_folder_file))
        shutil.copyfile('./dug-seis.yaml', _folder_file)
    elif os.path.isfile('./config/dug-seis.yaml'):
        logger.info("copying ./config/dug-seis.yaml to {}".format(_folder_file))
        shutil.copyfile('./config/dug-seis.yaml', _folder_file)
    else:
        logger.error("could not find ./dug-seis.yaml or ./config/dug-seis.yaml")


def _write_used_param_to_log_recursive(param_dict):
    for key, value in param_dict.items():
        if type(value) == dict:
            # print('next call, key:{}, value:{}'.format(key, value))
            _write_used_param_to_log_recursive(value)
        else:
            # print('{}: {}'.format(key, value))
            logger.info('{}: {}'.format(key, value))


def _sorted_input_ranges(param):
    input_range = param['Acquisition']['hardware_settings']['input_range']
    reorder_channels = param['Acquisition']['asdf_settings']['reorder_channels']
    multiplex_order = [x - 1 for x in reorder_channels]
    input_range_sorted = input_range.copy()
    input_range_sorted[:] = [input_range_sorted[i] for i in multiplex_order]
    # ch_nr = 0
    # for x in reorder_channels:
    #     input_range_sorted[int(x)-1] = (input_range[ch_nr])
    #     # logger.info('x: {}'.format( int(x) ))
    #     ch_nr = ch_nr+1
    input_range_sorted = input_range
    return input_range_sorted
