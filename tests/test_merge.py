/#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import pandas as pd
import numpy as np
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+r'/src')
from confluence.merge import merge, write, file_df_row, read, check_for_merge_conflict, run


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


def test_simple_merge(expected_dataframe):
    actual = merge(r'test_files/simple1.xlsx', r'test_files/simple2.xlsx')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_rows(expected_dataframe):
    actual = merge(r'test_files/extra_rows1.xlsx', r'test_files/extra_rows2.xlsx')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_columns(expected_dataframe_with_extra_column):
    actual = merge(r'test_files/extra_columns1.xlsx', r'test_files/extra_columns2.xlsx')
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_conflict(expected_dataframe):
    actual = merge(r'test_files/merge_conflict1.xlsx', r'test_files/merge_conflict2.xlsx', '-m', 'first')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_column_and_conflict(expected_dataframe_with_extra_column):
    actual = merge(r'test_files/extra_columns1.xlsx', r'test_files/merge_conflict2.xlsx', '-m', 'first')
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_four_filetypes(expected_dataframe):
    actual = merge(r'test_files/complete_excel.xlsx',
                   r'test_files/test_CSV_file.csv',
                   r'test_files/test_JSON_file.json',
                   r'test_files/test_txt_file.txt')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_write():
    df = file_df_row(r'test_files/complete_excel.xlsx', 'xlsx')
    write(df, r'test_files/complete_excel.xlsx', 'xlsx')
    write(df, r'test_files/test_CSV_file.csv', 'csv')
    write(df, r'test_files/test_JSON_file.json', None)
    write(df, r'test_files/test_txt_file.txt', 'txt')


def test_fails():
    with pytest.raises(OSError):
        write(file_df_row(r'test_files/simple1.xlsx', 'xlsx'), r'test_files/Newfile.xlsx', 'pdf')
    with pytest.raises(OSError):
        read(r'test_files/simple1.txt', ftype='pdf')
    with pytest.raises(ValueError):
        check_for_merge_conflict(read(r'test_files/merge_conflict1.xlsx').as_dataframe(),
                                 read(r'test_files/merge_conflict2.xlsx').as_dataframe(),
                                 None, None, None)


def test_run():
    run([r'test_files/complete_excel.xlsx', '-o', r'test_files/Newfile.xlsx'])


#merge('complete_excel.xlsx')
