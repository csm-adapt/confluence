import os
from enum import Enum, auto
from .excel import read as read_excel
from .excel import write as write_excel
from .JSON import read as read_json
from .JSON import write as write_json
from .CSV import read as read_csv
from .CSV import write as write_csv
from .text import read as read_text
from .text import write as write_text

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
    basename, ext = os.path.splitext(filename)
    return {
        '.xlsx': FileFormat.EXCEL,
        '.json': FileFormat.JSON,
        '.csv': FileFormat.CSV,
        '.txt': FileFormat.TEXT
    }[ext.lower()]


def read(filename, **kwds):
    print('io',kwds)
    print(kwds['index_col'])
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
