
class Ssh():
    def connect(self, passwd) -> None:
        transport = LocalTransport()
        args = ['-v', '-o', 'PreferredAuthentications=password', '-o',
                'PubkeyAuthentication=no', 'localhost', 'bash', '--norc']
        cmd = 'ssh'
        print(f'{cmd} {" ".join(args)}')
        self.proc = pexpect.spawn('ssh', args, timeout=60)
        print("wait for password:")
        self.proc.expect(b"password:")
        print("get password:")
        self.proc.send(passwd)
        self.proc.send("\n")
        print("sent password:")
        self.proc.expect("debug1: Sending command: bash")

    def run(self, command: str) -> Any:
        self.proc.send(b'{command}\n')
        print(f"type {type(self.proc)}")
        return self.proc.read()

    def close(self) -> None:
        self.proc.send(b'exit\n')
        self.proc.expect(pexpect.EOF)

    def kill(self) -> None:
        self.proc.kill(9)


