#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a file that contains the functions to list duplicates. It is called with 'confluence list duplicates',
followed by a list of files. If there are duplicate sample names, it lists them as logger warnings, along with
the file they came from. If there are none, nothing is printed.
"""
import sys
import argparse
import logging
from confluence.core.setup import setup_logging
from confluence.core.validate import validate_files
from confluence.io import read

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


def postprocess_cli(args):
    """
    Changes the command line arguments in place for
    this function.

    :param args: Argument namespace
    :return: None
    """
    if args.index is None:
        _logger.warning("No merge column was specified. Using the first column.")
        args.index = 0


def check_for_duplicates(container):
    df = container.df
    indexes = list(df.index)
    duplicates = []
    for duplicate in set([x for x in indexes if indexes.count(x) > 1]):
        duplicates.append(duplicate)
    if duplicates:
        raise ValueError(duplicates)


def main(args):
    """Main entry point allowing external calls to validate files
    Function: Takes an argparse command and validates each file.
    As of 2/21/2020, it does not change any files that are given.
    If the file has an internal conflict, it raises a ValueError
    that tells which file, sheet, and column is responsible.

    Args:
      args ([str]): command line parameter list
    """
    if isinstance(args, list):
        _logger.debug(f"Parsing command line arguments: {args}")
        args = parse_args(args)
    # handle non-standard CLI defaults
    postprocess_cli(args)
    # start logging
    setup_logging(args.loglevel)
    _logger.debug(f"Starting validate operation...")
    # read input files
    _logger.debug(f"Testing files for duplicate indexes: {args.filelist}")
    validate_files(args.filelist)
    for od, fname in [(read(fname, index_col=args.index), fname) for fname in args.filelist]:
        for k, v in od.items():
            try:
                _logger.info(f'Finding duplicates in for file {fname}, sheet {k}')
                check_for_duplicates(v)
            except ValueError as e:
                _logger.warning(f" Duplicated row(s) '{e}' found in file '{fname}' "
                               f"in sheet '{k}'.")
    _logger.info('Finished searching files for duplicates')


def run():
    """Entry point for console_scripts
    """
    try:
        main(sys.argv[1:])
    except Exception as e:
        _logger.error(f"Confluence failed: ({str(e)}).")
        sys.exit(1)


if __name__ == "__main__":
    run()