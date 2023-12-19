"""Module for the ExecuteRemoteProcess action."""

import asyncio
from typing import Callable
from typing import List
from typing import Optional
from typing import Text
from typing import Union

from ..action import Action
from ..descriptions import Executable
from ..descriptions import Machine
from ..events.process import ProcessExited
from ..launch_context import LaunchContext
from ..launch_description_entity import LaunchDescriptionEntity
from ..some_entities_type import SomeEntitiesType
from ..some_substitutions_type import SomeSubstitutionsType

class ExecuteRemoteProcess(Action):
    """
    Action that executes a process on a remote machine. This action is comparable to the ExecuteLocal
    action.
    """

    def __init__(
        self, *,
        process_description: Executable,
        machine: Machine,
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
    Construct an ExecuteRemoteProcess action.

    This action, once executed, emits events asynchronously when certain events related to the
    process occur.

    Handled events include:

    - launch.events.process.ShutdownProcess:

        - begins standard shutdown procedure for a running executable

    - launch.events.process.ProcessStdin:

        - passes the text provided by the event to the stdin of the process

    - launch.events.Shutdown:

        - same as ShutdownProcess
        
    Emitted events include:

    - launch.events.process.ProcessStarted:

        - emitted when the process starts

    - launch.events.process.ProcessExited:

        - emitted when the process exits
        - event contains return code

    - launch.events.process.ProcessStdout and launch.events.process.ProcessStderr:

        - emitted when the process produces data on either the stdout or stderr pipes
        - event contains the data from the pipe

    Note that output is just stored in this class and has to be properly
    implemented by the event handlers for the process's ProcessIO events.
    
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
    super().__init__(**kwargs)
    self.__process_description = process_description
    self.__machine = machine
    self.__prefix = prefix
    # Note: we need to use a temporary here so that we don't assign values with different types
    # to the same variable
    tmp_output: SomeSubstitutionsType = os.environ.get(
            'OVERRIDE_LAUNCH_PROCESS_OUTPUT', output
            )
    self.__output: Union[dict, List[Substitution]]
    if not isinstance(tmp_output, dict):
        self.__output = normalize_to_list_of_substitutions(tmp_output)
    else:
        self.__output = tmp_output
    self.__output_format = output_format

    self.__log_cmd = log_cmd
    self.__on_exit = on_exit

    self.__process_event_args = None  # type: Optional[Dict[Text, Any]]
    self._subprocess_protocol = None  # type: Optional[Any]
    self._subprocess_transport = None
    self.__completed_future = None  # type: Optional[asyncio.Future]
    self.__shutdown_future = None  # type: Optional[asyncio.Future]

    self.__executed = False

@property
def process_description(self):
    """Getter for process_description."""
    return self.__process_description

@property
def machine(self):
    """Getter for machine."""
    return self.__machine

@property
def output(self):
    """Getter for output."""
    return self.__output

@property
def process_details(self):
    """Getter for the process details, e.g. name, pid, cmd, etc., or None if not started."""
    return self.__process_event_args

def get_sub_entities(self):
    if isinstance(self.__on_exit, list):
        return self.__on_exit
    return []

def execute(self, context: LaunchContext) -> Optional[List[LaunchDescriptionEntity]]:
    """
    Execute the action.

    This does the following:
    - register an event handler for the shutdown process event
    - register an event handler for the stdin event
    - configures logging for the IO process event
    - create a task for the coroutine that monitors the process
    """
    pass

def get_asyncio_future(self) -> Optional[asyncio.Future]:
    """Return an asyncio Future, used to let the launch system know when we're done."""
    return self.__completed_future