"""
Tool registry.

This module defines the tools available to the agent and exposes
them as a single list that can be passed to the language model.
"""

from .command_explainer import explain_shell_command
from .docker_log_analyzer import analyze_docker_logs
from .lucky_number_tool import lucky_number
from .tool import Tool


lucky_number_tool = Tool(
    name="lucky_number",
    description=(
        "Generates a lucky number based on the user's birth date "
        "and today's date."
    ),
    parameters={
        "type": "object",
        "properties": {
            "birth_date": {
                "type": "string",
                "description": (
                    "The user's birth date in DDMMYYYY format, "
                    "for example 31121993 for 31/12/1993."
                ),
            },
        },
        "required": ["birth_date"],
    },
    callback=lucky_number,
)


docker_log_analyzer_tool = Tool(
    name="analyze_docker_logs",
    description=(
        "Analyzes Docker container logs provided by the user "
        "and detects common DevOps problems."
    ),
    parameters={
        "type": "object",
        "properties": {
            "logs": {
                "type": "string",
                "description": (
                    "Docker logs copied by the user."
                ),
            },
        },
        "required": ["logs"],
        "additionalProperties": False,
    },
    callback=analyze_docker_logs,
)


command_explainer_tool = Tool(
    name="explain_shell_command",
    description=(
        "Explains a shell or DevOps command without executing it. "
        "Returns its purpose, arguments, command type, risk level "
        "and safety warnings."
    ),
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": (
                    "The complete shell command that should be explained."
                ),
            },
        },
        "required": ["command"],
        "additionalProperties": False,
    },
    callback=explain_shell_command,
)


# Tools exposed to the agent and language model.
tools = [
    lucky_number_tool,
    docker_log_analyzer_tool,
    command_explainer_tool,
]