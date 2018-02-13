import drt
import os
import subprocess
import shutil
import enum

from typing import List, Set, Dict, Tuple, Optional, Any, TypeVar
from typing import NamedTuple

from typing import Union

import subprocess
import pexpect
from pathlib import Path

import paramiko
from drt._secrets import id_rsa_passwd
import io
import pdb


def shell(client: paramiko.SSHClient, cmdargs: List[str]) -> drt.ExecResult:
    out = io.StringIO()
    err = io.StringIO()

    chan = client.get_transport().open_session()
    chan.setblocking(0)
    chan.exec_command(" ".join(cmdargs))
    # pdb.set_trace();
    while not chan.exit_status_ready():
        while chan.recv_ready():
            r = chan.recv(1024)
            # print(f"type r {type(r)}")
            out.write(r.decode('utf-8'))
            # print(f"out now {out.getvalue()}")
        while chan.recv_stderr_ready():
            r = chan.recv_stderr(1024)
            # print(f"type r {type(r)}")
            err.write(r.decode('utf-8'))
    retcode = chan.recv_exit_status()
    while chan.recv_ready():
        r = chan.recv(1024)
        # print(f"type r {type(r)}")
        out.write(r.decode('utf-8'))
        # print(f"out now {out.getvalue()}")
    while chan.recv_stderr_ready():
        r = chan.recv_stderr(1024)
        # print(f"type r {type(r)}")
        err.write(r.decode('utf-8'))
    chan.close()
    args = ' '.join(cmdargs)
    stdout = out.getvalue()
    stderr = err.getvalue()
    return drt.ExecResult(args=args, returncode=retcode, stdout=stdout, stderr=stderr)


class PsshTransport(drt.Transport):
    # client: paramiko.SSHClient
    # hostname: str
    # cred: drt.Credentials

    def __init__(self: 'PsshTransport', hostname: str, cred: drt.KeyPair) -> None:
        self.hostname = hostname
        self.cred = cred
        self.client = paramiko.SSHClient()

    def id(self) -> Tuple:
        return (type(self).__name__, self.hostname, self.cred.id())

    def get_hostname(self) -> str:
        return self.hostname

    def connect(self) -> None:
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("connecting")
        self.client.connect(hostname=self.hostname,
                            username=self.cred.username, pkey=self.cred.key)
        print("connected")

    def __enter__(self) -> 'PsshTransport':
        self.connect()
        return self

    def __exit__(self) -> None:
        self.close()

    def run(self, command: str, args: List[str]) -> drt.ExecResult:
        cmdargs: List[str] = list(map(str, [command] + args))
        print("run", " ".join(cmdargs))
        return shell(self.client, cmdargs)

    def close(self) -> None:
        if self.client:
            self.client.close()
        self.client = None

    def kill(self) -> None:
        self.close()

    def to_remote_file(self, lfile: drt.File) -> drt.RemoteFile:
        return drt.RemoteFile(path=lfile.path)

    def readfile(self, path: drt.File) -> drt.Text:
        with self.client.open_sftp() as sftp:
            with sftp.file(path, "r", -1) as f:
                data = f.read()
                return drt.Text(text=data)

    def createfile(self, text: drt.Text, dest: drt.LocalFile) -> None:
        print(f'createfile {text.text}')
        with self.client.open_sftp() as sftp:
            with sftp.file(dest.path, "w", -1) as f:
                f.write(text.text)

    def copy(self, srcdest: drt.SrcDest) -> drt.LocalFile:
        shutil.copyfile(srcdest.src.path, srcdest.dest.path)
        return srcdest.dest

    def diff(self, r1: drt.File, r2: drt.File) -> drt.DiffResult:
        """ result=diff: patch: text"""
        """ result=create: """

        if not os.path.exists(r2.path):
            return drt.DiffResult(result=drt.Action.Create, diff=None)
        r = self.run("diff", [r1.path, r2.path])
        if r.returncode == 0:
            return drt.DiffResult(result=drt.Action.Done, diff=r)
        else:
            return drt.DiffResult(result=drt.Action.Patch, diff=r)
