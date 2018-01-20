# -*- coding: utf-8 -*-

import drt

import unittest
import json
import pickle
from pyannotate_runtime import collect_types


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_text_file(self) -> None:
        transport = drt.LocalTransport()
        input = drt.SrcDest(src="tests/test.txt", dest="/tmp/test.txt")
        rsrc = drt.LocalFile(input.src)
        rdest = transport.copy(input)
        out = transport.diff(rsrc, rdest)
        print(pickle.dumps(out.dict()))
        print(json.dumps(out.dict(), indent=2))
        # assert "< three" in out.diff.stdout

    def _test_pyannotate(self):
        collect_types.init_types_collection()
        with collect_types.collect():
            self._test_text_file()
        collect_types.dump_stats('type_info.json')


if __name__ == '__main__':
    unittest.main()
