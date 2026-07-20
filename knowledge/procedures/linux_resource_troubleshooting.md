# Linux resource troubleshooting

Use this procedure when a Linux system is slow, out of memory, low on disk space, overloaded, or experiencing high CPU usage.

## Information to request

Ask for:

- the affected host or environment;
- whether it is development, staging, or production;
- the observed symptom;
- when the problem started;
- whether a specific service or process is affected;
- whether restarts or process termination are allowed.

## Initial diagnosis

Start with no more than three steps.

### 1. Check system load and uptime

```bash
uptime
```

Explain that this shows uptime, active users, and load averages.

Ask for the output before interpreting the load.

### 2. Check memory

```bash
free -h
```

Focus on:

- available memory;
- swap usage;
- whether memory pressure is increasing.

Do not diagnose only from the `free` column.

### 3. Check disk usage

```bash
df -h
```

Look for:

- filesystems near 100%;
- full root, log, or data partitions;
- inode exhaustion if space appears available.

If needed:

```bash
df -i
```

## Follow-up diagnosis

Only use checks relevant to the symptom.

### High CPU usage

```bash
ps aux --sort=-%cpu | head
```

Or interactively:

```bash
top
```

Identify the process before suggesting any action.

### High memory usage

```bash
ps aux --sort=-%mem | head
```

Check whether the process is expected and whether usage is growing over time.

### Disk space problems

Find large directories carefully:

```bash
du -xhd1 / 2>/dev/null | sort -h
```

For a known path:

```bash
du -sh PATH/*
```

Do not recommend deleting files before identifying what they are and whether they are safe to remove.

### Log growth

Check journal usage:

```bash
journalctl --disk-usage
```

Inspect large log files:

```bash
find /var/log -type f -printf '%s %p
' 2>/dev/null | sort -n | tail
```

Do not truncate or delete logs without confirmation.

### I/O problems

```bash
iostat
```

If unavailable, do not assume it is installed.

Use system logs and process state to determine whether storage is the bottleneck.

### Process or service problems

For a known service:

```bash
systemctl status SERVICE_NAME --no-pager
```

For a known process:

```bash
ps -fp PID
```

## Corrective actions

Only suggest an action after identifying a probable cause.

Potentially disruptive actions include:

- restarting a service;
- stopping or killing a process;
- deleting files;
- clearing caches;
- changing resource limits;
- adding swap;
- resizing a filesystem.

Warn the user and ask for confirmation when production may be affected.

Never recommend deleting unknown files or using broad commands such as:

```bash
rm -rf
```

without a verified target and explicit confirmation.

## Verification

After corrective action, repeat the relevant checks:

```bash
uptime
free -h
df -h
```

Also verify the affected service or process.

Do not claim the issue is fixed unless the resource pressure is reduced and the affected workload operates normally.