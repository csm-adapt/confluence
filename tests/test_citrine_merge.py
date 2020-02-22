import os
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from confluence.citrine.merge import convert
from confluence.io import read


import logging
_logger = logging.getLogger(__name__)


@pytest.fixture()
def expected_merge():
    return pd.DataFrame({
        'foo': [1, 2, 3, 4, 5, 6],
        'bar': ['A', 'B', 'C', 'D', 'E', 'F']
    }).set_index('foo')


@pytest.fixture()
def expected_accept_first():
    return pd.DataFrame({
        'foo': [1, 2, 3],
        'bar': ['A', 'B', 'C'],
    }).set_index('foo')


@pytest.fixture()
def expected_accept_second():
    return pd.DataFrame({
        'foo': [1, 2, 3],
        'bar': ['D', 'E', 'F'],
    }).set_index('foo')


@pytest.fixture
def output_file():
    yield "output.xlsx"
    os.remove("output.xlsx")


def test_simple_merge(expected_merge, output_file):
    ofile = output_file
    f1 = "test_files/123-ABC.xlsx"
    f2 = "test_files/456-DEF.xlsx"
    _ = convert([f1, f2], dest=ofile, backup=False)
    actual = read(ofile, index_col=0)['Sheet1']
    assert_frame_equal(actual, expected_merge)


def test_merge_conflict_accept_first(expected_accept_first, output_file):
    ofile = output_file
    f1 = "test_files/123-ABC.xlsx"
    f2 = "test_files/123-DEF.xlsx"
    _ = convert([f1, f2], dest=ofile, resolve='old', backup=False)
    actual = read(ofile, index_col=0)['Sheet1']
    assert_frame_equal(actual, expected_accept_first)


def test_merge_conflict_accept_second(expected_accept_second, output_file):
    ofile = output_file
    f1 = "test_files/123-ABC.xlsx"
    f2 = "test_files/123-DEF.xlsx"
    _ = convert([f1, f2], dest=ofile, resolve='new', backup=False)
    actual = read(ofile, index_col=0)['Sheet1']
    assert_frame_equal(actual, expected_accept_second)
