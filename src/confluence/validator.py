import pandas as pd
from .dataframe import *


class QMDataFrameValidator(object):
    def __init__(self):
        self._callbacks = []

    def __call__(self, df, filename, sheet, ftype):
        for callback in self._callbacks:
            df = callback(df, filename, sheet, ftype)
        return df

    def add_callback(self, func):
        #if not hasattr('__call__', func):
            #raise ValueError("Callback functions must have a ‘__call__’ attribute.")
        self._callbacks.append(func)


def setup_validator():
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
    validate.add_callback(check_sample_name_is_represented_in_dataframe)
    validate.add_callback(check_for_sample_name_completeness)
    validate.add_callback(check_for_sample_name_uniqueness)
    return validate
