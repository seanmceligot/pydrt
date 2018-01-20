import os
import subprocess
import shutil
import enum

from typing import List, Iterable, Tuple
from pydantic import BaseModel
from typing import Union


class LocalFile():
    def __init__(self, path):
        self.path = path


class RemoteFile():
    def __init__(self, path):
        # type: (str) -> None
        self.path = path


class Transport():
    pass


class SrcDest(BaseModel):
    src: str
    dest: str


class ExecResult(BaseModel):
    args: str
    returncode: int
    stderr: str
    stdout: str


class Action(enum.IntFlag):
    Done = 1
    Patch = 2
    Create = 3


class DiffResult(BaseModel):
    result: Action
    diff: ExecResult


class LocalTransport(Transport):

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
        print("type stdout", type(r['stdout']))
        print("stdout", r['stdout'])
        print("dir stderr", type(r['stderr']))
        print("stderr", r['stderr'])
        # print("r", json.dumps(r, indent=2))
        return ExecResult(**r)

    def to_remote_file(self, lfile) -> RemoteFile:
        return RemoteFile(lfile.path)

    def copy(self, srcdest: SrcDest) -> RemoteFile:
        shutil.copyfile(srcdest.src, srcdest.dest)
        return RemoteFile(srcdest.dest)

    def diff(self, r1, r2) -> DiffResult:
        """ result=diff: patch: text"""
        """ result=create: """

        if not os.path.exists(r2.path):
            return DiffResult(result="create")
        r = self.run("diff", [r1.path, r2.path])
        if r.returncode == 0:
            return DiffResult(result=Action.Done, diff=r)
        else:
            return DiffResult(result=Action.Patch, diff=r)
