# Docker container troubleshooting

Use this procedure when a Docker container does not start, exits unexpectedly, restarts repeatedly, or is unhealthy.

## Information to request

Before suggesting actions, ask for:

- the container name or ID;
- whether the environment is development, staging, or production;
- the exact symptom;
- whether restarting the container is allowed.

Do not ask again for information already provided.

## Initial diagnosis

Start with no more than three diagnostic steps.

### 1. Check container status

```bash
docker ps -a
```

Explain that this shows the container state, exit status, image, and restart behavior.

Ask the user to provide the relevant line for the affected container.

### 2. Inspect recent logs

```bash
docker logs --tail 100 CONTAINER_NAME
```

Use the container name or ID provided by the user.

Ask for the output before recommending further actions.

### 3. Inspect the container state

Prefer a focused inspection:

```bash
docker inspect CONTAINER_NAME   --format='Status={{.State.Status}} ExitCode={{.State.ExitCode}} Error={{.State.Error}} OOMKilled={{.State.OOMKilled}}'
```

Use the result to decide the next step.

## Follow-up diagnosis

Only recommend the checks that match the evidence.

### Configuration or startup command problems

```bash
docker inspect CONTAINER_NAME
```

Check:

- command and entrypoint;
- environment variables;
- restart policy;
- mounted volumes;
- exposed ports.

Do not ask the user to expose secrets from environment variables.

### Resource problems

```bash
docker stats --no-stream CONTAINER_NAME
```

Also check host resources when necessary:

```bash
free -h
df -h
```

### Volume or permission problems

Inspect mounts:

```bash
docker inspect CONTAINER_NAME   --format='{{json .Mounts}}'
```

Do not recommend `chmod 777`.

Ask for the relevant path, owner, permissions, and error message.

### Network problems

```bash
docker network ls
docker inspect CONTAINER_NAME   --format='{{json .NetworkSettings.Networks}}'
```

Check network membership, DNS resolution, ports, and dependencies.

### Image problems

```bash
docker image inspect IMAGE_NAME
```

If rebuilding is necessary, explain why before recommending it.

## Corrective actions

Do not restart, recreate, remove, or rebuild the container until a probable cause has been identified.

Before suggesting a disruptive action, warn the user about its impact.

Possible actions include:

```bash
docker restart CONTAINER_NAME
docker compose up -d --force-recreate SERVICE_NAME
docker compose build SERVICE_NAME
```

Never recommend removing containers, images, or volumes without explicit confirmation.

## Verification

After a corrective action, verify with:

```bash
docker ps
docker logs --tail 50 CONTAINER_NAME
```

Do not claim the issue is fixed unless the user provides evidence confirming normal operation.