import pandas as pd
from pypif import pif



class PifWriter():
    def __init__(self, fname=None, sheetname='Sheet1', **kwds):
        #super().__init__(self)
        self._filename = None
        self.set_filename(fname)
        self.sheetname = sheetname
        self.writer = pd.ExcelWriter(fname, engine='xlsxwriter')

    def set_filename(self, fname):
        self._filename = fname

    def get_filename(self):
        return self._filename

    def convert(self, df):
        """
        Converts a specialized CSV/TSV file to a physical information file.

        :param files: list of files to convert
        :return: yields PIFs created from the input files
        """

        for i in range(len(df)):
            row_pif = df.iloc[i, :]
            yield dict(row_pif)

    def write(self, df, sheetname='Sheet1'):
        result = self.convert(df)
        with open(self.get_filename(), 'w+') as output_file:
            pif.dump(list(result), output_file, indent=2)

