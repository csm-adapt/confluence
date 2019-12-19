"""
Confluence provides a set of tools for joining, merging,
listing, and manipulating Excel-formatted metadata files.
The goal is to use a familiar tool (Excel) to structure/
organize the collection of data and metadata that is flexible
enough to adapt to a wide-range of projects.
"""

import sys
import argparse
<<<<<<< .merge_file_yTqgRh
from .merge import run as merge_main
from .merge import generate_merge_args
from .list_items import list_items as list_main
from .list_items import generate_list_args
import logging
=======
from .merge import main as merge_main
from .merge import parse_args as merge_parse_args
#from .list_items import list_items as list_main
f#rom .list_items import generate_list_args
>>>>>>> .merge_file_CGOa2x


from confluence import __version__

__author__ = "Branden Kappes"
__copyright__ = "Branden Kappes"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def parse_args(args):
    if isinstance(args, list):
        parser = argparse.ArgumentParser(description=__doc__)
    else:
        parser = args

    subparsers = parser.add_subparsers(
        title="Commands",
        required=True,
        help="Operations available from confluence CLI")

    #Merge Parser
    merge_parser = subparsers.add_parser('merge', help='merge help')
    merge_parser.set_defaults(func=merge_main)
    merge_parse_args(merge_parser)

    #List Parser
    list_parser = subparsers.add_parser('list', help='list help')
    list_parser.set_defaults(func=list_main)
    generate_list_args(list_parser)
    return parser



def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel,
                        stream=sys.stdout,
                        format=logformat,
                        datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    if isinstance(args, list):
        args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting confluence...")
    try:
        args.func(args)
    except Exception as e:
        _logger.error(f"Unhandled exception raised message: {e}")
        sys.exit(1)
    _logger.debug("Confluence complete.")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
