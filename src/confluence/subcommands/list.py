import pandas as pd
import sys
import argparse
import logging
from confluence.core.setup import setup_logging
from confluence.io import read
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


def duplicates(args):
    """

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
    _logger.debug(f"Validating files: {args.filelist}")
    list_files(args.filelist)
    for od, fname in [(read(fname, index_col=args.index), fname) for fname in args.filelist]:
        for k, v in od.items():
            validate_dataframe(v, fname, k)


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