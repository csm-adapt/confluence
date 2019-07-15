import pandas as pd


class Excel_reader():
    def __init__(self, *filenames):
        self.filenames = filenames
        self.ifs = None
        self.combined = None

    def _open_excel(self, filename):
        self.ifs = pd.read_excel(filename)
        return self.ifs

    def _close(self):
        self.ifs.close()

    def _check_if_empty(self, filename, dataframe, column='Sample Name'):
        """
        Function: Raises an error if an element is empty

        :param filename: The name of the file
        :param dataframe: The dataframe containing the excel spreadsheet
        :param column: Name of the column being checked

        :return: none
        """
        try:
            numberRows = len(dataframe)
            for i in range(numberRows):
                cellValue = dataframe.iloc[i][column]
                if pd.isna(cellValue) is True:
                    raise IOError
        except IOError:
            raise IOError('1 or more empty columns found in file ', filename)

    def _check_for_duplicates(self, filename, dataframe, column=['Sample Name']):
        """
        Functions: raise an error if a duplicate sample name is found
        :param filename: name of the file
        :param dataframe: excel spreadsheet data
        :return: none
        """

        try:
            df = pd.DataFrame(dataframe, column)
            duplicated = df.duplicated()
            if duplicated.any():
                raise IOError
        except IOError:
            raise IOError('Duplicate sample name in file ', filename)

    def _remove_duplicates(self, dataframe):
        """
                function: Removes duplicate rows
                :param dataframe: excel spreadsheet data
                :return: dataframe with no duplicates
                """

        unduplicated = dataframe.drop_duplicates()
        return unduplicated

    def _check_for_merge_conflict(self, dataframe):
        """

        :param filename: name of the file
        :param dataframe: excel spreadsheet data
        :return: none
        """

        try:
            df = pd.DataFrame(dataframe, columns=['Sample Name'])
            duplicated = df.duplicated()
            if duplicated.any():
                raise IOError
        except IOError:
            raise IOError('Merge conflict')

    def write(self, filename):
        """
        function: write a dataframe to excel
        :param filename:
        :return: none
        """
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        self.combined.to_excel(writer, sheet_name='Sheet1')
        writer.save()

    def merge(self):
        """
        creates a merged dataframe. As of July 14, it has not yet been coded to delete duplicate rows.
        :return: merged dataframe
        """
        filenames = self.filenames
        for filename in filenames:
            ifs = self._open_excel(filename)
            self._check_if_empty(filename, ifs)
            self._check_for_duplicates(filename, ifs)
            self.combined = pd.concat([self.combined, ifs])
            self.combined = self._remove_duplicates(self.combined)
            self._check_for_merge_conflict(self.combined)
        self._close
        return self.combined
