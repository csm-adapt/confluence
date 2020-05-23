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


@pytest.fixture()
def outfile_xlsx():
    yield 'test_files/temporary_outfile.xlsx'
    try:
        os.remove('test_files/temporary_outfile.xlsx')
    except OSError:
        pass


@pytest.fixture()
def outfile_json():
    yield 'test_files/temporary_outfile.json'
    try:
        os.remove('test_files/temporary_outfile.json')
    except OSError:
        pass


@pytest.fixture()
def outfile_txt():
    yield 'test_files/temporary_outfile.txt'
    try:
        os.remove('test_files/temporary_outfile.txt')
    except OSError:
        pass


@pytest.fixture()
def outfile_csv():
    yield 'test_files/temporary_outfile.csv'
    try:
        os.remove('test_files/temporary_outfile.csv')
    except OSError:
        pass


def test_excel(expected_accept_first, outfile_xlsx):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', outfile_xlsx]
    merge_main(cli)
    df = read(outfile_xlsx, index_col=0)['Sheet1'].df
    assert_frame_equal(df, expected_accept_first)


def test_json(expected_accept_first, outfile_json):
    cli = ['test_files/123-ABC.json',
           '--index-column', 0,
           '-o', outfile_json]
    merge_main(cli)
    df = list(read(outfile_json, index_col=0).values())[0].df
    expected_accept_first.index.name = None
    expected_accept_first.index = expected_accept_first.index.map(str)
    assert_frame_equal(df, expected_accept_first)


def test_text(expected_accept_first, outfile_txt):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', 'test_files/123-ABC.txt']
    merge_main(cli)
    df = read('test_files/123-ABC.txt', index_col=0)['text'].df
    assert_frame_equal(df, expected_accept_first)


def test_csv(expected_accept_first):
    cli = ['test_files/123-ABC.xlsx',
           '--index-column', 0,
           '-o', 'test_files/123-ABC.csv']
    merge_main(cli)
    df = read('test_files/123-ABC.csv', index_col=0)['CSV'].df
    assert_frame_equal(df, expected_accept_first)