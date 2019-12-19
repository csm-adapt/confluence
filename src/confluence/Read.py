import os
from .io.text import TextReader
from .io.CSV import CSVReader
from .io.excel import ExcelReader
from. io.JSON import JSONReader


def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    return os.path.splitext(filename)[1].strip('.')


def read(filename, ftype=None, sheetname=None):
    """
    Function: This is the function we call when we want to read an unknown file. It first takes in the file name
    and file type. If the file type is 'None', it guesses the type based on the file extention. Each file type has an
    accompanying function that contains the reader for that file type (read_excel(), etc.).

    :param filename: name of file
    :param ftype: the type of the file ('xlsx', 'txt', etc)
    :param sheetname: name of the sheet being read. This only applies to .xlsx files
    :return: appropriate file reader
    """
    if ftype is None:
        ftype = guess_file_type(filename)
    try:
        return {
            'xlsx': read_excel(filename, sheetname),
            'txt': read_text(filename),
            'csv': read_csv(filename),
            'json': read_json(filename)
        }[ftype]
    except KeyError:
        raise IOError(f"{ftype} is not a recognized file type.")


def read_excel(filename, sheetname):
    """
    function: reads excel files. This will return an instance of the ExcelReader that you can add '.as_dataframe()' to
    get the file as a dataframe
    :param filename: file name to be read
    :param sheet: name of the sheet
    :return: reader object for a specific sheet name
    """
    reader = ExcelReader(filename, sheetname=sheetname)
    return reader


def read_text(filename):
    """
    Function: reads txt files
    :param filename: Name of the file
    :return: reader object
    """
    reader = TextReader(filename)
    return reader


def read_json(filename):
    """
    Function: Reads JSON files
    :param filename: name of the file
    :return: reader object
    """
    reader = JSONReader(filename)
    return reader


def read_csv(filename):
    """
    Function: reads csv files
    :param filename: file name
    :return: csv reader object
    """
    reader = CSVReader(filename)
    return reader
