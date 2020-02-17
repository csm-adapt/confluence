import pytest
import pandas as pd
import logging
from pandas.testing import assert_frame_equal
import os
from confluence.subcommands.merge import main as merge_main
from confluence.subcommands.merge import merge as merge_merge
from confluence.subcommands.merge import MergeMethod
from confluence.confluence import main as confluence_main
from confluence.io import read
_logger = logging.getLogger(__name__)


#@pytest.fixture()
def expected_merge():
    return pd.DataFrame({
        'foo': [1, 2, 3, 4, 5, 6],
        'bar': ['A', 'B', 'C', 'D', 'E', 'F']
    }).set_index('foo')

#
# @pytest.fixture()
# def expected_accept_first():
#     return pd.DataFrame({
#         'foo': [1, 2, 3],
#         'bar': ['A', 'B', 'C'],
#     }).set_index('foo')
#
#
# @pytest.fixture()
# def expected_accept_second():
#     return pd.DataFrame({
#         'foo': [1, 2, 3],
#         'bar': ['D', 'E', 'F'],
#     }).set_index('foo')
#
#
# def test_simple_merge(expected_merge):
#     df1 = read("test_files/123-ABC.xlsx", index_col="foo")['Sheet1']
#     df2 = read("test_files/456-DEF.xlsx", index_col="foo")['Sheet1']
#     actual = merge_merge(df1, df2)
#     assert_frame_equal(actual, expected_merge)
#
#
# def test_cli():
#     cli = ['merge',
#            'test_files/123-ABC.xlsx',
#            'test_files/123-DEF.xlsx',
#            '--index-column', 0,
#            '-m', 'keep_first',
#            '-o', 'test_files/temporary_outfile.xlsx']
#     confluence_main(cli)
#     try:
#         os.remove('test_files/temporary_outfile.xlsx')
#     except OSError:
#         pass
#
#
# def test_merge_conflict_accept_first(expected_accept_first):
#     df1 = read("test_files/123-ABC.xlsx", index_col="foo")['Sheet1']
#     df2 = read("test_files/123-DEF.xlsx", index_col="foo")['Sheet1']
#     actual = merge_merge(df1, df2, MergeMethod.FIRST)
#     assert_frame_equal(actual, expected_accept_first)
#
#
# def test_merge_conflict_accept_second(expected_accept_second):
#     df1 = read("test_files/123-ABC.xlsx", index_col="foo")['Sheet1']
#     df2 = read("test_files/123-DEF.xlsx", index_col="foo")['Sheet1']
#     actual = merge_merge(df1, df2, MergeMethod.SECOND)
#     assert_frame_equal(actual, expected_accept_second)
#
#
# def test_merge_conflict_from_cli(expected_accept_first):
#     cli = ['test_files/123-ABC.xlsx',
#            'test_files/123-DEF.xlsx',
#            '--index-column', 0,
#            '-m', 'keep_first',
#            '-o', 'test_files/temporary_outfile.xlsx']
#     merge_main(cli)
#     actual = read("test_files/temporary_outfile.xlsx", index_col="foo")['Sheet1']
#     assert_frame_equal(expected_accept_first, actual)
#     try:
#         os.remove('test_files/temporary_outfile.xlsx')
#     except OSError:
#         pass
#
#
# def test_duplicated_index():
#     cli = ['test_files/121-ABC.xlsx',
#            'test_files/123-DEF.xlsx',
#            '--index-column', 0,
#            '-m', 'keep_first',
#            '-o', 'test_files/temporary_outfile.xlsx']
#     with pytest.raises(ValueError):
#         merge_main(cli)
#     try:
#         os.remove('test_files/temporary_outfile.xlsx')
#     except OSError:
#         pass
#
#
# def test_empty_index():
#     cli = ['test_files/1_3-ABC.xlsx',
#            '-o', 'test_files/temporary_outfile.xlsx']
#     with pytest.raises(ValueError):
#         merge_main(cli)
#     try:
#         os.remove('test_files/temporary_outfile.xlsx')
#     except OSError:
#         pass


def test_json(expected_merge, **kwds):
    # cli = ['merge',
    #        'test_files/123-ABC.xlsx',
    #        'test_files/123-DEF.xlsx',
    #        '--index-column', 0,
    #        '-m', 'keep_first',
    #        '-o', 'test_files/temporary_outfile.xlsx']
    # merge_main(cli)
    # cli = ['test_files/test_JSON_file.json',
    #        '-o', 'test_files/test_JSON_file_o.json']
    #merge_main(cli)
    df = read('test_files/test_JSON_file.json', index_col='fpo')
    print(df)
    print(expected_merge)
    assert_frame_equal(df, expected_merge)

test_json(expected_merge(), index_col='foo')