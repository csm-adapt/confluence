class BaseWriter(object):
    """
    Base writer agent for abstracting the details of writing data
    from a confluence instance into various sources, e.g. local
    file systems to SQL databases to Citrination.

    This object acts as an iterator, serving data to the source
    one chunk at a time, for example, line-by-line if the derived
    writer is to a local file object.
    """
    def __init__(self):
        pass


    def __iter__(self):
        return self


    def __next__(self):
        raise NotImplementedError(
            "__next__ must be implemented in all Writers.")
