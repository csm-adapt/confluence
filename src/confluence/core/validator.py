class QMDataFrameValidator(object):
    """
    Function: Sets up a series of functions that take in a
    dataframe, check to see if it has any internal conflicts,
    and throws an error if one is found.
    """
    def __init__(self):
        self._callbacks = []

    def __call__(self, df, filename, sheet='Sheet1'):
        """
        Function: Cycles through each callback, feeding the
        dataframe to the next function to check for errors.
        :param df: dataframe to be tested
        :param filename: Filename corresponding to the dataframe
        :param sheet: Sheet corresponding to the dataframe
        :return: dataframe with no errors
        """
        for callback in self._callbacks:
            df = callback(df, filename, sheet)
        return df

    def add_callback(self, func):
        # if not hasattr('__call__', func):
        # raise ValueError("Callback functions must have a ‘__call__’ attribute.")
        self._callbacks.append(func)


def check_for_missing_index(df, filename, sheetname='Sheet1'):
    """
   Function: Checks the first column for empty cells. If there is an empty cell, throw an error. Otherwise, return
   the original dataframe
   :param df: dataframe to check
   :param filename: name of the file
   :param sheetname: name of the sheet
   :param column: name of the column that you are checking
   :return: dataframe with all entries in the 'column' filled. If there is an empty one, an error is thrown.
   """
    if any(pd.isna(df.index)):
        raise ValueError(f"Empty index cell in file '{filename}' "
                         f"in sheet '{sheetname}' "
                         f"in column '{df.index.name}'")
    return df


def check_unique_index(df, filename, sheetname='Sheet1'):
    """
   Functionality: Makes sure there are no repeated sample names, similar to the 'check_for_merge_conflict' function
   :param df: dataframe to check
   :param filename: name of the file
   :param sheetname: name of the sheet
   :param column: column that is being checked
   :return: dataframe
   """
    temp = df[df.index.duplicated(keep=False)]
    for key in temp:
        instances = temp[key].nunique()
        if instances > 1:
            raise ValueError(f"Duplicate entry in file '{filename}' "
                             f"in sheet '{sheetname}' "
                             f"in column '{df.index.name}'")
    return df
