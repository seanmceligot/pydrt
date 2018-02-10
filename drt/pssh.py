import drt
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
from drt._secrets import id_rsa_passwd
import io
import pdb


def shell(client: paramiko.SSHClient, cmdargs: List[str]) -> drt.ExecResult:
    out = io.StringIO() 
    err = io.StringIO()

    chan = client.get_transport().open_session()
    chan.setblocking(0)
    chan.exec_command(" ".join(cmdargs))
    #pdb.set_trace();
    while not chan.exit_status_ready():
        while chan.recv_ready():
            r = chan.recv(1024)
            print(f"type r {type(r)}")
            out.write(r.decode('utf-8'))
            print(f"out now {out.getvalue()}")
        while chan.recv_stderr_ready():
            r=chan.recv_stderr(1024)
            print(f"type r {type(r)}")
            err.write(r.decode('utf-8'))
    retcode = chan.recv_exit_status()
    while chan.recv_ready():
        r = chan.recv(1024)
        print(f"type r {type(r)}")
        out.write(r.decode('utf-8'))
        print(f"out now {out.getvalue()}")
    while chan.recv_stderr_ready():
        r=chan.recv_stderr(1024)
        print(f"type r {type(r)}")
        err.write(r.decode('utf-8'))
    chan.close()
    args = ' '.join(cmdargs)
    stdout = out.getvalue()
    stderr = err.getvalue()
    return drt.ExecResult(args=args, returncode=retcode, stdout= stdout, stderr=stderr)

class PSsh():
    client: paramiko.SSHClient
    
    def connect(self) -> None:
        transport = drt.LocalTransport()
        priv = Path.home() / ".ssh" / "id_rsa"
        k = paramiko.RSAKey.from_private_key_file(priv, id_rsa_passwd)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("connecting")
        self.client.connect(hostname=transport.hostname(), username="sean", pkey=k)
        print("connected")

    def run(self, command: str, args: List[str]) -> drt.ExecResult:
        cmdargs: List[str] = list(map(str, [command] + args))
        print("run", " ".join(cmdargs))
        return shell(self.client, cmdargs); 

    def close(self) -> None:
        self.client.close()

    def kill(self) -> None:
        self.client.close()
