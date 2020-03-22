import unittest

from confluence.io import read
from confluence.subcommands.merge import merge, MergeMethod

import logging
_logger = logging.getLogger(__name__)


class TestReadMethods(unittest.TestCase):
    def test_read_excel(self):
        # TODO: write tests for Quality Made-formatted reader
        pass


    def test_read_feature_log(self):
        # TODO: write tests for Quality Made build logs for features.
        result = None
        ifiles = ["data/"
                  "Feature 4/"
                  "Weld Logs Feature 4/"
                  f"N00014-004-00{i}.doc" for i in range(1, 6)]

        for fname in ifiles:
            df = read(fname, index_col=0)
            if result is None:
                result = df
            else:
                try:
                    result = merge(result, df, resolution=MergeMethod.ABORT)
                except:
                    print(result == df)
        print(result)
        pass


if __name__ == '__main__':
    unittest.main()