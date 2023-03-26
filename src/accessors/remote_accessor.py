import logging
import os

import paramiko
from paramiko import SSHClient
from scp import SCPClient

logger = logging.getLogger()


class RemoteAccessor:
    def __init__(self, address, private_key_path, ):
        self.address = address
        # self.private_key_path = private_key_path
        self.key = paramiko.RSAKey.from_private_key_file(private_key_path)

    def _create_file_locally(self, file, local_path: str):
        with open(local_path, "wb") as f:
            f.write(file.getbuffer())

    def _remove_file_locally(self, local_path: str):
        os.remove(local_path)

    def push_file_to_remote(self, file, remote_path):
        logger.info("pushing file")
        if self.address in ("127.0.0.1", "localhost"):
            return self._create_file_locally(file, remote_path)

        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.address, username="root", pkey=self.key)

            with SCPClient(ssh.get_transport()) as scp:
                scp.putfo(file, remote_path)

    def remove_file_from_remote(self, remote_path):
        logger.info("removing dockercompose file")
        if self.address in ("127.0.0.1", "localhost"):
            return self._remove_file_locally(remote_path)

        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.get_host_keys().add(self.address, "ssh-rsa", self.key)
            ssh.connect(self.address, username="root")
            ssh.exec_command(f"rm {remote_path}")
