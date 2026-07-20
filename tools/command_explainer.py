import re
import shlex
from typing import Any


DANGEROUS_PATTERNS = [
    {
        "pattern": r"\brm\s+.*(?:-rf|-fr)\b",
        "risk": "critical",
        "warning": (
            "Recursively and forcibly deletes files or directories. "
            "Deleted data may not be recoverable."
        )
    },
    {
        "pattern": r"\bmkfs(?:\.\w+)?\b",
        "risk": "critical",
        "warning": (
            "Creates a new filesystem and may destroy existing data "
            "on the selected device."
        )
    },
    {
        "pattern": r"\bdd\s+.*\bof=/dev/",
        "risk": "critical",
        "warning": (
            "Writes raw data directly to a device and may overwrite "
            "the disk."
        )
    },
    {
        "pattern": r"\bshutdown\b|\breboot\b|\bpoweroff\b",
        "risk": "high",
        "warning": "Stops or restarts the operating system."
    },
    {
        "pattern": r"\bsystemctl\s+(restart|stop|disable|mask)\b",
        "risk": "high",
        "warning": (
            "Changes the state or availability of a system service."
        )
    },
    {
        "pattern": r"\bdocker\s+(rm|rmi|prune|stop|restart|kill)\b",
        "risk": "high",
        "warning": (
            "Stops, removes or modifies Docker resources."
        )
    },
    {
        "pattern": r"\bchmod\s+(777|666)\b",
        "risk": "high",
        "warning": (
            "Grants broad permissions and may create a security risk."
        )
    },
    {
        "pattern": r"\bchown\b",
        "risk": "medium",
        "warning": "Changes file or directory ownership."
    },
    {
        "pattern": r"\bsudo\b",
        "risk": "medium",
        "warning": "Runs the command with elevated privileges."
    }
]


COMMAND_DESCRIPTIONS = {
    "docker": "Manages Docker containers, images, volumes and networks.",
    "systemctl": "Manages systemd services and system state.",
    "journalctl": "Reads logs collected by systemd.",
    "ps": "Displays running processes.",
    "grep": "Searches text using a pattern.",
    "find": "Searches for files and directories.",
    "ls": "Lists directory contents.",
    "cd": "Changes the current working directory.",
    "cp": "Copies files or directories.",
    "mv": "Moves or renames files and directories.",
    "rm": "Deletes files or directories.",
    "chmod": "Changes file permissions.",
    "chown": "Changes file ownership.",
    "curl": "Sends HTTP or other network requests.",
    "wget": "Downloads files from a URL.",
    "ping": "Tests network connectivity to a host.",
    "ss": "Displays network sockets and listening ports.",
    "df": "Displays filesystem disk usage.",
    "du": "Displays file or directory disk usage.",
    "free": "Displays system memory usage.",
    "tar": "Creates or extracts archive files.",
    "git": "Manages Git repositories.",
    "python": "Runs the Python interpreter or a Python script.",
    "python3": "Runs the Python 3 interpreter or a script.",
    "pip": "Installs and manages Python packages.",
    "pip3": "Installs and manages Python 3 packages.",
    "uvicorn": "Runs an ASGI web application server.",
    "sudo": "Runs another command with elevated privileges."
}


def _detect_risk(command: str) -> tuple[str, list[str]]:
    risk_order = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3
    }

    highest_risk = "low"
    warnings = []

    for item in DANGEROUS_PATTERNS:
        if re.search(item["pattern"], command, re.IGNORECASE):
            warnings.append(item["warning"])

            if risk_order[item["risk"]] > risk_order[highest_risk]:
                highest_risk = item["risk"]

    return highest_risk, warnings


def _classify_command(command: str) -> str:
    modification_patterns = [
        r"\brm\b",
        r"\bmv\b",
        r"\bcp\b",
        r"\bchmod\b",
        r"\bchown\b",
        r"\bmkdir\b",
        r"\btouch\b",
        r"\bsystemctl\s+(restart|stop|start|enable|disable)\b",
        r"\bdocker\s+(rm|rmi|stop|restart|kill|prune)\b",
        r"\bapt\s+(install|remove|upgrade)\b",
        r"\bpip\d*\s+install\b"
    ]

    for pattern in modification_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return "system modification"

    return "diagnostic or read-only"


def explain_shell_command(command: str) -> dict[str, Any]:
    """Explain a shell command without executing it."""

    if not command or not command.strip():
        return {
            "status": "error",
            "message": "The command cannot be empty."
        }

    if len(command) > 5_000:
        return {
            "status": "error",
            "message": "The command is too long."
        }

    command = command.strip()

    try:
        parts = shlex.split(command)
    except ValueError as error:
        return {
            "status": "error",
            "message": f"Invalid shell syntax: {error}"
        }

    if not parts:
        return {
            "status": "error",
            "message": "No command was provided."
        }

    base_command = parts[0]

    if base_command == "sudo" and len(parts) > 1:
        analyzed_command = parts[1]
    else:
        analyzed_command = base_command

    description = COMMAND_DESCRIPTIONS.get(
        analyzed_command,
        "No predefined description is available for this command."
    )

    risk, warnings = _detect_risk(command)
    command_type = _classify_command(command)

    arguments = parts[1:]

    return {
        "status": "success",
        "command": command,
        "base_command": analyzed_command,
        "description": description,
        "type": command_type,
        "risk": risk,
        "arguments": arguments,
        "warnings": warnings,
        "recommendation": (
            "Review placeholders, paths and target resources before running "
            "the command. Use a test environment for risky operations."
            if risk in {"high", "critical"}
            else "Verify the command arguments before running it."
        )
    }