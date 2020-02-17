import pandas as pd


class QMDataFrameValidator(object):
    def __init__(self):
        self._callbacks = []

    def __call__(self, df, filename, sheet='Sheet1'):
        for callback in self._callbacks:
            df = callback(df, filename, sheet)
        return df

    def add_callback(self, func):
        # if not hasattr('__call__', func):
        # raise ValueError("Callback functions must have a ‘__call__’ attribute.")
        self._callbacks.append(func)


def validate(df, filename, sheetname='Sheet1'):
    """
   Function: This sets up a validator. What this does is checks to make sure each file won't conflict against itself.

   The way a validator works is by gathering a few functions that test the dataframe for a certain condition. It will
   either fix the problem if possible, or throw an error. The two functions we have here will check to make sure there
   are no repeated sample names, and that there are no blank sample names.

   The check_for_sample_name_completeness is
   first. It will take in a dataframe as a parameter and go through the first column. If there are any empty spaces,
   it presents an error to the user. There is no way to fix this problem unless the user goes an manually adds it to
   the file. If no blank spaces are found, it will return the dataframe it started with and this will be passed to the
   next function.

   Next is the check_for_sample_name_uniqueness. This makes sure there aren't any repeated names in the file. If it
   does find a repeated value, it tries to fix it by first checking each cell for conflicting values. If none are
   found, it smushes the offending rows together into one. Then, it returns the corrected dataframe.

   With these, all we have to do is df = validate(df) and it'll make sure the incoming dataframe is good.

   :return: an instance of the validator that contains functions to make sure the dataframe won't throw any merge
   conflicts.
   """
    validate = QMDataFrameValidator()
    validate.add_callback(check_for_sample_name_completeness)
    validate.add_callback(check_for_sample_name_uniqueness)
    return validate(df, filename, sheetname)


def check_for_sample_name_completeness(df, filename, sheetname='Sheet1'):
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
        raise ValueError(f"Empty cell in sample name in file {filename} in sheet {sheetname}")
    return df


def check_for_sample_name_uniqueness(df, filename, sheetname='Sheet1'):
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
            raise ValueError(f'Duplicate entry in file {filename} in sheet {sheetname}')
    return df
