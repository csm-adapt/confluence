import re
from confluence.core.container import Container

import logging
_logger = logging.getLogger(__name__)


# # Set up a class that parses the Wolf .doc (.txt) formatted output file
class WolfDoc(dict):
    """
    Helper class to read the text-based log file produced by the Lincoln
    Electric (formerly Wolf) Quality Made robot.

    Despite the .doc extension, these are strictly text files.
    """
    def __init__(self, opens=r'^\\\\\\([^\\]+)\\\\\\\.*', closes='^-+\s*$'):
        super().__init__(self)
        # This defines the regular expressions that demarcate the start/end of blocks of data
        self.opens = re.compile(opens)
        self.closes = re.compile(closes)
        self.filename = None
        self.categories = set()
        self.container = None

    @staticmethod
    def converter(x):
        try:
            return int(x)
        except:
            try:
                return float(x)
            except:
                return x
    
    def load(self, fileobj):
        """
        Loads the contents of fileobj, which could be a string (filename)
        or file object.
        """
        # Is the object a file name or a file stream?
        if hasattr(fileobj, 'readline'):
            fs = fileobj
        else:
            self.filename = fileobj
            fs = open(fileobj)
        try:
            # If anything goes wrong, make sure to close the file.
            scope = None
            entries = {}
            for line in fs:
                # check for opening block
                match = re.search(self.opens, line)
                if match:
                    scope = match.group(1)
                    self.categories = self.categories.union([scope])
                    continue
                # check for closing block
                match = re.search(self.closes, line)
                if match:
                    scope = None
                    continue
                # read between opening and closing
                if scope is not None:
                    try:
                        # Most lines are key-value pairs
                        key, value = line.split(':', 1)
                        key = scope + ': ' + key
                    except ValueError:
                        # Some, however, are descriptive of the block.
                        # These become entries in the block.
                        key = scope
                        value = line
                    # Get rid of leading/trailing whitespace
                    key = key.strip()
                    value = value.strip()
                    # If the same key is repeated, then this entry should be a
                    # list.
                    if key in entries:
                        old = entries[key]
                        if isinstance(old, tuple):
                            entries[key] = old + (value,)
                        else:
                            entries[key] = (old, value)
                    else:
                        entries[key] = WolfDoc.converter(value)
        except:
            raise
        finally:
            # Regardless of an error, close the file
            if fs is not fileobj:
                fs.close()
        # Store this single entry as a DataFrame (not a series)
        for k,v in entries.items():
            entries[k] = [v]
        self.container = Container(entries)
        # Done, return self to enable anonymous use, e.g.
        # result = WolfDoc().load('filename.doc')
        return self

    def sort_columns(self):
        """
        Reorders the columns in the container based on the lexicographical
        order of categories read from the input file.

        :return: This WolfDoc object (to allow commands to be daisy-chained.)
        """
        categories = sorted(list(self.categories))
        keys = self.container.columns.tolist()
        columns = []
        for prefix in categories:
            # sort all keys that start with prefix alphabetically
            subkeys = sorted([k for k in keys if k.startswith(prefix)])
            # incrementally build list of columns
            columns.extend(subkeys)
            # remove the keys that were just added to columns
            keys = list(set(keys) - set(subkeys))
        # sort any remaining (uncategorized) keys.
        columns = list(sorted(keys)) + columns
        # reorder the container
        self.container = self.container[columns]
        # done
        return self

    def rename_column(self, old, new):
        """
        Renames a column. If a column with the new name already exists, it
        is overwritten. The location of the column may change.

        :param old: Old column name.
        :param new: New column name.
        :return: self
        """
        self.container[new] = self.container[old]
        del self.container[old]
        return self

    def add_column(self, name, dtype=str):
        """
        Adds a new, initialized column.
        :param name: Column name.
        :param dtype: Data type for this column.
        :return: self
        """
        self.container[name] = len(self.container)*[dtype()]
        return self

    def move(self, name, pos=0):
        """
        Moves the named column into a new position.

        :param name: Name of the column to move. A KeyError is raised if the
            key is not found.
        :param pos: New position of the column.
        :return: self
        """
        if name not in self.container:
            raise KeyError(f"Column {name} was not found.")
        names = [k for k in self.container.columns.tolist() if k != name]
        columns = names[:pos] + [name] + names[pos:]
        self.container = self.container[columns]
        return self


def read(fname, **kwds):
    """
    Reads a log file from the prototype robot built and developed for the
    Navy under Quality Made (2019-). If no sample name is provided, then
    the filename is used as the sample name.

    :param fname: Filename name or file object to be read.
    :param kwds: Optional keywords passed to DataFrame-like Container.
    :return: pandas DataFrame-like Container.
    """
    _logger.info(f"Reading Quality Made-formatted log file {fname}.")
    doc = WolfDoc()\
        .load(fname)\
        .sort_columns()\
        .rename_column('Identification Information: Sample No', 'Sample Name')\
        .add_column('Parent Sample Name')\
        .move('Sample Name', pos=0)\
        .move('Parent Sample Name', pos=1)
    if doc.container.loc[0, "Sample Name"] == '':
        doc.container.loc[0, "Sample Name"] = fname
    # map read options to DataFrame options
    options = {}
    if "index_col" in kwds:
        index = doc.container.columns.to_list()[kwds["index_col"]]
        doc.container.set_index(index, inplace=True)
    # done
    return doc.container
