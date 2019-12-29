import pandas as pd

class QMDataFrameValidator(object):
    def __init__(self):
        self._callbacks = []

    def __call__(self, args, df, filename, sheet, ftype):
        for callback in self._callbacks:
            df = callback(args, df, filename, sheet, ftype)
        return df

    def add_callback(self, func):
        #if not hasattr('__call__', func):
            #raise ValueError("Callback functions must have a ‘__call__’ attribute.")
        self._callbacks.append(func)
