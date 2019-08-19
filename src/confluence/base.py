class BaseReader(object):
    """
    Base reader agent for abstracting the details of reading data
    from various sources, e.g. local file systems to SQL databases
    to Citrination.

    This object acts as an iterator, serving data from the source
    one chunk at a time, for example, line-by-line if the derived
    reader is to a local file object.
    """
    def __init__(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError(
            "__next__ must be implemented in all Readers.")

    def as_dataframe(self, *args, **kwds):
        raise IOError("Cannot return object as a pandas.DataFrame.")
