#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import pandas as pd
from confluence.merge import merge

__author__ = "amikulichmines"
__copyright__ = "amikulichmines"
__license__ = "mit"


@pytest.fixture
def expected_dataframe():
    return pd.DataFrame(
        data={'foo': [1, 2, 3, 4],
              'bar': [5, 6, 7, 8]})


def test_simple_merge(expected_dataframe):
    actual = merge('data/simple1.xlsx', 'data/simple2.xlsx')
    expected = expected_dataframe
    assert actual == expected


def test_merge_with_extra_rows():
    actual = merge('data/extra_rows1.xlsx', 'data/extra_rows2.xlsx')
    expected = expected_dataframe
    assert actual == expected


def test_merge_with_extra_columns():
    actual = merge('data/extra_columns1.xlsx', 'data/extra_columns2.xlsx')
    expected = expected_dataframe
    assert actual == expected


def test_merge_with_conflict():
    actual = merge('data/conflict1.xlsx', 'data/conflict2.xlsx')
    expected = expected_dataframe
    assert actual == expected


def test_merge_with_extra_column_and_conflict():
    actual = merge('data/conflict1.xlsx', 'data/conflict2.xlsx')
    expected = expected_dataframe
    assert actual == expected


test_simple_merge(expected_dataframe)