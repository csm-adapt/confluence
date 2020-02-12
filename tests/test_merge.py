# import argparse
# import functools
# import logging
# import numpy as np
# from collections import OrderedDict
# from enum import Enum, auto
#
#
# __author__ = "Branden Kappes"
# __copyright__ = "Branden Kappes"
# __license__ = "mit"
#
# _logger = logging.getLogger(__name__)
#
#
# def parse_args(args):
#     """Parse command line parameters
#
#     Args:
#     :param args: Argument(s) to process. If args is a list of strings, then
#         this is the command line parser for the main function. Otherwise--
#         that is, args is a subparser instance--this adds subcommand
#         arguments to this function call.
#     :type args: list of str or subparser object (see above).
#
#     Returns:
#     :return: `argparse.Namespace` if `args` is a list of strings, otherwise
#         the subparser object passed as `args` is modified/augmented in place
#     :rtype: argparse.Namespace or None (see above).
#     """
#     if isinstance(args, list):
#         parser = argparse.ArgumentParser(description='Insert description')
#     else:
#         parser = args
#     # add required parameters for this application
#     parser.add_argument("all",
#                         nargs=1,
#                         type=str,
#                         help="files to be tested")
#     if isinstance(args, list):
#         return parser.parse_args(args)
#
# def main():
#     print('testing')
#

import pytest
from confluence.subcommands.merge import main as merge_main

def test_extra_columns():
    # equivalent to "confluence merge -h" or
    # "confluence-merge -h"
    cli = ["test_files/extra_columns1.xlsx",
           "test_files/extra_columns2.xlsx"]
    merge_main(cli)