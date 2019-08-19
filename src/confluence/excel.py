import pandas as pd
from base import BaseReader


class ExcelReader(BaseReader):
    def __init__(self, fname=None, sheetname='Sheet1', **kwds):
        super().__init__()
        self._filename = None
        self.set_filename(fname)
        self.sheetname = sheetname

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
        #print(sheetname)
        return pd.read_excel(args, sheet_name=self.sheetname).dropna(how='all').dropna(how='all', axis='columns') #**kwds,

    def sheetnames(self):
        df = pd.ExcelFile(self.get_filename())
        return list(df.sheet_names)


class ExcelWriter(BaseReader):
    def __init__(self, fname=None, sheetname='Sheet1', **kwds):
        super().__init__()
        self._filename = None
        self.set_filename(fname)
        self.sheetname = sheetname
        self.writer = pd.ExcelWriter(self.get_filename(), engine='xlsxwriter')

    def set_filename(self, fname):
        self._filename = fname

    def get_filename(self):
        return self._filename

    def get_header(self, workbook):
        return workbook.add_format({
            'bold': True,
            'text_wrap': False,
            'border': 1,
            'rotation': 70,
            'align': 'center'})

    def get_column_width(self, df, value):
        series = df[value]
        return series.astype(str).map(len).max() + 1  # adding a little extra space

    def write(self, df, sheetname='Sheet1'):
        df.to_excel(self.writer, sheet_name=sheetname, index=False, header=False, startrow=1)
        workbook = self.writer.book
        worksheet = self.writer.sheets[sheetname]
        header_format = self.get_header(workbook)
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, self.get_column_width(df, value))  # set column width

    def save_and_close(self):
        self.writer.save()
        self.writer.close()
