# Infrastructure

Use the following information as the default project infrastructure context.

## Environments

- The development environment uses Ubuntu 24.04.
- Production systems use Ubuntu Server.
- Do not assume that development and production have identical configuration.

## Containers

- Applications are deployed using Docker containers.
- When troubleshooting, prefer diagnostic commands before restart, recreation, rebuild, or removal.
- Do not assume a container name, image name, Compose service, port, volume, or network unless the user provides it.

## Source control

- Source code is stored in GitHub repositories.
- Do not assume a specific repository, branch, organization, or access level.

## CI/CD

- GitHub Actions is used for CI/CD pipelines.
- When investigating pipeline failures, ask for the workflow name, failed job or step, relevant log output, branch, and recent changes.
- Do not assume that a failed deployment was caused by the application without checking the workflow logs.

## Operating principles

- Treat production changes as potentially disruptive.
- Ask whether the environment is development, staging, or production when this affects safety.
- Do not claim access to servers, repositories, containers, workflows, or logs.
- Base conclusions only on information and command output provided by the user.