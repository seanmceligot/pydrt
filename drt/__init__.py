import os
import subprocess
import shutil
import enum

from typing import List, Set, Dict, Tuple, Optional, Any
from typing import NamedTuple

from typing import Union

import subprocess
import pexpect
from pathlib import Path

import paramiko
from abc import ABCMeta, abstractmethod


class File(NamedTuple):
    path: str


class RemoteFile(File):
    pass


class LocalFile(File):
    pass


class Text(NamedTuple):
    text: str


class SrcDest(NamedTuple):
    src: LocalFile
    dest: LocalFile


class ExecResult(NamedTuple):
    args: str
    returncode: int
    stderr: str
    stdout: str


class Action(enum.IntFlag):
    Done = 1
    Patch = 2
    Create = 3


class DiffResult(NamedTuple):
    result: Action
    diff: Optional[ExecResult]


class Credentials(metaclass=ABCMeta):
    @abstractmethod
    def get_username(self) -> str:
        pass


class KeyPair(Credentials):
    key: paramiko.RSAKey
    username: str

    def __init__(self, priv: Path, id_rsa_passwd: str, username: str) -> None:
        self.key = paramiko.RSAKey.from_private_key_file(priv, id_rsa_passwd)
        self.username = username

    def get_username(self) -> str:
        return self.username


class UserNamePassword(Credentials):
    username: str
    password: str

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password


class Transport(metaclass=ABCMeta):

    @abstractmethod
    def get_hostname(self) -> str:
        pass

    @abstractmethod
    def run(self, command: str, args: List[str]) -> ExecResult:
        pass

    @abstractmethod
    def to_remote_file(self, lfile: File) -> RemoteFile:
        pass

    @abstractmethod
    def readfile(self, path: File) -> Text:
        pass

    @abstractmethod
    def createfile(self, text: Text, dest: LocalFile) -> None:
        pass

    @abstractmethod
    def copy(self, srcdest: SrcDest) -> LocalFile:
        pass

    @abstractmethod
    def diff(self, r1: File, r2: File) -> DiffResult:
        pass


class LocalTransport(Transport):
    def get_hostname(self) -> str:
        return "localhost"

    def run(self, command: str, args: List[str]) -> ExecResult:
        cmdargs: List[str] = list(map(str, [command] + args))
        print("run", " ".join(cmdargs))
        proc = subprocess.Popen(cmdargs,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(timeout=500)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        # print("out", dir(out))
        outs = outs.decode('utf-8')
        errs = errs.decode('utf-8')
        r = {'args': " ".join(args), 'returncode': proc.returncode,
             'stderr': errs, 'stdout': outs}
        print("stdout", r['stdout'])
        print("stderr", r['stderr'])
        # print("r", json.dumps(r, indent=2))
        return ExecResult(**r)

    def to_remote_file(self, lfile: File) -> RemoteFile:
        return RemoteFile(path=lfile.path)

    def readfile(self, path: File) -> Text:
        with open(path.path, "r") as f:
            return Text(text=f.read())

    def createfile(self, text: Text, dest: LocalFile) -> None:
        with open(dest.path, "w") as f:
            print(text.text, file=f)

    def copy(self, srcdest: SrcDest) -> LocalFile:
        shutil.copyfile(srcdest.src.path, srcdest.dest.path)
        return srcdest.dest

    def diff(self, r1: File, r2: File) -> DiffResult:
        """ result=diff: patch: text"""
        """ result=create: """

        if not os.path.exists(r2.path):
            return DiffResult(result=Action.Create, diff=None)
        r = self.run("diff", [r1.path, r2.path])
        if r.returncode == 0:
            return DiffResult(result=Action.Done, diff=r)
        else:
            return DiffResult(result=Action.Patch, diff=r)
