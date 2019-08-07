from confluence.excel import ExcelReader
import os


def read(fname, fmt=None):
    """
    Determines the type of input and call the appropriate reader.

    :param fname: Object to be read.
    :type fname: str
    :param fmt: Explicitly specify the input format.
    :type fmt: str
    :return: BaseReader (or derived class)
    """
    try:
        # TODO: use os.path.splitext to get file extension
        # TODO: unless type is specified explicitly
        if fmt is None:
            basename, ext = os.path.splitext(fname)
            fmt = ext.strip().strip('.').lower()
        else:
            fmt = fmt.strip().strip('.').lower()

        return {
            'excel': ExcelReader,
            'xls': ExcelReader,
            'xlsx': ExcelReader
        }[fmt](fname)
    except KeyError:
        raise NotImplementedError(
            f"No reader for '{type}'' files was found.")
