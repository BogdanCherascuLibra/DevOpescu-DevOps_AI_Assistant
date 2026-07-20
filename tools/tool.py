"""
Tool definition model.

This module defines the structure used to register callable tools
that can be exposed to the language model.
"""


class Tool:
    """Store the metadata and callback associated with an agent tool."""

    def __init__(
        self,
        name,
        description,
        parameters,
        callback,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.callback = callback