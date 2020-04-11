import logging
import pandas as pd
from collections import OrderedDict
import os
from .container import Container
_logger = logging.getLogger(__name__)


def read(fname, **kwds):
    """
    Reads a JSON-formatted filename into a Container.
    Args:
        fname: File name or file object.
        **kwds: Keywords handled by pandas.read_excel

    Returns:
        Container object.
    """
    try:
        _logger.debug(f"Reading CSV file {fname}")
        df = pd.read_csv(fname, **kwds)
        return {'CSV': Container(df)}
    except KeyError:
        raise ValueError(f'Index column <{kwds["index_col"]}> is not in dataframe')


def write(fname, od, **kwds):
    """
    Write the Container, or OrderedDict of Containers, to a file.

    Args:
        fname: Output filename.
        df: Container or OrderedDict of Containers.
        **kwds: Arguments to pass to Container.to_excel()

    Returns:
        None
    """
    if isinstance(od, (OrderedDict, dict)):
        if len(od.keys()) > 1:
            # If there are multiple sheets in the data, create a folder named after the filename passed
            # in by the user (stripped of the extension). Each file will be labeled as the filename, followed
            # by and underscore, followed by the sheet name. If there is only one sheet, the file will be
            # written to as normal.
            folder, ext = os.path.splitext(fname)
            if not os.path.exists(folder):
                _logger.debug(f"Creating folder '{folder}'.")
                os.mkdir(folder)
            for key, container in od.items():
                fname = os.path.join(folder + '/' + folder + '_' + key, ext)
                _logger.debug(f"Writing {container.df} dataframe to {fname}.")
                container.df.to_csv(fname, **kwds)
        else:
            _logger.debug(f"Writing {list(od.values())[0].df} dataframe to {fname}.")
            list(od.values())[0].df.to_csv(fname, **kwds)
    else:
        _logger.debug(f"Writing {od.df.shape} dataframe to {fname}.")
        od.df.to_csv(fname, **kwds)
