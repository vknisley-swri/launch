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

from typing import Optional

from .machine import Machine

"""Module for a description of an SSH machine."""

class SshMachine(Machine):
    """
    Describes key elements of an ssh connection so that processes may be
    executed remotely.
    """

    def __init__(
        self, *,
        hostname: str,
        port: int = 22,
        ssh_key: str,
        passphrase: Optional[str] = None
    ) -> None:
        """
        Initialize an ssh connection description. This class presupposes that the SSH connection
        will be established using keys rather than a password.

        :param hostname: A string with the IP address or hostname (if in /etc/hosts)
            of the remote host.
        :param port: The port number over which to make the ssh connection.
        :param ssh_key: Filepath to ssh private key.
        :param passphrase: Optional passphrase, if the private key requires one.
        """
        self.__hostname = hostname
        self.__port = port
        self.__user = user
        self.__ssh_key = ssh_key
        self.__passphrase = passphrase


    @property
    def hostname(self):
        "Getter for hostname."
        return self.__hostname

    @property
    def port(self):
        "Getter for port."
        return self.__port

    @property
    def ssh_key(self):
        "Getter for ssh_key."
        return self.__ssh_key

    @property
    def passphrase(self):
        "Getter for passphrase"
        return self.__passphrase