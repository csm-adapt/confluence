class BaseReader(object):
    """
    Base reader agent for abstracting the details of reading data
    from various sources, e.g. local file systems to SQL databases
    to Citrination.

    This object acts as an iterator, serving data from the source
    one chunk at a time, for example, line-by-line if the derived
    reader is to a local file object.

    Example
    =======
    :code:`python`
        reader = BaseReader()
        reader.open('foo.txt')
        for line in reader:
            print(line)
        reader.close()

    :code:`python`
        reader = BaseReader('foo.txt')
        for line in reader:
            print(line)
        reader.close()
    """

    def __init__(self, file):
        self.file = file

    # Attribute proxy for wrapped file object

    def __iter__(self):
        return iter(self.file)


    def __next__(self):
        return next(self.file)

    def read(self):
        pass


    def as_dataframe(self, *args, **kwds):
        raise IOError("Cannot return object as a pandas.DataFrame.")
