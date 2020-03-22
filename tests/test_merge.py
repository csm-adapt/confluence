import pytest
import pandas as pd
import logging
from pandas.testing import assert_frame_equal
import os
import numpy as np
from confluence.subcommands.merge import main as merge_main
from confluence.subcommands.merge import merge as merge_merge
from confluence.subcommands.merge import MergeMethod
from confluence.confluence import main as confluence_main
from confluence.io import read
import glob
_logger = logging.getLogger(__name__)


@pytest.fixture()
def expected1():
    return pd.DataFrame({
        'foo': [1,2,3,4],
        'bar': ['A', 'B', 'C', 'D'],
    }).set_index('foo')


@pytest.fixture()
def expected2():
    return pd.DataFrame({
        'foo': [1,2,3,4],
        'bar': [5,6,7,8],
    }).set_index('foo')


def test_simple_merge(expected1):
    df1 = read("test_files/simple1.xlsx", index_col="foo")['Sheet1']
    df2 = read("test_files/simple2.xlsx", index_col="foo")['Sheet1']
    actual = merge_merge(df1, df2)
    assert_frame_equal(actual, expected1)


def test_cli():
    cli = ['merge',
           'test_files/merge_conflict1.xlsx',
           'test_files/merge_conflict2.xlsx',
           '--index-column', 0,
           '-m', 'keep_first',
           '-o', 'test_files/temporary_outfile.xlsx']
    confluence_main(cli)
    try:
        os.remove('test_files/temporary_outfile.xlsx')
    except OSError:
        pass


def test_merge_conflict_accept_first(expected1):
    df1 = read("test_files/merge_conflict1.xlsx", index_col="foo")['Sheet1']
    df2 = read("test_files/merge_conflict2.xlsx", index_col="foo")['Sheet1']
    actual = merge_merge(df1, df2, MergeMethod.FIRST)
    assert_frame_equal(actual, expected1)


def test_merge_conflict_accept_second(expected2):
    df1 = read("test_files/merge_conflict1.xlsx", index_col="foo")['Sheet1']
    df2 = read("test_files/merge_conflict2.xlsx", index_col="foo")['Sheet1']
    actual = merge_merge(df1, df2, MergeMethod.SECOND)
    print(actual)
    assert_frame_equal(actual, expected2)
