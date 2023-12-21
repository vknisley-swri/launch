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

def prepare(self, context: LaunchContext):
    """Prepare the action for execution."""
    self.__process_description.prepare(context, self)

    # store packed kwargs for all ProcessEvent based events
    self.__process_event_args = {
        'action': self,
        'name': self.__process_description.final_name,
        'cmd': self.__process_description.final_cmd,
        'cwd': self.__process_description.final_cwd,
        'env': self.__process_description.final_env,
        # pid is added to the dictionary in the connection_made() method of the protocol.
    }

    self.__respawn = cast(bool, perform_typed_substitution(context, self.__respawn, bool))

def execute(self, context: LaunchContext) -> Optional[List[LaunchDescriptionEntity]]:
    """
    Execute the action.

    This does the following:
    - register an event handler for the shutdown process event
    - register an event handler for the stdin event
    - configures logging for the IO process event
    - create a task for the coroutine that monitors the process
    """
    self.prepare(context)
    name = self.__process_description.final_name

    if self.__executed:
        raise RuntimeError(
            f"ExecuteLocal action '{name}': executed more than once: {self.describe()}"
        )
    self.__executed = True

    if context.is_shutdown:
        # If shutdown starts before execution can start, don't start execution.
        return None

    #TODO cached output?

    event_handlers = [
            EventHandler(
                matcher=lambda event: is_a_subclass(event, ShutdownProcess),
                entities=OpaqueFunction(function=self.__on_shutdown_process_event),
            ),
            OnProcessIO(
                target_action=self,
                on_stdin=self.__on_process_stdin,
                on_stdout=lambda event: on_output_method(
                    event, self.__stdout_buffer, self.__stdout_logger),
                on_stderr=lambda event: on_output_method(
                    event, self.__stderr_buffer, self.__stderr_logger),
            ),
            OnShutdown(
                on_shutdown=self.__on_shutdown,
            ),
            OnProcessExit(
                target_action=self,
                # TODO: This is also a little strange, OnProcessExit shouldn't ever be able to
                # take a None for the callable, but this seems to be the default case?
                on_exit=self.__on_exit,  # type: ignore
            ),
            OnProcessExit(
                target_action=self,
                on_exit=flush_buffers_method,
            ),
        ]
        for event_handler in event_handlers:
            context.register_event_handler(event_handler)

        try:
            self.__completed_future = context.asyncio_loop.create_future()
            self.__shutdown_future = context.asyncio_loop.create_future()
            self.__logger = launch.logging.get_logger(name)
            if not isinstance(self.__output, dict):
                self.__stdout_logger, self.__stderr_logger = \
                    launch.logging.get_output_loggers(
                            name, perform_substitutions(context, self.__output)
                            )
            else:
                self.__stdout_logger, self.__stderr_logger = \
                    launch.logging.get_output_loggers(name, self.__output)
            context.asyncio_loop.create_task(self.__execute_process(context))
        except Exception:
            for event_handler in event_handlers:
                context.unregister_event_handler(event_handler)
            raise
        return None

def get_asyncio_future(self) -> Optional[asyncio.Future]:
    """Return an asyncio Future, used to let the launch system know when we're done."""
    return self.__completed_future

def __cleanup(self):
    # Cancel any pending timers we started.
    if self.__sigterm_timer is not None:
        self.__sigterm_timer.cancel()
    if self.__sigkill_timer is not None:
        self.__sigkill_timer.cancel()
    # Close subprocess transport if any.
    if self._subprocess_transport is not None:
        self._subprocess_transport.close()
    # Signal that we're done to the launch system.
    self.__completed_future.set_result(None)

async def __execute_process(self, context: LaunchContext) -> None:
    process_event_args = self.__process_event_args
    if process_event_args is None:
        raise RuntimeError('process_event_args unexpectedly None')
    
    cmd = process_event_args['cmd']
    cwd = process_event_args['cwd']
    env = process_event_args['env']
    if self.__log_cmd:
        self.__logger.info("process details: cmd='{}', cwd='{}', custom_env?={}".format(
            ' '.join(filter(lambda part: part.strip(), cmd)),
            cwd,
            'True' if env is not None else 'False'
        ))

    # TODO take into account machine

    except Exception:
        self.__logger.error('exception occurred while executing process:\n{}'.format(
            traceback.format_exc()
        ))
        self.__cleanup()
        return
    
    # TODO get PID?

    if not context.is_shutdown\
            and self.__shutdown_future is not None\
            and not self.__shutdown_future.done()\
            and self.__respawn and \
            (self.__respawn_max_retries < 0 or
                self.__respawn_retries < self.__respawn_max_retries):
        # Increase the respawn_retries counter
        self.__respawn_retries += 1
        if self.__respawn_delay is not None and self.__respawn_delay > 0.0:
            # wait for a timeout(`self.__respawn_delay`) to respawn the process
            # and handle shutdown event with future(`self.__shutdown_future`)
            # to make sure `ros2 launch` exit in time
            await asyncio.wait(
                (self.__shutdown_future,),
                timeout=self.__respawn_delay
            )
        if not self.__shutdown_future.done():
            context.asyncio_loop.create_task(self.__execute_process(context))
            return
    self.__cleanup()