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

"""Module for the RemoteSubstitution substitution."""

from typing import Text

from ..descriptions import Machine
from ..launch_context import LaunchContext
from ..substitution import Substitution
from ..utilities import SSHConnection

class RemoteSubstitution(Substitution):
    """
    Substitution that uses a connection to a machine to run a command remotely.
    The result is returned as a string.
    """

    def __init__(self, *, command: Text, machine: Machine):
        """Create RemoteSubstitution."""
        super().__init__()

        if not isinstance(command, Text):
            raise TypeError(
                "RemoteSubstitution expected Text object got '{}' instead.".format(type(command))
            )

        self.__command = command
        self.__machine = machine
    
    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return "'{}'".format(self.__command)

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution on a remote machine and return it as a string."""
        #TODO: Get this to not overlap with execute_ssh_process
        connection = SSHConnection(self.__machine)
        result_tuple = connection.exec_on_connection(self.__command)
        result = "StdIn: \n" + str(result_tuple[0]) + "\nStdOut: \n" + str(result_tuple[1]) + "\nStdErr: \n" + str(result_tuple[2])
        return result