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

"""Module for the ExecuteSshProcess action."""

import paramiko

from .execute_remote_process import ExecuteRemoteProcess


class ExecuteSshProcess(ExecuteRemoteProcess):
    """
    Action that executes a process on a remote machine via an SSH connection.
    """
    def __init__(
        self, *,
        process_description: Executable,
        machine: SshMachine,
        prefix: List[SomeSubstitutionsType],
        output: SomeSubstitutionsType = 'log',
        output_format: Text = '[{this.process_description.final_name}] {line}',
        log_cmd: bool = False,
        on_exit: Optional[Union[
            SomeEntitiesType,
            Callable[[ProcessExited, LaunchContext], Optional[SomeEntitiesType]]
        ]] = None,
    **kwargs) -> None:
    """
    Construct an ExecuteSshProcess action. This action inherits from ExecuteRemoteProcess.

    :param: process_description the `launch.descriptions.Executable` to execute
            as a local process
    :param: machine an object defining information required to connect to the remote host
    :param: prefix a set of commands/arguments to preceed the cmd, used for things
        like gdb/valgrind and defaults to the LaunchConfiguration called launch-prefix
    :param: output configuration for process output logging. Defaults to 'log'
        i.e. log both stdout and stderr to launch main log file and stderr to
        the screen.
        Overridden externally by the OVERRIDE_LAUNCH_PROCESS_OUTPUT envvar value.
        See `launch.logging.get_output_loggers()` documentation for further
        reference on all available options.
    :param: output_format for logging each output line, supporting `str.format()`
        substitutions with the following keys in scope: `line` to reference the raw
        output line and `this` to reference this action instance.
    :param: log_cmd if True, prints the final cmd before executing the
        process, which is useful for debugging when substitutions are
        involved.
    :param: on_exit list of actions to execute upon process exit.
    """
    super().__init__(
        process_description, machine,
        prefix, output, output_format,
        log_cmd, on_exit)

    def open_ssh_connection():
        # Object for interacting with the SSH connection.
        return SSHConnection(self.__machine)
    
    def exec_remote_command():
        # Executes a command on the remote machine.
        ssh_connection = self.open_ssh_connection()
        # Need to eventually call execute() from parent class, OR, is execute meant to be overridden?
        # Or, will eventually need to use remote substitution
        pass