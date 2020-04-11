import logging
import pandas as pd
from collections import OrderedDict
import json
from .container import Container
import os
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
        with open(fname) as json_file:
            data = json.load(json_file)
        _logger.debug(f"Reading JSON file {fname}")
        dfod = {}
        try:
            for k, v in data.items():
                _logger.debug(f"Adding sheet {k} to OrderedDictionary of DataFrames (dfod).")
                dfod[k] = Container(v)
            return dfod
        except:
            return Container(data)

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
        with open(fname, 'w+') as outfile:
            for key, container in od.items():
                _logger.info(f"Writing {container.df} to {key} in {fname}.")
            json.dump({k: v.df.to_dict() for k, v in od.items()}, outfile)

    else:
        _logger.debug(f"Writing {od.df.shape} dataframe to {fname}.")
        jsonfile = od.df.to_json(index=True)
        with open(fname, 'w+') as outfile:
            json.dump(jsonfile, outfile)
