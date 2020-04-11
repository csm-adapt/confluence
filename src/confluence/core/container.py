import numpy as np
import pandas as pd
import re
from functools import reduce
from pypif import pif
from urllib.parse import quote

import logging
__logger__ = logging.getLogger(__name__)

Container = pd.DataFrame


def set_index(container, key):
    """
    Set the index of a container to a key, either a name or an
    integer index. If the columns of a container include an
    integer name, the position takes precedence over the
    name. That is, if a table contains columns named [1, 2, 0, 3],
    then `set_index(container, 0)` will result in a table
    with columns [2, 0, 3].

    If the Index already has an index, then the index is first reset.

    :param container, Container: Container whose index is to be
        assigned.
    :param key, str or int: Key, either by name, regex, or by position.
    :return: Copy of container with the Index set according to key.
    """
    df = container.df
    if df.index.name is not None:
        df = df.reset_index()
    try:
        key = df.columns[key]
    except KeyError:
        pass
    if key not in df.columns:
        raise KeyError(f"{key} was not found in the container/table.")
    container.df = df.set_index(key)
    return container


# ####################
# pif
# ####################
def split_name_and_units(name):
    name = name.strip()
    pattern = re.compile(r'(.*)\((.+?)\)$')
    try:
        name, units = re.match(pattern, name).groups()
        name = name.strip()
        units = name.strip()
    except AttributeError:
        units = None
    return (name, units)


def create_property(series):
    names, units = np.transpose([split_name_and_units(name)
                                 for name in series.index])
    return [pif.Property(name,
                         units=unit,
                         scalars=pif.Scalar(value=value))
            for name, unit, value in zip(names, units, series.values)]


def create_process_step(series):
    names, units = np.transpose([split_name_and_units(name)
                                 for name in series.index])
    return [pif.ProcessStep(name,
                details=pif.Value(name,
                    units=unit,
                    scalars=pif.Scalar(value=value)))
            for name, unit, value in zip(names, units, series.values)]


def create_system(series):
    names, units = np.transpose([split_name_and_units(name)
                                 for name in series.index])
    return [pif.System(name, uid=url_friendly(lambda x: x)(name))
            for name, unit, value in zip(names, units, series.values)]


def get_index(series):
    return series.name


def get_series(series):
    return series


def url_friendly(func):
    def f(series):
        return quote(str(func(series)).encode('ascii', 'xmlcharrefreplace'))
    return f


def match_regex(d):
    def f(series):
        return {r: v
                for r in series.keys()
                for k, v in d.items() if re.match(k, r)}
    return f


def to_pif(table,
           name=None,
           uid=None,
           subsystems={},
           properties={},
           preparation={},
           default=create_property):
    """
    Creates a Citrination PIF object from the Container object.

    :param table, Container: The DataFrame-like table. Each row becomes
        a new pif.System object.
    :param name: Callable that takes a pd.Series and generates a name
        for the PIF.
    :param uid: None or a callable that takes a pandas.Series and
        generates a name for the PIF. If None, then the UID is a
        URL-friendly version of the name.
    :param subsystems, dict: Dictionary/map between the name of the field
        and a callable that accepts a pd.Series and produces a pif.System
        stored as a subsystem of the pif.System.
    :param properties, dict: Dictionary/map between the name of the field
        and a callable that accepts a pd.Series and produces a list of
        pif.Property objects stored in the pif.Systems. This is the default
        location for all data not otherwise directed.
    :param preparation, dict: Dictionary/map between the name of the field
        and a callable that accepts a pd.Series and produces a
        pif.Preparation object stored in the pif.System.
    :param default, unary function: Default operation for keys not covered
        by any other parameter, e.g. subsystems, properties, or preparation.
    :return: List of pif.System objects.
    """
    container = table.df
    if name is None:
        container = set_index(table, 0).df
        name = get_index
    if uid is None:
        uid = url_friendly(name)
    # set default location for data: properties
    defaultKeys = set(container.columns)
    # subsystems
    defaultKeys = defaultKeys - subsystems.keys()
    subsystems = match_regex(subsystems)
    # preparation
    defaultKeys = defaultKeys - preparation.keys()
    preparation = match_regex(preparation)
    # default location for data
    defaultKeys = defaultKeys - properties.keys()
    properties = match_regex(properties)
    # create the PIF and store the results
    results = []
    for index, series in container.iterrows():
        system = pif.System(name=name(series),
                            uid=uid(series))
        system.sub_systems = [x
                              for k, f in subsystems(series).items()
                              for x in f(series[[k]])]
        system.properties = [x
                             for k, f in properties(series).items()
                             for x in f(series[[k]])]
        system.preparation = [x
                              for k, f in preparation(series).items()
                              for x in f(series[[k]])]
        for k in defaultKeys:
            result = default(series[[k]])[0]
            if isinstance(result, pif.System):
                system.sub_systems.append(result)
            elif isinstance(result, pif.ProcessStep):
                system.preparation.append(result)
            elif isinstance(result, pif.Property):
                system.properties.append(result)
            else:
                raise ValueError(f"The default in 'to_pif' produced an "
                                 f"unrecognized object of type {result}.")
        results.append(system)
    return results
