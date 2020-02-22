import logging
import pandas as pd
from collections import OrderedDict
import json
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
        df = pd.read_json(data)
        return {'JSON': df}

    except KeyError:
        raise ValueError(f'Index column <{kwds["index_col"]}> is not in dataframe')

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
        for key in df.keys():
            file, ext = os.path.splitext(fname)
            fname = file + '_' + key + ext if len(df.keys()) > 1 else fname
            with open(fname, 'w+') as outfile:
                _logger.info(f"Writing {key} to {fname}.")
                jsonfile = df[key].to_json()
                json.dump(jsonfile, outfile)

    else:
        _logger.debug(f"Writing {df.shape} dataframe to {fname}.")
        jsonfile = df.to_json(index=True)
        with open(fname, 'w+') as outfile:
            json.dump(jsonfile, outfile)