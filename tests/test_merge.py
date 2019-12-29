import pytest
import pandas as pd
import numpy as np
import os
import sys
import inspect
import subprocess
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+r'/src')
from confluence.confluence_merge import *
from confluence.confluence import *


__author__ = "amikulichmines"
__copyright__ = "amikulichmines"
__license__ = "mit"


@pytest.fixture
def expected_dataframe():
    return pd.DataFrame(
        data={'foo': [1, 2, 3, 4],
              'bar': [5, 6, 7, 8]})


@pytest.fixture
def expected_dataframe_with_extra_column():
    return pd.DataFrame(
        data={'foo': [1, 2, 3, 4],
              'bar': [5, 6, 7, 8],
              'baz': [1, 2, np.nan, np.nan]})


@pytest.fixture
def expected_dataframe_with_complex_data():
    return pd.DataFrame(
        data={'foo': [1, 2, 3, 4],
              'bar': [1.83546, -3.415, 941234, 'High'],
              'baz': ['564/194', '!!@#!', 'Low', np.datetime64('2012-09-12T00:00:00')]})


def test_simple_merge_files(expected_dataframe):
    actual = merge_files("test_files/simple1.xlsx test_files/simple2.xlsx -k foo".split())
    expected = expected_dataframe
    print('expected\n', expected)
    print('actual\n', actual)
    assert actual.equals(expected)


def test_merge_with_extra_rows(expected_dataframe):

    actual = merge_files("test_files/extra_rows1.xlsx test_files/extra_rows2.xlsx -k foo".split())
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_columns(expected_dataframe_with_extra_column):
    actual = merge_files("test_files/extra_columns1.xlsx test_files/extra_columns2.xlsx -k foo".split())
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_conflict(expected_dataframe):
    actual = merge_files("test_files/merge_conflict1.xlsx test_files/merge_conflict2.xlsx -m first -k foo".split())
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_column_and_conflict(expected_dataframe_with_extra_column):
    actual = merge_files("test_files/extra_columns1.xlsx test_files/merge_conflict2.xlsx -m first -k foo".split())
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_complex_data(expected_dataframe_with_complex_data):
    actual = merge_files("test_files/complex_data1.xlsx test_files/complex_data2.xlsx -m first -k foo".split())
    expected = expected_dataframe_with_complex_data
    assert actual.equals(expected)


def test_merge_with_three_filetypes(expected_dataframe):
    actual = merge_files("test_files/test_CSV_file.csv "
                         "test_files/test_JSON_file.json "
                         "test_files/test_txt_file.txt -k foo".split())
    expected = expected_dataframe
    assert actual.equals(expected)


def test_fails():
    with pytest.raises(OSError):
        execute('test_files/simple1.xlsx --ofmt pdf -o test_files/Newfile.xlsx -k foo'.split())
    with pytest.raises(OSError):
        read(r'test_files/simple1.txt', ftype='pdf')
    with pytest.raises(SystemExit):
        execute('test_files/merge_conflict1.xlsx test_files/merge_conflict2.xlsx -o test_files/Newfile.xlsx -k foo'.split())

def test_merge_default(expected_dataframe):
    actual = merge_files('test_files/merge_conflict1.xlsx test_files/merge_conflict2.xlsx -o test_files/Newfile.xlsx -k foo -m first'.split())
    expected = expected_dataframe
    assert actual.equals(expected)

# def test_with_extra_sheets(expected_dataframe, expected_dataframe_with_extra_column):
#     sheet1 = merge_files('test_files/multiple_sheets1.xlsx test_files/multiple_sheets2.xlsx -k foo'.split())
#     sheet2 = merge_files([r'test_files/multiple_sheets1.xlsx', r'test_files/multiple_sheets2.xlsx'], 'Bar')
#     expectedSheet1 = expected_dataframe
#     expectedSheet2 = expected_dataframe_with_extra_column
#     assert sheet1.equals(expectedSheet1)
#     assert sheet2.equals(expectedSheet2)
#
#
# # ############ Once the CLI parser is ready to go, we will go ahead and create this function.###########
#
# # def test_cli():
# #     commands = [["merge", "src/confluence/test_files/simple1.xlsx -k 'foo' -o newfile.xlsx"],
# #                 ["list", "duplicates", "src/confluence/test_files/simple1.xlsx -k 'foo'"]]
# #     for cmd in commands:
# #         CLIparser().parse_args(cmd)
#
#
#
def test_run():
    execute('test_files/complete_excel.xlsx -o test_files/complete_excel.xlsx -k foo'.split())
    execute('test_files/test_txt_file.txt -o test_files/test_txt_file.txt -k foo'.split())
    execute('test_files/test_JSON_file.json -o test_files/test_JSON_file.json -k foo'.split())
    execute('test_files/test_CSV_file.csv -o test_files/test_CSV_file.csv -k foo'.split())
