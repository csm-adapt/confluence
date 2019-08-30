#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, r'C:\Users\Alex\Documents\workspace\confluence\src')
from confluence.merge import merge, write, create_file_df, read, check_for_merge_conflict

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
    actual = merge('simple1.xlsx', 'simple2.xlsx')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_rows(expected_dataframe):
    actual = merge('extra_rows1.xlsx', 'extra_rows2.xlsx')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_columns(expected_dataframe_with_extra_column):
    actual = merge('extra_columns1.xlsx', 'extra_columns2.xlsx')
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_conflict(expected_dataframe):
    actual = merge('merge_conflict1.xlsx', 'merge_conflict2.xlsx')
    expected = expected_dataframe
    assert actual.equals(expected)


def test_merge_with_extra_column_and_conflict(expected_dataframe_with_extra_column):
    actual = merge('extra_columns1.xlsx', 'merge_conflict2.xlsx')
    expected = expected_dataframe_with_extra_column
    assert actual.equals(expected)


def test_merge_with_four_filetypes(expected_dataframe):
    actual = merge('complete_excel.xlsx',
                   'test_CSV_file.csv',
                   'test_JSON_file.json',
                   'test_txt_file.txt')
    expected = expected_dataframe
    assert actual.equals(expected)


# def test_parser():
#     #parser = parse_args(['-l', '-m'])
#     # print(parser.long)
#     # assert(parser.long)
#     parser = parse_args(['--something', 'test'])
#     assert(parser.something, 'test')


def test_write():
    df = create_file_df('complete_excel.xlsx', 'xlsx')
    write(df, 'complete_excel.xlsx', 'xlsx')
    write(df, 'test_CSV_file.csv', 'csv')
    write(df, 'test_JSON_file.json', None)
    write(df, 'test_txt_file.txt', 'txt')


def test_fails():
    with pytest.raises(OSError):
        write(create_file_df('simple1.xlsx', 'xlsx'), 'Newfile.xlsx', 'pdf')
    with pytest.raises(OSError):
        read('simple1.txt', ftype='pdf')
    with pytest.raises(OSError):
        check_for_merge_conflict(read('merge_conflict1'),
                                 read('merge_confice2'),
                                 None, None, None)
