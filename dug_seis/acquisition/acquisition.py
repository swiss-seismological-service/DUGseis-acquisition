"""
Acquisition module of DUG-Seis


# Copyright (c) 2018 by SCCER-SoE and SED at ETHZ

Version 0.0, 23.10.2018, Joseph Doetsch (doetschj)
             23.10.2018, Thomas Haag (thaag)

"""

import logging
import dug_seis.acquisition.card_manager as card_manager
import os.path

logger = logging.getLogger('dug-seis')


def acquisition_(param):
    logger.info('Acquisition script started')
    logger.info('==========================')
    # print("logger name: " + logger.name);
    # print("logger level: " + logging.getLevelName(logger.level));

    param['Acquisition']['simulation_mode'] = False     # should be False, or no real data is recorded when True!
    # 32 * 1024 * 1024   # in bytes (amount of data processed per python call)
    param['Acquisition']['bytes_per_transfer'] = 32*1024*1024
    # 128 * 1024 * 1024 # in bytes (computer memory reserved for data)
    param['Acquisition']['hardware_settings']['ram_buffer_size'] = 128*1024*1024
    # ms, when during this time not transfer_size data is available -> timeout
    param['Acquisition']['hardware_settings']['timeout'] = 8000
    # amount of generated data for simulation: 0...4
    # 0 = fastest, only zeroes used, will lead to high compression rate -> small files, low load
    # 4 = slow, all channels with sine, sawtooth and random data filled -> "worst cast data"
    param['Acquisition']['simulation_amount'] = 1

    _check_if_hardware_needs_to_be_simulated(param)
    logger.info('used configuration values (from .yaml file) :')
    _write_used_param_to_log_recursive(param)
    logger.info('additional information, os.name: {0}, os.getcwd(): {1}'.format(os.name, os.getcwd()))
    card_manager.run(param)


def _check_if_hardware_needs_to_be_simulated(param):
    if param['Acquisition']['simulation_mode']:
        logger.warning('param["Acquisition"]["simulation_mode"] = True, this is for testing purposes only.'
                        ' This setting should never be pushed to Git, the real system does only record simulated'
                        ' data this way. A computer without the acquisition hardware will detect the missing hardware'
                        ' and ask to change to the simulation mode automatically.')
        input('...')
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


def _write_used_param_to_log_recursive(param_dict):
    for key, value in param_dict.items():
        if type(value) == dict:
            # print('next call, key:{}, value:{}'.format(key, value))
            _write_used_param_to_log_recursive(value)
        else:
            # print('{}: {}'.format(key, value))
            logger.info('{}: {}'.format(key, value))
