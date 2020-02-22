import os
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from confluence.citrine.merge import convert
from confluence.io import read


import logging
_logger = logging.getLogger(__name__)


@pytest.fixture
def expected1():
    return pd.DataFrame({
        'foo': [1, 2, 3, 4],
        'bar': ['A', 'B', 'C', 'D']})


@pytest.fixture
def expected2():
    return pd.DataFrame({
        'foo': [1, 2, 3, 4],
        'bar': [5, 6, 7, 8]})


@pytest.fixture
def output_file():
    yield "output.xlsx"
    os.remove("output.xlsx")


def test_simple_merge(expected1, output_file):
    ofile = output_file
    f1 = "test_files/simple1.xlsx"
    f2 = "test_files/simple2.xlsx"
    _ = convert([f1, f2], dest=ofile, backup=False)
    actual = read(ofile)['Sheet1']
    assert_frame_equal(actual, expected1)


def test_merge_conflict_accept_first(expected1, output_file):
    ofile = output_file
    f1 = "test_files/merge_conflict1.xlsx"
    f2 = "test_files/merge_conflict2.xlsx"
    _ = convert([f1, f2], dest=ofile, resolve='old', backup=False)
    actual = read(ofile)['Sheet1']
    assert_frame_equal(actual, expected1)


def test_merge_conflict_accept_second(expected2, output_file):
    ofile = output_file
    f1 = "test_files/merge_conflict1.xlsx"
    f2 = "test_files/merge_conflict2.xlsx"
    _ = convert([f1, f2], dest=ofile, resolve='new', backup=False)
    actual = read(ofile)['Sheet1']
    assert_frame_equal(actual, expected2)
