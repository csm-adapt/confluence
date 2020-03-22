import os
import logging
from enum import Enum, auto
from .excel import read as read_excel
from .excel import write as write_excel
from .json import read as read_json
from .json import write as write_json
from .csv import read as read_csv
from .csv import write as write_csv
from .text import read as read_text
from .text import write as write_text
_logger = logging.getLogger(__name__)


class FileFormat(Enum):
    EXCEL = auto()
    JSON = auto()
    CSV = auto()
    TEXT = auto()


def guess_format(filename):
    """
    Guess the format of the filename.

    Args:
        filename: Filename whose format is to be guessed.

    Returns:
        File format defined in FileFormat.
    """
    # TODO: Return tuple of valid project-specific readers
    basename, ext = os.path.splitext(filename)
    fmt = {
        '.xlsx': FileFormat.EXCEL,
        '.json': FileFormat.JSON,
        '.csv': FileFormat.CSV,
        '.txt': FileFormat.TEXT
    }[ext.lower()]
    _logger.debug(f"File format of {basename} was identified as {str(fmt)}.")
    return fmt


def read(filename, **kwds):
    # TODO: Add for-loop with try/except statements to test each read function
    # TODO: Record project from successful read for subsequent write
    # TODO: Create IO class in the init file. Set read, write formats to None.
    #  If write is None and read is not, set 'write' to the same format as 'read'
    _logger.debug(f"Reading {filename}, with keywords {kwds}")
    return {
        FileFormat.EXCEL: read_excel,
        FileFormat.JSON: read_json,
        FileFormat.CSV: read_csv,
        FileFormat.TEXT: read_text
    }[guess_format(filename)](filename, **kwds)


def write(filename, df, **kwds):
    {
        FileFormat.EXCEL: write_excel,
        FileFormat.JSON: write_json,
        FileFormat.CSV: write_csv,
        FileFormat.TEXT: write_text
    }[guess_format(filename)](filename, df, **kwds)

