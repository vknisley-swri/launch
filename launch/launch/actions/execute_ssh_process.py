"""Module for the ExecuteSshProcess action."""

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
    """
    self.__ssh_connection = None
    super().__init__(
        process_description, machine,
        prefix, output, output_format,
        log_cmd, on_exit)
    
    def open_ssh_connection():
        # Object for interacting with the SSH connection.
        #TODO(vknisley) should operate on self.__machine and return an SSHConnection object.
        pass
    
    def exec_remote_command():
        # Executes a command on the remote machine.
        pass