# -*- coding: utf-8 -*-

import drt

from drt import LocalFile
import unittest
import json
import pickle
from pyannotate_runtime import collect_types


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_create(self) -> None:
        transport = drt.LocalTransport()
        input = drt.SrcDest(src=LocalFile(
            path="/tmp/create_test.txt"), dest=LocalFile(path="/tmp/does_not_exist.txt"))
        out = transport.diff(input.src, input.dest)
        print(json.dumps(out.dict(), indent=2))
        assert out.result == drt.Action.Create

    def test_path(self) -> None:
        transport = drt.LocalTransport()
        input = drt.SrcDest(src=LocalFile(
            path="/tmp/create_test.txt"), dest=LocalFile(path="/tmp/test.txt"))
        transport.createfile(drt.Text(text="one\ntwo"), input.src)
        transport.createfile(drt.Text(text="one\ntwothree"), input.dest)
        out = transport.diff(input.src, input.dest)
        print(json.dumps(out.dict(), indent=2))
        assert out.result == drt.Action.Patch

    def test_text_file(self) -> None:
        transport = drt.LocalTransport()
        input = drt.SrcDest(src=LocalFile(path="/tmp/same_test.txt"),
                            dest=LocalFile(path="/tmp/test.txt"))
        transport.createfile(drt.Text(text="one\ntwothree"), input.src)
        transport.createfile(drt.Text(text="one\ntwothree"), input.dest)
        out = transport.diff(input.src, input.dest)
        print(json.dumps(out.dict(), indent=2))
        assert out.result == drt.Action.Done

    def _test_pyannotate(self):
        collect_types.init_types_collection()
        with collect_types.collect():
            self._test_text_file()
        collect_types.dump_stats('type_info.json')


if __name__ == '__main__':
    unittest.main()
