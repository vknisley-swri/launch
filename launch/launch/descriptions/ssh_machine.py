# Copyright 2023 Southwest Research Institute, All Rights Reserved.
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
#
# DISTRIBUTION A. Approved for public release; distribution unlimited.
# OPSEC #4584.

from .machine import Machine

"""Module for a description of an SSH connection."""

class SshMachine(Machine):
    """
    Describes key elements of an ssh connection so that processes may be
    executed remotely.
    """

    def __init__(
        self, *,
        hostname: string = "",
        port: int = 22,
        ssh_key_path: string = "",
        passphrase: Optional[string] = None
    ) -> None:
        """
        Initialize an ssh connection description.

        :param hostname: A string with the IP address or hostname (if in /etc/hosts)
            of the remote host.
        :param port: The port number over which to make the ssh connection.
        :param ssh_key_path: Filepath to ssh private key.
        :param passphrase: Optional passphrase, if the private key requires one.
        """
        self.__hostname = hostname
        self.__port = port
        self.__user = user
        self.__password = password
        self.__priv_key_location = priv_key_location
        self.__ssh_opts = ssh_opts

    @property
    def host_ip(self):
        "Getter for host_ip."
        return self.__host_ip

    @property
    def port(self):
        "Getter for port."
        return self.__port

    @property
    def user(self):
        "Getter for user."
        return self.__user

    @property
    def password(self):
        "Getter for password."
        return self.__password

    @property
    def priv_key_location(self):
        "Getter for priv_key_location."
        return self.__priv_key_location

    @property
    def ssh_opts(self):
        "Getter for ssh_opts."
        return self.__ssh_opts