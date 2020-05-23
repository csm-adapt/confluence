import pandas as pd


class Container:
    def __init__(self, df=None):
        self._df = None
        self.df = df

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, obj):
        if obj is None:
            del self._df
            self._df = None
        else:
            try:
                self._df = pd.DataFrame(obj)
            except ValueError:
                raise ValueError(f"Unable to convert {obj} to dataframe.")
