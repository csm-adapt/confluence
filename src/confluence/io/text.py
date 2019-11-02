import pandas as pd
import numpy as np


class TextReader():
    def __init__(self, fname=None, delimiter=" ", **kwds):
        self._filename = None
        self.set_filename(fname)
        self._delimiter = delimiter

    def set_filename(self, fname):
        self._filename = fname


    def get_filename(self):
        return self._filename


    def as_dataframe(self, *args, **kwds):
        """
        Reads the requested sheetname (if specified) from the Excel file.

        :param args: Positional parameters passed to pandas.read_excel.
            The filename of this reader is appended to *args.
        :param kwds: Optional parameters to pass to pandas.read_excel.
        :return: pandas.DataFrame of the requested Excel worksheet.
        """
        #args = (self.get_filename() + args)
        args = self.get_filename()
        df = pd.read_csv(args, delim_whitespace=True, header=0)
        return df


class TextWriter():
    def __init__(self, fname=None, delimiter=" ", **kwds):
        self._filename = None
        self.set_filename(fname)
        self._delimiter = delimiter

    def set_filename(self, fname):
        self._filename = fname

    def get_filename(self):
        return self._filename

    def write(self, df):
        df.to_csv(self.get_filename(), index=False, sep=self._delimiter, na_rep=np.nan)