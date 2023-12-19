"""Module for the RemoteSubstitution substitution."""

from typing import Text

from ..descriptions import Machine
from ..launch_context import LaunchContext
from ..substitution import Substitution

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
        """Perform the substitution by returning the string itself."""
        pass