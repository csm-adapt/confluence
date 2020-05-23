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
from confluence.io import read_yaml
_logger = logging.getLogger(__name__)

@pytest.fixture()
def outfile_yaml():
    yield 'test_files/config.yaml'
    try:
        os.remove('test_files/config.yaml')
    except OSError:
        pass

@pytest.fixture()
def outfile_xlsx():
    yield 'test_files/temporary_outfile.xlsx'
    try:
        os.remove('test_files/temporary_outfile.xlsx')
    except OSError:
        pass


@pytest.fixture()
def expected_merge():
    return pd.DataFrame({
        'foo': [1, 2, 3, 4, 5, 6],
        'bar': ['A', 'B', 'C', 'D', 'E', 'F']
    }).set_index('foo')

@pytest.fixture()
def expected_yaml():
    return  {'dump':
                {'test_files/temporary_outfile.xlsx':
                    {'format': None}},
             'load':
                {'test_files/123-ABC.xlsx':
                    {'format': None},
                 'test_files/456-DEF.xlsx':
                    {'format': None}},
              'merge':
                {'index column': 0,
                 'merge method': 'abort'}}

def test_dry_run(expected_yaml, outfile_yaml, outfile_xlsx):
    """
    Creates a YAML file with the --dry-run feature
    """
    cli = ['merge',
           '--dry-run',
           'test_files/123-ABC.xlsx',
           'test_files/456-DEF.xlsx',
           '--index-column', 0,
           '-m', 'keep_first',
           '-o', outfile_xlsx,
           '->', outfile_yaml]
    with pytest.raises(SystemExit):
        confluence_main(cli)
    data = read_yaml(outfile_yaml)
    assert data == expected_yaml

def test_from_yaml(outfile_xlsx, expected_merge):
    cli = ['merge',
           'test_files/sample.yaml']
    with pytest.raises(SystemExit):
        confluence_main(cli)
    actual = read(outfile_xlsx, index_col="foo")['Sheet1'].df
    assert_frame_equal(actual, expected_merge)


