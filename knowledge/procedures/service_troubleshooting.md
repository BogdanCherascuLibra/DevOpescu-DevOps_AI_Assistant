# Linux service troubleshooting

Use this procedure when a systemd service fails to start, stops unexpectedly, reports errors, or does not provide its expected functionality.

## Information to request

Ask for:

- the exact service name;
- the Linux distribution;
- whether the system is production;
- the observed symptom or error;
- whether restarting the service is allowed.

Do not ask again for details already provided.

## Initial diagnosis

Start with no more than three diagnostic steps.

### 1. Check service status

```bash
systemctl status SERVICE_NAME --no-pager
```

Explain that this shows the service state, recent errors, exit code, and process information.

Ask the user to provide the relevant output.

### 2. Inspect recent logs

```bash
journalctl -u SERVICE_NAME --since "30 minutes ago" --no-pager
```

If the failure happened earlier, adapt the time range.

### 3. Check the service definition

```bash
systemctl cat SERVICE_NAME
```

Use this to inspect the command, environment files, dependencies, and overrides.

## Follow-up diagnosis

Choose only checks relevant to the evidence.

### Process state

```bash
pgrep -a SERVICE_NAME
```

Do not rely only on:

```bash
ps aux | grep SERVICE_NAME
```

because it may also match the grep command.

### Port problems

If the service should listen on a port:

```bash
ss -lntup
```

Prefer filtering when the expected port is known:

```bash
ss -lntup | grep ':PORT'
```

### Resource problems

```bash
free -h
df -h
```

Use these only when logs suggest memory, disk, or resource exhaustion.

### Configuration problems

Validate configuration before restarting whenever the service provides a validation command.

Examples:

```bash
nginx -t
apachectl configtest
sshd -t
```

Do not invent a validation command for an unknown service.

### Dependency problems

Check failed dependencies:

```bash
systemctl list-dependencies SERVICE_NAME
systemctl --failed
```

## Corrective actions

Restart only after identifying a probable cause and obtaining permission when the environment is sensitive:

```bash
sudo systemctl restart SERVICE_NAME
```

Warn that restarting may cause temporary downtime.

Do not recommend disabling security controls, changing permissions broadly, or deleting service data without explicit justification and confirmation.

## Verification

After corrective action:

```bash
systemctl status SERVICE_NAME --no-pager
journalctl -u SERVICE_NAME --since "5 minutes ago" --no-pager
```

If relevant, verify the expected port or endpoint.

Do not claim the service is fixed unless the user provides evidence confirming normal operation.