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
from confluence.merge import *
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parentdir = os.path.dirname(currentdir)
#sys.path.insert(0, parentdir+r'/src')
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
    set_global_variables
    actual = merge_files([r'test_files/simple1.xlsx', r'test_files/simple2.xlsx'])
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_rows(expected_dataframe):

    actual = merge_files([r'test_files/extra_rows1.xlsx', r'test_files/extra_rows2.xlsx'])
    expected = expected_dataframe
    print('\n\n\n\n\n\nactual\n\n\n\n\n\n', actual)
    print('expected \n')
    assert actual.equals(expected)


def test_merge_with_extra_columns(expected_dataframe_with_extra_column):
    actual = merge_files([r'test_files/extra_columns1.xlsx', r'test_files/extra_columns2.xlsx'])
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_conflict(expected_dataframe):
    set_global_variables(Default='first')
    actual = merge_files([r'test_files/merge_conflict1.xlsx', r'test_files/merge_conflict2.xlsx', '-m', 'first'])
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_column_and_conflict(expected_dataframe_with_extra_column):
    actual = merge_files([r'test_files/extra_columns1.xlsx', r'test_files/merge_conflict2.xlsx', '-m', 'first'])
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_complex_data(expected_dataframe_with_complex_data):
    actual = merge_files([r'test_files/complex_data1.xlsx', r'test_files/complex_data2.xlsx', '-m', 'first'])
    expected = expected_dataframe_with_complex_data
    assert actual.equals(expected)


def test_merge_with_four_filetypes(expected_dataframe):
    actual = merge_files([r'test_files/complete_excel.xlsx',
                   r'test_files/test_CSV_file.csv',
                   r'test_files/test_JSON_file.json',
                   r'test_files/test_txt_file.txt'])
    expected = expected_dataframe
    assert actual.equals(expected)


def test_write():
    df = file_df_row(r'test_files/complete_excel.xlsx', 'xlsx')
    write(df, r'test_files/complete_excel.xlsx', 'xlsx')
    write(df, r'test_files/test_CSV_file.csv', 'csv')
    write(df, r'test_files/test_JSON_file.json', None)
    write(df, r'test_files/test_txt_file.txt', 'txt')


def test_fails():
    set_global_variables(Default='abort')
    with pytest.raises(OSError):
        write(file_df_row(r'test_files/simple1.xlsx', 'xlsx'), r'test_files/Newfile.xlsx', 'pdf')
    with pytest.raises(OSError):
        read(r'test_files/simple1.txt', ftype='pdf')
    with pytest.raises(ValueError):
        file1 = read(r'test_files/merge_conflict1.xlsx').as_dataframe()
        file2 = read(r'test_files/merge_conflict2.xlsx').as_dataframe()
        file1['Filename'] = ['File1'] * len(file1)
        file2['Filename'] = ['File2'] * len(file2)
        check_two_dfs_for_merge_conflict(file1, file2, None)

def test_with_extra_sheets(expected_dataframe, expected_dataframe_with_extra_column):
    sheet1 = merge_files([r'test_files/multiple_sheets1.xlsx', r'test_files/multiple_sheets2.xlsx'], 'Foo')
    sheet2 = merge_files([r'test_files/multiple_sheets1.xlsx', r'test_files/multiple_sheets2.xlsx'], 'Bar')
    expectedSheet1 = expected_dataframe
    expectedSheet2 = expected_dataframe_with_extra_column
    assert sheet1.equals(expectedSheet1)
    assert sheet2.equals(expectedSheet2)

# def test_with_empty_df():
#     actual = merge_files([r'test_files/simple1.xlsx'], 'empty')
#     assert actual.empty

def test_cli():
    commands = [["merge", "src/confluence/test_files/simple1.xlsx -k 'foo' -o newfile.xlsx"],
                ["list", "duplicates", "src/confluence/test_files/simple1.xlsx -k 'foo'"]]
    for cmd in commands:
        # CLIparser().parse_args(cmd)



def test_run():
    args = create_parser(['test_files/complete_excel.xlsx', '-o', 'test_files/Newfile.xlsx'])
    run(args)
