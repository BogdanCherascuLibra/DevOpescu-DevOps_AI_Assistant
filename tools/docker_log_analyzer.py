"""
Docker log analysis utilities.

This module analyzes user-provided Docker logs using predefined
error patterns and returns probable causes, confidence levels,
and recommended diagnostic actions.
"""

import re
from typing import Any


# Known application and container error patterns.
ERROR_PATTERNS = [
    {
        "category": "Missing dependency",
        "pattern": (
            r"(ModuleNotFoundError|ImportError|cannot find module|"
            r"package .* not found)"
        ),
        "probable_cause": (
            "A required dependency is missing from the container image."
        ),
        "recommendation": (
            "Check requirements.txt, package.json or the image build steps, "
            "then rebuild the Docker image."
        ),
        "confidence": "high",
    },
    {
        "category": "Permission problem",
        "pattern": (
            r"(permission denied|operation not permitted|EACCES)"
        ),
        "probable_cause": (
            "The container process does not have permission to access "
            "a file, directory, port or mounted volume."
        ),
        "recommendation": (
            "Check file ownership, permissions, the container user "
            "and mounted volume permissions."
        ),
        "confidence": "high",
    },
    {
        "category": "Port conflict",
        "pattern": (
            r"(address already in use|port .* already allocated|"
            r"EADDRINUSE)"
        ),
        "probable_cause": (
            "The requested port is already used by another process "
            "or container."
        ),
        "recommendation": (
            "Check port mappings and verify which process or container "
            "already uses the port."
        ),
        "confidence": "high",
    },
    {
        "category": "Connection failure",
        "pattern": (
            r"(connection refused|ECONNREFUSED|could not connect|"
            r"connection timed out)"
        ),
        "probable_cause": (
            "The container cannot connect to a required service."
        ),
        "recommendation": (
            "Check the target hostname, port, Docker network, service status "
            "and startup order."
        ),
        "confidence": "high",
    },
    {
        "category": "DNS resolution failure",
        "pattern": (
            r"(temporary failure in name resolution|"
            r"name or service not known|ENOTFOUND)"
        ),
        "probable_cause": (
            "The container cannot resolve a hostname."
        ),
        "recommendation": (
            "Check the service name, Docker network configuration "
            "and DNS settings."
        ),
        "confidence": "high",
    },
    {
        "category": "Missing file",
        "pattern": (
            r"(no such file or directory|FileNotFoundError|ENOENT)"
        ),
        "probable_cause": (
            "A required file or directory is missing inside the container."
        ),
        "recommendation": (
            "Check COPY instructions, WORKDIR, mounted volumes "
            "and file paths."
        ),
        "confidence": "high",
    },
    {
        "category": "Missing environment variable",
        "pattern": (
            r"(environment variable .* not set|"
            r"missing environment variable|KeyError:)"
        ),
        "probable_cause": (
            "A required environment variable may be missing."
        ),
        "recommendation": (
            "Check docker-compose.yml, the docker run command "
            "and the environment file."
        ),
        "confidence": "medium",
    },
    {
        "category": "Out of memory",
        "pattern": (
            r"(out of memory|OOMKilled|cannot allocate memory|"
            r"killed process)"
        ),
        "probable_cause": (
            "The container or host may not have enough available memory."
        ),
        "recommendation": (
            "Check memory usage and configured container memory limits."
        ),
        "confidence": "high",
    },
    {
        "category": "Authentication failure",
        "pattern": (
            r"(authentication failed|access denied|unauthorized|"
            r"invalid credentials)"
        ),
        "probable_cause": (
            "The application could not authenticate to another service."
        ),
        "recommendation": (
            "Check credentials, secrets, tokens and environment variables. "
            "Do not expose secret values in logs."
        ),
        "confidence": "medium",
    },
    {
        "category": "Database connection problem",
        "pattern": (
            r"(database .* unavailable|could not connect to database|"
            r"database connection failed)"
        ),
        "probable_cause": (
            "The application could not establish a database connection."
        ),
        "recommendation": (
            "Check the database hostname, port, credentials, network "
            "and database service status."
        ),
        "confidence": "medium",
    },
]


def analyze_docker_logs(
    logs: str,
) -> dict[str, Any]:
    """
    Analyze Docker logs using known error patterns.

    The function does not access Docker directly. It only examines
    the log text provided by the user.
    """
    if not logs or not logs.strip():
        return {
            "status": "error",
            "message": "Docker logs cannot be empty.",
        }

    if len(logs) > 50_000:
        return {
            "status": "error",
            "message": (
                "The provided logs are too large. "
                "Provide at most 50,000 characters."
            ),
        }

    findings = []

    # Search the supplied logs for every known error pattern.
    for error_pattern in ERROR_PATTERNS:
        match = re.search(
            error_pattern["pattern"],
            logs,
            flags=re.IGNORECASE,
        )

        if match:
            findings.append(
                {
                    "category": error_pattern["category"],
                    "matched_text": match.group(0),
                    "probable_cause": (
                        error_pattern["probable_cause"]
                    ),
                    "recommendation": (
                        error_pattern["recommendation"]
                    ),
                    "confidence": error_pattern["confidence"],
                }
            )

    if not findings:
        return {
            "status": "no_known_pattern",
            "message": (
                "No known error pattern was identified. "
                "The logs should be analyzed manually."
            ),
            "findings": [],
        }

    return {
        "status": "findings_detected",
        "findings_count": len(findings),
        "findings": findings,
    }