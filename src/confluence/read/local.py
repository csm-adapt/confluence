# implement this...
import os
from base import BaseReader


class LocalReader(BaseReader):

    def __init__(self, filename):
        self.file = None
        self.filename = filename
        assert (os.access(filename, os.R_OK)) == True
        super().__init__(self)

    def open(self):
        self.open = open(self.filename)
        self.file = BaseReader(self.open)

    def read(self):
        """
        accesses the file and returns an array of the text separated by lines
        :return: text from the file in array format
        """
        filearray = self.open.readlines()
        return filearray

    def close(self):
        """
        Closes file
        :return: none
        """
        self.open.close()

    def __del__(self):
        pass

    def __iter__(self):
        return iter(self.open)

    def __next__(self):
        return next(self.open)

A = LocalReader('foo.txt')
A.open()
print(A.read())