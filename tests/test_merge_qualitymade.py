import pytest
from functools import reduce, partial
from glob import glob
from confluence.io import read
from confluence.subcommands.merge import merge, MergeMethod

import logging
_logger = logging.getLogger(__name__)


@pytest.fixture
def old_log():
    return read("data/Feature 4/LHW-build.xlsx")['build'].set_index("Sample Name")


@pytest.fixture
def merged_features():
    logs = [read(log).set_index("Sample Name")
            for log
            in sorted(glob('data/Feature 4/Weld Logs Feature 4/*.doc'))]
    return reduce(partial(merge, resolution=MergeMethod.SECOND), logs)


def test_merge_qualitymade_feature_logs(merged_features):
    # TODO: write tests to check that Quality Made feature logs merge properly.
    # result = merged_features
    # # check result
    # assert result is good
    pass


def test_merge_qualitymade_update(old_log, merged_features):
    # TODO: write tests to check that Quality Made Feature logs and the
    # TODO: current metadata spreadsheet merge cleanly.
    # init = old_log
    # added = merged_features
    # result = merge(init, added)
    # assert result is good
    pass
