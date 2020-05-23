#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
from ..io import write_yaml

__author__ = "amikulichmines <amikulich@mymail.mines.edu>, bkappes <bkappes@mines.edu>"
__copyright__ = "KMMD, LLC."
__license__ = "mit"

_logger = logging.getLogger(__name__)




def parse_args(args):
    """Parse command line parameters

    Args:
    :param args: Argument(s) to process. If args is a list of strings, then
        this is the command line parser for the main function. Otherwise--
        that is, args is a subparser instance--this adds subcommand
        arguments to this function call.
    :type args: list of str or subparser object (see above).

    Returns:
    :return: `argparse.Namespace` if `args` is a list of strings, otherwise
        the subparser object passed as `args` is modified/augmented in place
    :rtype: argparse.Namespace or None (see above).
    """
    if isinstance(args, list):
        parser = argparse.ArgumentParser(description="Merge two or more data files.")
    else:
        parser = args
    # add required parameters for this application
    parser.add_argument("filelist",
        nargs='+',
        type=str,
        help="List of files to be merged.")
    # add options for this application
    parser.add_argument('--index-column',
        dest="index",
        type=int,
        default=None,
        help="Which column should be treated as the Index.")
    parser.add_argument('-i',
        '--input',
        dest='filelist',
        action='append',
        type=str,
        help="List of files to be merged.")
    parser.add_argument('-m',
        '--merge-method',
        dest='resolve',
        choices=["abort", "keep_first", "keep_second"],
        default="abort",
        help="Choose how to handle merge conflicts.")
    parser.add_argument('-o',
        '--output',
        default="output.xlsx",
        help="Set the name of the output file.")
    parser.add_argument('--dry-run',
        dest='dry_run',
        action='store_true',
        help='Opt for a dry run instead of merging.')
    parser.add_argument('--validate',
        dest="validate",
        help="Validate output file",
        action='store_true')
    parser.add_argument('->',
        dest='yaml_file',
        default='config.yaml')
    if isinstance(args, list):
        return parser.parse_args(args)


def create_cli(args):
    try:
        cli = []
        load = args['load']
        dump = args['dump']
        for k,v in load.items():
            cli.append(k)
        for k,v in dump.items():
            cli.extend(['-o', k])
        cli.extend(['-m', args['merge']['merge method']])
        cli.extend(['--index-column', int(args['merge']['index column'])])
        return cli
    except KeyError:
        raise ValueError('YAML file incorrectly formatted.')


def get_format(args):
    """
    Function: Gets the format of the file (eg. 'Quality made', etc.)
    :param args: argparse object
    :return: Format of the file
    """
    # I will write this at a later date.
    pass


def get_resolve(args):
    """
    Converts the merge method from the argparse object into one that is written
    in the command line
    :param args: Argparse object
    :return: Converted merge method
    """
    return{
        'MergeMethod.FIRST': 'keep_first',
        'MergeMethod.SECOND': 'keep_second'
    }.get(args.resolve, 'abort')


def get_index(args):
    if args.index is None:
        args.index = 0
    return args.index


def create_dict(args):
    """
    Function: Creates dictionary to be output to the YAML file
    :param args: Argparse object
    :return: Dictionary with input and output data
    """
    try:
        load = {file: {'format': get_format(args)} for file in args.filelist}
        merge = {'merge method': get_resolve(args),
                 'index column': get_index(args)}
        dump= {args.output: {'format': get_format(args)}}
        data = {'load': load, 'dump': dump, 'merge': merge}
        return data
    except IndexError:
        raise IndexError("Arguments must contain input and output files")


def main(args):
    """
    Args:
      args ([str]): command line parameter list
    """
    _logger.debug(f"Running list_main with arguments: {args}")
    if isinstance(args, list):
        _logger.debug(f"Parsing command line arguments: {args}")
        args = parse_args(args)
    dict_file = create_dict(args)
    write_yaml(args.yaml_file, dict_file)
    _logger.debug(f"Writing file to {args.yaml_file}")


def run():
    """Entry point for console_scripts
    """
    try:
        main(sys.argv[1:])
    except Exception as e:
        _logger.error(f"Confluence failed: ({str(e)}).")
        sys.exit(1)
