import os
import shutil
from datetime import datetime as dt
from ..io import read
from ..subcommands.merge import main
from ..core.container import set_index, to_pif
from ..core.setup import setup_logging


import logging
_logger = logging.getLogger(__name__)
setup_logging(logging.DEBUG)


def convert(
        files=[],
        dest=None,
        resolve='abort',
        index=0,
        backup=True,
        **kwargs):
    """
    Merge records from all files into the current Dataset.

    :param files, list: Files that are to be integrated/merged.
    :param dest, str: Destination filename in the Dataset.
    :param resolve, str: How merge conflicts should be resolved.
        Recognized values: {abort, old, new}. Default: abort.
    :param index, int: Which column to use as the index (row name).
    :param backup, bool: Whether to create a backup copy of the uploaded file.
    :param kwargs: Any other arguments.
    :return: The PIF produced by this conversion.
    """
    # handle parameters
    # destination specified explicitly
    if dest is None:
        ext = os.path.splitext(files[0])[1]
        dest = '-'.join([os.path.splitext(os.path.basename(p))[0]
                         for p in files]) + ext
    # set resolution method
    resolve = {
        'abort': "abort",
        'old': "keep_first",
        'new': "keep_second"
    }.get(resolve.lower(), "abort")
    # archive destination file
    if backup:
        archive(dest)
    # generate command
    if os.path.isfile(dest):
        files = [dest] + files
    args = ["--index-column", str(index),
            "--merge-method", resolve,
            "--output", dest] + files
    # perform merge
    _logger.info(f"Executing '{' '.join([main.__name__] + args)}'")
    main(args)
    # convert table to PIF
    data = read(dest)  # returns an OrderedDict of Containers
    systems = []
    for value in data.values():
        value = set_index(value, 0)
        systems.extend(to_pif(value))
    return systems


def archive(src, dest="archive"):
    """
    Archives a file by appending YYYY-MM-DDTHHhMM to the filename.
    The file is stored in directory `dest`. Attempts to archive the
    same file more than once per minute will result in duplication.

    :param src: File to be archived.
    :param dest: Archival directory.
    :return: None
    """
    # archive destination file
    if os.path.isfile(src):
        _logger.info(f"Archiving {src} to {dest}.")
        if not os.path.isdir(dest):
            _logger.info(f"Creating directory {dest}.")
            os.mkdir(dest)
        _, fname = os.path.split(src)
        fname = f"{fname}-{dt.now().strftime('%Y-%m-%dT%Hh%M')}"
        fname = os.path.join(dest, fname)
        _logger.debug(f"Copying {src} to {fname}.")
        shutil.copyfile(src, fname)
    else:
        _logger.info(f"{src} not found, and was not archived.")
    return