#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a file that contains the parsing function for the listing qualities
about input files, such as duplicate sample names. It doesn't contain a
'main' function, instead importing from other files.
"""
import argparse
import logging
from .duplicates import main as duplicates_main
from .duplicates import parse_args as duplicates_parse_args

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
    subparsers = parser.add_subparsers(
        title='Subcommands',
        dest='command',
        help="File operations.")
    # add required parameters for this application
    subparsers.required = True
    # duplicates
    duplicates_parser = subparsers.add_parser('duplicates',
        help="List duplicate sample names, if any.")
    duplicates_parser.set_defaults(func=duplicates_main)
    duplicates_parse_args(duplicates_parser)

    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    if isinstance(args, list):
        return parser.parse_args(args)
