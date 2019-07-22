import pandas as pd


class ExcelReader():
    def __init__(self, *filenames):
        self.filenames = filenames
        self.ifs = None
        self.combined = None

    def _arrange_to_2d(self, tuple):
        self.arr = []
        for i in range(len(tuple)):
            self.arr.append([])
            self.arr[i].append(tuple[i])
            self.arr[i].append(self._open_excel(tuple[i]))
        return self.arr

    def _check_for_duplicates(self, dataframe):
        """
        Functions: raise an error if a duplicate sample name is found
        :param filename: name of the file
        :param dataframe: excel spreadsheet data
        :return: none
        """

        df = pd.DataFrame(dataframe, columns=['Sample Name'])
        duplicated = df.duplicated()
        if duplicated.any():
            return True

    def _check_each_for_duplicates(self, filename, dataframe):
        """
        Functions: raise an error if a duplicate sample name is found
        :param filename: name of the file
        :param dataframe: excel spreadsheet data
        :return: none
        """

        try:
            df = pd.DataFrame(dataframe)
            df = (df['Sample Name'])
            duplicated = df.duplicated()
            if duplicated.any():
                raise IOError
        except IOError:
            raise IOError(f'Duplicate sample name in file {filename}')

    def _open_excel(self, filename):
        return pd.read_excel(filename)

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

    def _remove_duplicates(self, dataframe):
        """
                function: Removes duplicate rows
                :param dataframe: excel spreadsheet data
                :return: dataframe with no duplicates
                """
        return dataframe.drop_duplicates()

    def _check_for_merge_conflict(self):
        """

        :param filename: name of the file
        :param dataframe: excel spreadsheet data
        :return: none
        """
        array = self._arrange_to_2d(self.filenames)
        length = len(self.filenames)
        for i in range(len(self.filenames)):
            for j in range(i + 1, length):
                df = pd.concat([array[i][1], array[j][1]])
                self._remove_duplicates(df)
                if self._check_for_duplicates(df):
                    raise IOError(f'Merge conflict between {array[i][0]} and {array[j][0]}')

    def merge(self):
        """
        creates a merged dataframe. As of July 14, it has not yet been coded to delete duplicate rows.
        :return: merged dataframe
        """
        filenames = self.filenames
        for filename in filenames:
            df = self._open_excel(filename)
            self._check_if_empty(filename, df)
            self._check_one_for_duplicates(filename, df)
        self._check_for_merge_conflict()
        for filename in filenames:
            df = self._open_excel(filename)
            self.combined = pd.concat([self.combined, df])
        self._remove_duplicates(self.combined)
        return self.combined

class ExcelWriter():
    def __init__(self,*filenames):
        self.filenames = filenames

    def write(self, filename):
        """
        function: write a dataframe to excel
        :param filename:
        :return: none
        """
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        self.combined.to_excel(writer, sheet_name='Sheet1')
        writer.save()

A = ExcelReader()