import logging
import pandas as pd
from collections import OrderedDict

_logger = logging.getLogger(__name__)


def read(fname, **kwds):
    """
    Reads an Excel-formatted filename into a Container.
    Args:
        fname: File name or file object.
        **kwds: Keywords handled by pandas.read_excel

    Returns:
        Container object.
    """
    options = {
        'sheet_name': None
    }
    options.update(kwds)
    _logger.info(f"Reading Excel-formatted file {fname} "
                 f"with options: {options}")
    return pd.read_excel(fname, **options)


def write(fname, df, **kwds):
    """
    Write the Container, or OrderedDict of Containers, to a file.

    Args:
        fname: Output filename.
        df: Container or OrderedDict of Containers.
        **kwds: Arguments to pass to Container.to_excel()

    Returns:
        None
    """
    if isinstance(df, (OrderedDict, dict)):
        _logger.debug(f"Writing dataframes to {fname}.")
        with pd.ExcelWriter(fname) as writer:
            for key in df.keys():
                _logger.debug(f"Writing sheet {key}.")
                df[key].to_excel(writer, sheet_name=key, **kwds)
    else:
        _logger.debug(f"Writing {df.shape} dataframe to {fname}.")
        df.to_excel(fname, **kwds)
