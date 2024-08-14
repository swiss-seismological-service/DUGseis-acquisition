# Software for data acquisition and real-time processing of induced
# seismicity during rock-laboratory experiments.
#
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#
"""Command line."""

import click
import yaml
import logging
import os
import datetime
import numpy as np
from logging.handlers import RotatingFileHandler
from dug_seis.acquisition.acquisition import acquisition_ as acquisition_function
# from dug_seis.processing.processing import processing as processing_function
# from dug_seis.merge import merge as merge_function
# from dug_seis.visualization.dashboard import dashboard as dashboard_function

# shut up libraries
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

CONFIG_VERSION = 3

@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('--cfg', metavar='<config file>',
              help='Source config file. If not specified,'
                   'the script tries ./dug-seis.yaml and config/dug-seis.yaml',
              default=None)
@click.option('--mode', metavar='<mode>', default='live',
              help='Mode can be either "live" (default) or'
                   '"post", for post processing mode)')
@click.option('--log', metavar='<path>', help='Specify a log file')
@click.version_option()
@click.pass_context
def cli(ctx, cfg, verbose, mode, log):
    """
    Run data acquisition and real-time processing of induced
    seismicity during rock-laboratory experiments

    """
    # kill leftover celery workers
    #os.system("pkill -9 -f 'celery worker'")
    os.system("pkill -9 -f 'redis-server'")
    # Setup logging. By default we log to stdout with ERROR level and to a log
    # file (if specified) with INFO level. Setting verbose logs to both
    # handlers with DEBUG level.
    logger = logging.getLogger('dug-seis')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-7s %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if not log: log = 'dugseis_acquisition.log'
    fh = RotatingFileHandler(log)
    fh.setLevel(logging.DEBUG if verbose else logging.INFO)
    fh.formatter = formatter
    logger.addHandler(fh)
    logger.info('DUG-Seis started')
    # Load config file and set the context for the subcommand
    search = [cfg or '', 'dug-seis.yaml', 'config/dug-seis.yaml']
    cfg_path = next((p for p in search if os.path.exists(p)), None)
    if not cfg_path:
        logger.error('no parameter file found')
        exit(-1)
    with open(cfg_path) as f:
        try:
            param = yaml.load(f, Loader=yaml.FullLoader)
        except IOError:
            logger.error(f'could not read parameter file at {cfg_path}')
            exit(-1)
        if param['Version'] != CONFIG_VERSION:
            logger.error(f'Configuration Version is {param["Version"]} but it must be {CONFIG_VERSION}')
            exit(-1)
    param['General']['mode'] = mode
    ctx.obj = {
        'param': param
    }


@cli.command()
@click.pass_context
def acquisition(ctx):
    """
    Run data acquisition

    The output goes to ASDF files in the folder defined in the options file

    """
    param = ctx.obj['param']
    acquisition_function(param)

@cli.command()
@click.pass_context
def merge(ctx):
    """
    Merge short ASDF files

    The output goes to ASDF files in the folder defined in the options file

    """
    param = ctx.obj['param']
    merge_function(param)

@cli.command()
@click.pass_context
def processing(ctx):
    """
    Run event trigger on ASDF files

    """
    param = ctx.obj['param']
    processing_function(param)


@cli.command()
@click.pass_context
def show_parameters(ctx):
    """
    Show parameters

    """
    param = ctx.obj['param']
    print(yaml.dump(param))

@cli.command()
@click.pass_context
def dashboard(ctx):
    """
    Run dashboard to show recent events

    """
    param = ctx.obj['param']
    dashboard_function(param)
