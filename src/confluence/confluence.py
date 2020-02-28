#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following line in the
entry_points section in setup.py:

    [console_scripts]
    fibonacci = climath.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import argparse
import sys
import logging

from .core.setup import setup_logging
from .subcommands.merge import parse_args as merge_parse_args
from .subcommands.merge import main as merge_main
from confluence.subcommands.validate import parse_args as validate_parse_args
from confluence.subcommands.validate import main as validate_main

from confluence import __version__

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
    # This is the key. If args is an list (ostensibly of strings), then
    # this is a "top level" argument parser. If, instead, args is not
    # and is ostensibly a ArgumentParser instance, then we are adding
    # subcommand options to an existing parser.
    if isinstance(args, list):
        parser = argparse.ArgumentParser(
            description="Combines data from multiple files.")
    else:
        parser = args
    # add required parameters for this application
    subparsers = parser.add_subparsers(
        title='Subcommands',
        dest='command',
        help="File operations.")
    subparsers.required = True
    # merge
    merge_parser = subparsers.add_parser('merge',
        help="Merge the contents of two or more files.")
    merge_parser.set_defaults(func=merge_main)
    merge_parse_args(merge_parser)
    # validate
    _logger.debug("Validating")
    validate_parser = subparsers.add_parser('validate',
        help="Check file(s) for internal merge conflicts")
    validate_parser.set_defaults(func=validate_main)
    validate_parse_args(validate_parser)
    # add options for this application
    parser.add_argument(
        '--version',
        action='version',
        version='confluence {ver}'.format(ver=__version__))
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="Set loglevel to INFO.",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="Set loglevel to DEBUG.",
        action='store_const',
        const=logging.DEBUG)
    # Only return the parsed args (argparse.Namespace) if this is a top-level
    # argument parser. (See comment above.)
    if isinstance(args, list):
        return parser.parse_args(args)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    if isinstance(args, list):
        args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting confluence...")
    args.func(args)
    _logger.info("Confluence complete.")


def run():
    """Entry point for console_scripts
    """
    try:
        main(sys.argv[1:])
    except Exception as e:
        _logger.error(f"Confluence failed: ({str(e)}).")
        _logger.error("Try setting --index-column to ensure the "
                      "index is set properly.")
        sys.exit(1)


if __name__ == "__main__":
    run()
