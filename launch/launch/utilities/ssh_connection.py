# Copyright 2024 Southwest Research Institute, All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module for SSHConnection utility."""

from paramiko.client import SSHClient
from paramiko.pkey import PKey

from ..descriptions import SshMachine

class SSHConnection:
    """
    Object used to send or receive data with a remote process over SSH.
    """

    def __init__(
        self, *,
        machine: SshMachine
    ):
        """
        Instantiate SSH connection. This is effectively a wrapper around paramiko's
        SSH client.
        
        :param machine: An SshMachine object with the appropriate connection details.
        """
        # Create a client
        self.__machine = machine
        self.__connection = SSHClient()

        self.open_connection()
    
    def open_connection(self):
        """Set up and return an open SSH connection."""

        result = self.__connection.connect(
            hostname=self.__machine.hostname(),
            port=self.__machine.port(),
            key_filename=self.__machine.ssh_key(),
            passphrase=self.__machine.passphrase(),
            look_for_keys=False
        )
    
    def exec_on_connection(self, cmd: str, env: dict = None):
        """Execute a command via an SSH connection"""
        self.__connection.exec_command(command=cmd, environment=env)
    
    def close_connection(self):
        """Close an SSH connection."""
        self.__connection.close()
    
    @property
    def connection(self):
        "Getter for connection"
        return self.__connection
    