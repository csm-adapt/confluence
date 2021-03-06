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


import sys
import argparse
import functools
import logging
import numpy as np
from collections import OrderedDict
from enum import Enum, auto
from ..core.setup import setup_logging
from ..io import read, write


__author__ = "Branden Kappes"
__copyright__ = "Branden Kappes"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class MergeMethod(Enum):
    ABORT = auto()
    FIRST = auto()
    SECOND = auto()


def merge(lhs, rhs, resolution=None):
    """
    Merge two containers.

    Args:
        lhs: Left hand (first) Container.
        rhs: Right hand (second) Container.
        resolution: How to handle merge conflicts (MergeMethod).
            Default: MergeMethod.ABORT

    Returns:
        Merged data.
    """
    def ordered_unique_keys(lhs, rhs):
        """
        Returns the unique keys from lhs and rhs while maintaining their order.
        """
        # unique columns in lhs
        left = list(OrderedDict((k, None) for k in lhs.columns.to_list()))
        # unique columns in rhs
        right = list(OrderedDict((k, None) for k in rhs.columns.to_list()))
        # unique columns in (lhs + rhs), unique columns in (rhs + lhs)
        return list(OrderedDict((k, None) for k in left + right))
    # check merge
    left = lhs.combine_first(rhs).sort_index()
    right = rhs.combine_first(lhs).sort_index()
    # TODO: Dates are not handled properly.
    equal = left.fillna('').equals(right.fillna(''))
    if equal:
        return left[ordered_unique_keys(lhs, rhs)]
    else:
        _logger.debug(f"{left == right}")
        if resolution is MergeMethod.FIRST:
            result = left[ordered_unique_keys(lhs, rhs)]
        elif resolution is MergeMethod.SECOND:
            result = right[ordered_unique_keys(rhs, lhs)]
        else:
            raise ValueError("An unresolved merge conflict was identified.")
    # remove duplicate columns, if they exist.
    return result.T.loc[~result.T.index.duplicated(keep='first'), :].T.shape


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
    class MergeAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            method = {
                'abort': MergeMethod.ABORT,
                'keep_first': MergeMethod.FIRST,
                'keep_second': MergeMethod.SECOND
            }.get(values.lower(), MergeMethod.ABORT)
            setattr(namespace, self.dest, method)
    # If called as a main function, this processes command line arguments
    # as main. If this is called as part of an action
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
    parser.add_argument('-m',
        '--merge-method',
        dest='resolve',
        choices=["abort", "keep_first", "keep_second"],
        default="abort",
        action=MergeAction,
        help="Choose how to handle merge conflicts.")
    parser.add_argument('-o',
        '--output',
        default="output.xlsx",
        help="Set the name of the output file.")
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

def main(args):
    """Main entry point allowing external calls

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
    _logger.debug(f"Starting merge operation...")
    # read input files
    _logger.debug(f"Reading files: {args.filelist}")
    data = OrderedDict()
    for od in [read(fname, index_col=args.index) for fname in args.filelist]:
        for k,v in od.items():
            data[k] = data.get(k, []) + [v]
    # merge consecutive data frames
    _logger.debug(f"Joining data using {args.resolve} to "
                  "resolve merge conflicts.")
    for k, v in data.items():
        data[k] = functools.reduce(
            lambda lhs, rhs: merge(lhs, rhs, args.resolve), data[k])
    _logger.debug(f"Merged sheets: {list(data.keys())}.")
    # write result
    _logger.debug(f"Writing result to {args.output}.")
    write(args.output, data)
    _logger.info(f"Merge complete.")


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
