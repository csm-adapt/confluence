import logging
import pandas as pd
from collections import OrderedDict
import json
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
        return pd.read_json(data).set_index(kwds['index_col'])
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
        ext = fname.split('.')[1]
        for key in df.keys():
            fname = fname.split('.')[0] + '_' + key + '.' + ext
            with open(fname, 'w+') as outfile:
                jsonfile = df[key].to_json()
                json.dump(jsonfile, outfile)
    else:
        _logger.debug(f"Writing {df.shape} dataframe to {fname}.")
        jsonfile = df.to_json()
        with open(fname, 'w+') as outfile:
            json.dump(jsonfile, outfile)