# GitHub Actions troubleshooting

Use this procedure when a GitHub Actions workflow, job, step, build, test, or deployment fails.

## Information to request

Ask for:

- the repository and workflow name;
- the failed job and step;
- the relevant log output;
- the branch or pull request;
- whether the failure started after a recent change;
- whether the workflow runs in development, staging, or production deployment context.

Do not ask the user to expose secrets, tokens, private keys, or credentials.

## Initial diagnosis

Start with no more than three steps.

### 1. Inspect the failed step

Ask the user to open the failed workflow run and provide:

- the failed job name;
- the failed step name;
- the exact error message;
- several lines before and after the error.

Do not diagnose only from the workflow status.

### 2. Check the workflow trigger and branch

Inspect the workflow file:

```yaml
on:
  push:
  pull_request:
  workflow_dispatch:
```

Check whether:

- the expected branch matches the trigger;
- path filters exclude the changed files;
- the workflow is disabled;
- the event is different from what the job expects.

### 3. Check recent changes

Ask whether the failure appeared after changes to:

- the workflow YAML;
- dependencies;
- build scripts;
- Dockerfiles;
- environment variables;
- deployment configuration;
- permissions.

Use this information to choose the next checks.

## Follow-up diagnosis

Only recommend checks relevant to the observed error.

### YAML or workflow syntax problems

Validate:

- indentation;
- job and step structure;
- reusable workflow syntax;
- expression syntax;
- referenced actions and versions.

Use the GitHub Actions interface error message before suggesting changes.

### Permission problems

Check the workflow permissions:

```yaml
permissions:
  contents: read
```

Depending on the operation, additional permissions may be required, such as:

```yaml
permissions:
  contents: write
  packages: write
  id-token: write
```

Do not recommend broad write permissions unless they are necessary.

### Secret or variable problems

Check that:

- the secret or variable exists;
- the name matches exactly;
- repository, environment, or organization scope is correct;
- the target environment allows access;
- pull requests from forks are not blocked from accessing secrets.

Never ask the user to paste secret values.

### Dependency or build failures

Check:

- dependency lock files;
- runtime version;
- package manager cache;
- working directory;
- build command;
- test command;
- artifact paths.

Do not assume that clearing caches will fix the issue.

### Docker build failures

Inspect the exact failing Docker build step.

Useful local comparison:

```bash
docker build .
```

If the workflow uses Buildx or multiple platforms, verify the same configuration before comparing results.

### Deployment failures

Check:

- authentication;
- target environment;
- deployment permissions;
- artifact availability;
- image tags;
- environment protection rules;
- service health after deployment.

Treat production deployments as potentially disruptive.

## Corrective actions

Make the smallest justified change.

Possible actions include:

- correcting workflow syntax;
- fixing a secret or variable name;
- pinning a compatible action version;
- correcting the runtime version;
- fixing a path or working directory;
- adjusting only the required permissions.

Do not rerun failed deployments repeatedly without understanding the failure.

## Verification

After a change:

- run the workflow again;
- confirm that the previously failing step succeeds;
- inspect later jobs for secondary failures;
- verify the deployed service when deployment is involved.

Do not claim the pipeline is fixed until the new workflow run completes successfully.