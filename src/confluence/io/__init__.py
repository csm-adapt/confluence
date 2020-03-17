import os
from enum import Enum, auto
from .qualitymade.excel import read as read_excel
from .qualitymade.build import read as read_build_log
from .qualitymade.excel import write as write_excel


class FileFormat(Enum):
    EXCEL = auto()
    BUILD_LOG = auto()


def guess_format(filename):
    """
    Guess the format of the filename.

    Args:
        filename: Filename whose format is to be guessed.

    Returns:
        File format defined in FileFormat.
    """
    basename, ext = os.path.splitext(filename)
    return {
        '.doc': FileFormat.BUILD_LOG,
        '.xlsx': FileFormat.EXCEL
    }[ext.lower()]


def read(filename, **kwds):
    return {
        FileFormat.BUILD_LOG: read_build_log,
        FileFormat.EXCEL: read_excel
    }[guess_format(filename)](filename, **kwds)


def write(filename, df, **kwds):
    {
        FileFormat.EXCEL: write_excel
    }[guess_format(filename)](filename, df, **kwds)
