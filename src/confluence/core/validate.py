import pandas as pd
import sys
import argparse
import logging
from ..core.setup import setup_logging
from ..io import read

__author__ = "amikulichmines <amikulich@mymail.mines.edu>, bkappes <bkappes@mines.edu>"
__copyright__ = "KMMD, LLC."
__license__ = "mit"

_logger = logging.getLogger(__name__)


class QMDataFrameValidator(object):
    """
    Function: Sets up a series of functions that take in a
    dataframe, check to see if it has any internal conflicts,
    and throws an error if one is found.
    """
    def __init__(self):
        self._callbacks = []

    def __call__(self, df, filename, sheet='Sheet1'):
        """
        Function: Cycles through each callback, feeding the
        dataframe to the next function to check for errors.
        :param df: dataframe to be tested
        :param filename: Filename corresponding to the dataframe
        :param sheet: Sheet corresponding to the dataframe
        :return: dataframe with no errors
        """
        for callback in self._callbacks:
            df = callback(df, filename, sheet)
        return df

    def add_callback(self, func):
        # if not hasattr('__call__', func):
        # raise ValueError("Callback functions must have a ‘__call__’ attribute.")
        self._callbacks.append(func)


def validate_dataframe(df, filename, sheetname='Sheet1'):
    """
   Function: This sets up a validator. What this does is checks to make sure each file won't conflict against itself.

   The way a validator works is by gathering a few functions that test the dataframe for a certain condition. It will
   either fix the problem if possible, or throw an error. The two functions we have here will check to make sure there
   are no repeated sample names, and that there are no blank sample names.

   The check_for_sample_name_completeness is
   first. It will take in a dataframe as a parameter and go through the first column. If there are any empty spaces,
   it presents an error to the user. There is no way to fix this problem unless the user goes an manually adds it to
   the file. If no blank spaces are found, it will return the dataframe it started with and this will be passed to the
   next function.

   Next is the check_for_sample_name_uniqueness. This makes sure there aren't any repeated names in the file. If it
   does find a repeated value, it tries to fix it by first checking each cell for conflicting values. If none are
   found, it smushes the offending rows together into one. Then, it returns the corrected dataframe.

   With these, all we have to do is df = validate(df) and it'll make sure the incoming dataframe is good.

   :return: an instance of the validator that contains functions to make sure the dataframe won't throw any merge
   conflicts.
   """
    validate = QMDataFrameValidator()
    validate.add_callback(check_for_sample_name_completeness)
    validate.add_callback(check_for_sample_name_uniqueness)
    return validate(df, filename, sheetname)


def check_for_sample_name_completeness(df, filename, sheetname='Sheet1'):
    """
   Function: Checks the first column for empty cells. If there is an empty cell, throw an error. Otherwise, return
   the original dataframe
   :param df: dataframe to check
   :param filename: name of the file
   :param sheetname: name of the sheet
   :param column: name of the column that you are checking
   :return: dataframe with all entries in the 'column' filled. If there is an empty one, an error is thrown.
   """
    if any(pd.isna(df.index)):
        raise ValueError(f"Empty index cell in file '{filename}' "
                         f"in sheet '{sheetname}' "
                         f"in column '{df.index.name}'")
    return df


def check_for_sample_name_uniqueness(df, filename, sheetname='Sheet1'):
    """
   Functionality: Makes sure there are no repeated sample names, similar to the 'check_for_merge_conflict' function
   :param df: dataframe to check
   :param filename: name of the file
   :param sheetname: name of the sheet
   :param column: column that is being checked
   :return: dataframe
   """
    temp = df[df.index.duplicated(keep=False)]
    for key in temp:
        instances = temp[key].nunique()
        if instances > 1:
            raise ValueError(f"Duplicate entry in file '{filename}' "
                             f"in sheet '{sheetname}' "
                             f"in column '{df.index.name}'")
    return df


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


def main(args):
    """Main entry point allowing external calls to validate files
    Function: Takes an argparse command and validates each file.
    As of 2/21/2020, it does not change any files that are given
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
    _logger.debug(f"Reading files: {args.filelist}")
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

