import pytest
import pandas as pd
import logging
from pandas.testing import assert_frame_equal
import os
from confluence.subcommands.merge import main as merge_main
from confluence.subcommands.merge import merge as merge_merge
from confluence.subcommands.merge import MergeMethod
from confluence.subcommands.duplicates import main as duplicates_main
from confluence.confluence import main as confluence_main
from confluence.io import read
_logger = logging.getLogger(__name__)


@pytest.fixture()
def expected_accept_first():
    return pd.DataFrame({
        'foo': [1, 2, 3],
        'bar': ['A', 'B', 'C'],
    }).set_index('foo')


def test_excel(expected_accept_first):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', 'test_files/123-ABC.xlsx']
    merge_main(cli)
    df = read('test_files/123-ABC.xlsx', index_col=0)['Sheet1']
    assert_frame_equal(df, expected_accept_first)


def test_json(expected_accept_first):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', 'test_files/123-ABC.json']
    merge_main(cli)
    df = list(read('test_files/123-ABC.json', index_col=0).values())[0]
    expected_accept_first.index.name = None
    expected_accept_first.index = expected_accept_first.index.map(str)
    assert_frame_equal(df, expected_accept_first)


def test_text(expected_accept_first):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', 'test_files/123-ABC.txt']
    merge_main(cli)
    df = read('test_files/123-ABC.txt', index_col=0)['text']
    assert_frame_equal(df, expected_accept_first)


def test_csv(expected_accept_first):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', 'test_files/123-ABC.csv']
    merge_main(cli)
    df = read('test_files/123-ABC.csv', index_col=0)['CSV']
    assert_frame_equal(df, expected_accept_first)
