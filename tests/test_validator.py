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
           '-o', 'test_files/temporary_outfile.xlsx']
    with pytest.raises(ValueError):
        merge_main(cli)


def test_empty_index():
    cli = ['test_files/1_3-ABC.xlsx',
           '-o', 'test_files/temporary_outfile.xlsx']
    with pytest.raises(ValueError):
        merge_main(cli)

def test_nonexistent_file():
    cli = ['test_files/nonexistent_file.xlsx',
           '-o', 'test_files/temporary_outfile.xlsx']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        merge_main(cli)
    assert pytest_wrapped_e.type == SystemExit
    try:
        os.remove('test_files/temporary_outfile.xlsx')
    except OSError:
        pass