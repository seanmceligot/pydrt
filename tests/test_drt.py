# -*- coding: utf-8 -*-

import drt

from drt import LocalFile
from drt import pssh
import unittest
import json
import pickle
from pyannotate_runtime import collect_types
import subprocess
import pexpect
from pexpect.popen_spawn import PopenSpawn
from drt._secrets import id_rsa_passwd
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional, Any, Iterator
from contextlib import contextmanager


@contextmanager
def psshconnection() -> Iterator[pssh.PsshTransport]:
    priv = Path.home() / ".ssh" / "id_rsa"
    ssh = pssh.PsshTransport(
        "localhost", drt.KeyPair(priv, id_rsa_passwd, "sean"))
    print("ssh id:", json.dumps(ssh.id(), indent=2))
    ssh.connect()
    try:
        yield ssh
        ssh.close()
    finally:
        ssh.kill()


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_create(self) -> None:
        self.create(drt.LocalTransport())
        with psshconnection() as ssh:
            self.create(ssh)

    def create(self, transport: drt.Transport) -> None:
        input = drt.SrcDest(src=LocalFile(
            path="/tmp/create_test.txt"), dest=LocalFile(path="/tmp/does_not_exist.txt"))
        out = transport.diff(input.src, input.dest)
        print(json.dumps(out, indent=2))
        assert out.result == drt.Action.Create

    def test_path(self) -> None:
        self.path(drt.LocalTransport())
        with psshconnection() as ssh:
            self.path(ssh)

    def path(self, transport: drt.Transport) -> None:
        input = drt.SrcDest(src=LocalFile(
            path="/tmp/create_test.txt"), dest=LocalFile(path="/tmp/test.txt"))
        transport.createfile(drt.Text(text="one\ntwo"), input.src)
        transport.createfile(drt.Text(text="one\ntwothree"), input.dest)
        out = transport.diff(input.src, input.dest)
        print(json.dumps(out, indent=2))
        assert out.result == drt.Action.Patch

    def test_text_file(self) -> None:
        transport = drt.LocalTransport()
        input = drt.SrcDest(src=LocalFile(path="/tmp/same_test.txt"),
                            dest=LocalFile(path="/tmp/test.txt"))
        transport.createfile(drt.Text(text="one\ntwothree"), input.src)
        transport.createfile(drt.Text(text="one\ntwothree"), input.dest)
        out = transport.diff(input.src, input.dest)
        print(json.dumps(out, indent=2))
        assert out.result == drt.Action.Done

    def test_multi(self) -> None:
        t1 = drt.LocalTransport()
        with psshconnection() as t2:
            fname1 = "/etc/syslog-ng/syslog-ng.conf.pacnew"
            fname2 = "/etc/syslog-ng/syslog-ng.conf.pacsave"
#    def _test_pyannotate(self):
#        collect_types.init_types_collection()
#        with collect_types.collect():
#            self._test_text_file()
#        collect_types.dump_stats('type_info.json')

    def test_ssh(self) -> None:
        with psshconnection() as ssh:
            result = ssh.run("echo", ["hello", "PsshTransport"])
            print(json.dumps(result, indent=2))

#     def expect(self):
#         index = p.expect(['good', 'bad', pexpect.EOF, pexpect.TIMEOUT])
#         if index == 0:
#             do_something()
#         elif index == 1:
#             do_something_else()
#         elif index == 2:
#             do_some_other_thing()
#         elif index == 3:
#             do_something_completely_different()


if __name__ == '__main__':
    unittest.main()
