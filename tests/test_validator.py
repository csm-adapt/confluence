import pytest
import logging
import os
from confluence.subcommands.merge import main as merge_main
_logger = logging.getLogger(__name__)


def test_duplicated_index():
    cli = ['test_files/121-ABC.xlsx',
           'test_files/123-DEF.xlsx',
           '--index-column', 0,
           '-m', 'keep_first',
           '-o', 'test_files/temporary_outfile.xlsx',
           '--validate']
    with pytest.raises(ValueError):
        merge_main(cli)


def test_empty_index():
    cli = ['test_files/1_3-ABC.xlsx',
           '-o', 'test_files/temporary_outfile.xlsx',
           '--validate']
    with pytest.raises(ValueError):
        merge_main(cli)

